"""
消息 ORM 模型
==============
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
except ImportError:
    from base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.conversation import Conversation


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """消息表 — 存储完整对话历史"""

    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)       # user / assistant / system / tool
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), default="text")  # text / audio / image
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    # 关系
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
