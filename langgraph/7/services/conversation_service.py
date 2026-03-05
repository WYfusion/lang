"""
会话服务 — 业务逻辑层
========================
"""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from db.repositories import ConversationRepository, MessageRepository


class ConversationService:
    """
    会话服务

    教程要点:
        Service 层封装业务逻辑, 协调多个 Repository
        - 创建会话 (同时创建 LangGraph thread)
        - 发送消息 (调用 Graph + 持久化)
        - 获取历史 (从 DB + Checkpoint)
    """

    def __init__(
        self,
        conv_repo: ConversationRepository,
        msg_repo: MessageRepository,
    ):
        self.conv_repo = conv_repo
        self.msg_repo = msg_repo

    async def create_conversation(self, user_id: str, title: str = "") -> dict:
        """创建新会话"""
        thread_id = str(uuid4())
        conv = await self.conv_repo.create(
            user_id=user_id,
            thread_id=thread_id,
            title=title or "新对话",
        )
        return {"id": conv.id, "thread_id": thread_id}

    async def get_or_create(self, user_id: str, conversation_id: Optional[str] = None) -> dict:
        """获取或创建会话"""
        if conversation_id:
            conv = await self.conv_repo.get_by_id(conversation_id)
            if conv:
                return {"id": conv.id, "thread_id": conv.thread_id}
        return await self.create_conversation(user_id)

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        latency_ms: float = 0.0,
    ) -> None:
        """保存消息"""
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_used=tokens,
            latency_ms=latency_ms,
        )
        await self.conv_repo.increment_message_count(conversation_id, tokens)
