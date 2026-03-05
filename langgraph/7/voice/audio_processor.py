"""
音频处理管线 — 降噪 + VAD + 音频转换
=======================================

教程要点:
    1. 音频处理管线设计: Pipeline 模式
    2. 各步骤可独立测试, 也可组合使用
    3. 异步处理, 适合流式场景
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config.settings import Settings, get_settings


@dataclass
class AudioSegment:
    """音频片段"""
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    start_ms: float = 0.0
    end_ms: float = 0.0


class AudioProcessingPipeline:
    """
    音频处理管线

    教程要点:
        pipeline = AudioProcessingPipeline(settings)
        result = await pipeline.process(raw_audio)
        # result.denoised_audio, result.vad_segments, result.stt_text

    管线步骤:
        1. 格式转换 (PCM 16bit, 16kHz, mono)
        2. 降噪 (noisereduce / RNNoise)
        3. VAD 检测 (WebRTC VAD)
        4. 语音段切分
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    async def process(self, raw_audio: bytes) -> dict:
        """
        完整管线处理

        Returns:
            {"denoised_audio": bytes, "vad_segments": list, "duration_ms": float}
        """
        # Step 1: 格式归一化
        normalized = await self._normalize(raw_audio)

        # Step 2: 降噪
        denoised = await self._denoise(normalized)

        # Step 3: VAD
        segments = await self._vad(denoised)

        return {
            "denoised_audio": denoised,
            "vad_segments": segments,
            "duration_ms": len(raw_audio) / (self.settings.VOICE_SAMPLE_RATE * 2) * 1000,
        }

    async def _normalize(self, audio: bytes) -> bytes:
        """格式归一化"""
        # TODO: 使用 soundfile / scipy 做采样率转换
        return audio

    async def _denoise(self, audio: bytes) -> bytes:
        """降噪"""
        if not self.settings.VOICE_NOISE_REDUCE:
            return audio
        # TODO: noisereduce 实现
        return audio

    async def _vad(self, audio: bytes) -> list[tuple[float, float]]:
        """VAD 检测"""
        # TODO: webrtcvad 实现
        return []
