from typing import List
from fastapi import APIRouter
from app.core.supabase import SupaClientDep
from source.helpers.routes import handle_exception
from source.api.organization.create import create_organization
from source.api.organization.read import get_organization, list_organizations
from source.api.organization.update import (
    update_organization,
)
from source.api.organization.delete import delete_organization
from source.models.supabase.organization import OrganizationsModel

router = APIRouter()


@router.post("/organization/create")
async def api_create_organization(
    organization: OrganizationsModel,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    try:
        org: OrganizationsModel = await create_organization(supabase, organization)
        return org
    except Exception as e:
        if "organization already exists" in str(e):
            raise handle_exception(e, "Failed to create organization", 409)
        raise handle_exception(e, "Failed to create organization")


@router.get("/organization/{organization_id}")
async def api_get_organization(
    organization_id: str,
    supabase: SupaClientDep,
) -> OrganizationsModel:
    try:
        org: OrganizationsModel = await get_organization(supabase, organization_id)
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
            org: OrganizationsModel = await update_organization(supabase, org_data)
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
        org: OrganizationsModel = await update_organization(supabase, organization_data)
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
        org: OrganizationsModel = await update_organization(supabase, organization_data)
        return org
    except Exception as e:
        raise handle_exception(e, "Failed to update organization")


@router.delete("/organization/{organization_id}")
async def api_delete_organization(
    organization_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_organization(supabase, organization_id):
            return {"detail": "Organization deleted successfully"}
        else:
            return {"detail": "Failed to delete organization"}
    except Exception as e:
        raise handle_exception(e, "Failed to delete organization", 404)


@router.delete("/organization")
async def api_delete_organization_from_data(
    organization_data: OrganizationsModel,
    supabase: SupaClientDep,
):
    try:
        if await delete_organization(supabase, organization_data.id):
            return {"detail": "Organization deleted successfully"}
        else:
            return {"detail": "Failed to delete organization"}
    except Exception as e:
        raise handle_exception(e, "Failed to delete organization", 404)
