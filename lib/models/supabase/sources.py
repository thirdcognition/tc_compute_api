from datetime import datetime
from typing import Optional
from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import field_validator, UUID4, Field
from enum import Enum
import json
from supabase.client import AsyncClient


class SourceTypeEnum(Enum):
    DOCUMENT = "document"
    WEBPAGE = "webpage"
    WEBSITE = "website"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TOPIC = "topic"
    CONCEPT = "concept"


class SourceModel(SupabaseModel):
    id: UUID4
    type: Optional[SourceTypeEnum] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    current_version_id: Optional[UUID4] = Field(default=None)
    updated_by: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "source")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "source", self.id)


class SourceChunkModel(SupabaseModel):
    id: UUID4
    source_id: Optional[UUID4] = Field(default=None)
    source_version_id: Optional[UUID4] = Field(default=None)
    chunk_next_id: Optional[UUID4] = Field(default=None)
    chunk_prev_id: Optional[UUID4] = Field(default=None)
    data: Optional[dict] = Field(default=None)
    metadata: Optional[dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID4

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "source_chunk")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "source_chunk", self.id)


class SourceRelationshipModel(SupabaseModel):
    source_version_id: UUID4
    related_source_version_id: UUID4
    relationship_type: Optional[str] = Field(default=None)
    metadata: Optional[dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "source_relationship")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "source_relationship", self.source_version_id
        )


class SourceVersionModel(SupabaseModel):
    id: UUID4
    title: Optional[str] = Field(default=None)
    lang: Optional[str] = Field(default=None)
    content_hash: Optional[str] = Field(default=None)
    data: Optional[dict] = Field(default=None)
    metadata: Optional[dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    version_of_id: Optional[UUID4] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "source_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "source_version", self.id)
