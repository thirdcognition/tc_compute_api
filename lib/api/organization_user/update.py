from typing import Dict, Optional
from pydantic import UUID4, BaseModel
from supabase import AsyncClient
from postgrest import APIResponse

from lib.models.supabase.organization import OrganizationUsersModel


class UpdateOrganizationUserRequestData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict] = None
    is_admin: Optional[bool] = None


async def update_organization_user(
    supabase: AsyncClient,
    organization_id: UUID4,
    request_data: UpdateOrganizationUserRequestData,
) -> OrganizationUsersModel:
    """
    Update an organization user's details in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.
        request_data (UpdateOrganizationUserRequestData): User update data.
        user_id (UUID4): The user ID of the user.
        auth_id (UUID4): The auth ID of the user.

    Returns:
        OrganizationUsersModel: The updated organization user.

    Raises:
        ValueError: If user_id is not provided.
        ValueError: If the user is not found.
    """
    if request_data.user_id is None:
        raise ValueError("User_id must be provided")

    # Fetch the existing user
    query = (
        supabase.table("organization_users")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("user_id", request_data.user_id)
        .limit(1)
    )

    response: APIResponse = await query.execute()
    if not response.data:
        raise ValueError("User not found")

    # Update the user
    update_data = request_data.model_dump(exclude_unset=True)
    update_query = (
        supabase.table("organization_users")
        .update(update_data)
        .eq("organization_id", organization_id)
        .eq("user_id", request_data.user_id)
    )

    await update_query.execute()

    # Fetch the updated user
    updated_response: APIResponse = await query.execute()
    updated_user_data = updated_response.data[0]
    return OrganizationUsersModel(**updated_user_data)
