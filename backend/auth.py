"""Authentication and authorization logic for MongoDB"""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

import crud
import models
from database import get_officers_collection
from password_utils import hash_password as _hash_password
from password_utils import verify_password as _verify_password

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return _hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return _verify_password(plain_password, hashed_password)


def create_access_token(subject: str, clearance_level: int) -> tuple[str, int]:
    """Create JWT access token"""
    expire_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expire_delta
    payload = {
        "sub": subject,
        "clearance_level": clearance_level,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expire_delta.total_seconds())


async def authenticate_officer(
    officers_collection, email: str, password: str
) -> models.Officer | None:
    """Authenticate officer by email and password"""
    officer = await crud.get_officer_by_email(officers_collection, email)
    if not officer or not officer.is_active:
        return None
    if not verify_password(password, officer.hashed_password):
        return None
    return officer


async def get_current_officer(
    officers_collection=None,
    token: str = Depends(oauth2_scheme),
) -> models.Officer:
    """Get current officer from JWT token"""
    if officers_collection is None:
        officers_collection = get_officers_collection()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    officer = await crud.get_officer_by_email(officers_collection, email)
    if officer is None or not officer.is_active:
        raise credentials_exception
    return officer


def require_clearance(minimum_level: int, officers_collection_dep=None):
    """Factory for creating clearance-level checkers"""
    async def _checker(
        current_officer: models.Officer = Depends(lambda: get_current_officer(officers_collection_dep)),
    ) -> models.Officer:
        if current_officer.clearance_level < minimum_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient clearance level",
            )
        return current_officer

    return _checker
