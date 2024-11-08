from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.organization import OrganizationsModel


async def delete_organization(supabase: AsyncClient, organization_id: UUID) -> None:
    """
    Delete an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID): The ID of the organization to delete.

    Raises:
        ValueError: If the organization is not found.
    """
    # Initialize the organization model
    organization = OrganizationsModel(id=organization_id)

    # Check if the organization exists
    if not await organization.exists_in_supabase(supabase):
        raise ValueError("Organization not found")

    # Delete the organization using the model's method
    await organization.delete_from_supabase(supabase)
