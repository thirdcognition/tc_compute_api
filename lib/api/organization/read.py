from typing import List
from uuid import UUID
from supabase import AsyncClient

from lib.models.organization import Organization
from lib.models.supabase.organization import OrganizationsModel


async def get_organization(
    supabase: AsyncClient, organization_id: UUID
) -> Organization:
    """
    Retrieve an organization by its ID from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization.

    Returns:
        Organization: The retrieved organization.
    """
    print(f"{organization_id=}")
    organization_model = await OrganizationsModel.fetch_from_supabase(
        supabase, organization_id
    )
    if not organization_model:
        raise ValueError("Organization not found")
    return Organization(supabase, organization_model)


async def list_organizations(supabase: AsyncClient) -> List[Organization]:
    """
    List all organizations from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.

    Returns:
        List[Organization]: A list of organizations.
    """
    # Fetch all organizations using the model's method
    organization_model = OrganizationsModel()
    response = await supabase.table(organization_model.TABLE_NAME).select("*").execute()
    organizations = [
        Organization(supabase, OrganizationsModel(**org_data))
        for org_data in response.data
    ]
    return organizations
