"""
LangGraph State 定义 — 图的数据流核心
=========================================

教程要点 (★ 核心概念):
    1. TypedDict 定义 State — LangGraph 的数据流血脉
    2. Annotated + operator.add 实现 Reducer (消息列表自动追加)
    3. State 字段设计决定了整个图的数据流向
    4. 区分「可变状态」与「只读配置」
    5. 嵌套 State 支持子图数据隔离

LangGraph 状态流转机制:
    - 每个节点接收完整 State, 返回 **部分更新** dict
    - 带 Reducer 的字段 (如 messages) 会自动合并而非替换
    - 无 Reducer 的字段为 **直接覆盖** 语义
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Optional, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# ──────────────────────────────────────────────
# 主图 State
# ──────────────────────────────────────────────
class GraphState:
    """
    主编排图的状态定义

    教程要点:
        - messages: 使用 add_messages Reducer, 每个节点返回新消息会自动追加
        - current_intent: 路由节点写入, 下游节点读取
        - retrieved_docs: RAG 节点写入, 对话节点读取
        - memory_context: 记忆节点写入, 注入系统提示
        - voice_state: 语音处理全链路状态
    """
    pass  # 使用 TypedDict 方式定义, 见下方


from typing import TypedDict


class VoiceState(TypedDict, total=False):
    """语音处理子状态"""
    raw_audio: bytes                     # 原始音频
    denoised_audio: bytes                # 降噪后音频
    stt_text: str                        # STT 识别文本
    stt_confidence: float                # 识别置信度
    tts_audio: bytes                     # TTS 合成音频
    tts_text: str                        # 待合成文本


class RAGState(TypedDict, total=False):
    """RAG 检索子状态"""
    query: str                           # 检索查询 (可能经过改写)
    retrieved_docs: list[dict[str, Any]]  # 检索到的文档块
    relevance_scores: list[float]         # 相关性分数
    context_text: str                    # 拼接后的上下文文本


class MemoryState(TypedDict, total=False):
    """记忆子状态"""
    short_term_messages: list[dict]       # 短期记忆消息
    long_term_facts: list[str]            # 长期事实记忆
    long_term_preferences: list[str]      # 长期偏好记忆
    summary: str                          # 会话摘要
    memory_prompt: str                    # 注入系统提示的记忆文本


class MainGraphState(TypedDict, total=False):
    """
    ★ 主图 State — LangGraph StateGraph 的类型参数

    设计原则:
        1. messages 使用 add_messages Reducer → 消息自动追加
        2. 其他字段为直接覆盖 → 每个节点只更新自己负责的字段
        3. 子状态 (voice / rag / memory) 嵌套 TypedDict, 保持扁平可读
    """
    # ── 核心消息流 (Reducer: 自动追加) ────────
    messages: Annotated[list[BaseMessage], add_messages]

    # ── 会话元信息 ────────────────────────────
    conversation_id: str
    user_id: str
    thread_id: str

    # ── 意图路由 ──────────────────────────────
    current_intent: str                   # chat / rag / voice / tool_call / multi_agent
    confidence: float                      # 路由置信度

    # ── 输入类型标记 ─────────────────────────
    input_type: str                        # text / audio

    # ── 子状态 ────────────────────────────────
    voice: VoiceState
    rag: RAGState
    memory: MemoryState

    # ── 多 Agent 协作 ────────────────────────
    active_agent: str                      # 当前激活的 Agent 名称
    agent_outputs: Annotated[list[dict[str, Any]], operator.add]  # Agent 输出累积

    # ── 工具调用 ──────────────────────────────
    tool_calls: list[dict[str, Any]]
    tool_results: Annotated[list[dict[str, Any]], operator.add]

    # ── 输出控制 ──────────────────────────────
    response_text: str                     # 最终文本响应
    response_audio: Optional[bytes]        # 最终音频响应
    should_continue: bool                  # 是否继续循环
    error: Optional[str]                   # 错误信息


# ──────────────────────────────────────────────
# 子图 States — 隔离子图的数据边界
# ──────────────────────────────────────────────
class RAGSubgraphState(TypedDict, total=False):
    """RAG 子图专用 State"""
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    rewritten_query: str
    retrieved_docs: list[dict[str, Any]]
    relevance_scores: list[float]
    grounded_response: str
    needs_retry: bool


class VoiceSubgraphState(TypedDict, total=False):
    """语音处理子图专用 State"""
    raw_audio: bytes
    sample_rate: int
    denoised_audio: bytes
    vad_segments: list[tuple[float, float]]  # (start_ms, end_ms)
    stt_text: str
    stt_confidence: float
    processed: bool


class MultiAgentState(TypedDict, total=False):
    """多 Agent 协作子图 State"""
    messages: Annotated[list[BaseMessage], add_messages]
    task_description: str
    supervisor_plan: str
    agent_assignments: list[dict[str, str]]  # [{agent, task}]
    agent_results: Annotated[list[dict[str, Any]], operator.add]
    final_synthesis: str
    iteration: int
    max_iterations: int
