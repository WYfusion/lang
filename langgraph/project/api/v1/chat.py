"""
对话 API — REST + SSE 流式
============================

教程要点 (★★★ 流式输出核心):
    1. POST /chat — 同步响应
    2. POST /chat/stream — SSE (Server-Sent Events) 流式响应
    3. 使用 LangGraph 的 astream_events() 实现 token 级流式
    4. StreamingResponse 返回 SSE 格式
"""

from __future__ import annotations

import json
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.deps import get_compiled_graph, get_current_user_id, get_conversation_repo
from schemas.message import ChatMessageRequest, MessageResponse, StreamChunkResponse

router = APIRouter()


@router.post("/", response_model=MessageResponse)
async def chat(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    graph=Depends(get_compiled_graph),
    conv_repo=Depends(get_conversation_repo),
):
    """
    同步对话接口

    教程要点 — LangGraph ainvoke:
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=request.content)]},
            config={"configurable": {"thread_id": thread_id}},
        )
    """
    from langchain_core.messages import HumanMessage

    thread_id = str(request.conversation_id or uuid4())

    # 执行 LangGraph 图
    config = {"configurable": {"thread_id": thread_id}}
    state = {
        "messages": [HumanMessage(content=request.content)],
        "user_id": user_id,
        "conversation_id": str(request.conversation_id or ""),
        "thread_id": thread_id,
        "input_type": "text",
    }

    # TODO: result = await graph.ainvoke(state, config)
    result = {"response_text": "[Response placeholder]", "messages": []}

    return MessageResponse(
        conversation_id=request.conversation_id or uuid4(),
        role="assistant",
        content=result.get("response_text", ""),
    )


@router.post("/stream")
async def chat_stream(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    graph=Depends(get_compiled_graph),
):
    """
    SSE 流式对话接口

    教程要点 (★★★ LangGraph 流式输出):
        async for event in graph.astream_events(state, config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                # LLM token 级流式
                token = event["data"]["chunk"].content
                yield f"data: {json.dumps({'event': 'token', 'delta': token})}\\n\\n"

            elif kind == "on_tool_start":
                # 工具调用开始
                tool_name = event["name"]
                yield f"data: {json.dumps({'event': 'tool_call', 'tool_name': tool_name})}\\n\\n"

    SSE 格式:
        data: {"event": "token", "delta": "你"}
        data: {"event": "token", "delta": "好"}
        data: {"event": "end", "delta": ""}
    """
    from langchain_core.messages import HumanMessage

    thread_id = str(request.conversation_id or uuid4())

    async def event_generator() -> AsyncGenerator[str, None]:
        config = {"configurable": {"thread_id": thread_id}}
        state = {
            "messages": [HumanMessage(content=request.content)],
            "user_id": user_id,
            "thread_id": thread_id,
            "input_type": "text",
        }

        # TODO: 实际使用 astream_events
        # async for event in graph.astream_events(state, config, version="v2"):
        #     kind = event["event"]
        #     if kind == "on_chat_model_stream":
        #         chunk = event["data"]["chunk"]
        #         if chunk.content:
        #             sse_data = StreamChunkResponse(event="token", delta=chunk.content)
        #             yield f"data: {sse_data.model_dump_json()}\n\n"
        #
        #     elif kind == "on_tool_start":
        #         sse_data = StreamChunkResponse(event="tool_call", tool_name=event["name"])
        #         yield f"data: {sse_data.model_dump_json()}\n\n"

        # 框架占位: 模拟流式输出
        for char in "[Streaming response placeholder]":
            sse_data = StreamChunkResponse(event="token", delta=char)
            yield f"data: {sse_data.model_dump_json()}\n\n"

        # 结束信号
        yield f"data: {StreamChunkResponse(event='end').model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 禁止缓冲
        },
    )
