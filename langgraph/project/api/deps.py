"""
FastAPI 依赖注入 — 企业级 DI 模式
====================================

教程要点:
    1. Depends() 实现依赖注入
    2. 数据库 Session / Repository / Service 层层注入
    3. 当前用户认证 (可扩展 JWT)
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Request

from db.base import get_async_session
from db.repositories import ConversationRepository, MessageRepository, MemoryRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """数据库 Session 依赖"""
    async for session in get_async_session():
        yield session


async def get_conversation_repo(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationRepository:
    """会话仓储依赖"""
    return ConversationRepository(session)


async def get_message_repo(
    session: AsyncSession = Depends(get_db_session),
) -> MessageRepository:
    """消息仓储依赖"""
    return MessageRepository(session)


async def get_memory_repo(
    session: AsyncSession = Depends(get_db_session),
) -> MemoryRepository:
    """记忆仓储依赖"""
    return MemoryRepository(session)


async def get_compiled_graph(request: Request):
    """获取预编译的 LangGraph 图"""
    return request.app.state.graph


async def get_vectorstore(request: Request):
    """获取向量存储管理器"""
    return request.app.state.vectorstore


async def get_current_user_id() -> str:
    """
    获取当前用户 ID

    教程要点: 生产环境替换为 JWT 认证
        from fastapi.security import OAuth2PasswordBearer
        oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")
        async def get_current_user(token: str = Depends(oauth2)) -> User:
            return decode_jwt(token)
    """
    return "default_user"  # 开发环境默认用户
