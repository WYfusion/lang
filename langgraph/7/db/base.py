"""
数据库引擎与 Base — SQLAlchemy 2.0 异步模式
=============================================

教程要点:
    1. SQLAlchemy 2.0 异步引擎 (create_async_engine)
    2. 声明式 Base + mapped_column 新语法
    3. 异步 Session 工厂用于依赖注入
    4. 引擎生命周期跟随应用 (lifespan)
"""

from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy import MetaData, String, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ──────────────────────────────────────────────
# 命名约定 — 生产标准, 让 Alembic 自动生成规范命名
# ──────────────────────────────────────────────
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(AsyncAttrs, DeclarativeBase):
    """ORM 基类 — 所有模型继承此类"""
    metadata = metadata


class TimestampMixin:
    """时间戳 Mixin — 自动管理 created_at / updated_at"""
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())


class UUIDPrimaryKeyMixin:
    """UUID 主键 Mixin"""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))


# ──────────────────────────────────────────────
# 全局引擎 & Session 工厂
# ──────────────────────────────────────────────
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def import_all_db_models() -> list[str]:
    """
    导入全部 ORM 模型。

    兼容两种运行方式:
    1) 在 `db` 目录执行 Alembic (`from base import Base`)
    2) 作为包导入 (`from db.base import Base`)
    """
    try:
        from import_models import import_all_model_modules
    except ImportError:
        from db.import_models import import_all_model_modules

    return import_all_model_modules()


async def init_db() -> None:
    """初始化数据库引擎 & 创建表 (仅开发环境使用 create_all, 生产用 Alembic)"""
    global _engine, _session_factory
    from config.settings import get_settings

    settings = get_settings()

    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,           # 连接健康检查
        # PostgreSQL 生产环境配置:
        # pool_size=20,
        # max_overflow=10,
        # pool_recycle=3600,
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    if settings.ENV == "dev":
        import_all_db_models()
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """优雅关闭引擎"""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """异步 Session 依赖 — 用于 FastAPI Depends"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# 关键: Base 被导入时自动注册所有模型，便于 Alembic autogenerate。
import_all_db_models()
