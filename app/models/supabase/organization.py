from typing import Dict, List, Optional
from app.models.supabase.supabase_model import SupabaseModel
from pydantic import Field, UUID4
from pydantic.types import PositiveInt
from datetime import datetime
from postgrest import APIResponse
from supabase.client import AsyncClient


class UserProfileModel(SupabaseModel):
    id: UUID4 | None = None
    auth_id: UUID4 | None = None
    name: Optional[str] = None
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    active_organization_id: Optional[UUID4] = None
    active_conversation_id: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "user_profile")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "user_profile", self.id)

class OrganizationRoleModel(SupabaseModel):
    id: UUID4 | None = None
    name: str
    description: str | None = None
    seniority: PositiveInt
    disabled: bool = False
    disabled_at: datetime | None = None
    created_at: datetime | None = None
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "organization_role")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "organization_role", self.id)


class OrganizationTeamModel(SupabaseModel):
    id: UUID4 | None = None
    name: str
    disabled: bool = False
    disabled_at: datetime | None = None
    created_at: datetime | None = None
    owner_id: UUID4 | None = None
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "organization_team")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "organization_team", self.id)


class OrganizationTeamMembersModel(SupabaseModel):
    auth_id: UUID4
    user_id: UUID4
    team_id: UUID4
    role_id: UUID4
    disabled: bool = False
    disabled_at: datetime | None = None
    created_at: datetime | None = None
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase, "organization_team_members", ["auth_id", "team_id"]
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "organization_team_members",
            {"auth_id": self.auth_id, "team_id": self.team_id},
        )


class OrganizationUsersModel(SupabaseModel):
    auth_id: UUID4
    user_id: UUID4
    organization_id: UUID4
    is_admin: bool = False
    disabled: bool = False
    disabled_at: datetime | None = None
    created_at: datetime | None = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase, "organization_users", ["auth_id", "organization_id"]
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "organization_users",
            {"auth_id": self.auth_id, "organization_id": self.organization_id},
        )


class OrganizationsModel(SupabaseModel):
    id: UUID4 | None = None
    name: str
    website: str | None = None
    disabled: bool = False
    disabled_at: datetime | None = None
    created_at: datetime | None = None
    owner_id: UUID4 | None = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "organizations")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "organizations", self.id)
