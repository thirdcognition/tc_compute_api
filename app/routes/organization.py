from typing import List
from fastapi import APIRouter, HTTPException
from app.core.supabase import SupaClientDep
from lib.api.organization.create import OrganizationRequestData, create_organization
from lib.api.organization.read import get_organization, list_organizations
from lib.api.organization.update import (
    UpdateOrganizationRequestData,
    update_organization,
)
from lib.api.organization.delete import delete_organization
from lib.models.organization import Organization
from lib.models.supabase.organization import OrganizationsModel

router = APIRouter()


@router.post("/organization/create")
async def api_create_organization(
    organization: OrganizationRequestData,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    try:
        org: Organization = await create_organization(supabase, organization)
        return org.model
    except ValueError as e:
        if "organization already exists" in str(e):
            raise HTTPException(status_code=409, detail="Organization already exists")
        raise


@router.get("/organization/{organization_id}")
async def api_get_organization(
    organization_id: str,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    org: Organization = await get_organization(supabase, organization_id)
    return org.model


@router.get("/organizations")
async def api_list_organizations(
    supabase: SupaClientDep,
) -> list[OrganizationsModel]:
    orgs = await list_organizations(supabase)
    return [org.model for org in orgs]


@router.put("/organizations")
async def api_bulk_update_organizations(
    organizations_data: List[UpdateOrganizationRequestData],
    supabase: SupaClientDep,
) -> List[OrganizationsModel]:
    updated_organizations = []
    for org_data in organizations_data:
        try:
            org: Organization = await update_organization(supabase, org_data)
            updated_organizations.append(org.model)
        except Exception as e:
            # Log the exception e if needed
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update organization with id {org_data.id}: {str(e)}",
            )
    return updated_organizations


@router.put("/organization")
async def api_update_organization_from_data(
    organization_data: UpdateOrganizationRequestData,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    org: Organization = await update_organization(supabase, organization_data)
    return org.model


@router.put("/organization/{organization_id}")
async def api_update_organization(
    organization_id: str,
    organization_data: UpdateOrganizationRequestData,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    organization_data.id = organization_id
    org: Organization = await update_organization(supabase, organization_data)
    return org.model


@router.delete("/organization/{organization_id}")
async def api_delete_organization(
    organization_id: str,
    supabase: SupaClientDep,
) -> None:
    await delete_organization(supabase, organization_id)


@router.delete("/organization")
async def api_delete_organization_from_data(
    organization_data: UpdateOrganizationRequestData,
    supabase: SupaClientDep,
) -> None:
    await delete_organization(supabase, organization_data.id)
