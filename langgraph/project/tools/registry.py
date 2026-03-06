"""
工具注册表 — 动态工具管理
============================

教程要点:
    1. 工具注册表: 集中管理所有可用工具
    2. @tool 装饰器创建 LangChain Tool
    3. StructuredTool 支持 Pydantic 输入模型
    4. 工具可按 Agent / 场景过滤
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from langchain_core.tools import BaseTool


class ToolRegistry:
    """
    工具注册表 — 单例模式管理所有 Tool

    教程要点:
        registry = ToolRegistry()
        registry.register(search_tool)
        registry.register(noise_reduce_tool, tags=["voice"])

        # 按标签获取
        voice_tools = registry.get_by_tags(["voice"])

        # 传给 Agent
        agent = create_react_agent(llm, tools=registry.get_all())
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._tags: dict[str, list[str]] = {}  # tool_name → [tags]

    def register(self, tool: BaseTool, tags: Optional[list[str]] = None) -> None:
        """注册工具"""
        self._tools[tool.name] = tool
        self._tags[tool.name] = tags or []

    def get(self, name: str) -> Optional[BaseTool]:
        """按名称获取"""
        return self._tools.get(name)

    def get_all(self) -> list[BaseTool]:
        """获取所有工具"""
        return list(self._tools.values())

    def get_by_tags(self, tags: list[str]) -> list[BaseTool]:
        """按标签过滤"""
        result = []
        for name, tool in self._tools.items():
            if any(tag in self._tags.get(name, []) for tag in tags):
                result.append(tool)
        return result

    def list_names(self) -> list[str]:
        """列出所有工具名称"""
        return list(self._tools.keys())
