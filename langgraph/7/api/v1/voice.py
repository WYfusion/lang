"""
语音 API — REST 上传 + WebSocket 地址指引
===========================================
"""

from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Depends

from api.deps import get_current_user_id
from schemas.voice import STTResult

router = APIRouter()


@router.post("/stt", response_model=STTResult)
async def speech_to_text(
    file: UploadFile = File(..., description="音频文件"),
    language: str = "zh",
    user_id: str = Depends(get_current_user_id),
):
    """
    REST 语音转文字

    教程要点:
        - 适合非实时场景 (上传录音文件)
        - 实时语音对话请使用 WebSocket /ws/voice
    """
    audio_data = await file.read()
    # TODO: 实际 STT
    return STTResult(text="[STT result placeholder]", language=language)


@router.get("/voices")
async def list_voices():
    """列出可用的 TTS 声色"""
    return {
        "voices": [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "language": "zh-CN", "gender": "female"},
            {"id": "zh-CN-YunxiNeural", "name": "云希", "language": "zh-CN", "gender": "male"},
            {"id": "zh-CN-XiaoyiNeural", "name": "晓伊", "language": "zh-CN", "gender": "female"},
        ]
    }
