"""
短期记忆 — 会话内消息窗口
============================

教程要点:
    1. 短期记忆 = 最近 K 轮消息
    2. LangGraph 的 messages State + checkpointer 天然支持
    3. 也可用 ConversationBufferWindowMemory 做额外管理
"""

from __future__ import annotations

from typing import Any, Sequence

from langchain_core.messages import BaseMessage


class ShortTermMemory:
    """
    短期记忆管理器

    教程要点:
        在 LangGraph 中, 短期记忆天然由 State.messages 承载:
        - checkpointer 负责持久化 (MemorySaver / SqliteSaver)
        - add_messages Reducer 自动追加消息
        - 窗口截断在 memory_loader 节点中实现

    额外功能:
        - 消息窗口截断 (保留最近 K 轮)
        - Token 计数, 避免超出上下文窗口
    """

    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens

    def truncate(self, messages: Sequence[BaseMessage]) -> list[BaseMessage]:
        """
        截断消息窗口

        策略:
            1. 保留 system 消息
            2. 从最新消息往回保留 max_messages 条
            3. Token 计数超限时进一步截断
        """
        if len(messages) <= self.max_messages:
            return list(messages)

        # 保留 system 消息
        system_msgs = [m for m in messages if hasattr(m, "type") and m.type == "system"]
        non_system = [m for m in messages if not (hasattr(m, "type") and m.type == "system")]

        # 截断
        truncated = non_system[-self.max_messages:]
        return system_msgs + truncated

    def estimate_tokens(self, messages: Sequence[BaseMessage]) -> int:
        """粗略估计 token 数"""
        # 简单估算: 中文 ~1.5 token/字, 英文 ~0.75 token/word
        total_chars = sum(len(m.content) for m in messages if hasattr(m, "content"))
        return int(total_chars * 1.5)
