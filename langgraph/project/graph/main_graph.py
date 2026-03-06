"""
LangGraph 主编排图 — 系统的核心调度中枢
==========================================

教程要点 (★★★ 最重要的文件):
    1. StateGraph 构建有向图 — 节点 (Node) + 边 (Edge)
    2. 条件边 (conditional_edge) 实现动态路由
    3. 子图 (Subgraph) 封装复杂子流程
    4. Checkpoint 持久化实现对话恢复
    5. 流式执行 astream_events() 实现 token 级流式
    6. LCEL 语法在节点内部构建处理链

主图流程:
    ┌─────────┐
    │  START   │
    └────┬─────┘
         │
    ┌────▼─────┐
    │ 输入预处理 │ ← 语音: 降噪→VAD→STT; 文本: 直接传递
    └────┬─────┘
         │
    ┌────▼─────┐
    │ 记忆加载  │ ← 短期(会话窗口) + 长期(语义检索)
    └────┬─────┘
         │
    ┌────▼─────┐     ┌──────────────┐
    │ 意图路由  │────►│ RAG 子图      │
    └────┬─────┘     ├──────────────┤
         │           │ 多Agent子图   │
         │           ├──────────────┤
         │           │ 工具调用节点   │
         │           ├──────────────┤
         │           │ 直接对话节点   │
         │           └───────┬──────┘
         │                   │
    ┌────▼───────────────────▼─┐
    │    响应合成 + 记忆更新      │
    └────┬─────────────────────┘
         │
    ┌────▼─────┐
    │ TTS 合成  │ ← 仅语音模式
    └────┬─────┘
         │
    ┌────▼─────┐
    │   END    │
    └──────────┘
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from config.settings import Settings, get_settings
from graph.state import MainGraphState
from graph.edges.conditions import route_by_intent, should_continue_loop


def build_main_graph(settings: Settings | None = None) -> Any:
    """
    构建并编译主编排图

    教程要点:
        - StateGraph(MainGraphState): 以 State 类型参数化图
        - add_node(): 注册节点, 值为 async callable
        - add_edge(): 无条件边
        - add_conditional_edges(): 条件分支
        - compile(): 编译为可执行 Runnable (支持 LCEL 管道)
        - checkpointer: 传入 MemorySaver / SqliteSaver 实现持久化

    Returns:
        CompiledGraph — 可直接 ainvoke / astream / astream_events
    """
    if settings is None:
        settings = get_settings()

    # ── 导入所有节点函数 ─────────────────────
    from graph.nodes.input_processor import process_input
    from graph.nodes.memory_loader import load_memory
    from graph.nodes.router import route_intent
    from graph.nodes.chat import chat_node
    from graph.nodes.rag_retriever import rag_node
    from graph.nodes.voice_processor import tts_node
    from graph.nodes.response_synthesizer import synthesize_response
    from graph.nodes.memory_updater import update_memory
    from graph.nodes.tool_executor import execute_tools

    # ── 导入子图 ─────────────────────────────
    from graph.subgraphs.rag_subgraph import build_rag_subgraph
    from graph.subgraphs.multi_agent_subgraph import build_multi_agent_subgraph

    # ── 构建 StateGraph ─────────────────────
    graph = StateGraph(MainGraphState)

    # ── 注册节点 ─────────────────────────────
    graph.add_node("input_processor", process_input)
    graph.add_node("memory_loader", load_memory)
    graph.add_node("router", route_intent)
    graph.add_node("chat", chat_node)
    graph.add_node("rag", rag_node)
    graph.add_node("tool_executor", execute_tools)
    graph.add_node("multi_agent", build_multi_agent_subgraph(settings))
    graph.add_node("response_synthesizer", synthesize_response)
    graph.add_node("memory_updater", update_memory)
    graph.add_node("tts", tts_node)

    # ── 边: 线性流水线部分 ───────────────────
    graph.add_edge(START, "input_processor")
    graph.add_edge("input_processor", "memory_loader")
    graph.add_edge("memory_loader", "router")

    # ── 条件边: 意图路由 → 不同处理分支 ─────
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "chat": "chat",
            "rag": "rag",
            "tool_call": "tool_executor",
            "multi_agent": "multi_agent",
        },
    )

    # ── 各分支 → 响应合成 ────────────────────
    graph.add_edge("chat", "response_synthesizer")
    graph.add_edge("rag", "response_synthesizer")
    graph.add_edge("tool_executor", "response_synthesizer")
    graph.add_edge("multi_agent", "response_synthesizer")

    # ── 响应合成 → 记忆更新 ──────────────────
    graph.add_edge("response_synthesizer", "memory_updater")

    # ── 记忆更新 → 条件: 是否需要 TTS ────────
    graph.add_conditional_edges(
        "memory_updater",
        lambda state: "tts" if state.get("input_type") == "audio" else "end",
        {
            "tts": "tts",
            "end": END,
        },
    )

    # ── TTS → 结束 ──────────────────────────
    graph.add_edge("tts", END)

    # ── 编译: 注入 Checkpointer 实现持久化 ──
    # 开发环境用 MemorySaver, 生产环境换 SqliteSaver / PostgresSaver
    checkpointer = MemorySaver()

    compiled = graph.compile(
        checkpointer=checkpointer,
        # interrupt_before=["tool_executor"],  # 可选: 人工审批工具调用
    )

    return compiled
