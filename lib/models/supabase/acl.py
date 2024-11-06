from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import UUID4, BaseModel, Field
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
    id: Optional[UUID4] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "acl_group")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "acl_group", self.id)


class ACLGroupItemsModel(SupabaseModel):
    acl_group_id: UUID4
    acl: ACL = Field(default=ACL.private)
    item_id: UUID4
    item_type: str
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase, "acl_group_items", ["item_id", "acl_group_id"]
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "acl_group_items", {"acl_group_id": self.acl_group_id}
        )


class ACLGroupUsersModel(SupabaseModel):
    auth_id: UUID4
    user_id: UUID4
    acl_group_id: UUID4
    acl: UserACL = Field(default=UserACL.ro)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase, "acl_group_users", ["user_id", "acl_group_id"]
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "acl_group_users",
            {"acl_group_id": self.acl_group_id, "auth_id": self.auth_id},
        )


class ACLGroupUsersWithItems(BaseModel):
    organization_id: UUID4
    acl_group_id: UUID4
    item_id: UUID4
    item_type: str
    item_acl: ACL
    item_created_at: Optional[datetime]
    item_disabled: bool
    item_disabled_at: Optional[datetime]
    auth_id: UUID4
    user_acl: UserACL
    user_id: UUID4
    user_created_at: Optional[datetime]
    user_disabled: bool
    user_disabled_at: Optional[datetime]
