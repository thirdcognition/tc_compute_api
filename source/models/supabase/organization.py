import json
from typing import ClassVar, Dict, Optional
from uuid import UUID
from pydantic import Field, field_validator
from pydantic.types import PositiveInt
from datetime import datetime
from supabase.client import AsyncClient

from source.models.supabase.supabase_model import SupabaseModel
from source.models.supabase.acl import ACLGroupUsersModel, UserACL


class UserProfileModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "user_profile"
    id: Optional[UUID] = Field(default=None)
    auth_id: Optional[UUID] = Field(default=None)
    email: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    profile_picture: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    lang: Optional[str] = Field(default=None)
    active_panel_id: Optional[UUID] = Field(default=None)
    preferences: Optional[Dict] = Field(default=None)
    payment_details: Optional[Dict] = Field(default=None)
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


class UserDataModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "user_data"
    id: Optional[UUID] = Field(default=None)
    auth_id: Optional[UUID] = Field(default=None)
    item: str
    target_id: Optional[UUID] = Field(default=None)
    data: Optional[Dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class OrganizationRoleModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organization_role"
    id: Optional[UUID] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    seniority: PositiveInt
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

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
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

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
    organization_id: Optional[UUID] = Field(default=None)

    @classmethod
    async def save_to_supabase(
        cls, supabase: AsyncClient, instance, on_conflict=["auth_id", "team_id"]
    ):
        return await super(OrganizationTeamMembersModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["auth_id", "team_id"],
        id_column=None,
    ):
        return await super(OrganizationTeamMembersModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "team_id": value.team_id}
        return await super(OrganizationTeamMembersModel, cls).fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "team_id": value.team_id}
        return await super(OrganizationTeamMembersModel, cls).exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "team_id": value.team_id}
        return await super(OrganizationTeamMembersModel, cls).delete_from_supabase(
            supabase, value=value, id_column=id_column
        )


class OrganizationUsersModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organization_users"
    auth_id: Optional[UUID] = Field(default=None)
    user_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
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
        return await super(OrganizationUsersModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["auth_id", "organization_id"],
        id_column=None,
    ):
        return await super(OrganizationUsersModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "organization_id": value.organization_id}
        return await super(OrganizationUsersModel, cls).fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "organization_id": value.organization_id}
        return await super(OrganizationUsersModel, cls).exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column=None
    ):
        if isinstance(value, cls):
            value = {"auth_id": value.auth_id, "organization_id": value.organization_id}
        return await super(OrganizationUsersModel, cls).delete_from_supabase(
            supabase, value=value, id_column=id_column
        )

    async def in_acl_group(self, supabase: AsyncClient, acl_group_id: UUID):
        return await ACLGroupUsersModel.exists_in_supabase(
            supabase, value={"user_id": self.user_id, "acl_group_id": acl_group_id}
        )

    async def connect_with_acl_group(
        self, supabase: AsyncClient, acl_group_id: UUID, acl: UserACL
    ):
        """Connect the user to an ACL group with specified ACL level."""
        # Attempt to fetch the existing relationship
        existing_acl_group_user = await ACLGroupUsersModel.fetch_from_supabase(
            supabase, {"user_id": self.user_id, "acl_group_id": acl_group_id}
        )

        if existing_acl_group_user:
            # If the relationship exists, update the ACL level
            existing_acl_group_user.acl = acl
            await existing_acl_group_user.update()
        else:
            # Otherwise, create a new ACL group user relationship
            acl_group_user = ACLGroupUsersModel(
                user_id=self.user_id,
                auth_id=self.auth_id,
                acl_group_id=acl_group_id,
                acl=acl,
                organization_id=self.organization_id,
            )
            await ACLGroupUsersModel.save_to_supabase(supabase, acl_group_user)

    async def disconnect_with_acl_group(
        self, supabase: AsyncClient, acl_group_id: UUID
    ):
        """Disconnect the user from an ACL group."""
        await ACLGroupUsersModel.delete_from_supabase(
            supabase, {"user_id": self.user_id, "acl_group_id": acl_group_id}
        )

    async def create(
        self,
        supabase: AsyncClient,
        groups_with_levels: dict[UUID, UserACL] = None,
    ) -> "OrganizationUsersModel":
        """Create a new organization user and connect to specified ACL groups."""
        # Save the organization user
        org_user = await self.save_to_supabase(supabase, self)

        # Connect to specified ACL groups
        if groups_with_levels:
            for acl_group_id, acl in groups_with_levels.items():
                await org_user.connect_with_acl_group(supabase, acl_group_id, acl)

        return org_user


class OrganizationsModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "organizations"
    id: Optional[UUID] = Field(default=None)
    default_acl_group_id: Optional[UUID] = Field(default=None)
    default_bucket_id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    logo: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
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
