"""
Voice Agent — 语音任务专家
=============================
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from agents.base_agent import BaseAgent


class VoiceAgent(BaseAgent):
    """
    语音 Agent — 负责语音相关子任务

    教程要点:
        - 配备语音工具: STT, TTS, 降噪, VAD
        - 这些工具嵌入为 LangChain Tool, Agent 可灵活调用
        - 支持流式语音处理
    """

    def __init__(self, **kwargs: Any):
        super().__init__(
            name="voice_agent",
            description="语音处理专家, 擅长语音识别、合成、降噪等音频任务",
            system_prompt=(
                "你是一个语音处理专家。你可以使用以下工具处理音频任务:\n"
                "- noise_reduce: 语音降噪\n"
                "- stt: 语音转文字\n"
                "- tts: 文字转语音\n"
                "- vad: 语音活动检测\n"
            ),
            **kwargs,
        )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs: Any) -> dict[str, Any]:
        # TODO: 使用 voice tools 执行任务
        return {"messages": [AIMessage(content="[Voice processing result]")]}

    async def astream(self, messages: list[BaseMessage], **kwargs: Any):
        result = await self.ainvoke(messages, **kwargs)
        yield result
