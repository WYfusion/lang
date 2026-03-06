"""
LangChain 回调处理器 — 监控与日志
====================================

教程要点:
    1. Callback Handler 拦截 LLM / Tool / Chain 事件
    2. 用于: 日志、监控、Token 统计、流式输出
    3. 通过 RunnableConfig.callbacks 传入
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from utils.logging import get_logger

logger = get_logger("callbacks")


class LoggingCallbackHandler(AsyncCallbackHandler):
    """日志回调 — 记录 LLM / Tool / Chain 事件"""

    async def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs) -> None:
        logger.info("llm_start", model=serialized.get("name", ""))

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        # Token 统计
        token_usage = {}
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
        logger.info("llm_end", token_usage=token_usage)

    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        logger.error("llm_error", error=str(error))

    async def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        logger.info("tool_start", tool=serialized.get("name", ""), input=input_str[:100])

    async def on_tool_end(self, output: str, **kwargs) -> None:
        logger.info("tool_end", output=output[:100])

    async def on_tool_error(self, error: Exception, **kwargs) -> None:
        logger.error("tool_error", error=str(error))


class TokenCounterCallback(AsyncCallbackHandler):
    """Token 计数回调"""

    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)

    def get_usage(self) -> dict[str, int]:
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }
