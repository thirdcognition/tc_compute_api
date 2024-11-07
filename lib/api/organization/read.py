from typing import List
from pydantic import UUID4
from supabase import AsyncClient
from postgrest import APIResponse

from lib.models.organization import Organization
from lib.models.supabase.organization import OrganizationsModel


async def get_organization(
    supabase: AsyncClient, organization_id: UUID4
) -> Organization:
    """
    Retrieve an organization by its ID from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.

    Returns:
        Organization: The retrieved organization.
    """
    response: APIResponse = (
        await supabase.table("organizations")
        .select("*")
        .eq("id", organization_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        raise ValueError("Organization not found")

    organization_data = response.data[0]
    organization_model = OrganizationsModel(**organization_data)
    return Organization(supabase, organization_model)


async def list_organizations(supabase: AsyncClient) -> List[Organization]:
    """
    List all organizations from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.

    Returns:
        List[Organization]: A list of organizations.
    """
    response: APIResponse = await supabase.table("organizations").select("*").execute()
    organizations = [
        Organization(supabase, OrganizationsModel(**org_data))
        for org_data in response.data
    ]
    return organizations
