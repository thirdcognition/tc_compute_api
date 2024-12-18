# from typing import Dict, Optional
# from pydantic import BaseModel
from supabase import AsyncClient

# from source.models.organization import Organization
from source.models.supabase.organization import OrganizationsModel


async def update_organization(
    supabase: AsyncClient,
    request_data: OrganizationsModel,
) -> OrganizationsModel:
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

    # Fetch the existing organization using fetch_from_supabase
    organization_model = await OrganizationsModel.fetch_from_supabase(
        supabase, request_data.id
    )
    if not organization_model:
        raise ValueError("Organization not found")

    # Update the organization model with new data
    update_data = request_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(organization_model, key, value)

    # Save the updated organization using update
    await organization_model.update(supabase)
    return organization_model
    # return Organization(supabase, organization_model)
