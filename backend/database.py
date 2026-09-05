# database.py
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncClient, AsyncDatabase, AsyncCollection

# MongoDB connection
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017",
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "intel_dashboard")

# Create MongoDB client
client: AsyncClient = None
db: AsyncDatabase = None


async def connect_to_mongo():
    """Connect to MongoDB on app startup"""
    global client, db
    try:
        client = AsyncClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        # Verify connection
        await client.admin.command('ping')
        print(f"Connected to MongoDB: {DATABASE_NAME}")
        # Create indexes
        await create_indexes()
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection on app shutdown"""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Officers collection indexes
        officers = db["officers"]
        await officers.create_index("email", unique=True)
        await officers.create_index("is_active")
        
        # ThreatPosts collection indexes
        threats = db["threat_posts"]
        await threats.create_index("platform")
        await threats.create_index("threat_level")
        await threats.create_index("is_resolved")
        await threats.create_index("timestamp", background=True)
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")


def get_database() -> AsyncDatabase:
    """Get the MongoDB database instance"""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db


def get_officers_collection() -> AsyncCollection:
    """Get the officers collection"""
    return get_database()["officers"]


def get_threats_collection() -> AsyncCollection:
    """Get the threat_posts collection"""
    return get_database()["threat_posts"]


@asynccontextmanager
async def lifespan_resources():
    """Call on app startup/shutdown to validate connectivity and dispose cleanly."""
    try:
        await connect_to_mongo()
        yield
    finally:
        await close_mongo_connection()