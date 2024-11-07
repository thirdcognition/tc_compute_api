from typing import Dict, Optional
from pydantic import UUID4, BaseModel
from supabase import AsyncClient
from postgrest import APIResponse

from lib.models.organization import Organization
from lib.models.supabase.organization import OrganizationsModel


class OrganizationRequestData(BaseModel):
    name: str
    website: Optional[str] = None
    logo: Optional[str] = None
    metadata: Optional[Dict] = None


async def create_organization(
    supabase: AsyncClient, request_data: OrganizationRequestData
) -> Organization:
    """
    Create a new organization in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        request_data (OrganizationRequestData): Organization creation data.

    Returns:
        Organization: The created organization.

    Raises:
        ValueError: If an organization already exists with the given name.
    """
    # Get the current user's auth.id
    user = await supabase.auth.get_user()
    owner_id: UUID4 = user.user.id

    # Check if the organization already exists
    response: APIResponse = (
        await supabase.table("organizations")
        .select("*")
        .eq("name", request_data.name)
        .limit(1)
        .execute()
    )
    if response.data:
        # Raise ValueError if the organization already exists
        raise ValueError(
            f"An organization already exists with the name: {request_data.name}"
        )

    # If the organization doesn't exist, create it
    organization_model = OrganizationsModel(
        name=request_data.name,
        website=request_data.website,
        logo=request_data.logo,
        metadata=request_data.metadata,
        owner_id=owner_id,
    )
    await organization_model.save_to_supabase(supabase)
    return Organization(supabase, organization_model)
