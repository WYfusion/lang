"""
条件边 — 图的动态路由逻辑
============================

教程要点:
    1. 条件边函数接收 State, 返回字符串 (目标节点名)
    2. add_conditional_edges() 的映射表定义所有可能目标
    3. 可结合 LLM 判断 + 规则判断 做混合路由
"""

from __future__ import annotations

from graph.state import MainGraphState


def route_by_intent(state: MainGraphState) -> str:
    """
    根据意图路由到对应处理节点

    教程要点:
        add_conditional_edges("router", route_by_intent, {
            "chat": "chat",
            "rag": "rag",
            "tool_call": "tool_executor",
            "multi_agent": "multi_agent",
        })
    """
    intent = state.get("current_intent", "chat")

    # 置信度低时降级到 chat
    confidence = state.get("confidence", 0.0)
    if confidence < 0.5:
        return "chat"

    return intent


def should_continue_loop(state: MainGraphState) -> str:
    """
    循环控制条件边 — 用于需要多轮迭代的场景

    教程要点:
        - Tool-calling loop: LLM → tool → LLM → tool → ... → 最终回答
        - 使用 should_continue 标志或 max_iterations 防止无限循环
    """
    should_continue = state.get("should_continue", False)
    if should_continue:
        return "continue"
    return "end"


def route_voice_or_end(state: MainGraphState) -> str:
    """TTS 路由: 语音输入才走 TTS"""
    if state.get("input_type") == "audio":
        return "tts"
    return "end"
