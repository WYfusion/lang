# Agent 使用 MCP 完整实战 README

本文档基于当前项目 `langgraph/6.py`，给出一套可运行、可排错、可扩展的 **Agent + MCP** 使用方案。

---

## 1. 目标与效果

你将获得一个能做以下事情的 Agent：

- 使用 `ChatTongyi`（通义千问）作为大模型
- 同时挂载本地 Python Tool（例如 `get_current_date`）和 MCP Tool（例如高德地图）
- 通过自然语言提问（如路线规划）自动调用工具并返回结果

---

## 2. 前置环境

### 2.1 系统与运行时

- Windows
- Python 3.10（建议与你当前 `lang310` 保持一致）
- Node.js（MCP 的 `npx` 启动依赖）

### 2.2 Python 依赖

在 Conda 环境中安装：

```bash
pip install -U langchain langgraph langchain-community langchain-mcp-adapters dashscope
```

> 注意：
> - `langchain-mcp-adapters` 是关键依赖。
> - 如果只装了 `mcp` 而没装适配器，`MultiServerMCPClient` 相关能力仍不可用。

### 2.3 Node 依赖

`amap` 的 MCP Server 通过 `npx` 临时拉起：

```bash
npx -y @amap/amap-maps-mcp-server --help
```

如果能看到帮助信息，说明 Node + npx 正常。

---

## 3. 密钥准备

你需要两类密钥：

1. 通义千问：`DASHSCOPE_API_KEY`
2. 高德地图：`AMAP_MAPS_API_KEY`

推荐放在环境变量或 `env_utils.py`，避免硬编码。

示例（PowerShell）：

```powershell
$env:DASHSCOPE_API_KEY = "你的通义密钥"
$env:AMAP_MAPS_API_KEY = "你的高德密钥"
```

---

## 4. 推荐代码模板（可直接替换）

下面是一个稳定写法，重点处理了三个常见坑：

- 顶层 `await` 错误（必须放到 `async def main()`）
- `ChatTongyi` 参数名错误（应使用 `dashscope_api_key`）
- MCP 配置缺失 `transport`（stdio 模式必须写）

```python
import io
import os
import sys
import asyncio
import datetime
from pathlib import Path

from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from env_utils import ALIBABA_API_KEY

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


@tool
def get_current_date():
    """获取今天日期"""
    return datetime.datetime.today().strftime("%Y-%m-%d")


llm = ChatTongyi(
    model="qwen-plus",
    dashscope_api_key=ALIBABA_API_KEY,
    checkpointer=InMemorySaver(),
)


client = MultiServerMCPClient(
    {
        "amap-maps": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@amap/amap-maps-mcp-server"],
            "env": {
                "AMAP_MAPS_API_KEY": os.getenv("AMAP_MAPS_API_KEY", "")
            },
        }
    }
)


async def main():
    tools = await client.get_tools()

    agent = create_agent(
        llm,
        tools=[get_current_date, *tools],
        system_prompt="你是我的人工智能助手，协助我获取信息并完成任务。",
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "从北京大学到广州大学城的驾车路线怎么走？"}
            ]
        }
    )

    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. 运行方式

在项目根目录执行：

```bash
python langgraph/6.py
```

如果返回路线规划文本，说明 Agent + MCP 已跑通。

---

## 6. 配置字段说明（MCP）

`MultiServerMCPClient` 单个服务配置常见字段：

- `transport`：必须，常见 `stdio` / `sse` / `websocket` / `http`
- `command`：stdio 模式下启动命令（如 `npx`）
- `args`：命令参数
- `env`：子进程环境变量

> 你当前用的是 `stdio + npx`，这是本地开发最常见组合。

---

## 7. 常见报错与解决

### 7.1 `SyntaxError: 'await' outside function`

原因：在模块顶层直接写了 `await`。

解决：把异步逻辑放进 `async def main()`，入口使用 `asyncio.run(main())`。

### 7.2 `ValidationError ... Did not find dashscope_api_key`

原因：把 `DASHSCOPE_API_KEY` 当成参数名传给 `ChatTongyi`。

解决：改为参数 `dashscope_api_key=...`。

### 7.3 `Missing 'transport' key in server configuration`

原因：MCP server 配置缺少 `transport`。

解决：补上 `"transport": "stdio"`（或其他对应传输协议）。

### 7.4 `_create_stdio_session() got an unexpected keyword argument 'autoApprove'`

原因：当前 Python 适配器不识别 `autoApprove` 字段。

解决：删除该字段，或查阅你所用版本文档改为支持的配置方式。

### 7.5 `ModuleNotFoundError: No module named 'langchain'`

原因：未激活正确环境或依赖未安装。

解决：确认激活目标 Conda 环境，再执行 `pip install -U ...`。

---

## 8. 最佳实践

- 把密钥放环境变量，不要硬编码到仓库
- Tool 描述（docstring）写清楚，便于 Agent 选择工具
- 先验证 MCP 服务能独立启动，再接 Agent
- 一次只接入一个 MCP 服务，跑通后再逐步增加
- 保持日志可读，必要时打印 `response["messages"]`

---

## 9. 扩展方向

- 增加多个 MCP 服务（天气、搜索、数据库）
- 增加你自己的本地 Tool（文件检索、业务规则）
- 引入会话记忆、RAG、权限控制与审计

---

## 10. 一句话总结

**Agent 负责决策，MCP 负责能力接入。** 只要处理好异步入口、模型参数名、MCP 传输配置这三个关键点，整套链路就能稳定运行。
