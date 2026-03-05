"""
RAG 子图 — 完整的检索增强生成流水线
======================================

教程要点 (★★ 重要):
    1. 子图 (Subgraph) 封装独立的 StateGraph
    2. 子图有自己的 State, 与主图通过输入/输出映射连接
    3. RAG 流水线: 查询改写 → 检索 → 相关性评估 → 生成 → 质量检查

    子图流程:
        ┌─────────┐
        │  START   │
        └────┬─────┘
             │
        ┌────▼──────┐
        │ 查询改写   │
        └────┬──────┘
             │
        ┌────▼──────┐
        │ 检索文档   │
        └────┬──────┘
             │
        ┌────▼──────┐     ┌──────────┐
        │ 相关性评估 │───►│ 重新检索  │ (评分太低时循环)
        └────┬──────┘     └──────────┘
             │
        ┌────▼──────┐
        │ 有据生成   │
        └────┬──────┘
             │
        ┌────▼──────┐
        │   END     │
        └───────────┘
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from config.settings import Settings
from graph.state import RAGSubgraphState


async def rewrite_query(state: RAGSubgraphState) -> dict[str, Any]:
    """
    查询改写节点

    教程要点 — LCEL:
        rewrite_chain = (
            rewrite_prompt
            | llm
            | StrOutputParser()
        )
        rewritten = await rewrite_chain.ainvoke({"query": original_query})
    """
    query = state.get("query", "")
    # TODO: LLM 改写查询
    rewritten = query  # 占位: 原样返回
    return {"rewritten_query": rewritten}


async def retrieve_documents(state: RAGSubgraphState) -> dict[str, Any]:
    """
    文档检索节点

    教程要点:
        - 使用 LangChain Retriever 接口
        - 支持多种后端: Chroma / FAISS / Pinecone / Elasticsearch
        - 可用 EnsembleRetriever 混合 BM25 + 向量检索
    """
    query = state.get("rewritten_query", state.get("query", ""))
    # TODO: 实际检索
    docs: list[dict[str, Any]] = []
    scores: list[float] = []
    return {"retrieved_docs": docs, "relevance_scores": scores}


async def evaluate_relevance(state: RAGSubgraphState) -> dict[str, Any]:
    """
    相关性评估节点

    教程要点:
        - LLM 判断检索文档是否与查询相关
        - 可用 Cross-Encoder 重排序
        - 阈值过滤: 低于分数线的文档丢弃
    """
    scores = state.get("relevance_scores", [])
    needs_retry = all(s < 0.5 for s in scores) if scores else True
    return {"needs_retry": needs_retry}


def should_retry_retrieval(state: RAGSubgraphState) -> str:
    """条件边: 是否需要重新检索"""
    if state.get("needs_retry", False):
        return "rewrite"  # 重新改写查询再检索
    return "generate"


async def grounded_generate(state: RAGSubgraphState) -> dict[str, Any]:
    """
    有据生成节点

    教程要点:
        - 基于检索文档生成回答
        - 添加引用标注 (citation)
        - 检测幻觉 (hallucination detection)
    """
    docs = state.get("retrieved_docs", [])
    query = state.get("query", "")
    # TODO: 实际生成
    response = f"[RAG grounded response for: {query}]"
    return {
        "grounded_response": response,
        "messages": [AIMessage(content=response)],
    }


def build_rag_subgraph(settings: Settings) -> StateGraph:
    """
    构建 RAG 子图

    教程要点:
        - 子图作为节点注册到主图: graph.add_node("rag", build_rag_subgraph(settings))
        - 子图编译后是一个 Runnable, 可独立测试
    """
    graph = StateGraph(RAGSubgraphState)

    graph.add_node("rewrite", rewrite_query)
    graph.add_node("retrieve", retrieve_documents)
    graph.add_node("evaluate", evaluate_relevance)
    graph.add_node("generate", grounded_generate)

    graph.add_edge(START, "rewrite")
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        should_retry_retrieval,
        {"rewrite": "rewrite", "generate": "generate"},
    )

    graph.add_edge("generate", END)

    return graph.compile()
