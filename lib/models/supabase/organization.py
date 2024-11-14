import json
from typing import ClassVar, Optional
from uuid import UUID
from pydantic import Field, Json, field_validator
from pydantic.types import PositiveInt
from datetime import datetime
from supabase.client import AsyncClient

from lib.models.supabase.supabase_model import SupabaseModel


class UserProfileModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "user_profile"
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
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class OrganizationRoleModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organization_role"
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
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class OrganizationTeamModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organization_team"
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
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class OrganizationTeamMembersModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organization_team_members"
    auth_id: UUID
    user_id: UUID
    team_id: UUID
    role_id: UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID

    @classmethod
    async def save_to_supabase(
        cls, supabase: AsyncClient, instance, on_conflict=["auth_id", "team_id"]
    ):
        await super(OrganizationTeamMembersModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["auth_id", "team_id"],
        id_field_name=None,
    ):
        await super(OrganizationTeamMembersModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_field_name
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "team_id": value.team_id}
        return await super(OrganizationTeamMembersModel, cls).fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "team_id": value.team_id}
        return await super(OrganizationTeamMembersModel, cls).exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "team_id": value.team_id}
        return await super(OrganizationTeamMembersModel, cls).delete_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class OrganizationUsersModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organization_users"
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
        elif isinstance(v, dict):
            return json.dumps(v)
        return v

    @classmethod
    async def save_to_supabase(
        cls, supabase: AsyncClient, instance, on_conflict=["auth_id", "organization_id"]
    ):
        await super(OrganizationUsersModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["auth_id", "organization_id"],
        id_field_name=None,
    ):
        await super(OrganizationUsersModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_field_name
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "organization_id": value.organization_id}
        return await super(OrganizationUsersModel, cls).fetch_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "organization_id": value.organization_id}
        return await super(OrganizationUsersModel, cls).exists_in_supabase(
            supabase, value=value, id_field_name=id_field_name
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_field_name=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "organization_id": value.organization_id}
        return await super(OrganizationUsersModel, cls).delete_from_supabase(
            supabase, value=value, id_field_name=id_field_name
        )


class OrganizationsModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organizations"
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
        elif isinstance(v, dict):
            return json.dumps(v)
        return v
