from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.organization import UserProfileModel


async def delete_user_profile(
    supabase: AsyncClient,
    auth_id: UUID,
) -> bool:
    """
    Delete a user profile from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        auth_id (UUID): The user ID of the profile to delete.

    Returns:
        bool: True if the profile was deleted, False otherwise.

    Raises:
        ValueError: If the user profile is not found.
    """
    if not await UserProfileModel.exists_in_supabase(supabase, value={"id": auth_id}):
        raise ValueError("User profile not found")

    # Delete the user profile
    return await UserProfileModel.delete_from_supabase(
        supabase,
        value=auth_id,
        id_column="auth_id",
    )
