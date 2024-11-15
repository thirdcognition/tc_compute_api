from datetime import datetime
from typing import ClassVar, Optional
from uuid import UUID
from pydantic import field_validator, Field, Json
from enum import Enum
import json
from supabase.client import AsyncClient

from lib.models.supabase.supabase_model import SupabaseModel


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
    TABLE_NAME: ClassVar[str] = "source"
    id: UUID
    type: Optional[SourceTypeEnum] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)


class SourceChunkModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "source_chunk"
    id: UUID
    source_id: Optional[UUID] = Field(default=None)
    source_version_id: Optional[UUID] = Field(default=None)
    chunk_next_id: Optional[UUID] = Field(default=None)
    chunk_prev_id: Optional[UUID] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID

    @field_validator("metadata", "data", mode="before")
    def validate_json_fields(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class SourceRelationshipModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "source_relationship"
    source_version_id: UUID
    related_source_version_id: UUID
    relationship_type: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v

    @classmethod
    async def save_to_supabase(cls, supabase: AsyncClient, instance, on_conflict=None):
        await super(SourceRelationshipModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=None,
        id_column="source_version_id",
    ):
        await super(SourceRelationshipModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="source_version_id"
    ):
        return await super(SourceRelationshipModel, cls).fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column="source_version_id"
    ):
        return await super(SourceRelationshipModel, cls).exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="source_version_id"
    ):
        return await super(SourceRelationshipModel, cls).delete_from_supabase(
            supabase, value=value, id_column=id_column
        )


class SourceVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "source_version"
    id: UUID
    title: Optional[str] = Field(default=None)
    lang: Optional[str] = Field(default=None)
    content_hash: Optional[str] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    version_of_id: Optional[UUID] = Field(default=None)

    @field_validator("metadata", "data", mode="before")
    def validate_json_fields(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v
