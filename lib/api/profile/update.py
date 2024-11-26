from supabase import AsyncClient
from lib.models.supabase.organization import UserProfileModel


async def update_user_profile(
    supabase: AsyncClient,
    user_profile: UserProfileModel,
) -> UserProfileModel:
    """
    Update a user profile's details in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        user_profile (UserProfileModel): User profile data.

    Returns:
        UserProfileModel: The updated user profile.

    Raises:
        ValueError: If the user profile is not found.
    """
    if user_profile.auth_id is not None:
        existing_profile = await UserProfileModel.fetch_from_supabase(
            supabase,
            value=user_profile.auth_id,
            id_column="auth_id",
        )
    elif user_profile.id is not None:
        existing_profile = await UserProfileModel.fetch_from_supabase(
            supabase,
            value=user_profile.id,
            id_column="id",
        )
    if not existing_profile:
        raise ValueError("User profile not found")

    # Update the user profile model with new data
    update_data = user_profile.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_profile, key, value)

    # Save the updated user profile using update
    return await existing_profile.update(supabase)
