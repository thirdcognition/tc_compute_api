from pydantic import UUID4
from supabase import AsyncClient
from postgrest import APIResponse


async def delete_organization(supabase: AsyncClient, organization_id: UUID4) -> None:
    """
    Delete an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization to delete.

    Raises:
        ValueError: If the organization is not found.
    """
    # Check if the organization exists
    response: APIResponse = (
        await supabase.table("organizations")
        .select("*")
        .eq("id", organization_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise ValueError("Organization not found")

    # Delete the organization
    await supabase.table("organizations").delete().eq("id", organization_id).execute()
