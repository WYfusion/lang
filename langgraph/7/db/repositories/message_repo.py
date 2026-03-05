"""
消息仓储
=========
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.message import Message


class MessageRepository:
    """消息仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: str,
        role: str,
        content: str,
        message_type: str = "text",
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        metadata_json: str = "{}",
    ) -> Message:
        msg = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            metadata_json=metadata_json,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def get_history(
        self, conversation_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[Message]:
        """获取对话历史 (按时间正序)"""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent(self, conversation_id: str, k: int = 20) -> Sequence[Message]:
        """获取最近 K 条消息 — 用于短期记忆窗口"""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(k)
        )
        messages = list(result.scalars().all())
        messages.reverse()  # 恢复时间正序
        return messages
