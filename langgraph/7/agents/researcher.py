"""
Researcher Agent — 信息搜集专家
=================================
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from agents.base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    """
    研究 Agent — 负责搜索、检索、事实核查

    教程要点:
        - 配备搜索工具 (web search, RAG retriever)
        - ReAct 模式: Think → Search → Think → Answer
        - 可用 create_react_agent 快速构建
    """

    def __init__(self, **kwargs: Any):
        super().__init__(
            name="researcher",
            description="信息搜集与事实验证专家, 擅长搜索和检索相关资料",
            system_prompt="你是一个研究专家。请仔细搜索和验证信息, 确保准确性。",
            **kwargs,
        )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs: Any) -> dict[str, Any]:
        # TODO: create_react_agent(self.llm, self.tools)
        return {"messages": [AIMessage(content="[Research result placeholder]")]}

    async def astream(self, messages: list[BaseMessage], **kwargs: Any):
        result = await self.ainvoke(messages, **kwargs)
        yield result
