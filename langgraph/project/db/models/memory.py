"""
长期记忆 ORM 模型
==================

教程要点:
    1. 长期记忆独立于会话, 跨会话持久化
    2. importance 字段支持记忆衰减策略
    3. embedding_vector 列预留, 生产可用 pgvector 扩展
    4. access_count + last_accessed_at 支持频率加权检索
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Float, Index, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

try:
    from db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
except ImportError:
    from base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Memory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """长期记忆表"""

    __tablename__ = "memories"

    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    memory_type: Mapped[str] = mapped_column(String(20), nullable=False)   # fact / preference / summary / episodic
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 来源会话 (可选)
    source_conversation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # 嵌入向量 — 开发环境存 JSON 文本, 生产环境用 pgvector
    embedding_text: Mapped[str] = mapped_column(Text, default="", comment="JSON 序列化的嵌入向量")

    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    __table_args__ = (
        Index("ix_memories_user_type", "user_id", "memory_type"),
        Index("ix_memories_importance", "importance"),
    )
