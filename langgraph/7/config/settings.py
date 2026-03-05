"""
集中配置管理 — 基于 pydantic-settings
=========================================

教程要点:
    1. 使用 pydantic-settings 的 BaseSettings 做类型安全的环境变量注入
    2. 通过 @lru_cache 实现配置单例，避免重复解析
    3. 多环境配置 (dev / staging / prod) 通过 ENV 字段切换
    4. 所有 API Key / URL 集中管理，绝不硬编码
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ──────────────────────────────────────────────
# 向上查找项目根目录的 .env（兼容从子目录启动）
# ──────────────────────────────────────────────
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class Settings(BaseSettings):
    """全局配置 — 所有字段均可通过环境变量或 .env 覆盖"""

    model_config = SettingsConfigDict(
        env_file=os.path.join(_PROJECT_ROOT, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",          # 忽略 .env 中不在 schema 内的字段
        case_sensitive=False,
    )

    # ── 应用 ─────────────────────────────────
    APP_VERSION: str = "0.1.0"
    ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]

    # ── LLM Provider — OpenAI 兼容 ──────────
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_CHAT_MODEL: str = "gpt-4o-mini"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── LLM Provider — 阿里 DashScope ──────
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # ── LLM Provider — DeepSeek ─────────────
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # ── LLM Provider — 智谱 ────────────────
    ZHIPU_API_KEY: str = ""
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"

    # ── 数据库 ──────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"   # 开发环境
    # 生产环境示例: "postgresql+asyncpg://user:pass@host:5432/dbname"

    # ── 向量数据库 ──────────────────────────
    VECTOR_STORE_TYPE: Literal["chroma", "faiss"] = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    FAISS_INDEX_PATH: str = "./data/faiss_index"

    # ── RAG 参数 ─────────────────────────────
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.7

    # ── 语音参数 ─────────────────────────────
    VOICE_SAMPLE_RATE: int = 16000
    VOICE_CHANNELS: int = 1
    VOICE_VAD_MODE: int = 3               # WebRTC VAD aggressiveness (0-3)
    VOICE_NOISE_REDUCE: bool = True
    TTS_VOICE: str = "zh-CN-XiaoxiaoNeural"  # edge-tts 声色
    STT_MODEL: str = "base"               # whisper 模型尺寸

    # ── 记忆管理 ─────────────────────────────
    SHORT_TERM_MEMORY_K: int = 20         # 短期记忆保留的消息轮数
    LONG_TERM_MEMORY_ENABLED: bool = True
    MEMORY_SUMMARIZE_THRESHOLD: int = 30  # 超过此轮数触发摘要压缩


@lru_cache()
def get_settings() -> Settings:
    """获取全局配置单例"""
    return Settings()
