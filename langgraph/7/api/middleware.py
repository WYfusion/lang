"""
中间件 — 请求日志 & 异常处理
================================

教程要点:
    1. ASGI 中间件拦截所有请求
    2. 结构化日志记录请求/响应
    3. 统一异常处理, 返回规范错误响应
"""

from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from utils.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", "")

        # 记录请求
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )

        response = await call_next(request)

        # 记录响应
        latency_ms = (time.time() - start_time) * 1000
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=round(latency_ms, 2),
            request_id=request_id,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{latency_ms:.2f}ms"
        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """统一异常处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "unhandled_exception",
                error=str(e),
                error_type=type(e).__name__,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": str(e) if request.app.debug else "An unexpected error occurred",
                },
            )
