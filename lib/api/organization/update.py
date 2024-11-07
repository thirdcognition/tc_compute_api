from typing import Dict, Optional
from pydantic import BaseModel
from supabase import AsyncClient
from postgrest import APIResponse

from lib.models.organization import Organization
from lib.models.supabase.organization import OrganizationsModel


class UpdateOrganizationRequestData(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    metadata: Optional[Dict] = None


async def update_organization(
    supabase: AsyncClient,
    request_data: UpdateOrganizationRequestData,
) -> Organization:
    """
    Update an organization's details in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        request_data (UpdateOrganizationRequestData): Organization update data.

    Returns:
        Organization: The updated organization.

    Raises:
        ValueError: If the organization ID is not provided or the organization is not found.
    """
    if not request_data.id:
        raise ValueError("Organization ID must be defined")

    # Fetch the existing organization
    response: APIResponse = (
        await supabase.table("organizations")
        .select("*")
        .eq("id", request_data.id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise ValueError("Organization not found")

    # Update the organization
    update_data = request_data.model_dump(exclude_unset=True)
    await supabase.table("organizations").update(update_data).eq(
        "id", request_data.id
    ).execute()

    # Fetch the updated organization
    updated_response: APIResponse = (
        await supabase.table("organizations")
        .select("*")
        .eq("id", request_data.id)
        .limit(1)
        .execute()
    )
    updated_organization_data = updated_response.data[0]
    organization_model = OrganizationsModel(**updated_organization_data)
    return Organization(supabase, organization_model)
