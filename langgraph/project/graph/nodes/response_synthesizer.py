"""
响应合成节点 — 统一各分支输出
===============================

教程要点:
    1. 汇总各处理分支(chat/rag/tool/multi_agent)的输出
    2. 后处理: 格式化、安全过滤、长度控制
    3. 为 response_text 提供统一出口
"""

from __future__ import annotations

from typing import Any

from graph.state import MainGraphState


async def synthesize_response(state: MainGraphState) -> dict[str, Any]:
    """
    响应合成节点

    教程要点:
        - 作为多分支汇聚点, 统一输出格式
        - 可在此加入后处理链 (LCEL):
            post_process_chain = (
                RunnablePassthrough()
                | safety_filter      # 安全过滤
                | length_limiter     # 长度控制
                | format_output      # 格式化
            )
    """
    response_text = state.get("response_text", "")

    # 后处理 (框架占位)
    # TODO: 实际实现安全过滤、格式化等
    processed_text = response_text

    return {
        "response_text": processed_text,
    }
