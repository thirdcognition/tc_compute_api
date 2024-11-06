from datetime import datetime
from typing import Optional
from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import UUID4, Field
from supabase.client import AsyncClient


class ContextQuery(SupabaseModel):
    id: UUID4
    params: Optional[dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "context_query")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "context_query", self.id)


class ContextQueryResponse(SupabaseModel):
    id: UUID4
    query_id: Optional[UUID4] = Field(default=None)
    response_data: Optional[dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "context_query_response")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "context_query_response", self.id
        )


class ContextQueryResult(SupabaseModel):
    id: UUID4
    query_id: Optional[UUID4] = Field(default=None)
    result_data: Optional[dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "context_query_result")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "context_query_result", self.id
        )
