"""Learning agent — extract and apply profile facts from conversations."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
import json
import re

from backend.agent.llm import complete
from backend.agent.prompts import LEARNING_SYSTEM
from backend.core.config import get_settings

FactAction = Literal["add", "update", "delete"]

INJURY_KEYWORDS = ("broke", "broken", "injured", "injury", "sprain", "fracture", "surgery")
TRAVEL_KEYWORDS = ("traveling", "travelling", "trip to", "in japan", "on vacation", "away until")
FORGET_PATTERN = re.compile(r"forget\s+(?:that\s+)?(.+)", re.IGNORECASE)


def _fact_matches_delete(subject: str, fact_text: str) -> bool:
    subject_l = subject.lower().strip()
    fact_l = fact_text.lower().strip()
    if subject_l in fact_l or fact_l in subject_l:
        return True
    subject_words = set(subject_l.split()) - {"i", "that", "my", "the"}
    fact_words = set(fact_l.split())
    return len(subject_words & fact_words) >= 2


@dataclass
class ExtractedFact:
    category: str
    fact: str
    valid_until: datetime | None
    action: FactAction


def _parse_duration_weeks(text: str, default_weeks: int = 6) -> datetime:
    return datetime.now(UTC) + timedelta(weeks=default_weeks)


def extract_facts_mock(message: str) -> list[ExtractedFact]:
    """Rule-based fact extraction when no LLM API key."""
    text = message.strip()
    lower = text.lower()
    facts: list[ExtractedFact] = []

    forget_match = FORGET_PATTERN.search(text)
    if forget_match:
        subject = forget_match.group(1).strip().rstrip(".")
        return [ExtractedFact(category="preference", fact=subject, valid_until=None, action="delete")]

    if any(kw in lower for kw in INJURY_KEYWORDS):
        facts.append(
            ExtractedFact(
                category="injury",
                fact=text,
                valid_until=_parse_duration_weeks(text, 6),
                action="add",
            )
        )

    if any(kw in lower for kw in TRAVEL_KEYWORDS):
        facts.append(
            ExtractedFact(
                category="travel",
                fact=text,
                valid_until=datetime.now(UTC) + timedelta(days=21),
                action="add",
            )
        )

    if "prefer morning" in lower or "mornings only" in lower:
        facts.append(
            ExtractedFact(
                category="preference",
                fact="prefers morning sessions",
                valid_until=None,
                action="add",
            )
        )

    return facts


async def extract_facts_from_message(
    message: str,
    user_context: dict[str, Any] | None = None,
    *,
    mock: bool | None = None,
) -> list[ExtractedFact]:
    settings = get_settings()
    use_mock = mock if mock is not None else settings.use_mock_llm

    if use_mock:
        return extract_facts_mock(message)

    prompt = f"User message: {message}\nExisting context: {user_context or {}}"
    text = await complete(
        system=LEARNING_SYSTEM,
        user=prompt,
        max_tokens=400,
        settings=settings,
    )
    if text:
        try:
            raw = json.loads(text)
            results: list[ExtractedFact] = []
            for item in raw:
                valid_until = None
                if item.get("valid_until"):
                    valid_until = datetime.fromisoformat(item["valid_until"])
                results.append(
                    ExtractedFact(
                        category=item["category"],
                        fact=item["fact"],
                        valid_until=valid_until,
                        action=item.get("action", "add"),
                    )
                )
            return results
        except Exception:
            pass

    return extract_facts_mock(message)


def apply_facts_to_profile(
    existing_facts: list[dict[str, Any]],
    extracted: list[ExtractedFact],
) -> list[dict[str, Any]]:
    """Apply extracted facts to an in-memory profile fact list (mock/CLI mode)."""
    updated = list(existing_facts)

    for fact in extracted:
        if fact.action == "delete":
            updated = [
                f
                for f in updated
                if not _fact_matches_delete(fact.fact, f.get("fact", ""))
            ]
            continue

        entry = {
            "category": fact.category,
            "fact": fact.fact,
            "valid_until": fact.valid_until.isoformat() if fact.valid_until else None,
            "source": "conversation",
        }

        if fact.action == "update":
            for i, existing in enumerate(updated):
                if existing.get("category") == fact.category:
                    updated[i] = entry
                    break
            else:
                updated.append(entry)
        else:
            updated.append(entry)

    return updated


async def process_inbound_message(
    message: str,
    user_context: dict[str, Any],
) -> dict[str, Any]:
    """Full learning pipeline for a single inbound message."""
    extracted = await extract_facts_from_message(message, user_context)
    existing = user_context.get("user", {}).get("profile_facts", [])
    updated_facts = apply_facts_to_profile(existing, extracted)

    return {
        "extracted": [
            {
                "category": f.category,
                "fact": f.fact,
                "valid_until": f.valid_until.isoformat() if f.valid_until else None,
                "action": f.action,
            }
            for f in extracted
        ],
        "profile_facts": updated_facts,
        "reply": _build_reply(extracted),
    }


def _build_reply(extracted: list[ExtractedFact]) -> str:
    if not extracted:
        return "Got it — I'll keep that in mind."
    parts = []
    for f in extracted:
        if f.action == "delete":
            parts.append(f"I'll forget about {f.fact}.")
        elif f.category == "injury":
            parts.append("I'll hold off on physical activity suggestions while you recover.")
        elif f.category == "travel":
            parts.append("Enjoy your trip — I'll adjust suggestions until you're back.")
        else:
            parts.append(f"Noted: {f.fact}")
    return " ".join(parts)
