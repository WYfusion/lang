"""
长期记忆 — 跨会话持久化记忆
===============================

教程要点:
    1. 长期记忆存储用户事实、偏好、重要信息
    2. LLM 自动从对话中提取记忆
    3. 向量化存储, 支持语义检索
    4. 记忆更新策略: 新增 / 更新 / 遗忘
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ── 记忆提取提示词 ────────────────────────
MEMORY_EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """分析以下对话, 提取值得长期记住的用户信息。

请输出 JSON 格式:
{{
    "facts": ["用户的事实性信息..."],
    "preferences": ["用户的偏好..."],
    "importance": 0.7
}}

如果没有值得记忆的信息, 返回空列表。"""),
    ("placeholder", "{messages}"),
])


# ── 记忆摘要提示词 ────────────────────────
MEMORY_SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "请将以下对话历史压缩为简洁的摘要, 保留关键信息和结论。"),
    ("placeholder", "{messages}"),
])


class LongTermMemory:
    """
    长期记忆管理器

    教程要点:
        manager = LongTermMemory(llm, memory_repo, vectorstore)

        # 从对话中提取记忆
        new_memories = await manager.extract(messages)

        # 语义检索相关记忆
        relevant = await manager.recall(query, user_id)

        # 会话摘要压缩
        summary = await manager.summarize(messages)

    LCEL 链:
        extract_chain = MEMORY_EXTRACT_PROMPT | llm.with_structured_output(MemoryExtraction)
        summarize_chain = MEMORY_SUMMARIZE_PROMPT | llm | StrOutputParser()
    """

    def __init__(self, llm=None, memory_repo=None, vectorstore=None):
        self.llm = llm
        self.memory_repo = memory_repo
        self.vectorstore = vectorstore

    async def extract(self, messages: Sequence[Any], user_id: str = "") -> list[dict]:
        """
        从对话中提取记忆

        LCEL:
            chain = MEMORY_EXTRACT_PROMPT | llm.with_structured_output(MemoryExtraction)
            result = await chain.ainvoke({"messages": messages[-4:]})
        """
        # TODO: 实际实现
        return []

    async def recall(self, query: str, user_id: str, top_k: int = 5) -> list[dict]:
        """
        语义检索相关记忆

        步骤:
            1. 向量检索 (语义相似)
            2. DB 查询 (按类型/重要性过滤)
            3. 合并去重
            4. 更新 access_count (记忆强化)
        """
        # TODO: 实际实现
        return []

    async def summarize(self, messages: Sequence[Any]) -> str:
        """
        会话摘要压缩

        当消息数超过阈值时, 将旧消息压缩为摘要
        """
        # TODO: summarize_chain.ainvoke({"messages": messages})
        return ""
