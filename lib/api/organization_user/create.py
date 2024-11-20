from typing import Dict, Optional
from supabase.client import AsyncClient
from supabase_auth.types import UserResponse, AdminUserAttributes
from uuid import UUID
from pydantic import BaseModel

from app.core.supabase import get_supabase_service_client
from lib.models.supabase.organization import OrganizationUsersModel, OrganizationsModel
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

    if not await OrganizationsModel.exists_in_supabase(supabase, organization_id):
        raise ValueError(f"Invalid organization id: {organization_id}")

    service_client: AsyncClient = None
    auth_id = None
    user_profile = None
    # Check if the user already exists
    if request_data.email is not None:
        if await UserProfileModel.exists_in_supabase(
            supabase, request_data.email, id_column="email"
        ):
            user_profile = await UserProfileModel.fetch_from_supabase(
                supabase, value=request_data.email, id_column="email"
            )
            auth_id = user_profile.auth_id
        else:
            service_client: AsyncClient = (
                service_client or await get_supabase_service_client()
            )
            user_data = await service_client.rpc(
                "get_user_id_by_email", {"email": request_data.email}
            ).execute()
            if len(user_data.data) > 0:
                auth_id = user_data.data[0]["id"]

    elif request_data.auth_id is not None:
        # Check existence directly with the class method using auth_id
        if await UserProfileModel.exists_in_supabase(
            supabase, request_data.auth_id, id_column="auth_id"
        ):
            user_profile: UserProfileModel = await UserProfileModel.fetch_from_supabase(
                supabase, value=request_data.auth_id, id_column="auth_id"
            )
            auth_id = request_data.auth_id
        else:
            service_client: AsyncClient = (
                service_client or await get_supabase_service_client()
            )
            user_data = await service_client.auth.admin.get_user_by_id(
                request_data.auth_id
            )
            auth_id = (
                user_data.user.id if (user_data.user and user_data.user.id) else None
            )
    else:
        raise ValueError("Either email or auth_id must be provided")

    if auth_id:
        # user_profile = await UserProfileModel.fetch_from_supabase(
        #     supabase, request_data.auth_id, id_column="auth_id"
        # )
        if await OrganizationUsersModel.exists_in_supabase(
            supabase,
            value={"auth_id": auth_id, "organization_id": organization_id},
            id_column="auth_id",
        ):
            raise ValueError("User is already a member of the organization")
        else:
            # If the user is not a member of the organization, add them as a member

            organization_user = OrganizationUsersModel(
                auth_id=auth_id,
                organization_id=organization_id,
                is_admin=request_data.is_admin,
                user_id=user_profile.id if user_profile else None,
            )
            await organization_user.create(supabase)
            return organization_user
    else:
        service_client: AsyncClient = (
            service_client or await get_supabase_service_client()
        )
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

        organization_user = await OrganizationUsersModel.fetch_from_supabase(
            supabase,
            value={"auth_id": resp.user.id, "organization_id": organization_id},
            id_column="auth_id",
        )
        return organization_user
