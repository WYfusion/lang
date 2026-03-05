"""
意图路由节点 — LLM 驱动的智能路由
====================================

教程要点:
    1. 使用 LLM + structured output 做意图分类
    2. LCEL: prompt | llm.with_structured_output(RouterOutput)
    3. 路由结果写入 State.current_intent
    4. 条件边根据 intent 值分发到不同节点
"""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel as LCBaseModel, Field as LCField

from graph.state import MainGraphState


# ──────────────────────────────────────────────
# 路由 LLM 输出结构
# ──────────────────────────────────────────────
class RouterOutput(LCBaseModel):
    """LLM 结构化输出 — 意图路由结果

    教程要点:
        with_structured_output() 让 LLM 强制输出此结构
        比正则解析更稳健, 也是企业级常用模式
    """
    intent: Literal["chat", "rag", "tool_call", "multi_agent"] = LCField(
        description="用户意图分类: chat=闲聊, rag=需检索知识库, tool_call=需调用工具, multi_agent=需多Agent协作"
    )
    confidence: float = LCField(description="路由置信度 0-1", ge=0.0, le=1.0)
    reasoning: str = LCField(description="简短推理说明")


# 路由提示词模板
ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个意图路由器。分析用户最新消息，判断应该路由到哪个处理分支:

- **chat**: 日常闲聊、问候、简单问答
- **rag**: 需要检索知识库/文档才能回答的问题
- **tool_call**: 需要调用外部工具 (搜索、计算、语音处理等)
- **multi_agent**: 复杂任务需要多个专家Agent协作完成

请根据消息内容做出判断。"""),
    ("placeholder", "{messages}"),
])


async def route_intent(state: MainGraphState) -> dict[str, Any]:
    """
    意图路由节点

    教程要点 — LCEL 链:
        chain = ROUTER_PROMPT | llm.with_structured_output(RouterOutput)
        result = await chain.ainvoke({"messages": messages})

    实现:
        1. 取最近几条消息作为上下文
        2. LCEL 链: prompt → LLM (structured output)
        3. 将路由结果写入 State
    """
    messages = state.get("messages", [])

    # TODO: 实际实现
    # from services.llm_service import get_chat_model
    # llm = get_chat_model()
    # chain = ROUTER_PROMPT | llm.with_structured_output(RouterOutput)
    # result = await chain.ainvoke({"messages": messages[-5:]})

    # 框架占位: 默认路由到 chat
    result = RouterOutput(intent="chat", confidence=0.9, reasoning="默认路由")

    return {
        "current_intent": result.intent,
        "confidence": result.confidence,
    }
