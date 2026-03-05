"""
工具执行节点 — 动态工具调用
==============================

教程要点:
    1. LangGraph 的 ToolNode 自动解析 LLM 的 tool_calls
    2. 也可手动实现工具分发逻辑
    3. 支持并行工具调用 (parallel tool execution)
    4. 工具结果注入为 ToolMessage 回到 messages
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import ToolMessage

from graph.state import MainGraphState


async def execute_tools(state: MainGraphState) -> dict[str, Any]:
    """
    工具执行节点

    教程要点 — 两种工具执行模式:

    模式 1: LangGraph 内置 ToolNode (推荐)
        from langgraph.prebuilt import ToolNode
        tool_node = ToolNode(tools=[search_tool, voice_tool, ...])
        # 自动解析 messages 中最后一条 AIMessage 的 tool_calls

    模式 2: 手动分发
        for tool_call in state["tool_calls"]:
            tool = registry.get(tool_call["name"])
            result = await tool.ainvoke(tool_call["args"])
            tool_messages.append(ToolMessage(...))

    企业级实践:
        - 工具注册表 (Tool Registry) 动态管理工具
        - 工具调用审计日志
        - 超时控制 + 重试
        - 敏感工具人工审批 (interrupt_before)
    """
    tool_calls = state.get("tool_calls", [])
    messages = state.get("messages", [])

    # 从最后一条 AI 消息提取 tool_calls
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            tool_calls = last_msg.tool_calls

    tool_results = []
    tool_messages = []

    for call in tool_calls:
        # TODO: 实际实现 — 从工具注册表获取并执行
        # tool = tool_registry.get(call["name"])
        # result = await tool.ainvoke(call["args"])
        result = f"[Tool result placeholder for {call.get('name', 'unknown')}]"

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call.get("id", ""),
            )
        )
        tool_results.append({"name": call.get("name"), "result": result})

    return {
        "messages": tool_messages,
        "tool_results": tool_results,
        "response_text": "\n".join(str(r["result"]) for r in tool_results),
    }
