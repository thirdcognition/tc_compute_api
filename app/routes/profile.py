from fastapi import APIRouter
from app.core.supabase import SupaClientDep
from app.routes.journey import handle_exception
from source.api.profile.read import get_user_profile
from source.api.profile.update import update_user_profile
from source.models.supabase.organization import UserProfileModel

router = APIRouter()


@router.get("/user")
async def api_get_user_profile(
    supabase: SupaClientDep = SupaClientDep,
) -> UserProfileModel:
    try:
        session = await supabase.auth.get_session()
        auth_id = session.user.id
        return await get_user_profile(supabase, auth_id)
    except Exception as e:
        raise handle_exception(e, "User profile not found", 404)


@router.get("/user/{user_id}")
async def api_get_user_profile_by_id(
    user_id: str = None,
    supabase: SupaClientDep = SupaClientDep,
) -> UserProfileModel:
    print(f"{user_id=}")
    try:
        return await get_user_profile(supabase, user_id=user_id)
    except Exception as e:
        raise handle_exception(e, "User profile not found", 404)


@router.put("/user")
async def api_update_user_profile(
    user_profile: UserProfileModel = None,
    supabase: SupaClientDep = SupaClientDep,
) -> UserProfileModel:
    try:
        session = await supabase.auth.get_session()
        auth_id = session.user.id
        user_profile.auth_id = user_profile.auth_id or auth_id
        return await update_user_profile(supabase, user_profile)
    except Exception as e:
        raise handle_exception(e, "Failed to update user profile")


@router.put("/user/{user_id}")
async def api_update_user_profile_by_id(
    user_id: str = None,
    user_profile: UserProfileModel = None,
    supabase: SupaClientDep = SupaClientDep,
) -> UserProfileModel:
    try:
        user_profile.id = user_id
        return await update_user_profile(supabase, user_profile)
    except Exception as e:
        raise handle_exception(e, "Failed to update user profile")
