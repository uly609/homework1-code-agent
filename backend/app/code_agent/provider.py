from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass
from urllib import request


class CodeAgentProviderError(RuntimeError):
    """Raised when an external provider cannot be used safely."""


@dataclass(frozen=True)
class ProviderReply:
    content: str
    degraded: bool
    provider: str


class CodeAgentProvider:
    async def complete(self, prompt: str) -> ProviderReply:
        raise NotImplementedError


class FakeCodeAgentProvider(CodeAgentProvider):
    async def complete(self, prompt: str) -> ProviderReply:
        del prompt
        return ProviderReply(
            content="已完成静态代码审查。请优先修复 error 级问题，再针对 warning 运行测试并补充边界用例。",
            degraded=True,
            provider="fake_code_agent_provider",
        )


class OpenAICompatibleCodeAgentProvider(CodeAgentProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 12.0, retries: int = 2) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retries = max(0, retries)

    async def complete(self, prompt: str) -> ProviderReply:
        return await asyncio.to_thread(self._complete_sync, prompt)

    def _complete_sync(self, prompt: str) -> ProviderReply:
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": "你是严格、简洁的 Python 代码审查助手。"},
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                req = request.Request(
                    f"{self.base_url}/chat/completions",
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    method="POST",
                )
                with request.urlopen(req, timeout=self.timeout) as response:  # noqa: S310 - URL is operator-configured.
                    payload = json.loads(response.read().decode("utf-8"))
                content = payload["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise CodeAgentProviderError("provider returned empty content")
                return ProviderReply(content=content.strip(), degraded=False, provider="openai_compatible")
            except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.25 * (attempt + 1))
                    continue
        raise CodeAgentProviderError(f"provider failed after bounded retries: {last_error}")


def build_provider() -> CodeAgentProvider:
    url = os.getenv("CODE_AGENT_API_URL", "").strip()
    key = os.getenv("CODE_AGENT_API_KEY", "").strip()
    model = os.getenv("CODE_AGENT_MODEL", "qwen-plus").strip()
    if url and key:
        return OpenAICompatibleCodeAgentProvider(url, key, model)
    return FakeCodeAgentProvider()
