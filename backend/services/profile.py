"""Profile CRUD — contacts, hobbies, facts, conversations."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.learning import ExtractedFact, _fact_matches_delete
from backend.models import Conversation, User, UserContact, UserHobby, UserProfileFact
from backend.skills import SKILL_REGISTRY

HOBBY_KEY_ALIASES: dict[str, str] = {
    "min_wave": "min_wave_height",
    "max_wave": "max_wave_height",
    "min_wind": "min_wind_knots",
    "max_wind": "max_wind_knots",
    "min_period": "min_swell_period",
    "min_temp": "min_temp_c",
    "max_rain": "max_rain_probability",
}


def normalize_hobby_config_key(key: str) -> str:
    key = key.strip()
    return HOBBY_KEY_ALIASES.get(key, key)


def parse_config_value(raw: str) -> bool | int | float | str:
    lower = raw.lower()
    if lower in ("true", "yes"):
        return True
    if lower in ("false", "no"):
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


async def get_or_create_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int,
    *,
    telegram_username: str | None = None,
) -> tuple[User, bool]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user:
        if telegram_username and user.telegram_username != telegram_username:
            user.telegram_username = telegram_username
        return user, False

    user = User(telegram_id=telegram_id, telegram_username=telegram_username)
    session.add(user)
    await session.flush()
    return user, True


async def record_conversation(
    session: AsyncSession,
    user_id: UUID,
    *,
    direction: str,
    message_text: str,
    extracted_facts: list[dict] | None = None,
) -> Conversation:
    entry = Conversation(
        user_id=user_id,
        direction=direction,
        channel="telegram",
        message_text=message_text,
        extracted_facts={"facts": extracted_facts} if extracted_facts else None,
    )
    session.add(entry)
    await session.flush()
    return entry


async def build_user_context(session: AsyncSession, user: User) -> dict:
    facts = await get_active_profile_facts(session, user.id)
    hobbies = await list_hobbies(session, user.id)
    contacts = await list_contacts(session, user.id)
    return {
        "user": {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "telegram_username": user.telegram_username,
            "timezone": user.timezone,
            "location_lat": user.location_lat,
            "location_lng": user.location_lng,
            "location_label": user.location_label,
            "profile_facts": [
                {
                    "id": str(f.id),
                    "category": f.category,
                    "fact": f.fact,
                    "valid_until": f.valid_until.isoformat() if f.valid_until else None,
                    "source": f.source,
                }
                for f in facts
            ],
            "hobbies": [
                {"hobby_type": h.hobby_type, "enabled": h.enabled, "config": h.config}
                for h in hobbies
            ],
            "contacts": [
                {
                    "name": c.name,
                    "relationship_type": c.relationship_type,
                    "contact_frequency_days": c.contact_frequency_days,
                }
                for c in contacts
            ],
        }
    }


# ── Contacts ─────────────────────────────────────────────────────────────────


async def list_contacts(session: AsyncSession, user_id: UUID) -> list[UserContact]:
    result = await session.execute(
        select(UserContact).where(UserContact.user_id == user_id).order_by(UserContact.name)
    )
    return list(result.scalars().all())


async def add_contact(
    session: AsyncSession,
    user_id: UUID,
    *,
    name: str,
    relationship_type: str | None = None,
    frequency_days: int = 30,
) -> UserContact:
    contact = UserContact(
        user_id=user_id,
        name=name.strip(),
        relationship_type=relationship_type.strip() if relationship_type else None,
        contact_frequency_days=frequency_days,
    )
    session.add(contact)
    await session.flush()
    return contact


async def delete_contact_by_name(session: AsyncSession, user_id: UUID, name: str) -> bool:
    contacts = await list_contacts(session, user_id)
    target = name.strip().lower()
    for contact in contacts:
        if contact.name.lower() == target:
            await session.delete(contact)
            await session.flush()
            return True
    return False


def format_contacts_list(contacts: list[UserContact]) -> str:
    if not contacts:
        return "No contacts yet. Add one with:\n/add_contact Name | friend | 30"
    lines = []
    for c in contacts:
        rel = c.relationship_type or "contact"
        lines.append(f"• {c.name} ({rel}, every {c.contact_frequency_days}d)")
    return "Your contacts:\n" + "\n".join(lines)


# ── Hobbies ──────────────────────────────────────────────────────────────────


async def list_hobbies(session: AsyncSession, user_id: UUID, *, enabled_only: bool = True) -> list[UserHobby]:
    query = select(UserHobby).where(UserHobby.user_id == user_id)
    if enabled_only:
        query = query.where(UserHobby.enabled.is_(True))
    result = await session.execute(query.order_by(UserHobby.hobby_type))
    return list(result.scalars().all())


async def get_hobby(session: AsyncSession, user_id: UUID, hobby_type: str) -> UserHobby | None:
    result = await session.execute(
        select(UserHobby).where(
            UserHobby.user_id == user_id,
            UserHobby.hobby_type == hobby_type.strip().lower(),
        )
    )
    return result.scalar_one_or_none()


async def add_hobby(
    session: AsyncSession,
    user_id: UUID,
    hobby_type: str,
    *,
    config: dict | None = None,
) -> UserHobby:
    normalized = hobby_type.strip().lower()
    if normalized not in SKILL_REGISTRY:
        known = ", ".join(sorted(SKILL_REGISTRY))
        raise ValueError(f"Unknown hobby '{normalized}'. Supported: {known}")

    existing = await get_hobby(session, user_id, normalized)
    if existing:
        existing.enabled = True
        if config:
            existing.config = {**existing.config, **config}
        await session.flush()
        return existing

    hobby = UserHobby(user_id=user_id, hobby_type=normalized, config=config or {})
    session.add(hobby)
    await session.flush()
    return hobby


async def delete_hobby(session: AsyncSession, user_id: UUID, hobby_type: str) -> bool:
    hobby = await get_hobby(session, user_id, hobby_type)
    if hobby is None:
        return False
    await session.delete(hobby)
    await session.flush()
    return True


async def update_hobby_config(
    session: AsyncSession,
    user_id: UUID,
    hobby_type: str,
    config_updates: dict,
) -> UserHobby | None:
    hobby = await get_hobby(session, user_id, hobby_type)
    if hobby is None:
        return None
    hobby.config = {**hobby.config, **config_updates}
    await session.flush()
    return hobby


def format_hobbies_list(hobbies: list[UserHobby]) -> str:
    if not hobbies:
        return "No hobbies yet. Add one with:\n/add_hobby surf"
    lines = []
    for h in hobbies:
        cfg = ", ".join(f"{k}={v}" for k, v in sorted(h.config.items())) if h.config else "defaults"
        lines.append(f"• {h.hobby_type}: {cfg}")
    return "Your hobbies:\n" + "\n".join(lines)


# ── Profile facts ──────────────────────────────────────────────────────────────


async def get_active_profile_facts(
    session: AsyncSession, user_id: UUID, *, at: datetime | None = None
) -> list[UserProfileFact]:
    now = at or datetime.now(UTC)
    result = await session.execute(
        select(UserProfileFact).where(
            UserProfileFact.user_id == user_id,
            (UserProfileFact.valid_until.is_(None)) | (UserProfileFact.valid_until > now),
        ).order_by(UserProfileFact.created_at)
    )
    return list(result.scalars().all())


async def add_profile_fact(
    session: AsyncSession,
    user_id: UUID,
    *,
    category: str,
    fact: str,
    valid_until: datetime | None = None,
    source: str = "telegram",
) -> UserProfileFact:
    entry = UserProfileFact(
        user_id=user_id,
        category=category.strip(),
        fact=fact.strip(),
        valid_until=valid_until,
        source=source,
    )
    session.add(entry)
    await session.flush()
    return entry


async def delete_profile_fact(
    session: AsyncSession, user_id: UUID, id_or_keyword: str
) -> bool:
    facts = await get_active_profile_facts(session, user_id)
    needle = id_or_keyword.strip().lower()

    try:
        fact_id = UUID(id_or_keyword.strip())
        for fact in facts:
            if fact.id == fact_id:
                await session.delete(fact)
                await session.flush()
                return True
        return False
    except ValueError:
        pass

    for fact in facts:
        if needle in fact.fact.lower() or needle in str(fact.id).lower():
            await session.delete(fact)
            await session.flush()
            return True
    return False


async def persist_extracted_facts(
    session: AsyncSession, user_id: UUID, extracted: list[ExtractedFact]
) -> int:
    """Apply extracted facts to the database. Returns number of changes."""
    if not extracted:
        return 0

    changes = 0
    facts = await get_active_profile_facts(session, user_id)

    for item in extracted:
        if item.action == "delete":
            for fact in list(facts):
                if _fact_matches_delete(item.fact, fact.fact):
                    await session.delete(fact)
                    facts.remove(fact)
                    changes += 1
            continue

        if item.action == "update":
            replaced = False
            for fact in facts:
                if fact.category == item.category:
                    fact.fact = item.fact
                    fact.valid_until = item.valid_until
                    fact.source = "conversation"
                    replaced = True
                    changes += 1
                    break
            if not replaced:
                new_fact = await add_profile_fact(
                    session,
                    user_id,
                    category=item.category,
                    fact=item.fact,
                    valid_until=item.valid_until,
                    source="conversation",
                )
                facts.append(new_fact)
                changes += 1
            continue

        new_fact = await add_profile_fact(
            session,
            user_id,
            category=item.category,
            fact=item.fact,
            valid_until=item.valid_until,
            source="conversation",
        )
        facts.append(new_fact)
        changes += 1

    await session.flush()
    return changes


def format_facts_list(facts: list[UserProfileFact]) -> str:
    if not facts:
        return "No profile facts yet. Add one with:\n/add_fact preference | prefers morning sessions"
    lines = []
    for f in facts:
        short_id = str(f.id)[:8]
        lines.append(f"• [{short_id}] [{f.category}] {f.fact}")
    return "Your profile facts:\n" + "\n".join(lines)


def format_what_i_know(facts: list[UserProfileFact]) -> str:
    if not facts:
        return "I don't have any stored facts about you yet."
    lines = [f"• [{f.category}] {f.fact}" for f in facts]
    return "Here's what I know:\n" + "\n".join(lines)


HELP_TEXT = """Kairos commands:

