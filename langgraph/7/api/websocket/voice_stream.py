"""
WebSocket 语音流 — 实时语音对话端点
======================================

教程要点 (★★★ 流式语音对话核心):
    1. WebSocket 全双工: 同时接收音频 + 返回文字/音频
    2. 混合帧协议: JSON (控制帧) + Binary (音频帧)
    3. 语音对话全流程:
       客户端→音频帧 → 服务端→降噪→VAD→STT→LangGraph→TTS→客户端
    4. 打断机制: 用户说话时中断当前 TTS
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config.settings import get_settings
from schemas.voice import VoiceConfig, VoiceWebSocketMessage, VoiceEvent
from voice.stream_handler import VoiceStreamHandler

voice_ws_router = APIRouter()


@voice_ws_router.websocket("/voice")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket 语音对话端点

    协议说明:
        客户端 → 服务端:
            - JSON 帧: {"action": "start/stop/config/interrupt", "data": {...}}
            - Binary 帧: PCM 音频数据

        服务端 → 客户端:
            - JSON 帧: {"event": "stt_partial/stt_final/llm_token/tts_start/tts_end/error", "data": {...}}
            - Binary 帧: TTS 音频数据

    生命周期:
        1. WebSocket 握手
        2. 客户端发送 config JSON
        3. 循环: 接收音频 → 处理 → 返回结果
        4. 客户端发送 stop 或断开

    教程要点 — LangGraph 流式集成:
        async for event in graph.astream_events(state, config, version="v2"):
            if event["event"] == "on_chat_model_stream":
                token = event["data"]["chunk"].content
                await websocket.send_json({"event": "llm_token", "data": {"token": token}})
    """
    await websocket.accept()
    settings = get_settings()
    handler = VoiceStreamHandler(settings)

    try:
        # 等待客户端配置
        config_data = await websocket.receive_json()
        voice_config = VoiceConfig(**config_data.get("data", {}))
        await websocket.send_json({"event": "ready", "data": voice_config.model_dump()})

        # 主循环
        while True:
            message = await websocket.receive()

            if "text" in message:
                # JSON 控制帧
                ws_msg = VoiceWebSocketMessage(**json.loads(message["text"]))

                if ws_msg.action == "stop":
                    break
                elif ws_msg.action == "interrupt":
                    handler.interrupt()
                    await websocket.send_json({"event": "interrupted", "data": {}})
                elif ws_msg.action == "ping":
                    await websocket.send_json({"event": "pong", "data": {}})

            elif "bytes" in message:
                # Binary 音频帧
                audio_chunk = message["bytes"]
                handler.feed_audio(audio_chunk)

                # TODO: VAD 检测到语音结束时, 触发处理
                # 简化版: 收到一定量音频后处理
                # async for event in handler.process_utterance(audio_chunk):
                #     if "audio" in event.get("data", {}):
                #         # 音频数据用 Binary 帧发送
                #         audio_bytes = base64.b64decode(event["data"]["audio"])
                #         await websocket.send_bytes(audio_bytes)
                #     else:
                #         # 其他事件用 JSON 帧发送
                #         await websocket.send_json(event)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"event": "error", "data": {"message": str(e)}})
        except Exception:
            pass
    finally:
        handler.reset()
