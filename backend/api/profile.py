from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.deps import get_current_user_key
from backend.providers.mock.provider import MockProvider
from backend.scheduler.jobs import evaluate_user

router = APIRouter(prefix="/profile", tags=["profile"])


class ContactOut(BaseModel):
    name: str
    relationship_type: str | None = None
    contact_frequency_days: int = 30
    last_contacted_at: str | None = None
    notes: str | None = None


class CalendarOut(BaseModel):
    connected: bool
    provider: str = "google"
    sync_enabled: bool = False
    calendar_id: str = "primary"


class HobbyOut(BaseModel):
    hobby_type: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class ProfileFactOut(BaseModel):
    category: str
    fact: str
    valid_from: str | None = None
    valid_until: str | None = None
    source: str | None = None


class ConversationOut(BaseModel):
    direction: str
    channel: str
    message_text: str
    created_at: str
    extracted_facts: dict[str, Any] | None = None


class SuggestionHistoryOut(BaseModel):
    hobby_type: str
    window_start: str
    window_end: str
    score: float
    conditions_summary: str | None = None
    message_text: str | None = None
    sent_at: str | None = None
    response: str | None = None


class UpcomingSuggestionOut(BaseModel):
    hobby_type: str
    score: float
    window_start: str
    window_end: str
    conditions: str
    message: str


class UserPreferencesOut(BaseModel):
    timezone: str
    location_label: str | None = None
    quiet_hours_start: int = 22
    quiet_hours_end: int = 7
    max_suggestions_per_day: int = 2
    check_in_frequency_days: int = 14
    telegram_username: str | None = None


class ProfileSummaryOut(BaseModel):
    user_key: str
    preferences: UserPreferencesOut
    contacts: list[ContactOut]
    calendar: CalendarOut
    hobbies: list[HobbyOut]
    profile_facts: list[ProfileFactOut]
    conversations: list[ConversationOut]
    suggestions: list[SuggestionHistoryOut]
    upcoming_suggestions: list[UpcomingSuggestionOut]


async def _build_summary(user_key: str, *, include_upcoming: bool = True) -> ProfileSummaryOut:
    provider = MockProvider()
    fixture = provider.get_user_fixture(user_key)

    calendar_fixture = fixture.get("calendar", {})
    calendar = CalendarOut(
        connected=bool(calendar_fixture.get("connected", False)),
        provider=str(calendar_fixture.get("provider", "google")),
        sync_enabled=bool(calendar_fixture.get("sync_enabled", False)),
        calendar_id=str(calendar_fixture.get("calendar_id", "primary")),
    )

    contacts = [ContactOut(**c) for c in fixture.get("contacts", [])]
    hobbies = [HobbyOut(**h) for h in fixture.get("hobbies", [])]
    profile_facts = [ProfileFactOut(**f) for f in fixture.get("profile_facts", [])]
    conversations = [ConversationOut(**c) for c in fixture.get("conversations", [])]
    suggestions = [SuggestionHistoryOut(**s) for s in fixture.get("suggestions", [])]

    upcoming: list[UpcomingSuggestionOut] = []
    if include_upcoming:
        scenario = fixture.get("default_scenario")
        result = await evaluate_user(user_key, mock=True, scenario=scenario)
        upcoming = [UpcomingSuggestionOut(**s) for s in result.get("suggestions", [])]

    preferences = UserPreferencesOut(
        timezone=str(fixture.get("timezone", "UTC")),
        location_label=fixture.get("location_label"),
        quiet_hours_start=int(fixture.get("quiet_hours_start", 22)),
        quiet_hours_end=int(fixture.get("quiet_hours_end", 7)),
        max_suggestions_per_day=int(fixture.get("max_suggestions_per_day", 2)),
        check_in_frequency_days=int(fixture.get("check_in_frequency_days", 14)),
        telegram_username=fixture.get("telegram_username"),
    )

    return ProfileSummaryOut(
        user_key=user_key,
        preferences=preferences,
        contacts=contacts,
        calendar=calendar,
        hobbies=hobbies,
        profile_facts=profile_facts,
        conversations=conversations,
        suggestions=suggestions,
        upcoming_suggestions=upcoming,
    )


@router.get("/summary", response_model=ProfileSummaryOut)
async def get_profile_summary(
    current_user: str = Depends(get_current_user_key),
) -> ProfileSummaryOut:
    """Return user-centric profile data (fixtures when DB empty)."""
    return await _build_summary(current_user)


@router.get("/settings", response_model=UserPreferencesOut)
async def get_user_settings(
    current_user: str = Depends(get_current_user_key),
) -> UserPreferencesOut:
    """Return user preference fields from the users table (fixture-backed in dev)."""
    summary = await _build_summary(current_user, include_upcoming=False)
    return summary.preferences
