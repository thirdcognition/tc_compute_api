from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import ClassVar, Optional
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
    TABLE_NAME: ClassVar[str] = "acl_group"
    id: Optional[UUID] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)


class ACLGroupItemsModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "acl_group_items"
    acl_group_id: UUID
    acl: ACL = Field(default=ACL.private)
    item_id: UUID
    item_type: str
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @classmethod
    async def save_to_supabase(
        cls, supabase: AsyncClient, instance, on_conflict=["item_id", "acl_group_id"]
    ):
        return await super(ACLGroupItemsModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["item_id", "acl_group_id"],
        id_column="acl_group_id",
    ):
        return await super(ACLGroupItemsModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="acl_group_id"
    ):
        return await super(ACLGroupItemsModel, cls).fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column="acl_group_id"
    ):
        return await super(ACLGroupItemsModel, cls).exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="acl_group_id"
    ):
        return await super(ACLGroupItemsModel, cls).delete_from_supabase(
            supabase, value=value, id_column=id_column
        )


class ACLGroupUsersModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "acl_group_users"
    auth_id: UUID
    user_id: UUID
    acl_group_id: UUID
    acl: UserACL = Field(default=UserACL.ro)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @classmethod
    async def save_to_supabase(
        cls, supabase: AsyncClient, instance, on_conflict=["user_id", "acl_group_id"]
    ):
        return await super(ACLGroupUsersModel, cls).save_to_supabase(
            supabase, instance, on_conflict
        )

    @classmethod
    async def upsert_to_supabase(
        cls,
        supabase: AsyncClient,
        instances,
        on_conflict=["user_id", "acl_group_id"],
        id_column="acl_group_id",
    ):
        return await super(ACLGroupUsersModel, cls).upsert_to_supabase(
            supabase, instances, on_conflict, id_column
        )

    @classmethod
    async def fetch_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="acl_group_id"
    ):
        return await super(ACLGroupUsersModel, cls).fetch_from_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value=None, id_column="acl_group_id"
    ):
        return await super(ACLGroupUsersModel, cls).exists_in_supabase(
            supabase, value=value, id_column=id_column
        )

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value=None, id_column="acl_group_id"
    ):
        return await super(ACLGroupUsersModel, cls).delete_from_supabase(
            supabase, value=value, id_column=id_column
        )


class ACLGroupUsersWithItems(BaseModel):
    organization_id: Optional[UUID] = Field(default=None)
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
