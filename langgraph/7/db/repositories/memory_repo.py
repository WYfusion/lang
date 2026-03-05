"""
记忆仓储
=========

教程要点:
    1. 长期记忆的 CRUD + 语义检索
    2. 访问计数自动更新 — 支持记忆强化策略
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence
from uuid import uuid4

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.memory import Memory


class MemoryRepository:
    """长期记忆仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        importance: float = 0.5,
        source_conversation_id: Optional[str] = None,
        embedding_text: str = "",
        metadata_json: str = "{}",
    ) -> Memory:
        mem = Memory(
            id=str(uuid4()),
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            source_conversation_id=source_conversation_id,
            embedding_text=embedding_text,
            metadata_json=metadata_json,
        )
        self.session.add(mem)
        await self.session.flush()
        return mem

    async def get_by_user(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 50,
    ) -> Sequence[Memory]:
        """按用户查询记忆"""
        query = (
            select(Memory)
            .where(Memory.user_id == user_id, Memory.importance >= min_importance)
            .order_by(Memory.importance.desc(), Memory.updated_at.desc())
            .limit(limit)
        )
        if memory_type:
            query = query.where(Memory.memory_type == memory_type)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def touch(self, memory_id: str) -> None:
        """更新访问计数和时间 — 记忆强化"""
        await self.session.execute(
            update(Memory)
            .where(Memory.id == memory_id)
            .values(
                access_count=Memory.access_count + 1,
                last_accessed_at=datetime.utcnow(),
            )
        )

    async def update_importance(self, memory_id: str, importance: float) -> None:
        """更新重要性评分"""
        await self.session.execute(
            update(Memory)
            .where(Memory.id == memory_id)
            .values(importance=importance)
        )

    async def delete_by_user(self, user_id: str, memory_type: Optional[str] = None) -> int:
        """清除用户记忆"""
        from sqlalchemy import delete as sa_delete
        query = sa_delete(Memory).where(Memory.user_id == user_id)
        if memory_type:
            query = query.where(Memory.memory_type == memory_type)
        result = await self.session.execute(query)
        return result.rowcount
