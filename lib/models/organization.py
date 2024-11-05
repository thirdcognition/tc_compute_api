from app.core.supabase import get_supabase_service_client
from lib.models.supabase.organization import (
    OrganizationUsersModel,
    OrganizationsModel,
    UserProfileModel,
)
from supabase.client import AsyncClient
from gotrue.types import UserResponse, AdminUserAttributes
from pydantic import UUID4, BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Union
from postgrest import APIResponse

class Organization:
    """
    A class used to represent an Organization.

    Attributes
    ----------
    supabase : AsyncClient
        The Supabase client.
    model : OrganizationsModel
        The organization model.
    """

    def __init__(self, supabase: AsyncClient, organization_model: OrganizationsModel):
        """
        Constructs all the necessary attributes for the organization object.

        Parameters
        ----------
            supabase : AsyncClient
                The Supabase client.
            organization_model : OrganizationsModel
                The organization model.
        """
        self.supabase: AsyncClient = supabase
        self.model: OrganizationsModel = organization_model
    async def refresh_model(self, organization_instance: OrganizationsModel) -> None:
        """
        Refresh the organization data.

        Args:
            organization_instance (OrganizationsModel): The new organization data.
        """
        self.model = organization_instance

    @property
    def id(self) -> UUID4:
        """
        Returns the ID of the organization.

        Returns
        -------
        UUID4
            The ID of the organization.
        """
        return self.model.id

    @property
    def name(self) -> str:
        """
        Returns the name of the organization.

        Returns
        -------
        str
            The name of the organization.
        """
        return self.model.name

    @property
    def website(self) -> Optional[str]:
        """
        Returns the website of the organization.

        Returns
        -------
        Optional[str]
            The website of the organization.
        """
        return self.model.website

    @property
    def disabled(self) -> bool:
        """
        Returns whether the organization is disabled.

        Returns
        -------
        bool
            Whether the organization is disabled.
        """
        return self.model.disabled

    @property
    def disabled_at(self) -> Optional[datetime]:
        """
        Returns the time at which the organization was disabled.

        Returns
        -------
        Optional[datetime]
            The time at which the organization was disabled.
        """
        return self.model.disabled_at

    @property
    def created_at(self) -> datetime:
        """
        Returns the time at which the organization was created.

        Returns
        -------
        datetime
            The time at which the organization was created.
        """
        return self.model.created_at

    @property
    def owner_id(self) -> UUID4:
        """
        Returns the ID of the organization's owner.

        Returns
        -------
        UUID4
            The ID of the organization's owner.
        """
        return self.model.owner_id

    def to_json(self) -> str:
        """
        Convert the organization data into a JSON format.

        Returns
        -------
        Dict
            The organization data in JSON format.
        """
        return self.model.model_dump_json()


async def get_organization(
    supabase: AsyncClient, organization: Union[OrganizationsModel, UUID4]
) -> Organization:
    """
    Retrieve an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization (Union[OrganizationsModel, UUID4]): The organization model or its ID.

    Returns:
        Organization: The retrieved organization.

    Raises:
        ValueError: If the organization type is invalid.
    """
    if isinstance(organization, OrganizationsModel):
        organization_model = organization
    elif isinstance(organization, UUID4):
        # Check if the organization already exists
        response: APIResponse = (
            await supabase.table("organizations")
            .select("*")
            .eq("id", organization)
            .execute()
        )
        if response.data:
            # If the organization already exists, return the existing organization
            organization_data = response.data[0]
            organization_model = OrganizationsModel(**organization_data)
    else:
        raise ValueError("Invalid organization type")

    return Organization(supabase, organization_model)


class OrganizationRequestData(BaseModel):
    name: str
    website: str | None = None

async def create_organization(
    supabase: AsyncClient, request_data: OrganizationRequestData
) -> Organization:
    """
    Create a new organization in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        request_data (OrganizationRequestData): Organization creation data.

    Returns:
        Organization: The created organization.
    """
    # Get the current user's auth.id
    user = await supabase.auth.get_user()
    owner_id:UUID4 = user.user.id

    # Check if the organization already exists
    response: APIResponse = (
        await supabase.table("organizations")
        .select("*")
        .eq("name", request_data.name)
        .limit(1)
        .execute()
    )
    if response.data:
        # If the organization already exists, return the existing organization
        organization_data = response.data[0]
        organization_model = OrganizationsModel(**organization_data)
        return Organization(supabase, organization_model)

    # If the organization doesn't exist, create it
    organization_model = OrganizationsModel(name=request_data.name, website=request_data.website, owner_id=owner_id)
    await organization_model.save_to_supabase(supabase)
    return Organization(supabase, organization_model)


class AddOrganizationUserRequestData(BaseModel):
    email: str | None = None
    auth_id: UUID4 | None = None
    as_admin: bool = False


async def add_organization_user(
    supabase: AsyncClient,
    organization_id: UUID4,
    request_data: AddOrganizationUserRequestData
) -> OrganizationUsersModel:
    """
    Add a user to an organization in Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization_id (UUID4): The ID of the organization.
        request_data (AddOrganizationUserRequestData): User data.

    Raises:
        ValueError: If neither email nor auth_id is provided.
        ValueError: If the user is already a member of the organization.
    """
    print(f"{request_data=}")
    # Check if the user already exists
    if request_data.email is not None:
        user_data: APIResponse = (
            await supabase.table("user_profile")
            .select("*")
            .eq("email", request_data.email)
            .limit(1)
            .execute()
        )
    elif request_data.auth_id is not None:
        user_data: APIResponse = (
            await supabase.table("auth.users").select("*").eq("id", request_data.auth_id).execute()
        )
    else:
        raise ValueError("Either email or auth_id must be provided")

    print(f"{user_data=}")

    if user_data.data or (user_data.count and user_data.count > 0):
        if request_data.auth_id is None:
            auth_id = user_data.data[0]["auth_id"]
        else:
            auth_id = request_data.auth_id
        # Check if the user is already a member of the organization
        member_data: APIResponse = (
            await supabase.table("organization_users")
            .select("*")
            .eq("auth_id", auth_id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )
        if member_data.data or (member_data.count and member_data.count > 0):
            # If the user is already a member of the organization, return the existing member
            raise ValueError("User is already a member of the organization")
        else:
            # If the user is not a member of the organization, add them as a member

            organization_user = OrganizationUsersModel(
                auth_id=auth_id,
                organization_id=organization_id,
                is_admin=request_data.as_admin,
                user_id=user_data.data[0]["id"],
            )
            await organization_user.save_to_supabase(supabase)
            return organization_user
    else:
        service_client: AsyncClient = await get_supabase_service_client()
        resp: UserResponse = await service_client.auth.admin.create_user(
            AdminUserAttributes(
                email=request_data.email,
                email_confirm=True,
                data={"organization_id": organization_id, "is_admin": request_data.as_admin},
            )
        )
        member_data: APIResponse = (
            await supabase.table("organization_users")
            .select("*")
            .eq("auth_id", resp.user.id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )
        organization_user = OrganizationUsersModel(**member_data.data[0])
        return organization_user

