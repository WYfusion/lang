"""
Supervisor Agent — 多 Agent 协作的调度者
==========================================

教程要点:
    1. Supervisor 负责: 任务理解 → 分解 → 分配 → 监督 → 综合
    2. 使用 structured output 输出分配决策
    3. 是 Multi-Agent 架构的核心控制器
"""

from __future__ import annotations

from typing import Any, Literal, Sequence

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from agents.base_agent import BaseAgent


SUPERVISOR_PROMPT = """你是一个任务调度器 (Supervisor)。你负责管理一组专家Agent来完成用户任务。

可用的 Agent:
{agent_descriptions}

你的职责:
1. 分析用户任务
2. 决定下一步应该交给哪个 Agent
3. 当所有子任务完成后, 输出 FINISH

请以 JSON 格式输出你的决策。"""


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent

    教程要点:
        supervisor_chain = (
            supervisor_prompt
            | llm.with_structured_output(SupervisorDecision)
        )

        用法:
            supervisor = SupervisorAgent(
                worker_agents=[researcher, writer, analyst],
                llm=llm,
            )
    """

    def __init__(
        self,
        worker_agents: Sequence[BaseAgent],
        **kwargs: Any,
    ):
        self.worker_agents = list(worker_agents)
        agent_descriptions = "\n".join(
            f"- **{a.name}**: {a.description}" for a in worker_agents
        )
        super().__init__(
            name="supervisor",
            description="任务调度与分配",
            system_prompt=SUPERVISOR_PROMPT.format(agent_descriptions=agent_descriptions),
            **kwargs,
        )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs: Any) -> dict[str, Any]:
        """执行 Supervisor 决策"""
        # TODO: 实际 LLM 调用
        # chain = supervisor_prompt | self.llm.with_structured_output(SupervisorDecision)
        # decision = await chain.ainvoke({"messages": messages, "agent_descriptions": ...})
        return {"next_agent": "FINISH", "task": "", "reasoning": "All tasks complete"}

    async def astream(self, messages: list[BaseMessage], **kwargs: Any):
        """流式执行"""
        result = await self.ainvoke(messages, **kwargs)
        yield result
