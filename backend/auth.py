# auth.py
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models
from database import get_db

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, clearance_level: int) -> tuple[str, int]:
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
    db: AsyncSession, email: str, password: str
) -> models.Officer | None:
    officer = await crud.get_officer_by_email(db, email)
    if not officer or not officer.is_active:
        return None
    if not verify_password(password, officer.hashed_password):
        return None
    return officer


async def get_current_officer(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> models.Officer:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    officer = await crud.get_officer_by_email(db, email)
    if officer is None or not officer.is_active:
        raise credentials_exception
    return officer


def require_clearance(minimum_level: int):
    async def _checker(
        current_officer: models.Officer = Depends(get_current_officer),
    ) -> models.Officer:
        if current_officer.clearance_level < minimum_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient clearance level",
            )
        return current_officer

    return _checker