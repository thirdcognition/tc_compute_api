from supabase.client import AsyncClient
from uuid import UUID
from lib.models.data.user import UserData, CreateOrganizationUserRequestData
from lib.models.supabase.organization import OrganizationUsersModel


async def create_organization_user(
    supabase: AsyncClient,
    organization_id: UUID,
    request_data: CreateOrganizationUserRequestData,
) -> OrganizationUsersModel:
    print(f"{request_data=}")
    return await UserData.create_organization_user(
        supabase, organization_id, request_data
    )
