from app.models.supabase.supabase_model import SupabaseModel
from pydantic import Field, UUID4
from datetime import datetime
from typing import List, Optional
from supabase.client import AsyncClient

class LlmConversationModel(SupabaseModel):
    id: UUID4 | None = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4 | None = None
    state: str | None = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "llm_conversation")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "llm_conversation", self.id)
class LlmConversationMessageModel(SupabaseModel):
    id: UUID4 | None = None
    type: str | None = None
    conversation_id: UUID4 | None
    content: Optional[str] = None
    model: Optional[str] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4 | None = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "llm_conversation_message")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "llm_conversation_message", self.id)
class LlmConversationMessageHistoryModel(SupabaseModel):
    organization_id: UUID4 | None = None
    conversation_id: UUID4 | None = None
    session_id: UUID4 | None = None
    query_id: Optional[UUID4] = None
    message_id: UUID4 | None = None
    response_id: Optional[UUID4] = None
    previous_message_id: Optional[UUID4] = None
    next_message_id: Optional[UUID4] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "llm_conversation_message_history", ['conversation_id', 'message_id'])

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "llm_conversation_message_history",
            {"conversation_id": self.conversation_id, "message_id": self.message_id},
        )

class LlmConversationThreadModel(SupabaseModel):
    conversation_id: UUID4 | None = None
    parent_message_id: UUID4 | None = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4 | None = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "llm_conversation_thread", ['conversation_id', 'parent_message_id'])

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "llm_conversation_thread",
            {"conversation_id": self.conversation_id, "parent_message_id": self.parent_message_id},
        )
