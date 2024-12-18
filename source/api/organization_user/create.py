from supabase.client import AsyncClient
from uuid import UUID
from source.models.data.user import UserData, CreateOrganizationUserRequestData
from source.models.supabase.organization import OrganizationUsersModel


async def create_organization_user(
    supabase: AsyncClient,
    organization_id: UUID,
    request_data: CreateOrganizationUserRequestData,
) -> OrganizationUsersModel:
    print(f"{request_data=}")
    return await UserData.create_organization_user(
        supabase, organization_id, request_data
    )
