from uuid import UUID
from supabase import AsyncClient
from source.models.supabase.organization import OrganizationsModel


async def delete_organization(supabase: AsyncClient, organization_id: UUID):
    """
    Delete an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization to delete.

    Raises:
        ValueError: If the organization is not found.
    """
    # Initialize the organization model
    # Initialize the organization model with the given ID
    # Check if the organization exists using the class method
    if not await OrganizationsModel.exists_in_supabase(supabase, organization_id):
        raise ValueError("Organization not found")

    # Delete the organization using the model's method
    return await OrganizationsModel.delete_from_supabase(supabase, organization_id)
