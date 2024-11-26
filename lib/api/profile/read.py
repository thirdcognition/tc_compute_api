from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.organization import UserProfileModel


async def get_user_profile(
    supabase: AsyncClient, auth_id: UUID = None, user_id: UUID = None
) -> UserProfileModel:
    """
    Retrieve a user profile by user ID from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        auth_id (UUID): The user ID of the profile to retrieve.

    Returns:
        UserProfileModel: The retrieved user profile.

    Raises:
        ValueError: If the user profile is not found.
    """
    user_profile: UserProfileModel
    if auth_id:
        user_profile = await UserProfileModel.fetch_from_supabase(
            supabase,
            value=auth_id,
            id_column="auth_id",
        )
    elif user_id:
        user_profile = await UserProfileModel.fetch_from_supabase(
            supabase,
            value=user_id,
            id_column="id",
        )
    if not user_profile:
        raise ValueError("User profile not found")
    return user_profile
