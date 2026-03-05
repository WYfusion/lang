"""
搜索工具 — Web 搜索
=====================
"""

from __future__ import annotations

from langchain_core.tools import tool


@tool
async def web_search(query: str) -> str:
    """
    Web 搜索工具 — 搜索互联网获取最新信息

    教程要点:
        @tool 装饰器自动将函数包装为 LangChain Tool
        - 函数签名 → 工具输入 schema
        - docstring → 工具描述 (LLM 用来决定何时调用)
        - 支持 async

    Args:
        query: 搜索查询关键词

    Returns:
        搜索结果摘要文本
    """
    # TODO: 集成实际搜索 API
    # from langchain_community.tools import TavilySearchResults
    # search = TavilySearchResults(max_results=5)
    # results = await search.ainvoke(query)
    return f"[Search results for: {query}]"
