"""
记忆 Schema — 长期记忆与摘要
==============================

教程要点:
    1. 短期记忆: 会话内 K 轮消息窗口 (存于 LangGraph State)
    2. 长期记忆: 跨会话事实/偏好，持久化到 DB
    3. 摘要记忆: 会话消息超长时自动压缩为摘要
    4. 向量记忆: 语义相关的历史信息, 存入向量库
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """记忆类型枚举"""
    FACT = "fact"           # 用户事实: "我住在北京"
    PREFERENCE = "preference"  # 用户偏好: "我喜欢简洁回答"
    SUMMARY = "summary"     # 会话摘要
    EPISODIC = "episodic"   # 情景记忆: 某次对话的关键信息


class MemoryCreate(BaseModel):
    """创建记忆"""
    user_id: str
    memory_type: MemoryType
    content: str = Field(..., min_length=1, description="记忆内容")
    source_conversation_id: Optional[UUID] = None
    importance: float = Field(0.5, ge=0.0, le=1.0, description="重要性评分, LLM 自动打分")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryResponse(BaseModel):
    """记忆详情"""
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    memory_type: MemoryType
    content: str
    importance: float
    access_count: int = 0
    last_accessed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemorySearchRequest(BaseModel):
    """记忆检索请求"""
    user_id: str
    query: str = Field(..., description="检索查询, 语义搜索")
    memory_types: Optional[list[MemoryType]] = None
    top_k: int = Field(5, ge=1, le=50)
    min_importance: float = Field(0.0, ge=0.0, le=1.0)


class MemorySearchResponse(BaseModel):
    """记忆检索响应"""
    memories: list[MemoryResponse]
    query: str
    total_found: int
