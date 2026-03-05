"""
LangGraph 企业级流式语音对话系统
=================================
应用入口 — 使用 FastAPI + Uvicorn 提供 HTTP/WebSocket 服务

启动命令:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

教程要点:
    1. Lifespan 管理应用生命周期（初始化 DB / 向量库 / Graph）
    2. 中间件链：CORS → 请求日志 → 异常捕获
    3. 路由版本化 (api/v1/)
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from utils.logging import setup_logging


# ──────────────────────────────────────────────
# Lifespan: 应用启动 / 关闭时的资源管理
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    企业级实践: 使用 lifespan 替代 @app.on_event
    - 启动时: 初始化数据库连接池 / 向量存储 / LangGraph 编译
    - 关闭时: 优雅释放所有资源
    """
    settings = get_settings()
    logger = setup_logging(settings.LOG_LEVEL)
    logger.info("application_starting", version=settings.APP_VERSION)

    # === 启动阶段 ===
    # 1) 初始化数据库引擎 & 创建表 (开发环境)
    from db.base import init_db
    await init_db()

    # 2) 初始化向量存储
    from rag.vectorstore import VectorStoreManager
    vs_manager = VectorStoreManager(settings)
    await vs_manager.initialize()
    app.state.vectorstore = vs_manager

    # 3) 预编译 LangGraph 主图
    from graph.main_graph import build_main_graph
    compiled_graph = build_main_graph(settings)
    app.state.graph = compiled_graph

    logger.info("application_ready")
    yield

    # === 关闭阶段 ===
    logger.info("application_shutting_down")
    from db.base import dispose_engine
    await dispose_engine()
    logger.info("application_stopped")


# ──────────────────────────────────────────────
# FastAPI 应用实例
# ──────────────────────────────────────────────
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="LangGraph Voice Assistant",
        description="企业级 LangGraph 流式语音对话系统",
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # === 中间件 ===
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from api.middleware import RequestLoggingMiddleware, ExceptionHandlerMiddleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ExceptionHandlerMiddleware)

    # === 路由注册 ===
    from api.v1.router import api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")

    # === WebSocket 路由 ===
    from api.websocket.voice_stream import voice_ws_router
    app.include_router(voice_ws_router, prefix="/ws")

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
