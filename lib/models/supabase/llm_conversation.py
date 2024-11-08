import json
from uuid import UUID
from pydantic import Field, Json, field_validator
from datetime import datetime
from typing import List, Optional
from supabase.client import AsyncClient

from lib.models.supabase.supabase_model import SupabaseModel


class LlmConversationModel(SupabaseModel):
    TABLE_NAME: str = "llm_conversation"
    id: Optional[UUID] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    state: Optional[str] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class LlmConversationMessageModel(SupabaseModel):
    TABLE_NAME: str = "llm_conversation_message"
    id: Optional[UUID] = Field(default=None)
    type: Optional[str] = Field(default=None)
    conversation_id: UUID
    content: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID


class LlmConversationMessageHistoryModel(SupabaseModel):
    TABLE_NAME: str = "llm_conversation_message_history"
    organization_id: UUID
    conversation_id: UUID
    session_id: Optional[UUID] = Field(default=None)
    query_id: Optional[UUID] = Field(default=None)
    message_id: UUID
    response_id: Optional[UUID] = Field(default=None)
    previous_message_id: Optional[UUID] = Field(default=None)
    next_message_id: Optional[UUID] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)

    async def save_to_supabase(
        self, supabase: AsyncClient, on_conflict=["conversation_id", "message_id"]
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "conversation_id": self.conversation_id,
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
                "conversation_id": self.conversation_id,
                "message_id": self.message_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class LlmConversationThreadModel(SupabaseModel):
    TABLE_NAME: str = "llm_conversation_thread"
    conversation_id: UUID
    parent_message_id: UUID
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    async def save_to_supabase(
        self,
        supabase: AsyncClient,
        on_conflict=["conversation_id", "parent_message_id"],
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "conversation_id": self.conversation_id,
                "parent_message_id": self.parent_message_id,
            }
        return await super().fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {
                "conversation_id": self.conversation_id,
                "parent_message_id": self.parent_message_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )
