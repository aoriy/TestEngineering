"""LLM adapter for self-heal (ADR-0005).

OpenAI-compatible chat completions via requests, so any provider
(DeepSeek / Qwen / GLM / OpenAI) works by changing base_url/model/key.
"""

import abc
from dataclasses import dataclass, field

import requests

from app.core.config import settings


@dataclass
class HealCandidate:
    locator_type: str
    locator_value: str
    inner_text: str = ""
    aria_label: str = ""
    role: str = ""


@dataclass
class HealSuggestion:
    candidates: list[HealCandidate] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""


class LlmAdapter(abc.ABC):
    @abc.abstractmethod
    def suggest_locators(self, old_locator: str, page_html: str) -> HealSuggestion:
        """Return repair candidates for a failed locator."""


class DeepSeekAdapter(LlmAdapter):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self.model = model or settings.deepseek_model

    def suggest_locators(self, old_locator: str, page_html: str) -> HealSuggestion:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")

        from app.services.selfheal.prompts import build_messages, parse_reply

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": build_messages(old_locator, page_html),
                "response_format": {"type": "json_object"},
                "thinking": True,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        reasoning = data["choices"][0]["message"].get("reasoning_content", "")
        return parse_reply(content, reasoning)
