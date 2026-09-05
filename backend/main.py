# main.py
import asyncio
import contextlib
from contextlib import asynccontextmanager
import json
import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models
import schemas
from auth import ALGORITHM, SECRET_KEY, authenticate_officer, create_access_token, get_current_officer, require_clearance
from database import Base, LIVE_FEED_CHANNEL, engine, get_db, get_redis, redis_pool
from auth import authenticate_officer, create_access_token, get_current_officer, require_clearance
from database import Base, engine, get_db, get_redis, redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    redis_client = get_redis()
    await redis_client.ping()

    feed_task = asyncio.create_task(_redis_feed_listener())

    yield

    feed_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await feed_task
    await redis_pool.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Intelligence Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> schemas.Token:
    officer = await authenticate_officer(db, form_data.username, form_data.password)
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(
        subject=officer.email, clearance_level=officer.clearance_level
    )
    return schemas.Token(access_token=token, expires_in=expires_in)


@app.post(
    "/officers",
    response_model=schemas.OfficerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_officer(
    officer_in: schemas.OfficerCreate,
    db: AsyncSession = Depends(get_db),
    _: models.Officer = Depends(require_clearance(10)),
) -> models.Officer:
    existing = await crud.get_officer_by_email(db, officer_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Officer with this email already exists",
        )
    return await crud.create_officer(db, officer_in)


@app.get("/officers/me", response_model=schemas.OfficerRead)
async def read_current_officer(
    current_officer: models.Officer = Depends(get_current_officer),
) -> models.Officer:
    return current_officer


@app.post(
    "/threats",
    response_model=schemas.ThreatPostRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_threat(
    post_in: schemas.ThreatPostCreate,
    db: AsyncSession = Depends(get_db),
    _: models.Officer = Depends(get_current_officer),
) -> models.ThreatPost:
    return await crud.create_threat_post(db, post_in)


@app.get("/threats", response_model=schemas.ThreatPostList)
async def list_threats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    min_threat_level: int | None = Query(None, ge=1, le=5),
    is_resolved: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: models.Officer = Depends(get_current_officer),
) -> schemas.ThreatPostList:
    items, total = await crud.list_threat_posts(
        db, skip=skip, limit=limit, min_threat_level=min_threat_level, is_resolved=is_resolved
    )
    return schemas.ThreatPostList(total=total, items=items)


@app.get("/threats/{post_id}", response_model=schemas.ThreatPostRead)
async def get_threat(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: models.Officer = Depends(get_current_officer),
) -> models.ThreatPost:
    post = await crud.get_threat_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat post not found")
    return post


@app.patch("/threats/{post_id}", response_model=schemas.ThreatPostRead)
async def update_threat(
    post_id: uuid.UUID,
    post_in: schemas.ThreatPostUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.Officer = Depends(require_clearance(3)),
) -> models.ThreatPost:
    post = await crud.update_threat_post(db, post_id, post_in)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat post not found")
    return post


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

class ConnectionManager:
    """Tracks live WebSocket clients and fans out messages to all of them."""

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, officer_id: uuid.UUID) -> None:
        await websocket.accept()
        self._connections.setdefault(officer_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, officer_id: uuid.UUID) -> None:
        sockets = self._connections.get(officer_id)
        if sockets and websocket in sockets:
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(officer_id, None)

    async def broadcast(self, message: str) -> None:
        dead: list[tuple[uuid.UUID, WebSocket]] = []
        for officer_id, sockets in self._connections.items():
            for ws in sockets:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append((officer_id, ws))
        for officer_id, ws in dead:
            self.disconnect(ws, officer_id)

manager = ConnectionManager()

async def _authenticate_websocket(
    websocket: WebSocket, db: AsyncSession
) -> models.Officer | None:
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    officer = await crud.get_officer_by_email(db, email)
    if officer is None or not officer.is_active:
        return None
    return officer

@app.websocket("/ws/live-feed")
async def live_feed(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    officer = await _authenticate_websocket(websocket, db)
    if officer is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, officer.id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, officer.id)
    except Exception:
        manager.disconnect(websocket, officer.id)

async def _redis_feed_listener() -> None:
    redis_client = get_redis()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(LIVE_FEED_CHANNEL)
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            await manager.broadcast(message["data"])
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(LIVE_FEED_CHANNEL)
        await pubsub.close()