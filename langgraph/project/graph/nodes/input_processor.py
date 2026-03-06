"""
输入预处理节点 — 统一文本/语音输入
====================================

教程要点:
    1. 节点函数签名: async def node(state: State) -> dict
    2. 返回 dict 为 State 的部分更新
    3. 语音输入会先走降噪→VAD→STT管线
    4. 文本输入直接透传
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage

from graph.state import MainGraphState


async def process_input(state: MainGraphState) -> dict[str, Any]:
    """
    输入预处理节点

    流程:
        1. 检查 input_type
        2. 如果是 audio → 调用语音处理子图 (降噪→VAD→STT)
        3. 如果是 text → 直接从 messages 末尾取用户文本
        4. 返回统一的文本到 State

    教程要点:
        - 节点是 async 函数, LangGraph 原生支持异步
        - 返回的 dict 自动合并到 State
        - messages 字段使用 add_messages Reducer, 返回新消息会追加
    """
    input_type = state.get("input_type", "text")

    if input_type == "audio":
        # 语音输入: 调用语音处理管线
        voice_state = state.get("voice", {})
        raw_audio = voice_state.get("raw_audio", b"")

        if raw_audio:
            # TODO: 实际实现中调用 voice 模块
            # from voice.audio_processor import AudioProcessingPipeline
            # pipeline = AudioProcessingPipeline()
            # stt_result = await pipeline.process(raw_audio)
            stt_text = voice_state.get("stt_text", "")

            return {
                "voice": {
                    **voice_state,
                    "stt_text": stt_text,
                },
                "messages": [HumanMessage(content=stt_text)],
            }

    # 文本输入: messages 已经包含用户消息, 无需额外处理
    return {}
