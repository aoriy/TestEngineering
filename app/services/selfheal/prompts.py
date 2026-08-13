"""Prompt templates for self-heal (smart note #7 / ADR-0005)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.selfheal.llm import HealSuggestion

_SYSTEM = (
    "You are a UI test locator repair expert. Given a broken locator and the "
    "surrounding page HTML, propose 1-3 alternative locators (xpath/css) that "
    "uniquely identify the SAME element, plus a confidence score. Return JSON only."
)

_JSON_HINT = (
    'Return a JSON object with shape: {"locators": [{"locator_type": "xpath"|"css"|'
    '"data-testid", "locator_value": "...", "inner_text": "...", "aria_label": "...", '
    '"role": "..."}], "confidence": 0.0-1.0}. No prose.'
)

_MAX_HTML_CHARS = 8000


def truncate_html(html: str, max_chars: int = _MAX_HTML_CHARS) -> str:
    if len(html) <= max_chars:
        return html
    head = max_chars // 2
    tail = max_chars - head
    return html[:head] + "\n<!-- ...truncated... -->\n" + html[-tail:]


def build_messages(old_locator: str, page_html: str) -> list[dict]:
    user = (
        f"The locator `{old_locator}` failed to match (or is not unique/visible).\n\n"
        f"Page HTML (truncated):\n{truncate_html(page_html)}\n\n{_JSON_HINT}"
    )
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user},
    ]


def parse_reply(content: str, reasoning: str = "") -> "HealSuggestion":
    from app.services.selfheal.llm import HealCandidate, HealSuggestion

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        data = (
            json.loads(content[start : end + 1]) if start >= 0 and end > start else {}
        )

    candidates = [
        HealCandidate(
            locator_type=c.get("locator_type", "xpath"),
            locator_value=c.get("locator_value", ""),
            inner_text=c.get("inner_text", ""),
            aria_label=c.get("aria_label", ""),
            role=c.get("role", ""),
        )
        for c in data.get("locators", [])
        if c.get("locator_value")
    ]
    confidence = float(data.get("confidence", 0.0))
    return HealSuggestion(
        candidates=candidates, confidence=confidence, reasoning=reasoning
    )