Profile
/what — what I know about you
/help — this message

Contacts
/add_contact Name | friend | 30
/contacts — list contacts
/delete_contact Name

Hobbies
/add_hobby surf
/hobbies — list hobbies
/delete_hobby surf
/set_hobby surf min_wave=1.2 max_wave=2.5

Facts
/add_fact category | fact text
/facts — list active facts
/delete_fact keyword or id

Week forecast
"Check my week for Lisbon and surf"
/week Ericeira surfing, cycling"""


def format_help_text() -> str:
    return HELP_TEXT


def _parse_command(text: str) -> tuple[str, str]:
    text = text.strip()
    if not text.startswith("/"):
        return "", text
    parts = text.split(maxsplit=1)
    command = parts[0].split("@")[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""
    return command, args


async def handle_profile_command(session: AsyncSession, user: User, text: str) -> str | None:
    """Handle profile slash commands. Returns reply text, or None if not a command."""
    command, args = _parse_command(text)
    if not command:
        return None

    if command == "/help":
        return format_help_text()

    if command == "/what":
        facts = await get_active_profile_facts(session, user.id)
        return format_what_i_know(facts)

    if command == "/contacts":
        contacts = await list_contacts(session, user.id)
        return format_contacts_list(contacts)

    if command == "/add_contact":
        parts = [part.strip() for part in args.split("|")]
        if not parts or not parts[0]:
            return "Usage: /add_contact Name | friend | 30"
        name = parts[0]
        relationship = parts[1] if len(parts) > 1 and parts[1] else None
        try:
            frequency = int(parts[2]) if len(parts) > 2 and parts[2] else 30
        except ValueError:
            return "Frequency must be a number of days, e.g. 30"
        await add_contact(
            session,
            user.id,
            name=name,
            relationship_type=relationship,
            frequency_days=frequency,
        )
        return f"Added contact {name}."

    if command == "/delete_contact":
        if not args:
            return "Usage: /delete_contact Name"
        if await delete_contact_by_name(session, user.id, args):
            return f"Removed contact {args.strip()}."
        return f"No contact named '{args.strip()}'."

    if command == "/hobbies":
        hobbies = await list_hobbies(session, user.id, enabled_only=False)
        return format_hobbies_list(hobbies)

    if command == "/add_hobby":
        if not args:
            known = ", ".join(sorted(SKILL_REGISTRY))
            return f"Usage: /add_hobby surf\nSupported: {known}"
        hobby_type = args.split()[0]
        try:
            await add_hobby(session, user.id, hobby_type)
        except ValueError as exc:
            return str(exc)
        return f"Added hobby {hobby_type.strip().lower()}."

    if command == "/delete_hobby":
        if not args:
            return "Usage: /delete_hobby surf"
        if await delete_hobby(session, user.id, args):
            return f"Removed hobby {args.strip().lower()}."
        return f"No hobby '{args.strip()}'."

    if command == "/set_hobby":
        tokens = args.split()
        if len(tokens) < 2:
            return "Usage: /set_hobby surf min_wave=1.2 max_wave=2.5"
        hobby_type = tokens[0]
        updates: dict[str, bool | int | float | str] = {}
        for token in tokens[1:]:
            if "=" not in token:
                return f"Invalid config '{token}'. Use key=value pairs."
            key, _, raw_value = token.partition("=")
            updates[normalize_hobby_config_key(key)] = parse_config_value(raw_value)
        hobby = await update_hobby_config(session, user.id, hobby_type, updates)
        if hobby is None:
            return f"Hobby '{hobby_type}' not found. Add it with /add_hobby {hobby_type}"
        cfg = ", ".join(f"{k}={v}" for k, v in sorted(hobby.config.items()))
        return f"Updated {hobby.hobby_type}: {cfg or 'defaults'}"

    if command == "/facts":
        facts = await get_active_profile_facts(session, user.id)
        return format_facts_list(facts)

    if command == "/add_fact":
        parts = [part.strip() for part in args.split("|", maxsplit=1)]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            return "Usage: /add_fact category | fact text"
        await add_profile_fact(session, user.id, category=parts[0], fact=parts[1])
        return f"Added fact: [{parts[0]}] {parts[1]}"

    if command == "/delete_fact":
        if not args:
            return "Usage: /delete_fact keyword or id"
        if await delete_profile_fact(session, user.id, args):
            return "Deleted matching fact."
        return f"No fact matching '{args}'."

    return None


async def apply_extracted_facts(
    session: AsyncSession, user_id: UUID, extracted: list[ExtractedFact]
) -> int:
    """Apply extracted facts to the database. Returns number of changes."""
    return await persist_extracted_facts(session, user_id, extracted)
