from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import Field, UUID4
from datetime import datetime
from typing import List, Optional
from supabase.client import AsyncClient


class LlmConversationModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    metadata: Optional[dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    state: Optional[str] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "llm_conversation")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "llm_conversation", self.id)


class LlmConversationMessageModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    type: Optional[str] = Field(default=None)
    conversation_id: UUID4
    content: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "llm_conversation_message")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "llm_conversation_message", self.id
        )


class LlmConversationMessageHistoryModel(SupabaseModel):
    organization_id: UUID4
    conversation_id: UUID4
    session_id: Optional[UUID4] = Field(default=None)
    query_id: Optional[UUID4] = Field(default=None)
    message_id: UUID4
    response_id: Optional[UUID4] = Field(default=None)
    previous_message_id: Optional[UUID4] = Field(default=None)
    next_message_id: Optional[UUID4] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase,
            "llm_conversation_message_history",
            ["conversation_id", "message_id"],
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "llm_conversation_message_history",
            {"conversation_id": self.conversation_id, "message_id": self.message_id},
        )


class LlmConversationThreadModel(SupabaseModel):
    conversation_id: UUID4
    parent_message_id: UUID4
    created_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase,
            "llm_conversation_thread",
            ["conversation_id", "parent_message_id"],
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "llm_conversation_thread",
            {
                "conversation_id": self.conversation_id,
                "parent_message_id": self.parent_message_id,
            },
        )
