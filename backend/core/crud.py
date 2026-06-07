from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import (
    Suggestion,
    User,
    UserContact,
    UserHobby,
    UserProfileFact,
)


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_hobbies(session: AsyncSession, user_id: UUID) -> list[UserHobby]:
    result = await session.execute(
        select(UserHobby).where(UserHobby.user_id == user_id, UserHobby.enabled.is_(True))
    )
    return list(result.scalars().all())


async def get_active_profile_facts(
    session: AsyncSession, user_id: UUID, *, at: datetime | None = None
) -> list[UserProfileFact]:
    now = at or datetime.now(UTC)
    result = await session.execute(
        select(UserProfileFact).where(
            UserProfileFact.user_id == user_id,
            (UserProfileFact.valid_until.is_(None)) | (UserProfileFact.valid_until > now),
        )
    )
    return list(result.scalars().all())


async def get_user_contacts(session: AsyncSession, user_id: UUID) -> list[UserContact]:
    result = await session.execute(select(UserContact).where(UserContact.user_id == user_id))
    return list(result.scalars().all())


async def count_suggestions_sent_today(
    session: AsyncSession, user_id: UUID, *, at: datetime | None = None
) -> int:
    now = at or datetime.now(UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(Suggestion).where(
            Suggestion.user_id == user_id,
            Suggestion.sent_at.isnot(None),
            Suggestion.sent_at >= start_of_day,
        )
    )
    return len(list(result.scalars().all()))
