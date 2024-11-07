from fastapi import APIRouter, HTTPException
from app.core.supabase import SupaClientDep
from lib.api.organization_user.create import (
    CreateOrganizationUserRequestData,
    create_organization_user,
)
from lib.api.organization_user.read import (
    get_organization_user,
    list_organization_users,
)
from lib.api.organization_user.update import (
    UpdateOrganizationUserRequestData,
    update_organization_user,
)
from lib.api.organization_user.delete import delete_organization_user
from lib.models.supabase.organization import OrganizationUsersModel

router = APIRouter()


@router.post("/organization/{organization_id}/user")
async def api_create_organization_user(
    organization_id: str,
    user_data: CreateOrganizationUserRequestData,
    supabase: SupaClientDep,
) -> OrganizationUsersModel:
    try:
        return await create_organization_user(supabase, organization_id, user_data)
    except ValueError as ve:
        if "User is already a member" in str(ve):
            raise HTTPException(status_code=409, detail=str(ve))
        raise HTTPException(500, repr(ve))
    except Exception as e:
        raise HTTPException(500, repr(e))


@router.get("/organization/{organization_id}/user/{user_id}")
async def api_get_organization_user(
    organization_id: str,
    user_id: str,
    supabase: SupaClientDep,
) -> OrganizationUsersModel:
    return await get_organization_user(supabase, organization_id, user_id)


@router.get("/organization/{organization_id}/users")
async def api_list_organization_users(
    organization_id: str,
    supabase: SupaClientDep,
) -> list[OrganizationUsersModel]:
    users = await list_organization_users(supabase, organization_id)
    return users


@router.put("/organization/{organization_id}/users")
async def api_bulk_update_organization_users(
    organization_id: str,
    users_data: list[UpdateOrganizationUserRequestData],
    supabase: SupaClientDep = None,
) -> list[OrganizationUsersModel]:
    updated_users = []
    for user_data in users_data:
        if not hasattr(user_data, "user_id") or not user_data.user_id:
            raise HTTPException(
                status_code=400, detail="Each user_data must have a user_id"
            )
        updated_user = await update_organization_user(
            supabase, organization_id, user_data
        )
        updated_users.append(updated_user)
    return updated_users


@router.put("/organization/{organization_id}/user")
async def api_update_organization_user_from_data(
    organization_id: str,
    user_data: UpdateOrganizationUserRequestData,
    supabase: SupaClientDep,
) -> OrganizationUsersModel:
    # Ensure user_id is part of the user_data
    if not hasattr(user_data, "user_id") or not user_data.user_id:
        raise HTTPException(
            status_code=400, detail="user_id must be provided in user_data"
        )

    return await update_organization_user(supabase, organization_id, user_data)


@router.put("/organization/{organization_id}/user/{user_id}")
async def api_update_organization_user(
    organization_id: str,
    user_id: str,
    user_data: UpdateOrganizationUserRequestData,
    supabase: SupaClientDep,
) -> OrganizationUsersModel:
    user_data.user_id = user_id
    return await update_organization_user(supabase, organization_id, user_data)


@router.delete("/organization/{organization_id}/user/{user_id}")
async def api_delete_organization_user(
    organization_id: str,
    user_id: str,
    supabase: SupaClientDep,
) -> None:
    await delete_organization_user(supabase, organization_id, user_id)


@router.delete("/organization/{organization_id}/user")
async def api_delete_organization_user_from_data(
    organization_id: str,
    user_data: UpdateOrganizationUserRequestData,
    supabase: SupaClientDep,
) -> None:
    await delete_organization_user(supabase, organization_id, user_data.user_id)
