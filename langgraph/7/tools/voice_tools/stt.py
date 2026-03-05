"""
STT 工具 — 语音转文字 (作为 LangChain Tool)
===============================================

教程要点:
    1. StructuredTool 支持复杂输入参数
    2. 语音工具嵌入为 Tool, 可被任何 Agent 调用
    3. 支持多种后端: Whisper / API
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


class STTInput(BaseModel):
    """STT 工具输入"""
    audio_base64: str = Field(description="Base64 编码的音频数据")
    language: str = Field("zh", description="目标语言: zh / en / auto")
    model: str = Field("base", description="Whisper 模型: tiny / base / small / medium / large")


async def _speech_to_text(audio_base64: str, language: str = "zh", model: str = "base") -> str:
    """STT 核心逻辑"""
    # TODO: 实际实现
    # import whisper
    # import base64
    # audio_bytes = base64.b64decode(audio_base64)
    # ... save to temp file, transcribe ...
    return "[STT result placeholder]"


speech_to_text = StructuredTool.from_function(
    coroutine=_speech_to_text,
    name="speech_to_text",
    description="将音频转换为文字。输入 Base64 编码的音频, 输出识别文本。",
    args_schema=STTInput,
)
