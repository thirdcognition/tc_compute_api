import json
from uuid import UUID
from pydantic import Field, Json, field_validator
from datetime import datetime
from typing import ClassVar, List, Optional
from supabase.client import AsyncClient

from lib.models.supabase.supabase_model import SupabaseModel


class LlmConversationModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "llm_conversation"
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
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class LlmConversationMessageModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "llm_conversation_message"
    id: Optional[UUID] = Field(default=None)
    type: Optional[str] = Field(default=None)
    conversation_id: UUID
    content: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID


class LlmConversationMessageHistoryModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "llm_conversation_message_history"
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

    @classmethod
    async def save_to_supabase(
        cls, supabase: AsyncClient, value, on_conflict=["conversation_id", "message_id"]
    ):
        await super(LlmConversationMessageHistoryModel, cls).save_to_supabase(
            supabase, value, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["conversation_id", "message_id"],
        id_field_name=None,
    ):
        # Upsert logic which uses the same parameters and structure as save_to_supabase
        await super(LlmConversationMessageHistoryModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_field_name
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {
                "conversation_id": value.conversation_id,
                "message_id": value.message_id,
            }
        # If value is not provided or not an instance, it is used as is
        return await super(LlmConversationMessageHistoryModel, cls).fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        # Check if the value is an instance of the class and extract values from it
        if isinstance(value, cls):
            value = {
                "conversation_id": value.conversation_id,
                "message_id": value.message_id,
            }
        # If value is not provided or not an instance, it is used as is
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class LlmConversationThreadModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "llm_conversation_thread"
    conversation_id: UUID
    parent_message_id: UUID
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    @classmethod
    async def save_to_supabase(
        cls,
        supabase: AsyncClient,
        value,
        on_conflict=["conversation_id", "parent_message_id"],
    ):
        # Use the provided value instead of instance-specific data
        await super(LlmConversationThreadModel, cls).save_to_supabase(
            supabase, value, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["conversation_id", "parent_message_id"],
        id_field_name=None,
    ):
        # Use the provided instances instead of instance-specific data
        await super(LlmConversationThreadModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_field_name
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {
                "conversation_id": value.conversation_id,
                "parent_message_id": value.parent_message_id,
            }
        return await super(LlmConversationThreadModel, cls).fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {
                "conversation_id": value.conversation_id,
                "parent_message_id": value.parent_message_id,
            }
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )
