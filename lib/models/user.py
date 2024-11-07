import asyncio
from app.core.session_storage import SessionStorage, get_storage
from lib.models.organization import Organization
from lib.models.supabase.organization import (
    OrganizationRoleModel,
    OrganizationTeamModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel,
    UserProfileModel,
)
from lib.models.data.user import UserData
from supabase.client import AsyncClient
from pydantic import UUID4
from typing import Dict, List, Optional
from supabase_auth.types import Session


class User:
    def __init__(self, supabase: AsyncClient, auth_id: str, user_data: UserData = None):
        self.supabase: AsyncClient = supabase
        self.model: UserData = user_data
        self.auth_id = UUID4(auth_id)
        self._organization_dict: Dict[UUID4, Organization] = {}
        self._initialize_task: Optional[asyncio.Task] = None

    @property
    def is_initialized(self) -> bool:
        return self._initialize_task is not None and self._initialize_task.done()

    async def initialize(self) -> None:
        if self._initialize_task is None:
            self._initialize_task = asyncio.create_task(self._initialize())
        await self._initialize_task

    async def _initialize(self) -> None:
        if self.model is None:
            self.model = UserData(auth_id=self.auth_id)
        await self.model.fetch_user_profile()
        await self.model.fetch_organizations()

    async def connect_to_organization(
        self,
        organization: Organization,
        set_as_admin: bool = None,
        update_existing: bool = False,
    ) -> None:
        if self.model.as_user is None:
            await self.model.fetch_as_user()

        is_member = organization.id in self.model.as_user
        if is_member:
            if set_as_admin is not None and update_existing:
                self.model.as_user[organization.id].is_admin = set_as_admin
        else:
            if set_as_admin is None:
                set_as_admin = False
            self.model.as_user[organization.id] = OrganizationUsersModel(
                auth_id=self.model.auth_id,
                organization_id=organization.id,
                is_admin=set_as_admin,
            )
        self.model.save_all_to_supabase(self.supabase)

    @property
    def user_id(self) -> UUID4:
        return self.model.profile.id

    @property
    def account_disabled(self) -> bool:
        return self.model.profile.disabled

    @property
    def active_organization_id(self) -> Optional[UUID4]:
        return self.model.profile.active_organization_id

    @active_organization_id.setter
    async def set_active_organization(self, organization_id: UUID4) -> None:
        if organization_id in self.model.organizations:
            self.model.profile.active_organization_id = organization_id
            await self.model.profile.save_to_supabase(self.supabase)

    @property
    def active_conversation_id(self) -> Optional[UUID4]:
        return self.model.profile.active_conversation_id

    @active_conversation_id.setter
    async def set_active_conversation(self, conversation_id: UUID4) -> None:
        self.model.profile.active_conversation_id = conversation_id
        await self.model.profile.save_to_supabase(self.supabase)

    @property
    def organization_access_disabled(self) -> bool:
        return self.model.as_user[self.active_organization_id].disabled

    @property
    def is_admin(self) -> bool:
        return self.model.as_user[self.active_organization_id].is_admin

    @property
    def profile(self) -> UserProfileModel:
        return self.model.profile

    @property
    def organization(self) -> Optional[Organization]:
        return self.get_organization_by_id(self.active_organization_id)

    @property
    def teams(self) -> List[OrganizationTeamModel]:
        return self.model.get_teams_by_organization(self.active_organization_id)

    @property
    def roles(self) -> List[OrganizationRoleModel]:
        return self.model.get_roles_by_organization(self.active_organization_id)

    @property
    def memberships(self) -> List[OrganizationTeamMembersModel]:
        return self.model.get_memberships_by_organization(self.user_id)

    async def _init_organizations(
        self, refresh: bool = False
    ) -> Dict[UUID4, Organization]:
        """
        Create or refresh Organization instances from the items stored in self.organizations.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The dictionary of Organization instances, keyed by organization ID
        :rtype: Dict[UUID4, Organization]
        """
        if refresh or not self._organization_dict:
            if not self.model.organizations:
                await self.model.fetch_organizations()
            if not self._organization_dict:
                self._organization_dict = {}

            # Create new instances for organizations that don't exist in the dictionary
            for organization in self.model.organizations:
                if organization.id not in self._organization_dict:
                    self._organization_dict[organization.id] = Organization(
                        self.supabase, organization
                    )

            # Remove instances for organizations that no longer exist
            for organization_id in list(self._organization_dict.keys()):
                if not any(
                    organization.id == organization_id
                    for organization in self.model.organizations
                ):
                    del self._organization_dict[organization_id]

            # Refresh data for existing instances
            for organization in self.model.organizations:
                self._organization_dict[organization.id].refresh_model(organization)
        return self._organization_dict

    async def get_organization_by_id(
        self, organization_id: UUID4
    ) -> Optional[Organization]:
        """
        Get an Organization instance by its ID.

        :param organization_id: The ID of the organization
        :type organization_id: UUID4
        :return: The Organization instance, or None if not found
        :rtype: Optional[Organization]
        """
        if not self._organization_dict:
            await self._init_organizations()

        return self._organization_dict.get(organization_id)


async def get_current_user(supabase: AsyncClient) -> User:
    """
    Fetches the current user from the session storage or initializes a new one if not found.

    Args:
        supabase (AsyncClient): The Supabase client instance.

    Returns:
        User: The current user.
    """
    session: Session = await supabase.auth.get_session()
    session_store: SessionStorage = get_storage(session.access_token)

    user: Optional[User] = session_store.get("user")

    if user is None:
        user = User(supabase, session.user.id)
        session_store.set("user", user)

    if not user.is_initialized:
        await user.initialize()

    return user
