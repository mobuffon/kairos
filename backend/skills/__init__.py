"""Skill modules."""

from backend.skills.base import BaseSkill
from backend.skills.call_friend import CallFriendSkill
from backend.skills.cycling import CyclingSkill
from backend.skills.surf import SurfSkill

SKILL_REGISTRY: dict[str, type[BaseSkill]] = {
    "surf": SurfSkill,
    "cycling": CyclingSkill,
    "call_friend": CallFriendSkill,
}


def get_skill(hobby_type: str) -> BaseSkill:
    cls = SKILL_REGISTRY.get(hobby_type)
    if cls is None:
        raise ValueError(f"Unknown hobby type: {hobby_type}")
    return cls()
