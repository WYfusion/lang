"""
Writer Agent — 内容生成专家
==============================
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):
    """
    写作 Agent — 负责内容创作、优化、摘要

    教程要点:
        - 可配备编辑工具 (grammar check, style transfer)
        - 支持多轮修改: 初稿 → 审阅 → 修改
    """

    def __init__(self, **kwargs: Any):
        super().__init__(
            name="writer",
            description="内容生成与优化专家, 擅长写作、摘要、翻译",
            system_prompt="你是一个专业写作者。请生成高质量、结构清晰的内容。",
            **kwargs,
        )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs: Any) -> dict[str, Any]:
        return {"messages": [AIMessage(content="[Written content placeholder]")]}

    async def astream(self, messages: list[BaseMessage], **kwargs: Any):
        result = await self.ainvoke(messages, **kwargs)
        yield result
