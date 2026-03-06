"""
记忆存储工具 — 作为 LangChain Tool 暴露
==========================================
"""

from __future__ import annotations

from langchain_core.tools import tool


@tool
async def store_memory(user_id: str, content: str, memory_type: str = "fact") -> str:
    """
    存储用户记忆

    Args:
        user_id: 用户ID
        content: 记忆内容
        memory_type: 记忆类型 (fact / preference / episodic)

    Returns:
        存储结果确认
    """
    # TODO: 实际调用 MemoryRepository
    return f"Memory stored: [{memory_type}] {content}"


@tool
async def recall_memory(user_id: str, query: str, top_k: int = 5) -> str:
    """
    回忆用户记忆 — 语义检索

    Args:
        user_id: 用户ID
        query: 检索查询
        top_k: 返回数量

    Returns:
        相关记忆列表
    """
    # TODO: 实际调用 MemoryRepository + 向量检索
    return f"[Recalled memories for: {query}]"
