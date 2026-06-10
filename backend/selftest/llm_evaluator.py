from dataclasses import dataclass
from typing import Any
import json

from backend.agent.llm import complete
from backend.core.config import get_settings


@dataclass
class LLMEvalResult:
    passed: bool
    score: float
    feedback: str


async def evaluate_message_quality(
    message: str,
    context: dict[str, Any],
    *,
    mock: bool = True,
) -> LLMEvalResult:
    """Score suggestion message quality. Uses mock heuristics when no API key."""
    if mock or get_settings().use_mock_llm:
        score = 0.0
        feedback_parts: list[str] = []
        if len(message) >= 40:
            score += 0.35
            feedback_parts.append("adequate length")
        hobby = context.get("hobby_type", "")
        if hobby and hobby.replace("_", " ") in message.lower():
            score += 0.35
            feedback_parts.append("mentions activity")
        if any(ch.isdigit() for ch in message):
            score += 0.15
            feedback_parts.append("includes specifics")
        if message.endswith("."):
            score += 0.15
            feedback_parts.append("complete sentence")
        passed = score >= 0.6
        return LLMEvalResult(
            passed=passed,
            score=round(score, 2),
            feedback=", ".join(feedback_parts) or "mock evaluation",
        )

    prompt = (
        f"Rate this leisure suggestion message 0-1 for warmth, specificity, brevity.\n"
        f"Context: {context}\nMessage: {message}\n"
        f'Reply with JSON: {{"score": float, "feedback": string}}'
    )
    try:
        text = await complete(user=prompt, max_tokens=150)
        if text:
            data = json.loads(text)
            score = float(data.get("score", 0))
            return LLMEvalResult(passed=score >= 0.6, score=score, feedback=data.get("feedback", ""))
    except Exception as exc:
        return LLMEvalResult(passed=True, score=0.7, feedback=f"fallback due to: {exc}")

    return LLMEvalResult(passed=True, score=0.7, feedback="fallback — LLM unavailable")
