"""
记忆管理 API
==============
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends

from api.deps import get_current_user_id, get_memory_repo
from db.repositories import MemoryRepository
from schemas.memory import MemoryCreate, MemoryResponse, MemorySearchRequest, MemorySearchResponse

router = APIRouter()


@router.get("/", response_model=list[MemoryResponse])
async def list_memories(
    memory_type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    repo: MemoryRepository = Depends(get_memory_repo),
):
    """列出用户记忆"""
    memories = await repo.get_by_user(user_id, memory_type=memory_type)
    return [MemoryResponse(
        id=m.id,
        user_id=m.user_id,
        memory_type=m.memory_type,
        content=m.content,
        importance=m.importance,
        access_count=m.access_count,
    ) for m in memories]


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    repo: MemoryRepository = Depends(get_memory_repo),
):
    """语义检索记忆"""
    # TODO: 结合向量检索
    memories = await repo.get_by_user(request.user_id, limit=request.top_k)
    return MemorySearchResponse(
        memories=[],
        query=request.query,
        total_found=0,
    )


@router.delete("/")
async def clear_memories(
    memory_type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    repo: MemoryRepository = Depends(get_memory_repo),
):
    """清除用户记忆"""
    count = await repo.delete_by_user(user_id, memory_type=memory_type)
    return {"deleted": count}
