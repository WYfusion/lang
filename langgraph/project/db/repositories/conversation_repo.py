"""
会话仓储 — Repository 模式
=============================

教程要点:
    1. Repository 封装 DB 操作, 隔离 ORM 细节
    2. 所有方法均为 async — 配合 FastAPI 异步调度
    3. 使用 SQLAlchemy 2.0 select() 查询语法
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import uuid4

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.conversation import Conversation


class ConversationRepository:
    """会话仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: str, thread_id: str, title: str = "", metadata_json: str = "{}"
    ) -> Conversation:
        """创建新会话"""
        conv = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            thread_id=thread_id,
            title=title,
            metadata_json=metadata_json,
        )
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """按 ID 查询"""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_thread_id(self, thread_id: str) -> Optional[Conversation]:
        """按 LangGraph thread_id 查询"""
        result = await self.session.execute(
            select(Conversation).where(Conversation.thread_id == thread_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: str, status: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> tuple[Sequence[Conversation], int]:
        """分页列表"""
        query = select(Conversation).where(Conversation.user_id == user_id)
        count_query = select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)

        if status:
            query = query.where(Conversation.status == status)
            count_query = count_query.where(Conversation.status == status)

        query = query.order_by(Conversation.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return result.scalars().all(), count_result.scalar_one()

    async def update_status(self, conversation_id: str, status: str) -> None:
        """更新状态"""
        await self.session.execute(
            update(Conversation).where(Conversation.id == conversation_id).values(status=status)
        )

    async def increment_message_count(self, conversation_id: str, tokens: int = 0) -> None:
        """增量更新消息计数与 token 计数"""
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(
                message_count=Conversation.message_count + 1,
                total_tokens=Conversation.total_tokens + tokens,
            )
        )
