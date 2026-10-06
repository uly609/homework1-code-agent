from __future__ import annotations

import json
from pathlib import Path


class ConversationMemory:
    """Small bounded JSON memory for local demos and repeatable tests."""

    def __init__(self, path: str | Path | None = None, limit: int = 12) -> None:
        self.path = Path(path) if path else None
        self.limit = max(1, limit)

    def load(self, session_id: str) -> list[str]:
        if self.path is None or not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        values = payload.get(session_id, []) if isinstance(payload, dict) else []
        return [str(item) for item in values[-self.limit :]]

    def append(self, session_id: str, summary: str) -> None:
        if self.path is None:
            return
        payload: dict[str, list[str]] = {}
        try:
            existing = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
            if isinstance(existing, dict):
                payload = {str(key): [str(item) for item in value] for key, value in existing.items() if isinstance(value, list)}
        except (OSError, json.JSONDecodeError):
            payload = {}
        payload.setdefault(session_id, []).append(summary)
        payload[session_id] = payload[session_id][-self.limit :]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
