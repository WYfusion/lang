"""
记忆更新节点 — 对话后记忆提取与持久化
========================================

教程要点:
    1. LLM 自动提取对话中的事实/偏好
    2. 重要性评分 (importance scoring)
    3. 异步写入 DB + 向量库
    4. 会话超长时触发摘要压缩
"""

from __future__ import annotations

from typing import Any

from graph.state import MainGraphState


async def update_memory(state: MainGraphState) -> dict[str, Any]:
    """
    记忆更新节点

    教程要点 — LCEL 记忆提取链:

        extract_chain = (
            memory_extract_prompt
            | llm.with_structured_output(MemoryExtraction)
        )

        class MemoryExtraction(BaseModel):
            facts: list[str]        # 提取到的事实
            preferences: list[str]  # 提取到的偏好
            importance: float       # 整体重要性

    企业级实践:
        - 异步写入, 不阻塞响应返回
        - 去重: 与已有记忆做语义相似度比较
        - 冲突解决: 新事实覆盖旧事实
        - 摘要压缩: 消息超过阈值时生成摘要
    """
    messages = state.get("messages", [])
    user_id = state.get("user_id", "")

    # TODO: 实际实现
    # 1. 提取新记忆
    # extract_chain = memory_extract_prompt | llm.with_structured_output(MemoryExtraction)
    # extraction = await extract_chain.ainvoke({"messages": messages[-4:]})

    # 2. 去重 & 持久化
    # async with get_async_session() as session:
    #     repo = MemoryRepository(session)
    #     for fact in extraction.facts:
    #         await repo.create(user_id=user_id, memory_type="fact", content=fact, ...)

    # 3. 检查是否需要摘要压缩
    # if len(messages) > settings.MEMORY_SUMMARIZE_THRESHOLD:
    #     summary = await summarize_chain.ainvoke({"messages": messages})
    #     ...

    return {}
