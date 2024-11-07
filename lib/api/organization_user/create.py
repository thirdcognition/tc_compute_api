from typing import Dict, Optional
from supabase.client import AsyncClient
from supabase_auth.types import UserResponse, AdminUserAttributes
from pydantic import UUID4, BaseModel
from postgrest import APIResponse

from app.core.supabase import get_supabase_service_client
from lib.models.supabase.organization import (
    OrganizationUsersModel,
)


class CreateOrganizationUserRequestData(BaseModel):
    email: Optional[str] = None
    auth_id: Optional[UUID4] = None
    metadata: Optional[Dict] = None
    is_admin: bool = False


async def create_organization_user(
    supabase: AsyncClient,
    organization_id: UUID4,
    request_data: CreateOrganizationUserRequestData,
) -> OrganizationUsersModel:
    """
    Add a user to an organization in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.
        request_data (CreateOrganizationUserRequestData): User data.

    Raises:
        ValueError: If neither email nor auth_id is provided.
        ValueError: If the user is already a member of the organization.
    """
    print(f"{request_data=}")
    # Check if the user already exists
    if request_data.email is not None:
        user_data: APIResponse = (
            await supabase.table("user_profile")
            .select("*")
            .eq("email", request_data.email)
            .limit(1)
            .execute()
        )
    elif request_data.auth_id is not None:
        user_data: APIResponse = (
            await supabase.table("auth.users")
            .select("*")
            .eq("id", request_data.auth_id)
            .execute()
        )
    else:
        raise ValueError("Either email or auth_id must be provided")

    print(f"{user_data=}")

    if user_data.data or (user_data.count and user_data.count > 0):
        if request_data.auth_id is None:
            auth_id = user_data.data[0]["auth_id"]
        else:
            auth_id = request_data.auth_id
        # Check if the user is already a member of the organization
        member_data: APIResponse = (
            await supabase.table("organization_users")
            .select("*")
            .eq("auth_id", auth_id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )
        if member_data.data or (member_data.count and member_data.count > 0):
            # If the user is already a member of the organization, return the existing member
            raise ValueError("User is already a member of the organization")
        else:
            # If the user is not a member of the organization, add them as a member

            organization_user = OrganizationUsersModel(
                auth_id=auth_id,
                organization_id=organization_id,
                is_admin=request_data.is_admin,
                user_id=user_data.data[0]["id"],
            )
            await organization_user.save_to_supabase(supabase)
            return organization_user
    else:
        service_client: AsyncClient = await get_supabase_service_client()
        resp: UserResponse = await service_client.auth.admin.create_user(
            AdminUserAttributes(
                email=request_data.email,
                email_confirm=True,
                data={
                    "organization_id": organization_id,
                    "is_admin": request_data.is_admin,
                },
            )
        )
        member_data: APIResponse = (
            await supabase.table("organization_users")
            .select("*")
            .eq("auth_id", resp.user.id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )
        organization_user = OrganizationUsersModel(**member_data.data[0])
        return organization_user
