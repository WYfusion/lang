"""
文档分块策略
==============

教程要点:
    1. RecursiveCharacterTextSplitter: 通用分块器
    2. 语义分块 (Semantic Chunking): 按语义边界切分
    3. 分块大小 & 重叠对 RAG 质量影响巨大
"""

from __future__ import annotations

from typing import Sequence

from langchain_core.documents import Document


class ChunkingStrategy:
    """
    文档分块策略

    教程要点:
        # 基础分块
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            separators=["\n\n", "\n", "。", "！", "？", ".", " "],
        )
        chunks = splitter.split_documents(docs)

        # 语义分块 (更智能)
        from langchain_experimental.text_splitter import SemanticChunker
        splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, documents: Sequence[Document]) -> list[Document]:
        """分块文档"""
        # TODO: 实际实现
        # from langchain_text_splitters import RecursiveCharacterTextSplitter
        # splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=self.chunk_size,
        #     chunk_overlap=self.chunk_overlap,
        # )
        # return splitter.split_documents(documents)
        return list(documents)
