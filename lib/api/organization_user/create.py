from typing import Dict, Optional
from supabase.client import AsyncClient
from supabase_auth.types import UserResponse, AdminUserAttributes
from uuid import UUID
from pydantic import BaseModel
from postgrest import APIResponse

from app.core.supabase import get_supabase_service_client
from lib.models.supabase.organization import OrganizationUsersModel
from lib.models.user import UserProfileModel


class CreateOrganizationUserRequestData(BaseModel):
    email: Optional[str] = None
    auth_id: Optional[UUID] = None
    metadata: Optional[Dict] = None
    is_admin: bool = False


async def create_organization_user(
    supabase: AsyncClient,
    organization_id: UUID,
    request_data: CreateOrganizationUserRequestData,
) -> OrganizationUsersModel:
    """
    Add a user to an organization in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization.
        request_data (CreateOrganizationUserRequestData): User data.

    Raises:
        ValueError: If neither email nor auth_id is provided.
        ValueError: If the user is already a member of the organization.
    """
    print(f"{request_data=}")
    # Check if the user already exists
    if request_data.email is not None:
        user_profile = UserProfileModel(email=request_data.email)
        if await user_profile.exists_in_supabase(supabase, id_field_name="email"):
            user_profile = await user_profile.fetch_from_supabase(
                supabase, id_field_name="email"
            )
            auth_id = user_profile.auth_id
    elif request_data.auth_id is not None:
        user_profile = UserProfileModel(auth_id=request_data.auth_id)
        if await user_profile.exists_in_supabase(supabase, id_field_name="auth_id"):
            user_profile = await user_profile.fetch_from_supabase(
                supabase, id_field_name="auth_id"
            )
        else:
            user_data: APIResponse = (
                await supabase.table("auth.users")
                .select("*")
                .eq("id", request_data.auth_id)
                .execute()
            )
            auth_id = (
                user_data[0]["auth_id"]
                if (user_data.count and user_data.count > 0) > 0
                else None
            )
    else:
        raise ValueError("Either email or auth_id must be provided")

    print(f"{user_profile=}")

    if auth_id:
        member_model = OrganizationUsersModel(
            auth_id=auth_id, organization_id=organization_id
        )
        if member_model is not None and await member_model.exists_in_supabase(
            supabase,
            value={"auth_id": auth_id, "organization_id": organization_id},
            id_field_name="auth_id",
        ):
            raise ValueError("User is already a member of the organization")
        else:
            # If the user is not a member of the organization, add them as a member

            organization_user = OrganizationUsersModel(
                auth_id=auth_id,
                organization_id=organization_id,
                is_admin=request_data.is_admin,
                user_id=user_profile.id,
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
        organization_user = OrganizationUsersModel(
            auth_id=resp.user.id, organization_id=organization_id
        )
        organization_user = await organization_user.fetch_from_supabase(
            supabase,
            value={"auth_id": resp.user.id, "organization_id": organization_id},
            id_field_name="auth_id",
        )
        return organization_user
