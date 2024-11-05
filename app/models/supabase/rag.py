from datetime import datetime
from typing import Literal, List, Optional
from app.models.supabase.supabase_model import SupabaseModel
from pydantic import field_validator
from pydantic.types import UUID4
from enum import Enum
import json
from supabase.client import AsyncClient

class EmbeddingSize(str, Enum):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large"


class RAGDocumentModel(SupabaseModel):
    id: UUID4 | None = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    current_version_id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, 'rag_document')

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "rag_document", self.id)
class RAGDocumentChunkModel(SupabaseModel):
    id: UUID4 | None = None
    document_id: Optional[UUID4] = None
    document_version_id: Optional[UUID4] = None
    chunk_next_id: Optional[UUID4] = None
    chunk_prev_id: Optional[UUID4] = None
    start_char: Optional[int] = None
    total_length: Optional[int] = None
    embedding_size: EmbeddingSize
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    organization_id: UUID4

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, 'rag_document_chunk')

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "rag_document_chunk", self.id)

class RAGDocumentVersionModel(SupabaseModel):
    id: UUID4 | None = None
    title: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    source_metadata: Optional[dict] = None
    content_type: Optional[str] = None
    content_hash: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    lang: Optional[str] = None
    metadata: Optional[dict] = None
    ver: Optional[int] = None
    embedding_size: EmbeddingSize
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    version_of_id: Optional[UUID4] = None

    @field_validator("source_metadata", "metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, 'rag_document_version')
    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "rag_document_version", self.id)
class RAGQueryModel(SupabaseModel):
    id: UUID4 | None = None
    embedding_size: EmbeddingSize
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, 'rag_query')

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "rag_query", self.id)
class RAGResponseModel(SupabaseModel):
    id: UUID4 | None = None
    query_id: Optional[UUID4] = None
    response_text: Optional[str] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, 'rag_response')

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "rag_response", self.id)
class RAGResultModel(SupabaseModel):
    id: UUID4 | None = None
    query_id: Optional[UUID4] = None
    document_id: Optional[UUID4] = None
    document_chunk_id: Optional[UUID4] = None
    score: Optional[float] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, 'rag_result')

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "rag_result", self.id)

class EmbeddingSize(str, Enum):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large"


class RagEmbeddingBaseModel(SupabaseModel):
    id: UUID4 | None = None
    type: Literal["summary", "chunk", "query"]
    content: str
    hash: str
    lang: str
    document_id: Optional[UUID4] = None
    document_version_id: Optional[UUID4] = None
    document_chunk_id: Optional[UUID4] = None
    query_id: Optional[UUID4] = None
    embedding_model: str
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: datetime
    owner_id: Optional[UUID4] = None
    organization_id: UUID4

class RagEmbedding(RagEmbeddingBase):
    size: EmbeddingSize
    embedding: list[float]

    @field_validator("embedding")
    def check_embedding_length(cls, v, info):
        size = info.data.get("size")
        if size == EmbeddingSize.tiny:
            assert len(v) == 384
        elif size == EmbeddingSize.small:
            assert len(v) == 512
        elif size == EmbeddingSize.medium:
            assert len(v) == 1024
        elif size == EmbeddingSize.large:
            assert len(v) == 1536
        return v

    async def save_to_supabase(self, supabase: AsyncClient):
        table_name = f'rag_embedding_{self.size.value}'
        await super().save_to_supabase(supabase, table_name)

    async def fetch_from_supabase(self, supabase: AsyncClient):
        table_name = f'rag_embedding_{self.size.value}'
        await super().fetch_from_supabase(supabase, table_name, self.id)