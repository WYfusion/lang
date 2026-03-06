"""
记忆加载节点 — 注入短期/长期记忆上下文
=========================================

教程要点:
    1. LCEL 语法构建记忆检索链
    2. 短期记忆: 从 DB 加载最近 K 轮消息
    3. 长期记忆: 语义检索用户事实/偏好
    4. 记忆注入方式: 构造 system prompt 前缀
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import SystemMessage

from graph.state import MainGraphState


async def load_memory(state: MainGraphState) -> dict[str, Any]:
    """
    记忆加载节点

    流程:
        1. 获取 user_id & conversation_id
        2. 加载短期记忆 (最近 K 轮消息 — 已在 messages 中)
        3. 语义检索长期记忆 (事实 + 偏好)
        4. 构造记忆提示注入 State

    教程要点 — LCEL 链式记忆检索:
        memory_chain = (
            RunnablePassthrough.assign(query=lambda x: x["messages"][-1].content)
            | retriever
            | format_memories
        )
    """
    user_id = state.get("user_id", "")
    messages = state.get("messages", [])

    # 获取最后一条用户消息作为检索查询
    last_user_msg = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_user_msg = msg.content
            break

    # TODO: 实际实现中从 DB 检索长期记忆
    # async with get_async_session() as session:
    #     memory_repo = MemoryRepository(session)
    #     facts = await memory_repo.get_by_user(user_id, "fact")
    #     preferences = await memory_repo.get_by_user(user_id, "preference")

    # 构造记忆上下文 (框架占位)
    memory_context = {
        "short_term_messages": [],       # 已在 messages 中
        "long_term_facts": [],            # TODO: 从 DB 检索
        "long_term_preferences": [],      # TODO: 从 DB 检索
        "summary": "",                    # TODO: 历史摘要
        "memory_prompt": "",              # 拼接后的记忆提示
    }

    # 如果有长期记忆, 构造系统提示
    if memory_context["long_term_facts"] or memory_context["long_term_preferences"]:
        facts_text = "\n".join(f"- {f}" for f in memory_context["long_term_facts"])
        prefs_text = "\n".join(f"- {p}" for p in memory_context["long_term_preferences"])
        memory_prompt = (
            f"## 用户背景信息 (长期记忆)\n"
            f"### 已知事实:\n{facts_text}\n"
            f"### 用户偏好:\n{prefs_text}\n"
        )
        memory_context["memory_prompt"] = memory_prompt

    return {"memory": memory_context}
