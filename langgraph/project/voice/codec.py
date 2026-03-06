"""
音频编解码
===========
"""

from __future__ import annotations

import base64
from typing import Optional


class AudioCodec:
    """
    音频编解码器

    教程要点:
        - 支持 PCM ↔ WAV ↔ MP3 ↔ Opus 互转
        - Base64 编解码 (REST API 传输)
        - 流式编码 (WebSocket 传输)
    """

    @staticmethod
    def pcm_to_wav(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
        """PCM → WAV"""
        # TODO: import struct; 构造 WAV 头 + PCM 数据
        return pcm_data

    @staticmethod
    def wav_to_pcm(wav_data: bytes) -> bytes:
        """WAV → PCM"""
        # TODO: 跳过 44 字节 WAV 头
        return wav_data[44:] if len(wav_data) > 44 else wav_data

    @staticmethod
    def to_base64(audio_data: bytes) -> str:
        """二进制 → Base64"""
        return base64.b64encode(audio_data).decode("utf-8")

    @staticmethod
    def from_base64(b64_string: str) -> bytes:
        """Base64 → 二进制"""
        return base64.b64decode(b64_string)
