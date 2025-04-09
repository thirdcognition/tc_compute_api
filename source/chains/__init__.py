# source/chains/__init__.py
"""
Main entry point for the chains package.

This module exports the primary functions for retrieving configured
LLMs, embedding models, and chains (both general and specialized like RAG).
"""

from .llm_factory import get_llm
from .embedding_factory import get_embeddings
from .chain_factory import get_chain, get_base_chain
from .rag_chain import get_rag_chain  # Export RAG chain retrieval

__all__ = [
    "get_llm",
    "get_embeddings",
    "get_chain",
    "get_base_chain",
    "get_rag_chain",
]
