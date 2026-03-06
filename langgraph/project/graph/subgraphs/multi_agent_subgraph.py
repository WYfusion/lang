"""
多 Agent 协作子图 — Supervisor 模式
======================================

教程要点 (★★ 重要):
    1. Supervisor Agent 负责任务分解与分配
    2. Worker Agents 各司其职 (研究、写作、分析等)
    3. 迭代循环: Supervisor → Worker → Supervisor → ... → 最终综合
    4. 这是 LangGraph 多Agent协作的经典模式

    多Agent流程:
        ┌───────────┐
        │  START    │
        └────┬──────┘
             │
        ┌────▼────────┐
        │ Supervisor  │ ← 任务分解 & 分配
        └────┬────────┘
             │
        ┌────▼────────┐
        │  路由分发    │ ← 条件边选择 Agent
        ├─────────────┤
        │ Researcher  │
        │ Writer      │
        │ Analyst     │
        │ Voice Agent │
        └────┬────────┘
             │
        ┌────▼────────┐     (未完成)
        │ Supervisor  │ ──────────► 继续分配
        └────┬────────┘
             │ (完成)
        ┌────▼────────┐
        │ 最终综合    │
        └────┬────────┘
             │
        ┌────▼────────┐
        │   END       │
        └─────────────┘
"""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from config.settings import Settings
from graph.state import MultiAgentState


async def supervisor_node(state: MultiAgentState) -> dict[str, Any]:
    """
    Supervisor Agent 节点

    教程要点 — LCEL:
        supervisor_chain = (
            supervisor_prompt
            | llm.with_structured_output(SupervisorDecision)
        )

        class SupervisorDecision(BaseModel):
            next_agent: Literal["researcher", "writer", "analyst", "voice_agent", "FINISH"]
            task: str
            reasoning: str
    """
    iteration = state.get("iteration", 0) + 1
    max_iterations = state.get("max_iterations", 5)

    if iteration > max_iterations:
        return {"supervisor_plan": "FINISH", "iteration": iteration}

    # TODO: LLM 决策下一步
    # decision = await supervisor_chain.ainvoke(...)
    return {"supervisor_plan": "FINISH", "iteration": iteration}  # 占位


async def researcher_node(state: MultiAgentState) -> dict[str, Any]:
    """研究 Agent — 负责信息搜集与验证"""
    task = state.get("task_description", "")
    # TODO: researcher_chain.ainvoke(...)
    return {"agent_results": [{"agent": "researcher", "result": f"Research for: {task}"}]}


async def writer_node(state: MultiAgentState) -> dict[str, Any]:
    """写作 Agent — 负责内容生成与优化"""
    return {"agent_results": [{"agent": "writer", "result": "Written content placeholder"}]}


async def analyst_node(state: MultiAgentState) -> dict[str, Any]:
    """分析 Agent — 负责数据分析与推理"""
    return {"agent_results": [{"agent": "analyst", "result": "Analysis placeholder"}]}


async def voice_agent_node(state: MultiAgentState) -> dict[str, Any]:
    """语音 Agent — 负责语音相关任务"""
    return {"agent_results": [{"agent": "voice_agent", "result": "Voice task placeholder"}]}


async def synthesize_node(state: MultiAgentState) -> dict[str, Any]:
    """最终综合节点 — 汇总所有 Agent 结果"""
    results = state.get("agent_results", [])
    # TODO: LLM 综合所有结果
    synthesis = "\n".join(f"[{r['agent']}]: {r['result']}" for r in results)
    return {
        "final_synthesis": synthesis,
        "messages": [AIMessage(content=synthesis)],
    }


def route_to_agent(state: MultiAgentState) -> str:
    """条件边: Supervisor 决定路由到哪个 Agent"""
    plan = state.get("supervisor_plan", "FINISH")
    if plan == "FINISH":
        return "synthesize"
    return plan  # "researcher" / "writer" / "analyst" / "voice_agent"


def build_multi_agent_subgraph(settings: Settings) -> StateGraph:
    """
    构建多 Agent 协作子图

    教程要点:
        - Supervisor 模式是企业级多Agent最常用的架构
        - 也可用 Hierarchical / Consensus / Swarm 等模式
        - interrupt_before 可在关键决策点暂停等待人工审批
    """
    graph = StateGraph(MultiAgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("voice_agent", voice_agent_node)
    graph.add_node("synthesize", synthesize_node)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "researcher": "researcher",
            "writer": "writer",
            "analyst": "analyst",
            "voice_agent": "voice_agent",
            "synthesize": "synthesize",
        },
    )

    # 每个 Worker 完成后回到 Supervisor
    for agent in ["researcher", "writer", "analyst", "voice_agent"]:
        graph.add_edge(agent, "supervisor")

    graph.add_edge("synthesize", END)

    return graph.compile()
