import json
from datetime import datetime
from typing import ClassVar, Dict, Optional
from source.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, field_validator
from supabase.client import AsyncClient


class JourneyProgressModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_progress"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    journey_version_id: UUID
    assigned_at: Optional[datetime] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class JourneyProgressLLMConversationMessagesModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_progress_llm_conversation_messages"
    journey_item_progress_id: UUID
    message_id: UUID
    conversation_id: UUID
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @classmethod
    async def save_to_supabase(
        cls,
        supabase: AsyncClient,
        instance,
        on_conflict=["journey_item_progress_id", "message_id"],
    ):
        return await super(
            JourneyProgressLLMConversationMessagesModel, cls
        ).save_to_supabase(supabase, instance, on_conflict)

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["journey_item_progress_id", "message_id"],
        id_column=None,
    ):
        return await super(
            JourneyProgressLLMConversationMessagesModel, cls
        ).upsert_to_supabase(supabase, instances, on_conflict, id_column)

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {
                "journey_item_progress_id": value.journey_item_progress_id,
                "message_id": value.message_id,
            }
        return await super().fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {
                "journey_item_progress_id": value.journey_item_progress_id,
                "message_id": value.message_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {
                "journey_item_progress_id": value.journey_item_progress_id,
                "message_id": value.message_id,
            }
        return await super().delete_from_supabase(
            supabase, value=value, id_column=id_column
        )


class JourneyProgressLLMConversationsModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_progress_llm_conversations"
    progress_id: UUID
    conversation_id: UUID
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @classmethod
    async def save_to_supabase(
        cls,
        supabase: AsyncClient,
        instance,
        on_conflict=["progress_id", "conversation_id"],
    ):
        return await super(JourneyProgressLLMConversationsModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instance,
        on_conflict=["progress_id", "conversation_id"],
        id_column=None,
    ):
        return await super(
            JourneyProgressLLMConversationsModel, cls
        ).upsert_to_supabase(supabase, instance, on_conflict, id_column)

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {
                "progress_id": value.progress_id,
                "conversation_id": value.conversation_id,
            }
        return await super(
            JourneyProgressLLMConversationsModel, cls
        ).fetch_from_supabase(supabase, value=value, id_column=id_column)

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {
                "progress_id": value.progress_id,
                "conversation_id": value.conversation_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {
                "progress_id": value.progress_id,
                "conversation_id": value.conversation_id,
            }
        return await super().delete_from_supabase(
            supabase, value=value, id_column=id_column
        )


class JourneyItemProgressModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_item_progress"
    id: Optional[UUID] = Field(default=None)
    journey_progress_id: UUID
    journey_item_id: UUID
    journey_item_version_id: UUID
    data: Optional[Dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    @field_validator("data", mode="before")
    def validate_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v
