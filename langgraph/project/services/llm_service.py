"""
LLM 服务 — 统一模型管理
=========================

教程要点:
    1. 工厂函数: 按配置创建不同 Provider 的 LLM
    2. LCEL 兼容: 返回的 LLM 是 Runnable
    3. 企业级: with_retry + with_fallbacks
"""

from __future__ import annotations

from typing import Optional

from langchain_core.language_models import BaseChatModel

from config.settings import Settings, get_settings


def get_chat_model(
    settings: Optional[Settings] = None,
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.7,
    streaming: bool = True,
) -> BaseChatModel:
    """
    获取 Chat 模型

    教程要点 — 多 Provider 支持:
        # OpenAI 兼容 (ChatGPT / DashScope / 智谱 / DeepSeek)
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            streaming=streaming,
        )

        # 企业级: 重试 + 降级
        robust_llm = (
            llm
            .with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
            .with_fallbacks([fallback_llm])
        )

    Args:
        provider: "openai" / "dashscope" / "zhipu" / "deepseek"
        model: 模型名称, None 时使用默认
        temperature: 温度
        streaming: 是否启用流式

    Returns:
        BaseChatModel — LCEL 兼容的 Runnable
    """
    if settings is None:
        settings = get_settings()

    from langchain_openai import ChatOpenAI

    provider_config = {
        "openai": {
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_BASE_URL,
            "default_model": settings.DEFAULT_CHAT_MODEL,
        },
        "dashscope": {
            "api_key": settings.DASHSCOPE_API_KEY,
            "base_url": settings.DASHSCOPE_BASE_URL,
            "default_model": "qwen-plus",
        },
        "zhipu": {
            "api_key": settings.ZHIPU_API_KEY,
            "base_url": settings.ZHIPU_BASE_URL,
            "default_model": "glm-4-flash",
        },
        "deepseek": {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "default_model": "deepseek-chat",
        },
    }

    config = provider_config.get(provider, provider_config["openai"])

    llm = ChatOpenAI(
        model=model or config["default_model"],
        api_key=config["api_key"],
        base_url=config["base_url"],
        temperature=temperature,
        streaming=streaming,
    )

    return llm
