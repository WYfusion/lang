"""
会话 ORM 模型
==============

教程要点:
    1. SQLAlchemy 2.0 Mapped[] 类型注解语法
    2. 关联 LangGraph 的 thread_id — checkpoint 持久化的桥梁
    3. relationship() 懒加载 + selectinload 策略
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
except ImportError:
    from base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.message import Message


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """会话表 — 一个会话对应一个 LangGraph thread"""

    __tablename__ = "conversations"

    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")  # active / paused / archived
    thread_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False,
                                            comment="LangGraph checkpoint thread_id")
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    # 关系
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_conversations_user_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user={self.user_id}, thread={self.thread_id})>"
