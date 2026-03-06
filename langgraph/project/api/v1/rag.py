"""
RAG 管理 API
===============
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File

from api.deps import get_vectorstore
from schemas.rag import DocumentUploadRequest, RetrievalRequest, RetrievalResponse

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection: str = "default",
    vectorstore=Depends(get_vectorstore),
):
    """
    上传文档到知识库

    教程要点:
        1. 接收文件 → 解析 → 分块 → 嵌入 → 存储
        2. 支持 PDF / DOCX / TXT / MD
    """
    content = await file.read()
    # TODO: 实际处理
    return {"status": "uploaded", "filename": file.filename, "collection": collection}


@router.post("/search", response_model=RetrievalResponse)
async def search_documents(
    request: RetrievalRequest,
    vectorstore=Depends(get_vectorstore),
):
    """
    检索文档

    教程要点:
        - 支持相似度搜索 / MMR / 混合搜索
    """
    # TODO: 实际检索
    return RetrievalResponse(
        query=request.query,
        results=[],
        total_found=0,
    )


@router.get("/collections")
async def list_collections(vectorstore=Depends(get_vectorstore)):
    """列出所有集合"""
    return {"collections": ["default"]}
