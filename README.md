# Homework 1: Code Review Agent

本作业选择“代码审查 Agent”方向。项目源码在 `backend/app/code_agent/`，命令行入口在 `scripts/homework1_code_agent.py`。

## 运行

需要 Python 3.10 或更高版本。

```bash
python -m pip install -r homework1/requirements.txt
PYTHONPATH=backend python scripts/homework1_code_agent.py \
  --code $'def f(value=[]):\n    try:\n        return eval(value[0])\n    except:\n        return None'
```

检查现有文件：

```bash
PYTHONPATH=backend python scripts/homework1_code_agent.py --file path/to/example.py --json
```

没有配置模型服务时，程序使用明确标注的 fake provider；静态 AST 检查和工具调用仍可运行。配置真实模型：

```bash
export CODE_AGENT_API_URL=https://your-openai-compatible-endpoint/v1
export CODE_AGENT_API_KEY=your-key
export CODE_AGENT_MODEL=qwen-plus
```

记忆以会话为范围保存到 `.homework1/memory.json`，只记录问题数量摘要，不保存源码。Agent 不执行用户提供的 Python 代码。

详细设计见 `docs/homework1-design.md`。聚焦测试位于 `backend/tests/unit/test_homework1_code_agent.py`。
