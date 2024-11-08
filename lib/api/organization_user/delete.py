from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.organization import OrganizationUsersModel


async def delete_organization_user(
    supabase: AsyncClient,
    organization_id: UUID,
    user_id: UUID,
) -> None:
    """
    Delete an organization user from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization.
        user_id (UUID): The user ID of the user to delete.

    Raises:
        ValueError: If the user_id is not provided.
        ValueError: If the user is not found.
    """
    if user_id is None:
        raise ValueError("user_id must be provided")

    # Initialize the organization user model
    organization_user = OrganizationUsersModel(
        user_id=user_id, organization_id=organization_id
    )

    # Check if the user exists
    if not await organization_user.exists_in_supabase(
        supabase,
        value={"organization_id": organization_id, "user_id": user_id},
        id_field_name="user_id",
    ):
        raise ValueError("User not found")

    # Delete the user using the model's method
    await organization_user.delete_from_supabase(
        supabase,
        value={"organization_id": organization_id, "user_id": user_id},
        id_field_name="user_id",
    )
