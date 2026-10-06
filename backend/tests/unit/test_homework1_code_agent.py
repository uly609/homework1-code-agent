from __future__ import annotations

import pytest

from app.code_agent import CodeAgentRequest, CodeReviewAgent
from app.code_agent.memory import ConversationMemory


@pytest.mark.asyncio
async def test_code_review_agent_runs_plan_tools_and_fake_provider(tmp_path) -> None:
    agent = CodeReviewAgent(memory=ConversationMemory(tmp_path / "memory.json"))
    response = await agent.run(
        CodeAgentRequest(
            task="review",
            code="def f(value=[]):\n    try:\n        return eval(value[0])\n    except:\n        return None\n",
        )
    )

    assert {item.tool_name for item in response.tool_results} == {"read_source", "analyze_python"}
    assert {item.rule_id for item in response.issues} == {"PY002", "PY003", "PY004"}
    assert "fake_code_agent_provider" in response.degraded_mode
    assert [item.event for item in response.trace] == [
        "input_received",
        "memory_loaded",
        "plan_created",
        "tool_executed",
        "tool_executed",
        "answer_synthesized",
        "memory_saved",
    ]


@pytest.mark.asyncio
async def test_code_review_agent_reuses_session_memory(tmp_path) -> None:
    memory = ConversationMemory(tmp_path / "memory.json")
    agent = CodeReviewAgent(memory=memory)
    request = CodeAgentRequest(code="print('ok')", session_id="same")
    await agent.run(request)
    response = await agent.run(request)

    assert response.memory_used == ["review: 0 issues"]


def test_code_agent_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError):
        CodeAgentRequest(code="print('ok')", unexpected="value")
