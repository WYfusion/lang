"""
LCEL 检索链 — 完整的 RAG 管道
================================

教程要点 (★★★ LCEL 核心示例):
    这是一个完整的 LCEL (LangChain Expression Language) RAG 管道示例,
    展示如何用 | 运算符组合 Runnable 对象。

    完整链路:
        query → 改写 → 检索 → 格式化 → 生成 → 输出
"""

from __future__ import annotations

from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
)

from config.settings import Settings, get_settings


def format_docs(docs: list) -> str:
    """格式化检索文档为上下文文本"""
    formatted = []
    for i, doc in enumerate(docs, 1):
        content = doc.page_content if hasattr(doc, "page_content") else str(doc)
        source = doc.metadata.get("source", "unknown") if hasattr(doc, "metadata") else "unknown"
        formatted.append(f"[文档{i}] (来源: {source})\n{content}")
    return "\n\n".join(formatted)


# ──────────────────────────────────────────────
# RAG 提示词
# ──────────────────────────────────────────────
RAG_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个知识问答助手。请根据以下参考文档回答用户问题。

## 参考文档:
{context}

## 回答要求:
1. 仅基于参考文档中的信息回答
2. 如果文档中没有相关信息, 请明确告知
3. 在回答末尾标注引用来源 [文档N]
"""),
    ("human", "{question}"),
])


QUERY_REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个查询改写专家。将用户的口语化问题改写为更适合向量检索的查询关键词。只输出改写后的查询, 不要解释。"),
    ("human", "{question}"),
])


def build_retrieval_chain(settings: Settings | None = None):
    """
    构建完整的 LCEL RAG 链

    教程要点 (★★★ 核心 LCEL 模式):

    ```python
    # === 基础 RAG 链 ===
    basic_rag = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_GENERATION_PROMPT
        | llm
        | StrOutputParser()
    )

    # === 带查询改写的 RAG 链 ===
    advanced_rag = (
        RunnablePassthrough.assign(
            rewritten_query=QUERY_REWRITE_PROMPT | llm | StrOutputParser()
        )
        | RunnablePassthrough.assign(
            context=lambda x: retriever.invoke(x["rewritten_query"]) | format_docs
        )
        | RAG_GENERATION_PROMPT
        | llm
        | StrOutputParser()
    )

    # === 带多路检索的 RAG 链 ===
    multi_retrieval_rag = (
        RunnableParallel(
            bm25_results=bm25_retriever,
            vector_results=vector_retriever,
            question=RunnablePassthrough(),
        )
        | merge_and_rerank
        | RAG_GENERATION_PROMPT
        | llm
        | StrOutputParser()
    )
    ```

    Returns:
        Runnable — 可直接 ainvoke / astream
    """
    if settings is None:
        settings = get_settings()

    # TODO: 实际实现
    # from services.llm_service import get_chat_model
    # from rag.vectorstore import VectorStoreManager
    #
    # llm = get_chat_model(settings)
    # vs_manager = VectorStoreManager(settings)
    # retriever = vs_manager.get_retriever(search_kwargs={"k": settings.RAG_TOP_K})
    #
    # chain = (
    #     {"context": retriever | format_docs, "question": RunnablePassthrough()}
    #     | RAG_GENERATION_PROMPT
    #     | llm
    #     | StrOutputParser()
    # )
    # return chain

    # 框架占位: 返回一个简单的 Runnable
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: f"[RAG chain result for: {x}]")
    )
