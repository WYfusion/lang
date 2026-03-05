"""
VAD 工具 — 语音活动检测
=========================
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


class VADInput(BaseModel):
    """VAD 工具输入"""
    audio_base64: str = Field(description="Base64 编码的音频")
    sample_rate: int = Field(16000, description="采样率")
    aggressiveness: int = Field(3, ge=0, le=3, description="检测灵敏度: 0=宽松, 3=严格")


async def _detect_voice_activity(
    audio_base64: str, sample_rate: int = 16000, aggressiveness: int = 3
) -> str:
    """
    VAD 检测

    教程要点:
        - WebRTC VAD: Google 开源, 轻量高效
        - 输出语音段时间戳列表
        - 用于: 判断用户说完 / 切分静音段 / 滤除纯噪声
    """
    # TODO: 实际实现
    # import webrtcvad, base64
    # vad = webrtcvad.Vad(aggressiveness)
    # audio_bytes = base64.b64decode(audio_base64)
    # frames = frame_generator(30, audio_bytes, sample_rate)  # 30ms 帧
    # segments = vad_collector(sample_rate, 30, 300, vad, frames)
    return "[VAD segments: [(0, 1500), (2000, 3500)]]"


detect_voice_activity = StructuredTool.from_function(
    coroutine=_detect_voice_activity,
    name="voice_activity_detection",
    description="检测音频中的语音活动段。输入音频, 输出语音段时间戳列表。",
    args_schema=VADInput,
)
