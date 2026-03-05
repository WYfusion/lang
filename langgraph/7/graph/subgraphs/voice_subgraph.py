"""
语音处理子图 — 音频全链路处理
================================

教程要点:
    1. 语音降噪 → VAD 切分 → STT 识别
    2. 每步可独立作为 Tool 被其他 Agent 调用
    3. 异步流水线, 低延迟设计
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from config.settings import Settings
from graph.state import VoiceSubgraphState


async def noise_reduce_node(state: VoiceSubgraphState) -> dict[str, Any]:
    """
    降噪节点

    教程要点:
        - noisereduce 库: 频谱减法降噪
        - 也可调用外部 API (如 NVIDIA Maxine)
        - 作为 Tool 时签名: noise_reduce(audio: bytes) -> bytes
    """
    raw_audio = state.get("raw_audio", b"")
    # TODO: 实际实现
    # import noisereduce as nr
    # import numpy as np
    # audio_np = np.frombuffer(raw_audio, dtype=np.int16)
    # denoised = nr.reduce_noise(y=audio_np, sr=sample_rate)
    # denoised_bytes = denoised.astype(np.int16).tobytes()

    return {"denoised_audio": raw_audio}  # 占位: 原样返回


async def vad_node(state: VoiceSubgraphState) -> dict[str, Any]:
    """
    VAD (Voice Activity Detection) 节点

    教程要点:
        - WebRTC VAD: 轻量级, 实时性好
        - 输出语音段时间戳列表
        - 用于切分静音段, 判断用户说完
    """
    audio = state.get("denoised_audio", b"")
    # TODO: 实际实现
    # import webrtcvad
    # vad = webrtcvad.Vad(aggressiveness)
    # segments = detect_speech_segments(audio, vad)

    segments: list[tuple[float, float]] = []  # 占位
    return {"vad_segments": segments}


async def stt_node(state: VoiceSubgraphState) -> dict[str, Any]:
    """
    STT (Speech-to-Text) 节点

    教程要点:
        - OpenAI Whisper: 本地推理, 支持多语言
        - 也可用 API: OpenAI Whisper API / 讯飞 / 阿里
        - 流式 STT: 分段识别, 逐步输出 partial results
    """
    audio = state.get("denoised_audio", b"")
    # TODO: 实际实现
    # import whisper
    # model = whisper.load_model(settings.STT_MODEL)
    # result = model.transcribe(audio_path)
    # text = result["text"]

    return {
        "stt_text": "",       # 占位
        "stt_confidence": 0.0,
        "processed": True,
    }


def build_voice_subgraph(settings: Settings) -> StateGraph:
    """构建语音处理子图"""
    graph = StateGraph(VoiceSubgraphState)

    graph.add_node("noise_reduce", noise_reduce_node)
    graph.add_node("vad", vad_node)
    graph.add_node("stt", stt_node)

    graph.add_edge(START, "noise_reduce")
    graph.add_edge("noise_reduce", "vad")
    graph.add_edge("vad", "stt")
    graph.add_edge("stt", END)

    return graph.compile()
