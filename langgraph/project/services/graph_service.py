"""
Graph 执行服务 — LangGraph 调用封装
======================================

教程要点:
    1. 封装 LangGraph 的 ainvoke / astream_events
    2. 统一异常处理 & 日志
    3. 超时控制
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Optional

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from config.settings import Settings, get_settings
from utils.logging import get_logger

logger = get_logger(__name__)


class GraphService:
    """
    LangGraph 执行服务

    教程要点:
        service = GraphService(compiled_graph)

        # 同步执行
        result = await service.invoke("你好", thread_id="xxx")

        # 流式执行
        async for chunk in service.stream("你好", thread_id="xxx"):
            print(chunk)  # {"event": "token", "delta": "..."}
    """

    def __init__(self, compiled_graph, settings: Optional[Settings] = None):
        self.graph = compiled_graph
        self.settings = settings or get_settings()

    async def invoke(
        self,
        message: str,
        thread_id: str,
        user_id: str = "",
        input_type: str = "text",
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        """
        同步执行 LangGraph 图

        教程要点:
            config = {"configurable": {"thread_id": thread_id}}
            result = await graph.ainvoke(state, config)
        """
        config = RunnableConfig(configurable={"thread_id": thread_id})
        state = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "thread_id": thread_id,
            "input_type": input_type,
        }

        try:
            result = await asyncio.wait_for(
                self.graph.ainvoke(state, config),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            logger.error("graph_timeout", thread_id=thread_id, timeout=timeout)
            return {"error": "Request timeout", "response_text": "抱歉，处理超时，请重试。"}
        except Exception as e:
            logger.error("graph_error", thread_id=thread_id, error=str(e))
            return {"error": str(e), "response_text": "抱歉，处理出错，请重试。"}

    async def stream(
        self,
        message: str,
        thread_id: str,
        user_id: str = "",
        input_type: str = "text",
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        流式执行 LangGraph 图

        教程要点 (★★★ 核心流式模式):

        astream_events 返回的事件类型:
            - on_chat_model_start: LLM 开始
            - on_chat_model_stream: LLM token (最常用)
            - on_chat_model_end: LLM 结束
            - on_tool_start: 工具开始
            - on_tool_end: 工具结束
            - on_chain_start/end: 链开始/结束
            - on_retriever_start/end: 检索器开始/结束

        使用 version="v2" 获取最新事件格式
        """
        config = RunnableConfig(configurable={"thread_id": thread_id})
        state = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "thread_id": thread_id,
            "input_type": input_type,
        }

        try:
            async for event in self.graph.astream_events(state, config, version="v2"):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        yield {"event": "token", "delta": chunk.content}

                elif kind == "on_tool_start":
                    yield {
                        "event": "tool_call",
                        "tool_name": event.get("name", ""),
                        "tool_input": event.get("data", {}).get("input", {}),
                    }

                elif kind == "on_tool_end":
                    yield {
                        "event": "tool_result",
                        "tool_name": event.get("name", ""),
                        "result": str(event.get("data", {}).get("output", "")),
                    }

            yield {"event": "end", "delta": ""}

        except Exception as e:
            logger.error("graph_stream_error", thread_id=thread_id, error=str(e))
            yield {"event": "error", "delta": str(e)}
