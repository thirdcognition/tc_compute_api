import json
from typing import Optional
from uuid import UUID
from pydantic import Field, Json, field_validator
from pydantic.types import PositiveInt
from datetime import datetime
from supabase.client import AsyncClient

from lib.models.supabase.supabase_model import SupabaseModel


class UserProfileModel(SupabaseModel):
    TABLE_NAME: str = "user_profile"
    id: Optional[UUID] = Field(default=None)
    auth_id: Optional[UUID] = Field(default=None)
    email: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    profile_picture: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    active_organization_id: Optional[UUID] = Field(default=None)
    active_conversation_id: Optional[UUID] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class OrganizationRoleModel(SupabaseModel):
    TABLE_NAME: str = "organization_role"
    id: Optional[UUID] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    seniority: PositiveInt
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class OrganizationTeamModel(SupabaseModel):
    TABLE_NAME: str = "organization_team"
    id: Optional[UUID] = Field(default=None)
    name: str
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class OrganizationTeamMembersModel(SupabaseModel):
    TABLE_NAME: str = "organization_team_members"
    auth_id: UUID
    user_id: UUID
    team_id: UUID
    role_id: UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID

    async def save_to_supabase(
        self, supabase: AsyncClient, on_conflict=["auth_id", "team_id"]
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {"auth_id": self.auth_id, "team_id": self.team_id}
        return await super().fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {"auth_id": self.auth_id, "team_id": self.team_id}
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def delete_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {"auth_id": self.auth_id, "team_id": self.team_id}
        return await super().delete_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class OrganizationUsersModel(SupabaseModel):
    TABLE_NAME: str = "organization_users"
    auth_id: Optional[UUID] = Field(default=None)
    user_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    metadata: Optional[Json] = Field(default=None)
    is_admin: bool = Field(default=False)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    async def save_to_supabase(
        self, supabase: AsyncClient, on_conflict=["auth_id", "organization_id"]
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {"auth_id": self.auth_id, "organization_id": self.organization_id}
        return await super().fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {"auth_id": self.auth_id, "organization_id": self.organization_id}
        return await super().exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    async def delete_from_supabase(
        self, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if value is None:
            value = {"auth_id": self.auth_id, "organization_id": self.organization_id}
        return await super().delete_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class OrganizationsModel(SupabaseModel):
    TABLE_NAME: str = "organizations"
    id: Optional[UUID] = Field(default=None)
    name: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    logo: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
