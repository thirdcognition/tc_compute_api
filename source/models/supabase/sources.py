from datetime import datetime
from typing import ClassVar, Dict, Optional
from uuid import UUID
from pydantic import Field

# from enum import Enum
from supabase import Client
from supabase.client import AsyncClient

from source.helpers.json_exportable_enum import JSONExportableEnum
from source.models.supabase.supabase_model import SupabaseModel


class SourceTypeEnum(str, JSONExportableEnum):
    DOCUMENT = "document"
    WEBPAGE = "webpage"
    WEBSITE = "website"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TOPIC = "topic"
    CONCEPT = "concept"
    COLLECTION = "collection"


class SourceModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "source"
    id: Optional[UUID] = Field(default=None)
    original_source: Optional[str] = Field(default=None)
    resolved_source: Optional[str] = Field(default=None)
    type: Optional[SourceTypeEnum] = Field(default=None)
    title: Optional[str] = Field(default=None)
    lang: Optional[str] = Field(default=None)
    content_hash: Optional[str] = Field(default=None)
    data: Optional[Dict] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)


class SourceChunkModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "source_chunk"
    id: Optional[UUID] = Field(default=None)
    source_id: Optional[UUID] = Field(default=None)
    chunk_next_id: Optional[UUID] = Field(default=None)
    chunk_prev_id: Optional[UUID] = Field(default=None)
    data: Optional[Dict] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)


class SourceRelationshipModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "source_relationship"
    source_id: UUID
    related_source_id: UUID
    relationship_type: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    # @field_validator("metadata", mode="before")
    # def validate_metadata(cls, v):
    #     if isinstance(v, str):
    #         return json.loads(v)
    #     elif isinstance(v, dict):
    #         return json.dumps(v)
    #     return v

    @classmethod
    async def save_to_supabase(
        cls,
        supabase: AsyncClient,
        instance,
        on_conflict=["source_id", "related_source_id"],
    ):
        return await super(SourceRelationshipModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["source_id", "related_source_id"],
        id_column="source_id",
    ):
        return await super(SourceRelationshipModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="source_id"
    ):
        return await super(SourceRelationshipModel, cls).fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column="source_id"
    ):
        return await super(SourceRelationshipModel, cls).exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="source_id"
    ):
        return await super(SourceRelationshipModel, cls).delete_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    def save_to_supabase_sync(
        cls,
        supabase: Client,
        instance,
        on_conflict=["source_id", "related_source_id"],
    ):
        return super(SourceRelationshipModel, cls).save_to_supabase_sync(
            supabase, instance, on_conflict
        )

    @classmethod
    def upsert_to_supabase_sync(
        cls,
        supabase: Client,
        instances,
        on_conflict=["source_id", "related_source_id"],
        id_column="source_id",
    ):
        return super(SourceRelationshipModel, cls).upsert_to_supabase_sync(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    def fetch_from_supabase_sync(
        cls, supabase: Client, value=None, id_column="source_id"
    ):
        return super(SourceRelationshipModel, cls).fetch_from_supabase_sync(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    def exists_in_supabase_sync(
        cls, supabase: Client, value=None, id_column="source_id"
    ):
        return super(SourceRelationshipModel, cls).exists_in_supabase_sync(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    def delete_from_supabase_sync(
        cls, supabase: Client, value=None, id_column="source_id"
    ):
        return super(SourceRelationshipModel, cls).delete_from_supabase_sync(
            supabase, value=value, id_column=id_column
        )
