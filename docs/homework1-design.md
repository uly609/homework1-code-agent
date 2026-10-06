# Homework 1: Code Review Agent

本次作业选择“代码审查 Agent”方向。实现位于 `backend/app/code_agent/`，命令行入口为 `scripts/homework1_code_agent.py`。

## 功能

- Agent 循环：输入校验 → 上下文读取 → 模型工具规划（无凭证时用确定性规划）→ 工具执行 → 结果综合 → 保存记忆。
- 工具注册表：只执行已注册的 `read_source` 和 `analyze_python`。
- 静态检查：语法错误、裸 `except`、可变默认参数和 `eval` 风险。
- LLM 接口：支持 OpenAI-compatible `CODE_AGENT_API_URL` / `CODE_AGENT_API_KEY` / `CODE_AGENT_MODEL`；没有凭证时使用显式 `fake_code_agent_provider`，不会伪装成真实服务。
- 上下文记忆：按 `session_id` 保存最近 12 条审查摘要到 `.homework1/memory.json`，不保存提交的源码。
- 错误处理：工具输入错误返回结构化错误码；外部模型调用使用有限重试和超时。

## 运行

在项目根目录执行：

```bash
PYTHONPATH=backend python scripts/homework1_code_agent.py \
  --code $'def f(value=[]):\n    try:\n        return eval(value[0])\n    except:\n        return None'
```

也可以读取文件并输出结构化 JSON：

```bash
PYTHONPATH=backend python scripts/homework1_code_agent.py \
  --file backend/app/code_agent/tools.py --json
```

配置 OpenAI-compatible 服务后，Agent 会优先使用真实服务；否则输出会标注降级模式：

```bash
export CODE_AGENT_API_URL=https://example.invalid/v1
export CODE_AGENT_API_KEY=your-key
export CODE_AGENT_MODEL=qwen-plus
```

## 设计说明

```text
CodeAgentRequest
      |
      v
Memory -> Planner -> ToolRegistry -> Issues -> Provider -> CodeAgentResponse
                                              |
                                              v
                                           Memory
```

`ToolRegistry` 是唯一执行入口。Agent 不执行用户提交的 Python，只读取源码并使用 AST 分析。真实模型只负责选择已注册工具和把结构化检查结果转换为建议，执行前会验证工具名和参数 schema。模型规划不可用或无效时会使用确定性工具计划。静态检查结果始终保留在响应中，用户代码不会进入记忆文件。

## 验证

```bash
PYTHONPATH=backend pytest backend/tests/unit/test_homework1_code_agent.py
```
