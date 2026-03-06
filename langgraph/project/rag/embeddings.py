"""
Embedding 管理
================
"""

from __future__ import annotations

from typing import Optional

from config.settings import Settings, get_settings


class EmbeddingManager:
    """
    Embedding 模型管理器

    教程要点:
        from langchain_openai import OpenAIEmbeddings

        # OpenAI 兼容 API (DashScope / 智谱等)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-v3",
            openai_api_key=settings.DASHSCOPE_API_KEY,
            openai_api_base=settings.DASHSCOPE_BASE_URL,
        )

        # 本地 Embedding
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._embeddings = None

    def get_embeddings(self):
        """获取 Embedding 模型实例"""
        if self._embeddings is None:
            # TODO: 实际初始化
            pass
        return self._embeddings
