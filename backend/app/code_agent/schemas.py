from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CodeAgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: Literal["review", "explain", "refactor"] = "review"
    code: str = Field(min_length=1, max_length=100_000)
    language: Literal["python"] = "python"
    session_id: str = Field(default="homework-session", min_length=1, max_length=100)


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    success: bool
    data: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None


class CodeIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    severity: Literal["error", "warning", "info"]
    line: int | None = Field(default=None, ge=1)
    message: str
    suggestion: str


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: str
    detail: dict[str, Any] = Field(default_factory=dict)


class CodeAgentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str
    answer: str
    issues: list[CodeIssue] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    trace: list[TraceEvent] = Field(default_factory=list)
    memory_used: list[str] = Field(default_factory=list)
    degraded_mode: list[str] = Field(default_factory=list)
