from typing import List, Optional
from pydantic import UUID4
from supabase import AsyncClient
from postgrest import APIResponse

from lib.models.supabase.organization import OrganizationUsersModel


async def get_organization_user(
    supabase: AsyncClient,
    organization_id: UUID4,
    user_id: Optional[UUID4] = None,
) -> OrganizationUsersModel:
    """
    Retrieve an organization user by their user ID and organization ID from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.
        user_id (UUID4): The user ID of the user.

    Returns:
        OrganizationUsersModel: The retrieved organization user.

    Raises:
        ValueError: If user_id is not provided.
        ValueError: If the user is not found.
    """
    if user_id is None:
        raise ValueError("User_id must be provided")

    query = (
        supabase.table("organization_users")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
        .limit(1)
    )

    response: APIResponse = await query.execute()
    if not response.data:
        raise ValueError("User not found")

    user_data = response.data[0]
    return OrganizationUsersModel(**user_data)


async def list_organization_users(
    supabase: AsyncClient, organization_id: UUID4
) -> List[OrganizationUsersModel]:
    """
    List all users of an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.

    Returns:
        List[OrganizationUsersModel]: A list of organization users.
    """
    response: APIResponse = (
        await supabase.table("organization_users")
        .select("*")
        .eq("organization_id", organization_id)
        .execute()
    )
    users = [OrganizationUsersModel(**user_data) for user_data in response.data]
    return users
