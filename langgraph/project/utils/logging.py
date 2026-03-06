"""
结构化日志 — structlog 配置
==============================

教程要点:
    1. structlog: 结构化日志, JSON 格式, 生产级
    2. 支持 timestamp / level / event / 自定义字段
    3. 开发环境 Pretty Print, 生产环境 JSON
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def setup_logging(level: str = "INFO") -> Any:
    """
    配置 structlog

    教程要点:
        - 开发环境: ConsoleRenderer (彩色输出)
        - 生产环境: JSONRenderer (方便 ELK 采集)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),  # 开发环境
            # structlog.processors.JSONRenderer(),  # 生产环境
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def get_logger(name: str = "") -> Any:
    """获取 logger 实例"""
    return structlog.get_logger(name)
