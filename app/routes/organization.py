from typing import List
from fastapi import APIRouter
from app.core.supabase import SupaClientDep
from app.routes.journey import handle_exception
from lib.api.organization.create import create_organization
from lib.api.organization.read import get_organization, list_organizations
from lib.api.organization.update import (
    update_organization,
)
from lib.api.organization.delete import delete_organization
from lib.models.organization import Organization
from lib.models.supabase.organization import OrganizationsModel

router = APIRouter()


@router.post("/organization/create")
async def api_create_organization(
    organization: OrganizationsModel,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    # try:
    org: Organization = await create_organization(supabase, organization)
    return org
    # except ValueError as e:
    #     if "organization already exists" in str(e):
    #         raise HTTPException(status_code=409, detail="Organization already exists")
    #     raise handle_exception(e, "Failed to create organization")


@router.get("/organization/{organization_id}")
async def api_get_organization(
    organization_id: str,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    try:
        org: Organization = await get_organization(supabase, organization_id)
        return org
    except Exception as e:
        raise handle_exception(e, "Organization not found", 404)


@router.get("/organizations")
async def api_list_organizations(
    supabase: SupaClientDep,
) -> list[OrganizationsModel]:
    try:
        orgs = await list_organizations(supabase)
        return orgs
        # return [org for org in orgs]
    except Exception as e:
        raise handle_exception(e, "Failed to list organizations")


@router.put("/organizations")
async def api_bulk_update_organizations(
    organizations_data: List[OrganizationsModel],
    supabase: SupaClientDep,
) -> List[OrganizationsModel]:
    updated_organizations = []
    for org_data in organizations_data:
        try:
            org: Organization = await update_organization(supabase, org_data)
            updated_organizations.append(org)
        except Exception as e:
            raise handle_exception(
                e, f"Failed to update organization with id {org_data.id}", 400
            )
    return updated_organizations


@router.put("/organization")
async def api_update_organization_from_data(
    organization_data: OrganizationsModel,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    try:
        org: Organization = await update_organization(supabase, organization_data)
        return org
    except Exception as e:
        raise handle_exception(e, "Failed to update organization")


@router.put("/organization/{organization_id}")
async def api_update_organization(
    organization_id: str,
    organization_data: OrganizationsModel,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    try:
        organization_data.id = organization_id
        org: Organization = await update_organization(supabase, organization_data)
        return org
    except Exception as e:
        raise handle_exception(e, "Failed to update organization")


@router.delete("/organization/{organization_id}")
async def api_delete_organization(
    organization_id: str,
    supabase: SupaClientDep,
) -> None:
    try:
        await delete_organization(supabase, organization_id)
    except Exception as e:
        raise handle_exception(e, "Failed to delete organization", 404)


@router.delete("/organization")
async def api_delete_organization_from_data(
    organization_data: OrganizationsModel,
    supabase: SupaClientDep,
) -> None:
    try:
        await delete_organization(supabase, organization_data.id)
    except Exception as e:
        raise handle_exception(e, "Failed to delete organization", 404)
