"""
文档加载工具
=============
"""

from __future__ import annotations

from langchain_core.tools import tool


@tool
async def load_document(file_path: str, content_type: str = "text/plain") -> str:
    """
    加载并解析文档

    教程要点:
        - LangChain 提供丰富的 DocumentLoader
        - 支持: PDF, DOCX, HTML, Markdown, CSV 等
        - 加载后返回 Document 对象列表

    Args:
        file_path: 文档路径或 URL
        content_type: 文档类型

    Returns:
        解析后的文本内容
    """
    # TODO: 实际实现
    # from langchain_community.document_loaders import (
    #     PyPDFLoader, TextLoader, UnstructuredHTMLLoader
    # )
    # loader = get_loader(file_path, content_type)
    # docs = await loader.aload()
    # return "\n".join(d.page_content for d in docs)
    return f"[Loaded document from: {file_path}]"
