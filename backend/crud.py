# crud.py
import uuid
from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from auth import hash_password


# ---------- Officer ----------
async def get_officer_by_email(db: AsyncSession, email: str) -> models.Officer | None:
    result = await db.execute(
        select(models.Officer).where(models.Officer.email == email)
    )
    return result.scalar_one_or_none()


async def get_officer_by_id(db: AsyncSession, officer_id: uuid.UUID) -> models.Officer | None:
    result = await db.execute(
        select(models.Officer).where(models.Officer.id == officer_id)
    )
    return result.scalar_one_or_none()


async def create_officer(db: AsyncSession, officer_in: schemas.OfficerCreate) -> models.Officer:
    officer = models.Officer(
        email=officer_in.email,
        hashed_password=hash_password(officer_in.password),
        clearance_level=officer_in.clearance_level,
    )
    db.add(officer)
    await db.commit()
    await db.refresh(officer)
    return officer


# ---------- ThreatPost ----------
async def create_threat_post(
    db: AsyncSession, post_in: schemas.ThreatPostCreate
) -> models.ThreatPost:
    post = models.ThreatPost(**post_in.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_threat_post(
    db: AsyncSession, post_id: uuid.UUID
) -> models.ThreatPost | None:
    result = await db.execute(
        select(models.ThreatPost).where(models.ThreatPost.id == post_id)
    )
    return result.scalar_one_or_none()


async def list_threat_posts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    min_threat_level: int | None = None,
    is_resolved: bool | None = None,
) -> tuple[Sequence[models.ThreatPost], int]:
    query = select(models.ThreatPost)
    count_query = select(func.count()).select_from(models.ThreatPost)

    if min_threat_level is not None:
        query = query.where(models.ThreatPost.threat_level >= min_threat_level)
        count_query = count_query.where(
            models.ThreatPost.threat_level >= min_threat_level
        )
    if is_resolved is not None:
        query = query.where(models.ThreatPost.is_resolved == is_resolved)
        count_query = count_query.where(models.ThreatPost.is_resolved == is_resolved)

    query = query.order_by(models.ThreatPost.timestamp.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    total_result = await db.execute(count_query)

    return result.scalars().all(), total_result.scalar_one()


async def update_threat_post(
    db: AsyncSession, post_id: uuid.UUID, post_in: schemas.ThreatPostUpdate
) -> models.ThreatPost | None:
    values = post_in.model_dump(exclude_unset=True)
    if not values:
        return await get_threat_post(db, post_id)

    await db.execute(
        update(models.ThreatPost)
        .where(models.ThreatPost.id == post_id)
        .values(**values)
    )
    await db.commit()
    return await get_threat_post(db, post_id)