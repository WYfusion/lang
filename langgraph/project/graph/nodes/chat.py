"""
对话节点 — 核心 LLM 对话处理
===============================

教程要点:
    1. LCEL 链: system_prompt + memory_prompt + messages → LLM → response
    2. 流式输出: 节点内通过 astream() 逐 token 生成
    3. 回调机制: callbacks 传递流式事件给上层
    4. 记忆注入: 长期记忆作为 system prompt 的一部分
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from graph.state import MainGraphState


# ──────────────────────────────────────────────
# 对话提示词模板
# ──────────────────────────────────────────────
CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能助手。请用中文回答用户的问题。

{memory_prompt}

请保持回答简洁、准确、有帮助。"""),
    MessagesPlaceholder(variable_name="messages"),
])


async def chat_node(state: MainGraphState) -> dict[str, Any]:
    """
    直接对话节点

    教程要点 — LCEL 管道:
        chain = CHAT_PROMPT | llm
        response = await chain.ainvoke({
            "messages": messages,
            "memory_prompt": memory_context.get("memory_prompt", ""),
        })

    流式输出模式:
        async for chunk in chain.astream({...}):
            yield chunk  # 通过 callback 传递给 API 层

    企业级实践:
        - 使用 with_retry() 包装 LLM 调用, tenacity 自动重试
        - 使用 with_fallbacks() 实现模型降级 (主模型挂了切备用)
        - 使用 RunnableConfig 传递 callbacks 给流式处理器
    """
    messages = state.get("messages", [])
    memory = state.get("memory", {})
    memory_prompt = memory.get("memory_prompt", "")

    # TODO: 实际实现
    # from services.llm_service import get_chat_model
    # llm = get_chat_model()
    #
    # # 企业级: 重试 + 降级
    # robust_llm = llm.with_retry(stop_after_attempt=3).with_fallbacks([fallback_llm])
    #
    # chain = CHAT_PROMPT | robust_llm
    # response = await chain.ainvoke({
    #     "messages": messages,
    #     "memory_prompt": memory_prompt,
    # })

    # 框架占位
    response_text = "[AI Response Placeholder — 实际由 LLM 生成]"

    return {
        "messages": [AIMessage(content=response_text)],
        "response_text": response_text,
    }
