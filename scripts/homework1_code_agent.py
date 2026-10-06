from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from app.code_agent import CodeAgentRequest, CodeReviewAgent
from app.code_agent.memory import ConversationMemory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Homework 1 code-review Agent")
    parser.add_argument("--task", choices=("review", "explain", "refactor"), default="review")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="Python source file to inspect")
    source.add_argument("--code", help="Inline Python source")
    parser.add_argument("--session", default="homework-cli")
    parser.add_argument("--memory", type=Path, default=Path(".homework1/memory.json"))
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


async def run(args: argparse.Namespace) -> int:
    code = args.code
    if args.file is not None:
        code = args.file.read_text(encoding="utf-8")
    request = CodeAgentRequest(task=args.task, code=code or "", session_id=args.session)
    agent = CodeReviewAgent(memory=ConversationMemory(args.memory))
    response = await agent.run(request)
    if args.as_json:
        print(response.model_dump_json(indent=2))
    else:
        print(response.answer)
        for issue in response.issues:
            location = f"line {issue.line}" if issue.line else "file"
            print(f"- [{issue.severity}] {issue.rule_id} ({location}): {issue.message}")
            print(f"  suggestion: {issue.suggestion}")
        print(f"\ntrace events: {len(response.trace)}")
        if response.degraded_mode:
            print(f"mode: degraded ({', '.join(response.degraded_mode)})")
    return 0


def main() -> int:
    return asyncio.run(run(build_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
