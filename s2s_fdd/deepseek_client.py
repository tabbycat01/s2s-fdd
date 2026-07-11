"""Minimal DeepSeek Chat Completions client for semantic descriptions."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEEPSEEK_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"


class DeepSeekAPIError(RuntimeError):
    """Raised when the DeepSeek API request fails."""


def _extract_message_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    return content.strip() if isinstance(content, str) else ""


class DeepSeekClient:
    """Small standard-library client so first API use does not require SDK setup."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.model = model or os.environ.get("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL
        self.timeout = timeout
        if not self.api_key:
            raise DeepSeekAPIError(
                "DEEPSEEK_API_KEY is not set. Set it in the environment before enabling LLM semantics."
            )

    def generate_semantic_description(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only the final temporal description. Do not use Markdown, "
                        "headings, bullet points, or root-cause conclusions."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "max_tokens": 180,
            "thinking": {"type": "disabled"},
        }
        request = urllib.request.Request(
            DEEPSEEK_CHAT_COMPLETIONS_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DeepSeekAPIError(f"DeepSeek API request failed: HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise DeepSeekAPIError(f"DeepSeek API request failed: {exc.reason}") from exc

        text = _extract_message_text(payload)
        if not text:
            raise DeepSeekAPIError("DeepSeek API response did not contain message content.")
        return text
