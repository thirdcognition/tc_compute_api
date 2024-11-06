from typing import Dict, Optional
from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import Field, UUID4
from pydantic.types import PositiveInt
from datetime import datetime
from supabase.client import AsyncClient


class UserProfileModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    auth_id: Optional[UUID4] = Field(default=None)
    email: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    profile_picture: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    active_organization_id: Optional[UUID4] = Field(default=None)
    active_conversation_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "user_profile")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "user_profile", self.id)


class OrganizationRoleModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    seniority: PositiveInt
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "organization_role")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "organization_role", self.id)


class OrganizationTeamModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    name: str
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
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
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
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
    is_admin: bool = Field(default=False)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

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
    id: Optional[UUID4] = Field(default=None)
    name: str
    website: Optional[str] = Field(default=None)
    logo: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "organizations")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "organizations", self.id)
