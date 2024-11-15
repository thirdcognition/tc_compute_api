from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel
from supabase import AsyncClient

from lib.models.supabase.organization import OrganizationUsersModel


class UpdateOrganizationUserRequestData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict] = None
    is_admin: Optional[bool] = None


async def update_organization_user(
    supabase: AsyncClient,
    organization_id: UUID,
    request_data: UpdateOrganizationUserRequestData,
) -> OrganizationUsersModel:
    """
    Update an organization user's details in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization.
        request_data (UpdateOrganizationUserRequestData): User update data.

    Returns:
        OrganizationUsersModel: The updated organization user.

    Raises:
        ValueError: If user_id is not provided.
        ValueError: If the user is not found.
    """
    if request_data.user_id is None:
        raise ValueError("User_id must be provided")

    # Fetch the existing user using fetch_from_supabase
    # user_model = OrganizationUsersModel(
    #     user_id=request_data.user_id, organization_id=organization_id
    # )
    user_model = await OrganizationUsersModel.fetch_from_supabase(
        supabase,
        value={"organization_id": organization_id, "user_id": request_data.user_id},
        id_column="user_id",
    )
    if not user_model:
        raise ValueError("User not found")

    # Update the user model with new data
    update_data = request_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_model, key, value)

    # Save the updated user using update
    await user_model.update(supabase)
    return user_model
