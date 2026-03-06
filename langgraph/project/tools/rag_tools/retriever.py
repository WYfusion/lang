"""
向量检索工具 — 作为 LangChain Tool 暴露
==========================================
"""

from __future__ import annotations

from langchain_core.tools import tool


@tool
async def semantic_search_tool(query: str, collection: str = "default", top_k: int = 5) -> str:
    """
    语义检索工具 — 从向量库中检索相关文档

    Args:
        query: 搜索查询
        collection: 向量库集合名称
        top_k: 返回结果数量

    Returns:
        格式化的检索结果
    """
    # TODO: 实际实现
    # from rag.vectorstore import VectorStoreManager
    # manager = VectorStoreManager(get_settings())
    # results = await manager.search(query, collection, top_k)
    # return format_results(results)
    return f"[Semantic search results for: {query}]"
