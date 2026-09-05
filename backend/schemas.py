# schemas.py
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ---------- Officer ----------
class OfficerBase(BaseModel):
    email: EmailStr
    clearance_level: Annotated[int, Field(ge=1, le=10)] = 1


class OfficerCreate(OfficerBase):
    password: Annotated[str, Field(min_length=8, max_length=128)]


class OfficerRead(OfficerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
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

    id: uuid.UUID
    timestamp: datetime
    is_resolved: bool


class ThreatPostList(BaseModel):
    total: int
    items: list[ThreatPostRead]