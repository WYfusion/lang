"""
RAG Schema — 检索增强生成相关模型
==================================

教程要点:
    1. 文档生命周期: 上传 → 分块 → 嵌入 → 存储 → 检索
    2. 检索结果携带 score + source 方便溯源
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    filename: str
    content_type: str = "text/plain"  # text/plain, application/pdf, etc.
    content_base64: Optional[str] = None
    url: Optional[str] = None
    collection_name: str = Field("default", description="向量库集合名称")
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """文档分块"""
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    chunk_index: int
    embedding: Optional[list[float]] = Field(None, exclude=True)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalRequest(BaseModel):
    """检索请求"""
    query: str = Field(..., min_length=1)
    collection_name: str = "default"
    top_k: int = Field(5, ge=1, le=50)
    score_threshold: float = Field(0.0, ge=0.0, le=1.0)
    filter_metadata: Optional[dict[str, Any]] = None


class RetrievalResult(BaseModel):
    """单条检索结果"""
    chunk_id: UUID
    content: str
    score: float = Field(description="相似度分数")
    source: str = Field("", description="来源文档名称")
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalResponse(BaseModel):
    """检索响应"""
    query: str
    results: list[RetrievalResult]
    total_found: int
    latency_ms: float = 0.0
