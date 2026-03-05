"""
语音 Schema — 语音流式协议
============================

教程要点:
    1. WebSocket 语音流协议设计 — 二进制帧 + JSON 控制帧
    2. 语音状态机: idle → listening → processing → speaking
    3. VAD (Voice Activity Detection) 事件驱动
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class VoiceSessionState(str, Enum):
    """语音会话状态机"""
    IDLE = "idle"               # 空闲
    LISTENING = "listening"     # 正在接收语音
    PROCESSING = "processing"   # 正在处理 (STT → LLM → TTS)
    SPEAKING = "speaking"       # 正在播放 TTS
    ERROR = "error"


class VoiceConfig(BaseModel):
    """语音会话配置 (WebSocket 握手时传入)"""
    sample_rate: int = Field(16000, description="音频采样率")
    channels: int = Field(1, description="声道数")
    encoding: str = Field("pcm_s16le", description="编码格式: pcm_s16le / opus / mp3")
    vad_enabled: bool = Field(True, description="是否启用 VAD")
    noise_reduce: bool = Field(True, description="是否启用降噪")
    tts_enabled: bool = Field(True, description="是否返回 TTS 音频")
    tts_voice: str = Field("zh-CN-XiaoxiaoNeural", description="TTS 声色")
    interrupt_enabled: bool = Field(True, description="是否允许用户打断")


class VoiceWebSocketMessage(BaseModel):
    """WebSocket JSON 控制帧协议

    教程要点: 流式语音使用混合帧协议
    - JSON 帧 (type=text): 控制信令
    - Binary 帧 (type=bytes): 音频 PCM 数据
    """
    action: str = Field(..., description="动作: start / stop / config / interrupt / ping")
    data: dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None


class VoiceEvent(BaseModel):
    """语音事件 (服务端推送给客户端)"""
    event: str = Field(..., description="事件: vad_start / vad_end / stt_partial / stt_final / "
                                         "tts_start / tts_chunk / tts_end / llm_token / error")
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp_ms: int = 0


class STTResult(BaseModel):
    """STT 识别结果"""
    text: str
    language: str = "zh"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    duration_ms: int = 0
    is_final: bool = True


class TTSRequest(BaseModel):
    """TTS 合成请求"""
    text: str = Field(..., min_length=1)
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"
    volume: str = "+0%"
