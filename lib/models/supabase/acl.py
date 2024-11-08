from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from supabase.client import AsyncClient


class ACL(str, Enum):
    public = "public"
    group = "group"
    private = "private"


class UserACL(str, Enum):
    adm = "adm"
    rw = "rw"
    ro = "ro"


class ACLGroupModel(SupabaseModel):
    TABLE_NAME: str = "acl_group"
    id: Optional[UUID] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID


class ACLGroupItemsModel(SupabaseModel):
    TABLE_NAME: str = "acl_group_items"
    acl_group_id: UUID
    acl: ACL = Field(default=ACL.private)
    item_id: UUID
    item_type: str
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID

    async def save_to_supabase(
        self, supabase: AsyncClient, on_conflict=["item_id", "acl_group_id"]
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, id_field_name="acl_group_id", value=None
    ):
        return await super().fetch_from_supabase(
            supabase, id_field_name=id_field_name, value=value
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, id_field_name="acl_group_id", value=None
    ):
        return await super().exists_in_supabase(
            supabase, id_field_name=id_field_name, value=value
        )

    async def delete_from_supabase(
        self, supabase: AsyncClient, id_field_name="acl_group_id", value=None
    ):
        return await super().delete_from_supabase(
            supabase, id_field_name=id_field_name, value=value
        )


class ACLGroupUsersModel(SupabaseModel):
    TABLE_NAME: str = "acl_group_users"
    auth_id: UUID
    user_id: UUID
    acl_group_id: UUID
    acl: UserACL = Field(default=UserACL.ro)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID

    async def save_to_supabase(
        self, supabase: AsyncClient, on_conflict=["user_id", "acl_group_id"]
    ):
        await super().save_to_supabase(supabase, on_conflict)

    async def fetch_from_supabase(
        self, supabase: AsyncClient, id_field_name="acl_group_id", value=None
    ):
        return await super().fetch_from_supabase(
            supabase, id_field_name=id_field_name, value=value
        )

    async def exists_in_supabase(
        self, supabase: AsyncClient, id_field_name="acl_group_id", value=None
    ):
        return await super().exists_in_supabase(
            supabase, id_field_name=id_field_name, value=value
        )

    async def delete_from_supabase(
        self, supabase: AsyncClient, id_field_name="acl_group_id", value=None
    ):
        return await super().delete_from_supabase(
            supabase, id_field_name=id_field_name, value=value
        )


class ACLGroupUsersWithItems(BaseModel):
    organization_id: UUID
    acl_group_id: UUID
    item_id: UUID
    item_type: str
    item_acl: ACL
    item_created_at: Optional[datetime]
    item_disabled: bool
    item_disabled_at: Optional[datetime]
    auth_id: UUID
    user_acl: UserACL
    user_id: UUID
    user_created_at: Optional[datetime]
    user_disabled: bool
    user_disabled_at: Optional[datetime]
