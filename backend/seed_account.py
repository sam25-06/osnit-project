"""Create or verify a development officer account in MongoDB."""
import argparse
import asyncio
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

import database
from auth import hash_password

DEFAULT_EMAIL = "test@example.com"
DEFAULT_PASSWORD = "testpassword123"


async def seed_account(email: str, password: str, clearance_level: int) -> None:
    await database.connect_to_mongo()
    try:
        collection = database.get_officers_collection()
        existing = await collection.find_one({"email": email})

        if existing:
            await collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"is_active": True, "clearance_level": clearance_level}},
            )
            print(f"Account already exists and is active: {email}")
        else:
            await collection.insert_one(
                {
                    "email": email,
                    "hashed_password": hash_password(password),
                    "clearance_level": clearance_level,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                }
            )
            print(f"Created account: {email}")

        print(f"Password: {password}")
        print(f"Clearance level: {clearance_level}")
    finally:
        await database.close_mongo_connection()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--clearance-level", type=int, default=10, choices=range(1, 11))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    asyncio.run(seed_account(arguments.email, arguments.password, arguments.clearance_level))
