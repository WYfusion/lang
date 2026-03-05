"""
RAG 检索节点 — 检索增强生成
==============================

教程要点:
    1. LCEL 链: query_rewriter | retriever | context_formatter | llm
    2. 查询改写: 提升检索召回率
    3. 相关性评估: 过滤低分文档
    4. Grounded Generation: 基于检索上下文生成回答
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from graph.state import MainGraphState


RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个知识助手。请根据以下检索到的上下文回答用户问题。
如果上下文中没有相关信息，请如实告知。

## 检索上下文:
{context}

{memory_prompt}"""),
    ("placeholder", "{messages}"),
])


async def rag_node(state: MainGraphState) -> dict[str, Any]:
    """
    RAG 检索节点

    教程要点 — 完整 LCEL RAG 链:

        # 1. 查询改写链
        rewrite_chain = rewrite_prompt | llm | StrOutputParser()

        # 2. 检索链 (使用 LCEL RunnableParallel)
        retrieval_chain = RunnableParallel(
            context=rewrite_chain | retriever | format_docs,
            messages=RunnablePassthrough(),
        )

        # 3. 生成链
        rag_chain = retrieval_chain | RAG_PROMPT | llm

        # 完整管道
        full_chain = rewrite_chain | retriever | rag_prompt | llm

    企业级实践:
        - 查询改写 (Query Rewriting) 提升召回率
        - 多路检索 (Multi-Query Retriever)
        - 重排序 (Re-ranking) 提升精度
        - 引用溯源 (Citation)
        - 相关性评分过滤
    """
    messages = state.get("messages", [])
    memory = state.get("memory", {})

    # 获取查询文本
    query = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            query = msg.content
            break

    # TODO: 实际实现
    # from rag.retrieval_chain import build_retrieval_chain
    # retrieval_chain = build_retrieval_chain(settings)
    # result = await retrieval_chain.ainvoke({"query": query})

    # 框架占位
    retrieved_docs: list[dict[str, Any]] = []
    context_text = "[检索上下文占位 — 实际从向量库检索]"

    response_text = f"[RAG Response for: {query}]"

    return {
        "rag": {
            "query": query,
            "retrieved_docs": retrieved_docs,
            "context_text": context_text,
        },
        "messages": [AIMessage(content=response_text)],
        "response_text": response_text,
    }
