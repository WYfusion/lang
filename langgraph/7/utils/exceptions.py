"""
自定义异常
===========
"""

from __future__ import annotations


class AppError(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class LLMError(AppError):
    """LLM 调用异常"""
    def __init__(self, message: str = "LLM service error"):
        super().__init__(message, code="LLM_ERROR", status_code=502)


class RAGError(AppError):
    """RAG 检索异常"""
    def __init__(self, message: str = "RAG retrieval error"):
        super().__init__(message, code="RAG_ERROR", status_code=500)


class VoiceError(AppError):
    """语音处理异常"""
    def __init__(self, message: str = "Voice processing error"):
        super().__init__(message, code="VOICE_ERROR", status_code=500)


class ConversationNotFoundError(AppError):
    """会话不存在"""
    def __init__(self, conversation_id: str = ""):
        super().__init__(
            f"Conversation not found: {conversation_id}",
            code="CONVERSATION_NOT_FOUND",
            status_code=404,
        )


class MemoryError(AppError):
    """记忆管理异常"""
    def __init__(self, message: str = "Memory operation error"):
        super().__init__(message, code="MEMORY_ERROR", status_code=500)
