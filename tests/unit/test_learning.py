import pytest

from backend.agent.learning import (
    apply_facts_to_profile,
    extract_facts_mock,
    process_inbound_message,
)


def test_extract_injury_fact():
    facts = extract_facts_mock("I broke my right arm last week")
    assert len(facts) == 1
    assert facts[0].category == "injury"
    assert facts[0].action == "add"


def test_extract_travel_fact():
    facts = extract_facts_mock("I'm traveling in Japan until August")
    assert any(f.category == "travel" for f in facts)


def test_forget_command():
    facts = extract_facts_mock("forget that I prefer morning sessions")
    assert len(facts) == 1
    assert facts[0].action == "delete"


def test_apply_facts_add_and_delete():
    existing = [{"category": "preference", "fact": "prefers morning sessions"}]
    extracted = extract_facts_mock("forget that I prefer morning sessions")
    updated = apply_facts_to_profile(existing, extracted)
    assert len(updated) == 0


@pytest.mark.asyncio
async def test_process_inbound_message_injury():
    context = {"user": {"profile_facts": [], "telegram_username": "mo"}}
    result = await process_inbound_message("I broke my arm", context)
    assert len(result["extracted"]) == 1
    assert "recover" in result["reply"].lower()
    assert len(result["profile_facts"]) == 1
