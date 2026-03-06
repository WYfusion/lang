"""
WebSocket 流式语音处理器
=========================

教程要点 (★★★ 流式语音核心):
    1. WebSocket 双向流: 客户端发送音频 → 服务端返回文字/音频
    2. 音频处理管线: 降噪 → VAD → STT → LLM → TTS
    3. 低延迟设计: 分段处理, 流式输出
    4. 打断机制: 用户说话时中断 TTS 播放
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Optional

from config.settings import Settings, get_settings


class VoiceStreamHandler:
    """
    语音流处理器 — 管理单个 WebSocket 语音会话

    教程要点:
        handler = VoiceStreamHandler(settings)
        
        # WebSocket 循环中使用:
        async for audio_chunk in websocket:
            handler.feed_audio(audio_chunk)
        
        async for event in handler.process():
            await websocket.send_json(event)

    流式处理模式:
        1. 累积音频 buffer
        2. VAD 检测到语音结束
        3. 触发 STT + LLM 推理
        4. TTS 流式合成, 逐块返回
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._audio_buffer = bytearray()
        self._is_speaking = False       # 用户是否正在说话
        self._is_processing = False     # 是否正在处理
        self._cancel_tts = False        # TTS 打断标志

    def feed_audio(self, chunk: bytes) -> None:
        """接收音频块"""
        self._audio_buffer.extend(chunk)

    async def process_utterance(self, audio: bytes) -> AsyncGenerator[dict[str, Any], None]:
        """
        处理一段完整语音

        教程要点 — 全链路管线:
            1. 降噪
            2. STT
            3. 投入 LangGraph 主图
            4. TTS 流式合成

        Yields:
            事件字典: {"event": "stt_final", "data": {"text": "..."}}
        """
        self._is_processing = True

        try:
            # Step 1: 降噪
            # denoised = await self._noise_reduce(audio)
            yield {"event": "processing_start", "data": {}}

            # Step 2: STT
            # stt_result = await self._stt(denoised)
            stt_text = "[STT result placeholder]"
            yield {"event": "stt_final", "data": {"text": stt_text}}

            # Step 3: LangGraph 推理 (使用 astream_events 实现 token 级流式)
            # async for event in graph.astream_events(state, config):
            #     if event["event"] == "on_chat_model_stream":
            #         token = event["data"]["chunk"].content
            #         yield {"event": "llm_token", "data": {"token": token}}

            # Step 4: TTS 流式合成
            # async for audio_chunk in tts_stream(response_text):
            #     if self._cancel_tts:
            #         break
            #     yield {"event": "tts_chunk", "data": {"audio": base64.b64encode(audio_chunk).decode()}}

            yield {"event": "processing_end", "data": {}}

        finally:
            self._is_processing = False

    def interrupt(self) -> None:
        """打断当前 TTS 播放"""
        self._cancel_tts = True

    def reset(self) -> None:
        """重置状态"""
        self._audio_buffer.clear()
        self._is_speaking = False
        self._is_processing = False
        self._cancel_tts = False
