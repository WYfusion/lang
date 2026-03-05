"""
API v1 路由汇总
================
"""

from __future__ import annotations

from fastapi import APIRouter

from api.v1.chat import router as chat_router
from api.v1.voice import router as voice_router
from api.v1.memory import router as memory_router
from api.v1.rag import router as rag_router

api_v1_router = APIRouter()

api_v1_router.include_router(chat_router, prefix="/chat", tags=["对话"])
api_v1_router.include_router(voice_router, prefix="/voice", tags=["语音"])
api_v1_router.include_router(memory_router, prefix="/memory", tags=["记忆"])
api_v1_router.include_router(rag_router, prefix="/rag", tags=["RAG"])
