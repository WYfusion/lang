"""
Agent 基类 — 统一 Agent 接口与生命周期
==========================================

教程要点:
    1. Agent 基类定义统一接口: ainvoke / astream
    2. 每个 Agent 封装: system_prompt + tools + llm
    3. 使用 create_react_agent (LangGraph prebuilt) 或自定义图
    4. LCEL 风格: agent 本身是 Runnable
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool


class BaseAgent(ABC):
    """
    Agent 基类

    教程要点:
        所有 Agent 继承此类, 统一:
        - name: Agent 名称 (用于日志 & 路由)
        - description: Agent 描述 (用于 Supervisor 选择)
        - system_prompt: 系统提示
        - tools: 可用工具列表
        - llm: 语言模型

    创建 Agent 的两种方式:
        1. create_react_agent (LangGraph 预构建):
            from langgraph.prebuilt import create_react_agent
            agent = create_react_agent(llm, tools, state_modifier=system_prompt)

        2. 自定义 StateGraph (更灵活):
            graph = StateGraph(AgentState)
            graph.add_node("think", think_node)
            graph.add_node("act", act_node)
            ...
    """

    def __init__(
        self,
        name: str,
        description: str,
        llm: Optional[BaseChatModel] = None,
        tools: Optional[Sequence[BaseTool]] = None,
        system_prompt: str = "",
    ):
        self.name = name
        self.description = description
        self.llm = llm
        self.tools = list(tools or [])
        self.system_prompt = system_prompt

    @abstractmethod
    async def ainvoke(self, messages: list[BaseMessage], **kwargs: Any) -> dict[str, Any]:
        """异步执行 Agent"""
        ...

    @abstractmethod
    async def astream(self, messages: list[BaseMessage], **kwargs: Any):
        """异步流式执行 Agent — 生成器"""
        ...

    def get_system_message(self) -> SystemMessage:
        """获取系统消息"""
        return SystemMessage(content=self.system_prompt)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
