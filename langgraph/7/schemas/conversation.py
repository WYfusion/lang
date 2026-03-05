"""
会话 Schema — 会话生命周期管理
================================

教程要点:
    1. 会话是多轮对话的顶层容器
    2. 会话状态机: active → paused → archived
    3. 关联 LangGraph 的 thread_id 实现有状态图
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ConversationCreate(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field(None, max_length=200, description="会话标题, 可自动生成")
    user_id: str = Field(..., description="用户唯一标识")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    """会话详情响应"""
    id: UUID = Field(default_factory=uuid4)
    title: str = ""
    user_id: str
    status: ConversationStatus = ConversationStatus.ACTIVE
    thread_id: str = Field(description="LangGraph thread_id, 用于 checkpoint 恢复")
    message_count: int = 0
    total_tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationListResponse(BaseModel):
    """会话列表分页响应"""
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int


class ConversationUpdate(BaseModel):
    """更新会话"""
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    metadata: Optional[dict[str, Any]] = None
