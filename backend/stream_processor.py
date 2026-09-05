# stream_processor.py
"""
Standalone async Kafka consumer. Run as its own process/deployment:
    python stream_processor.py
Deliberately decoupled from the FastAPI process — broadcasts to
WebSocket clients via Redis pub/sub rather than in-memory state.
"""
import asyncio
import json
import logging
import os
import signal
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

import crud
import schemas
from database import AsyncSessionLocal, LIVE_FEED_CHANNEL, get_redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("stream_processor")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "social_intel_raw"
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "intel-dashboard-stream-processor")

_shutdown_event = asyncio.Event()

# High-signal keywords for the mock model. Swap this whole function for a
# real inference call (local model / hosted NLP endpoint) later — the
# interface (raw text in, (threat_level, panic_score) out) stays the same.
_HIGH_SEVERITY_TERMS = {"bomb", "attack", "weapon", "explosive", "kill", "shooting"}
_MEDIUM_SEVERITY_TERMS = {"threat", "riot", "protest", "unrest", "hostage"}


def mock_nlp_analysis(content: str) -> tuple[int, float]:
    """Deterministic placeholder NLP scorer. Returns (threat_level 1-5, panic_score 0-100)."""
    text = content.lower()
    hits_high = sum(1 for term in _HIGH_SEVERITY_TERMS if term in text)
    hits_medium = sum(1 for term in _MEDIUM_SEVERITY_TERMS if term in text)

    if hits_high >= 2:
        threat_level = 5
    elif hits_high == 1:
        threat_level = 4
    elif hits_medium >= 2:
        threat_level = 3
    elif hits_medium == 1:
        threat_level = 2
    else:
        threat_level = 1

    length_factor = min(len(text) / 500, 1.0) * 10
    panic_score = min(100.0, (hits_high * 30) + (hits_medium * 15) + length_factor)

    return threat_level, round(panic_score, 2)


async def handle_message(raw_value: bytes) -> None:
    try:
        payload = json.loads(raw_value.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("Skipping unparseable message: %s", exc)
        return

    content = payload.get("content")
    platform = payload.get("platform")
    if not content or not platform:
        logger.warning("Skipping message missing content/platform: %s", payload)
        return

    threat_level, panic_score = mock_nlp_analysis(content)

    post_in = schemas.ThreatPostCreate(
        content=content,
        platform=platform,
        threat_level=threat_level,
        panic_score=panic_score,
    )

    async with AsyncSessionLocal() as db:
        post = await crud.create_threat_post(db, post_in)

    post_out = schemas.ThreatPostRead.model_validate(post).model_dump(mode="json")

    redis_client = get_redis()
    await redis_client.publish(LIVE_FEED_CHANNEL, json.dumps(post_out))

    logger.info(
        "Processed post %s | platform=%s level=%s panic=%s",
        post_out["id"], platform, threat_level, panic_score,
    )


async def consume() -> None:
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        enable_auto_commit=False,       # commit manually after DB + publish succeed
        auto_offset_reset="earliest",
        value_deserializer=lambda v: v,  # raw bytes; we decode ourselves for error isolation
    )

    started = False
    backoff = 1
    while not started and not _shutdown_event.is_set():
        try:
            await consumer.start()
            started = True
        except KafkaConnectionError as exc:
            logger.error("Kafka connection failed (%s). Retrying in %ss...", exc, backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

    if not started:
        return

    logger.info("Consumer started. Listening on topic '%s'...", KAFKA_TOPIC)
    try:
        async for msg in consumer:
            if _shutdown_event.is_set():
                break
            try:
                await handle_message(msg.value)
                await consumer.commit()
            except Exception:
                # Isolate per-message failures — log and move on rather than
                # crashing the whole consumer loop over one bad record.
                logger.exception("Failed to process message at offset %s", msg.offset)
    finally:
        await consumer.stop()
        logger.info("Consumer stopped cleanly.")


def _handle_shutdown_signal(*_args) -> None:
    logger.info("Shutdown signal received.")
    _shutdown_event.set()


async def main() -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_shutdown_signal)
        except NotImplementedError:
            pass  # Windows fallback — Ctrl+C still raises KeyboardInterrupt

    await consume()


if __name__ == "__main__":
    asyncio.run(main())