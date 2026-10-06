from __future__ import annotations

import ast
from collections.abc import Callable
from typing import Any

from app.code_agent.schemas import CodeIssue, ToolResult


ToolFunction = Callable[[dict[str, Any]], ToolResult]


class ToolRegistry:
    """Allowlisted tools used by the homework Agent."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolFunction] = {}

    def register(self, name: str, tool: ToolFunction) -> None:
        if not name or name.startswith("_"):
            raise ValueError("tool name must be public")
        self._tools[name] = tool

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def call(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(
                tool_name=name,
                success=False,
                error_code="TOOL_NOT_REGISTERED",
                error_message=f"Tool is not registered: {name}",
            )
        try:
            return tool(arguments)
        except (SyntaxError, TypeError, ValueError) as exc:
            return ToolResult(
                tool_name=name,
                success=False,
                error_code="TOOL_INPUT_INVALID",
                error_message=str(exc),
            )


def read_source(arguments: dict[str, Any]) -> ToolResult:
    """Return source text from the request without executing it."""

    code = arguments.get("code")
    if not isinstance(code, str) or not code.strip():
        return ToolResult(
            tool_name="read_source",
            success=False,
            error_code="SOURCE_EMPTY",
            error_message="code must be a non-empty string",
        )
    return ToolResult(
        tool_name="read_source",
        success=True,
        data={"code": code, "line_count": len(code.splitlines())},
    )


def analyze_python(arguments: dict[str, Any]) -> ToolResult:
    """Perform deterministic AST checks that remain useful without an LLM key."""

    code = arguments.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("code must be a non-empty string")

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        issue = CodeIssue(
            rule_id="PY001",
            severity="error",
            line=exc.lineno,
            message=f"语法错误：{exc.msg}",
            suggestion="先修复语法错误，再运行测试或继续重构。",
        )
        return ToolResult(
            tool_name="analyze_python",
            success=True,
            data={"issues": [issue.model_dump(mode="json")], "syntax_valid": False},
        )

    issues: list[CodeIssue] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(
                CodeIssue(
                    rule_id="PY002",
                    severity="warning",
                    line=node.lineno,
                    message="捕获了所有异常，可能会隐藏真正的错误。",
                    suggestion="捕获具体异常，并保留结构化日志或错误码。",
                )
            )
        if isinstance(node, ast.FunctionDef):
            for default in [*node.args.defaults, *node.args.kw_defaults]:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(
                        CodeIssue(
                            rule_id="PY003",
                            severity="warning",
                            line=node.lineno,
                            message="函数参数使用了可变对象作为默认值。",
                            suggestion="改用 None，并在函数体内创建新的列表、字典或集合。",
                        )
                    )
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
            issues.append(
                CodeIssue(
                    rule_id="PY004",
                    severity="error",
                    line=node.lineno,
                    message="动态执行 eval 会引入代码注入风险。",
                    suggestion="使用显式解析器或白名单映射替代 eval。",
                )
            )

    return ToolResult(
        tool_name="analyze_python",
        success=True,
        data={
            "issues": [issue.model_dump(mode="json") for issue in issues],
            "syntax_valid": True,
            "line_count": len(code.splitlines()),
        },
    )


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("read_source", read_source)
    registry.register("analyze_python", analyze_python)
    return registry
