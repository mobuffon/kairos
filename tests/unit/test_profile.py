import pytest
from sqlalchemy import select

from backend.agent.learning import ExtractedFact
from backend.core.crud import get_user_by_telegram_id
from backend.models import Conversation, UserContact, UserHobby, UserProfileFact
from backend.services.profile import (
    add_contact,
    add_hobby,
    add_profile_fact,
    apply_extracted_facts,
    delete_contact_by_name,
    delete_hobby,
    delete_profile_fact,
    format_help_text,
    get_active_profile_facts,
    get_or_create_user_by_telegram_id,
    handle_profile_command,
    list_contacts,
    list_hobbies,
    persist_extracted_facts,
    update_hobby_config,
)


@pytest.fixture
async def db_session():
    from backend.core.db import async_session_factory

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_get_or_create_user_by_telegram_id(db_session):
    user, created = await get_or_create_user_by_telegram_id(
        db_session, 880001, telegram_username="alice"
    )
    assert created is True
    assert user.telegram_id == 880001
    assert user.telegram_username == "alice"

    same_user, created_again = await get_or_create_user_by_telegram_id(
        db_session, 880001, telegram_username="alice2"
    )
    assert created_again is False
    assert same_user.id == user.id
    assert same_user.telegram_username == "alice2"


@pytest.mark.asyncio
async def test_contact_crud(db_session):
    user, _ = await get_or_create_user_by_telegram_id(db_session, 880002)
    await add_contact(
        db_session,
        user.id,
        name="Sam",
        relationship_type="friend",
        frequency_days=14,
    )
    contacts = await list_contacts(db_session, user.id)
    assert len(contacts) == 1
    assert contacts[0].name == "Sam"

    assert await delete_contact_by_name(db_session, user.id, "sam") is True
    assert await list_contacts(db_session, user.id) == []


@pytest.mark.asyncio
async def test_hobby_crud(db_session):
    user, _ = await get_or_create_user_by_telegram_id(db_session, 880003)
    hobby = await add_hobby(db_session, user.id, "surf")
    assert hobby.hobby_type == "surf"

    updated = await update_hobby_config(
        db_session,
        user.id,
        "surf",
        {"min_wave_height": 1.2},
    )
    assert updated is not None
    assert updated.config["min_wave_height"] == 1.2

    assert await delete_hobby(db_session, user.id, "surf") is True
    assert await list_hobbies(db_session, user.id) == []


@pytest.mark.asyncio
async def test_profile_fact_crud(db_session):
    user, _ = await get_or_create_user_by_telegram_id(db_session, 880004)
    fact = await add_profile_fact(
        db_session,
        user.id,
        category="preference",
        fact="prefers morning sessions",
    )
    facts = await get_active_profile_facts(db_session, user.id)
    assert len(facts) == 1
    assert facts[0].id == fact.id

    assert await delete_profile_fact(db_session, user.id, "morning") is True
    assert await get_active_profile_facts(db_session, user.id) == []


@pytest.mark.asyncio
async def test_persist_extracted_facts(db_session):
    user, _ = await get_or_create_user_by_telegram_id(db_session, 880005)
    extracted = [
        ExtractedFact(
            category="preference",
            fact="prefers morning sessions",
            valid_until=None,
            action="add",
        )
    ]
    changes = await persist_extracted_facts(db_session, user.id, extracted)
    assert changes == 1
    assert len(await get_active_profile_facts(db_session, user.id)) == 1

    changes = await apply_extracted_facts(
        db_session,
        user.id,
        [
            ExtractedFact(
                category="preference",
                fact="prefers morning sessions",
                valid_until=None,
                action="delete",
            )
        ],
    )
    assert changes == 1
    assert await get_active_profile_facts(db_session, user.id) == []


@pytest.mark.asyncio
async def test_handle_profile_command_add_contact(db_session):
    user, _ = await get_or_create_user_by_telegram_id(db_session, 880006)
    reply = await handle_profile_command(
        db_session,
        user,
        "/add_contact Jamie | sibling | 21",
    )
    assert reply is not None
    assert "Added contact Jamie" in reply
    contacts = await list_contacts(db_session, user.id)
    assert contacts[0].relationship_type == "sibling"
    assert contacts[0].contact_frequency_days == 21


def test_format_help_text_lists_commands():
    help_text = format_help_text()
    assert "/add_contact" in help_text
    assert "/add_hobby" in help_text
    assert "/add_fact" in help_text
    assert "/help" in help_text
