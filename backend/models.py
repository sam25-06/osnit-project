# models.py
"""
MongoDB document models using Pydantic.
These define the structure of documents stored in MongoDB.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId serialization"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            return ObjectId(v)
        raise ValueError(f"Invalid ObjectId: {v}")

    def __repr__(self):
        return f"ObjectId('{self}')'"


class Officer(BaseModel):
    """Officer document model"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str = Field(..., index=True, unique=True)
    hashed_password: str
    clearance_level: int = Field(default=1, ge=1, le=10)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


class ThreatPost(BaseModel):
    """ThreatPost document model"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    content: str = Field(..., max_length=4000)
    platform: str = Field(..., max_length=100, index=True)
    threat_level: int = Field(..., ge=1, le=5, index=True)
    panic_score: int = Field(default=0, ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    is_resolved: bool = Field(default=False, index=True)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True