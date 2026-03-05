"""
消息 Schema — 对话消息的输入/输出模型
========================================

教程要点:
    1. Pydantic V2 BaseModel 替代 dict, 强类型保证接口安全
    2. 区分 Request / Response / Internal 三类 Schema
    3. 使用 Field 添加验证、描述、示例
    4. 支持序列化为 LangChain 的 MessageLikeRepresentation
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageType(str, Enum):
    """消息类型枚举 — 支持多模态"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    FILE = "file"


# ──────────────────────────────────────────────
# Request Schemas (API 输入)
# ──────────────────────────────────────────────
class ChatMessageRequest(BaseModel):
    """文本对话请求"""
    content: str = Field(..., min_length=1, max_length=10000, description="用户消息内容")
    conversation_id: Optional[UUID] = Field(None, description="会话ID, 为空则创建新会话")
    metadata: dict[str, Any] = Field(default_factory=dict, description="附加元数据")

    model_config = {"json_schema_extra": {"examples": [{"content": "你好，请介绍一下自己", "conversation_id": None}]}}


class AudioMessageRequest(BaseModel):
    """语音消息请求 (用于 REST 上传, WebSocket 另有协议)"""
    audio_base64: str = Field(..., description="Base64 编码的音频数据")
    format: str = Field("wav", description="音频格式: wav / mp3 / ogg / webm")
    sample_rate: int = Field(16000, description="采样率")
    conversation_id: Optional[UUID] = None


# ──────────────────────────────────────────────
# Response Schemas (API 输出)
# ──────────────────────────────────────────────
class MessageResponse(BaseModel):
    """消息响应"""
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    tokens_used: int = 0
    latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StreamChunkResponse(BaseModel):
    """SSE / WebSocket 流式响应的单个 chunk
    
    教程要点: 流式输出是企业级语音对话的核心要求
    - event 字段标识 chunk 类型, 前端据此分流处理
    - delta 为增量文本
    - audio_chunk 为增量音频 (TTS 实时合成)
    """
    event: str = Field(..., description="事件类型: token / audio / tool_call / end / error")
    delta: str = Field("", description="增量文本内容")
    audio_chunk: Optional[str] = Field(None, description="Base64 增量音频")
    tool_name: Optional[str] = Field(None, description="正在调用的工具名称")
    tool_input: Optional[dict] = Field(None, description="工具输入参数")
    metadata: dict[str, Any] = Field(default_factory=dict)


# ──────────────────────────────────────────────
# Internal Schemas (内部流转)
# ──────────────────────────────────────────────
class InternalMessage(BaseModel):
    """系统内部消息表示 — 用于 LangGraph State 流转"""
    id: UUID = Field(default_factory=uuid4)
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    audio_data: Optional[bytes] = Field(None, exclude=True, description="原始音频二进制, 不序列化")
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def to_langchain_message(self):
        """转换为 LangChain 消息对象 — LCEL 管道兼容"""
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        mapping = {
            MessageRole.USER: HumanMessage,
            MessageRole.ASSISTANT: AIMessage,
            MessageRole.SYSTEM: SystemMessage,
        }
        cls = mapping.get(self.role, HumanMessage)
        return cls(content=self.content, additional_kwargs=self.metadata)
