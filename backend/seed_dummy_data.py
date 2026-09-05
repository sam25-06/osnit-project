"""Replace the MongoDB threat feed with deterministic demo records."""
import asyncio
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

import crud
import database
import schemas


DEMO_POSTS = [
    ("twitter", "Transit station closure reported after unattended package near the east entrance.", 3, 54),
    ("telegram", "Local emergency services are responding to reports of smoke near the industrial district.", 4, 72),
    ("reddit", "Residents report a loud explosion followed by a brief power outage downtown.", 4, 78),
    ("news", "Authorities issue a precautionary evacuation notice for the waterfront market.", 3, 61),
    ("facebook", "Multiple eyewitnesses describe a suspicious vehicle circling the civic center.", 2, 38),
    ("twitter", "Police presence increased around the central rail interchange after a security alert.", 2, 35),
    ("telegram", "Unverified claim of a weapon sighting outside the south checkpoint.", 5, 88),
    ("reddit", "Crowd gathering near the stadium entrance is causing traffic and public-safety concerns.", 2, 42),
    ("news", "Fire crews contain a warehouse fire; investigators have not identified a cause.", 3, 57),
    ("facebook", "Residents hear repeated loud bangs in the north neighborhood overnight.", 3, 63),
    ("twitter", "Anonymous account posts a direct threat against a public event scheduled this weekend.", 5, 94),
    ("telegram", "Roadblocks reported on the western approach to the airport.", 3, 58),
    ("reddit", "Community volunteers report broken barriers around a restricted construction site.", 2, 31),
    ("news", "Emergency management team opens a temporary coordination center near the harbor.", 2, 28),
    ("facebook", "Several schools move outdoor activities indoors after a regional safety advisory.", 2, 40),
    ("twitter", "Video appears to show an altercation near the courthouse; authenticity is unconfirmed.", 3, 59),
    ("telegram", "Reports of an explosive device are being investigated at a commercial property.", 5, 91),
    ("reddit", "Residents report internet and mobile service disruption across three neighborhoods.", 2, 36),
    ("news", "Coast guard issues a warning after an unidentified vessel enters the restricted zone.", 3, 52),
    ("facebook", "Large protest forms outside the municipal building with traffic beginning to back up.", 3, 66),
    ("twitter", "Security staff report an attempted breach of a service entrance at the arena.", 4, 74),
    ("telegram", "A public account calls for an attack on a government facility; authorities are reviewing it.", 5, 97),
    ("reddit", "Minor riot reported after a sports match; police have restored access to the main road.", 4, 76),
    ("news", "Flooding blocks two underpasses and slows emergency response routes.", 3, 49),
    ("facebook", "Neighborhood group reports a suspicious package outside a residential building.", 3, 55),
    ("twitter", "Authorities ask residents to avoid the north plaza while an incident is assessed.", 2, 43),
    ("telegram", "Hostage situation rumor spreads online but has not been confirmed by officials.", 4, 79),
    ("reddit", "Power substation alarm triggers a brief evacuation of nearby maintenance crews.", 3, 51),
    ("news", "Airport screening delays follow discovery of prohibited items in a passenger area.", 3, 48),
    ("facebook", "Public gathering remains peaceful despite rising tension between two groups.", 2, 34),
    ("twitter", "Threatening graffiti discovered on the wall of a public services building.", 4, 69),
    ("telegram", "Emergency alert warns of possible unrest near the distribution center tonight.", 4, 73),
    ("reddit", "Firefighters respond to a suspected chemical leak at a research facility.", 4, 81),
    ("news", "City officials announce additional patrols after a series of theft reports.", 2, 29),
    ("facebook", "A witness reports seeing someone carrying a weapon near the stadium parking area.", 5, 90),
    ("twitter", "Transport workers begin a protest that may affect morning commuter routes.", 3, 56),
    ("telegram", "Unusual drone activity reported near a protected government complex.", 4, 77),
    ("reddit", "Residents report a loud argument and possible assault outside a nightlife district.", 3, 62),
    ("news", "Emergency services issue an all-clear after inspecting a suspicious container.", 2, 24),
    ("facebook", "Community leaders ask residents not to share unverified attack rumors.", 1, 18),
]


async def seed_dummy_data() -> None:
    await database.connect_to_mongo()
    try:
        collection = database.get_threats_collection()
        await collection.delete_many({"content": {"$regex": "^\\[DEMO\\]"}})

        now = datetime.now(timezone.utc)
        for index, (platform, content, threat_level, panic_score) in enumerate(DEMO_POSTS):
            post = schemas.ThreatPostCreate(
                content=f"[DEMO] {content}",
                platform=platform,
                threat_level=threat_level,
                panic_score=panic_score,
            )
            document = post.model_dump()
            document["timestamp"] = now - timedelta(minutes=index * 7)
            document["is_resolved"] = index % 7 == 0
            await collection.insert_one(document)

        demo_count = await collection.count_documents({"content": {"$regex": "^\\[DEMO\\]"}})
        print(f"Seeded {demo_count} demo threat posts into threat_posts")
    finally:
        await database.close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed_dummy_data())
