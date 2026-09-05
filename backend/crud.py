# crud.py
"""MongoDB CRUD operations using Motor (async MongoDB driver)"""
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

import models
import schemas
from password_utils import hash_password


# ---------- Officer ----------
async def get_officer_by_email(
    collection: AsyncIOMotorCollection, email: str
) -> models.Officer | None:
    """Get officer by email"""
    doc = await collection.find_one({"email": email})
    return models.Officer(**doc) if doc else None


async def get_officer_by_id(
    collection: AsyncIOMotorCollection, officer_id: str
) -> models.Officer | None:
    """Get officer by ID"""
    try:
        doc = await collection.find_one({"_id": ObjectId(officer_id)})
        return models.Officer(**doc) if doc else None
    except Exception:
        return None


async def create_officer(
    collection: AsyncIOMotorCollection, officer_in: schemas.OfficerCreate
) -> models.Officer:
    """Create new officer"""
    officer_dict = {
        "email": officer_in.email,
        "hashed_password": hash_password(officer_in.password),
        "clearance_level": officer_in.clearance_level,
        "is_active": True,
        "created_at": models.datetime.utcnow(),
    }
    result = await collection.insert_one(officer_dict)
    officer_dict["_id"] = result.inserted_id
    return models.Officer(**officer_dict)


# ---------- ThreatPost ----------
async def create_threat_post(
    collection: AsyncIOMotorCollection, post_in: schemas.ThreatPostCreate
) -> models.ThreatPost:
    """Create new threat post"""
    threat_dict = post_in.model_dump()
    threat_dict["timestamp"] = models.datetime.utcnow()
    threat_dict["is_resolved"] = False
    result = await collection.insert_one(threat_dict)
    threat_dict["_id"] = result.inserted_id
    return models.ThreatPost(**threat_dict)


async def get_threat_post(
    collection: AsyncIOMotorCollection, post_id: str
) -> models.ThreatPost | None:
    """Get threat post by ID"""
    try:
        doc = await collection.find_one({"_id": ObjectId(post_id)})
        return models.ThreatPost(**doc) if doc else None
    except Exception:
        return None


async def list_threat_posts(
    collection: AsyncIOMotorCollection,
    skip: int = 0,
    limit: int = 50,
    min_threat_level: int | None = None,
    is_resolved: bool | None = None,
) -> tuple[list[models.ThreatPost], int]:
    """List threat posts with filtering and pagination"""
    query = {}
    
    if min_threat_level is not None:
        query["threat_level"] = {"$gte": min_threat_level}
    if is_resolved is not None:
        query["is_resolved"] = is_resolved
    
    # Get total count
    total = await collection.count_documents(query)
    
    # Get paginated results
    cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    threats = [models.ThreatPost(**doc) for doc in docs]
    return threats, total


async def update_threat_post(
    collection: AsyncIOMotorCollection, post_id: str, post_in: schemas.ThreatPostUpdate
) -> models.ThreatPost | None:
    """Update threat post"""
    try:
        values = post_in.model_dump(exclude_unset=True)
        if not values:
            return await get_threat_post(collection, post_id)
        
        result = await collection.find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$set": values},
            return_document=True
        )
        return models.ThreatPost(**result) if result else None
    except Exception:
        return None