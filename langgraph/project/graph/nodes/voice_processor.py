"""
语音处理节点 — TTS 合成
=========================

教程要点:
    1. 仅在 input_type == "audio" 时执行
    2. 使用 edge-tts 异步合成
    3. 流式 TTS: 边合成边推送音频块
"""

from __future__ import annotations

from typing import Any

from graph.state import MainGraphState


async def tts_node(state: MainGraphState) -> dict[str, Any]:
    """
    TTS 合成节点

    教程要点:
        - edge-tts 支持流式合成, 适合实时语音对话
        - 音频块通过 WebSocket 逐步推送, 减少首包延迟
        - 可嵌入为 LangGraph Tool, 也可作为独立节点

    流式 TTS 模式:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]  # 通过 WebSocket 推送
    """
    response_text = state.get("response_text", "")

    if not response_text:
        return {}

    # TODO: 实际实现
    # from voice.stream_handler import synthesize_tts_stream
    # audio_data = await synthesize_tts_stream(response_text, voice=settings.TTS_VOICE)

    # 框架占位
    tts_audio = b""  # 实际为合成的音频字节

    return {
        "voice": {
            **state.get("voice", {}),
            "tts_audio": tts_audio,
            "tts_text": response_text,
        },
        "response_audio": tts_audio,
    }
