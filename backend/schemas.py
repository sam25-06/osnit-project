"""Request/Response Pydantic schemas for MongoDB"""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom Pydantic ObjectId type for JSON serialization"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if isinstance(v, cls):
            return v
        if isinstance(v, ObjectId):
            return cls(v)
        return cls(v)


# ---------- Officer ----------
class OfficerBase(BaseModel):
    email: EmailStr
    clearance_level: Annotated[int, Field(ge=1, le=10)] = 1


class OfficerCreate(OfficerBase):
    password: Annotated[str, Field(min_length=8, max_length=128)]


class OfficerRead(OfficerBase):
    model_config = ConfigDict(from_attributes=True)

    id: PyObjectId
    is_active: bool


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str
    clearance_level: int
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]


# ---------- ThreatPost ----------
class ThreatPostBase(BaseModel):
    content: Annotated[str, Field(min_length=1, max_length=4000)]
    platform: Annotated[str, Field(min_length=1, max_length=100)]
    threat_level: Annotated[int, Field(ge=1, le=5)]
    panic_score: Annotated[float, Field(ge=0.0, le=100.0)] = 0.0

    @field_validator("platform")
    @classmethod
    def normalize_platform(cls, v: str) -> str:
        return v.strip().lower()


class ThreatPostCreate(ThreatPostBase):
    pass


class ThreatPostUpdate(BaseModel):
    threat_level: Annotated[int, Field(ge=1, le=5)] | None = None
    panic_score: Annotated[float, Field(ge=0.0, le=100.0)] | None = None
    is_resolved: bool | None = None


class ThreatPostRead(ThreatPostBase):
    model_config = ConfigDict(from_attributes=True)

    id: PyObjectId
    timestamp: datetime
    is_resolved: bool


class ThreatPostList(BaseModel):
    total: int
    items: list[ThreatPostRead]
