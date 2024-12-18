from supabase.client import AsyncClient
from source.models.supabase.organization import UserProfileModel


async def create_user_profile(
    supabase: AsyncClient,
    user_profile: UserProfileModel,
) -> UserProfileModel:
    """
    Create a new user profile in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        user_profile (UserProfileModel): User profile data.

    Returns:
        UserProfileModel: The created user profile.
    """
    return await user_profile.create(supabase)
