"""
LCEL 记忆链 — 统一记忆接口
==============================

教程要点:
    memory_chain = (
        RunnablePassthrough.assign(
            long_term=recall_memories,
            short_term=get_recent_messages,
        )
        | format_memory_context
    )
"""

from __future__ import annotations

from langchain_core.runnables import RunnableLambda, RunnablePassthrough


def build_memory_chain():
    """
    构建 LCEL 记忆链

    教程要点 — LCEL 组合:
        memory_chain = (
            RunnablePassthrough.assign(
                # 并行获取短期记忆和长期记忆
                short_term_messages=RunnableLambda(fetch_short_term),
                long_term_facts=RunnableLambda(fetch_long_term_facts),
                long_term_preferences=RunnableLambda(fetch_long_term_prefs),
            )
            | RunnableLambda(format_memory_prompt)
        )

    Returns:
        Runnable — 输入 {"user_id", "query"}, 输出 {"memory_prompt"}
    """
    # TODO: 实际实现
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"memory_prompt": ""})
    )
