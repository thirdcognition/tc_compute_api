import json
from datetime import datetime
from typing import Optional
from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, Json, field_validator
from supabase.client import AsyncClient


class JourneyProgressModel(SupabaseModel):
    TABLE_NAME: str = "journey_progress"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    journey_version_id: UUID
    assigned_at: Optional[datetime] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class JourneyProgressLLMConversationMessagesModel(SupabaseModel):
    TABLE_NAME: str = "journey_progress_llm_conversation_messages"
    journey_item_progress_id: UUID
    message_id: UUID
    conversation_id: UUID
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    async def save_to_supabase(
        self,
        supabase: AsyncClient,
        on_conflict=["journey_item_progress_id", "message_id"],
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "journey_item_progress_id": self.journey_item_progress_id,
                "message_id": self.message_id,
            }
        return await super().fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "journey_item_progress_id": self.journey_item_progress_id,
                "message_id": self.message_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def delete_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "journey_item_progress_id": self.journey_item_progress_id,
                "message_id": self.message_id,
            }
        return await super().delete_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class JourneyProgressLLMConversationsModel(SupabaseModel):
    TABLE_NAME: str = "journey_progress_llm_conversations"
    progress_id: UUID
    conversation_id: UUID
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    async def save_to_supabase(
        self, supabase: AsyncClient, on_conflict=["progress_id", "conversation_id"]
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "progress_id": self.progress_id,
                "conversation_id": self.conversation_id,
            }
        return await super().fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "progress_id": self.progress_id,
                "conversation_id": self.conversation_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def delete_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "progress_id": self.progress_id,
                "conversation_id": self.conversation_id,
            }
        return await super().delete_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class JourneyItemProgressModel(SupabaseModel):
    TABLE_NAME: str = "journey_item_progress"
    id: Optional[UUID] = Field(default=None)
    journey_progress_id: UUID
    journey_item_id: UUID
    journey_item_version_id: UUID
    data: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    @field_validator("data", mode="before")
    def validate_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
