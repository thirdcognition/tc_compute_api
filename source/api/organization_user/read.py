from typing import List, Optional
from uuid import UUID
from supabase import AsyncClient

from source.models.supabase.organization import OrganizationUsersModel


async def get_organization_user(
    supabase: AsyncClient,
    organization_id: UUID,
    user_id: Optional[UUID] = None,
) -> OrganizationUsersModel:
    """
    Retrieve an organization user by their user ID and organization ID from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization.
        user_id (UUID): The user ID of the user.

    Returns:
        OrganizationUsersModel: The retrieved organization user.

    Raises:
        ValueError: If user_id is not provided.
        ValueError: If the user is not found.
    """
    if user_id is None:
        raise ValueError("User_id must be provided")

    # user_model = OrganizationUsersModel(
    #     organization_id=organization_id, user_id=user_id
    # )
    user_model = await OrganizationUsersModel.fetch_from_supabase(
        supabase,
        value={"organization_id": organization_id, "user_id": user_id},
        id_column="user_id",
    )
    if not user_model:
        raise ValueError("User not found")
    return user_model


async def list_organization_users(
    supabase: AsyncClient, organization_id: UUID
) -> List[OrganizationUsersModel]:
    """
    List all users of an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization.

    Returns:
        List[OrganizationUsersModel]: A list of organization users.
    """
    # Fetch all organization users using the model's method
    users = await OrganizationUsersModel.fetch_existing_from_supabase(
        supabase, filter={"organization_id": organization_id}
    )
    return users
