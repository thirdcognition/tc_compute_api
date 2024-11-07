from pydantic import UUID4
from supabase import AsyncClient
from postgrest import APIResponse


async def delete_organization_user(
    supabase: AsyncClient,
    organization_id: UUID4,
    user_id: UUID4,
) -> None:
    """
    Delete an organization user from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.
        user_id (UUID4): The user ID of the user to delete.

    Raises:
        ValueError: If the user_id is not provided.
        ValueError: If the user is not found.
    """
    if user_id is None:
        raise ValueError("user_id must be provided")

    # Check if the user exists
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

    # Delete the user
    delete_query = (
        supabase.table("organization_users")
        .delete()
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
    )

    await delete_query.execute()
