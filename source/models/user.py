import asyncio
from app.core.session_storage import SessionStorage, get_storage
from source.models.supabase.organization import (
    OrganizationsModel,
    UserDataModel,
)  # Updated import
from source.models.supabase.organization import (
    OrganizationRoleModel,
    OrganizationTeamModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel,
    UserProfileModel,
)
from source.models.structures.user import UserData, UserAvatarData, UserPreferencesData
from supabase.client import AsyncClient
from uuid import UUID
from typing import Dict, List, Optional
from supabase_auth.types import Session


class User:
    def __init__(self, supabase: AsyncClient, auth_id: str, user_data: UserData = None):
        self.supabase: AsyncClient = supabase
        self.model: UserData = user_data
        self.auth_id = UUID(auth_id)
        self._organization_dict: Dict[UUID, OrganizationsModel] = {}
        self._initialize_task: Optional[asyncio.Task] = None
        self._profile: Optional[UserAvatarData] = None
        self._preferences: Optional[UserPreferencesData] = None

    @property
    def is_initialized(self) -> bool:
        return self._initialize_task is not None and self._initialize_task.done()

    async def initialize(self) -> None:
        if self._initialize_task is None:
            self._initialize_task = asyncio.create_task(self._initialize())
        await self._initialize_task

    async def _initialize(self) -> None:
        if self.model is None:
            self.model = UserData(self.supabase, auth_id=self.auth_id)
        await self.model.fetch_user_profile()
        await self.model.fetch_organizations()

    async def connect_to_organization(
        self,
        organization: OrganizationsModel,
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
    def user_id(self) -> UUID:
        return self.model.profile.id

    @property
    def account_disabled(self) -> bool:
        return self.model.profile.disabled

    @property
    def active_organization_id(self) -> Optional[UUID]:
        return self.model.profile.active_organization_id

    @active_organization_id.setter
    async def set_active_organization(self, organization_id: UUID) -> None:
        if organization_id in self.model.organizations:
            self.model.profile.active_organization_id = organization_id
            await self.model.profile.update(self.supabase)

    @property
    def active_conversation_id(self) -> Optional[UUID]:
        return self.model.profile.active_conversation_id

    @active_conversation_id.setter
    async def set_active_conversation(self, conversation_id: UUID) -> None:
        self.model.profile.active_conversation_id = conversation_id
        await self.model.profile.update(self.supabase)

    @property
    def active_panel_id(self) -> Optional[UUID]:
        return self.model.profile.active_panel_id

    @active_panel_id.setter
    async def set_active_panel(self, panel_id: UUID) -> None:
        self.model.profile.active_panel_id = panel_id
        await self.model.profile.update(self.supabase)

    @property
    def preferences(self) -> UserPreferencesData:
        if not self._preferences:
            self._preferences = UserPreferencesData(
                lang=self.model.profile.lang,
                metadata=self.model.profile.metadata,
                preferences=self.model.profile.preferences,
                payment_details=self.model.profile.payment_details,
            )
        return self._preferences

    @preferences.setter
    async def preferences(self, new_preferences: UserPreferencesData) -> None:
        self.model.profile.lang = new_preferences.lang
        self.model.profile.metadata = new_preferences.metadata
        self.model.profile.preferences = new_preferences.preferences
        self.model.profile.payment_details = new_preferences.payment_details
        await self.model.profile.update(self.supabase)
        self._preferences = new_preferences

    @property
    def avatar(self) -> UserAvatarData:
        if not self._avatar:
            self._avatar = UserAvatarData(
                email=self.model.profile.email,
                name=self.model.profile.name,
                profile_picture=self.model.profile.profile_picture,
            )
        return self._profile

    @avatar.setter
    async def avatar(self, new_profile: UserAvatarData) -> None:
        self.model.profile.email = new_profile.email
        self.model.profile.name = new_profile.name
        self.model.profile.profile_picture = new_profile.profile_picture
        await self.model.profile.update(self.supabase)
        self._profile = new_profile

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
    def organization_user(self) -> Optional[OrganizationUsersModel]:
        return self.model.as_user[self.active_conversation_id]

    @property
    def organization(self) -> Optional[OrganizationsModel]:
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

    @property
    async def user_data(self) -> List[UserDataModel]:
        return await self.model.fetch_user_data()

    async def update_user_data(self, item: UserDataModel):
        await self.model.define_user_data(item)

    async def match_user_data(self, **filters) -> List[UserDataModel]:
        return await self.model.match_user_data(**filters)

    async def _init_organizations(
        self, refresh: bool = False
    ) -> Dict[UUID, OrganizationsModel]:
        if refresh or not self._organization_dict:
            if not self.model.organizations:
                await self.model.fetch_organizations()
            if not self._organization_dict:
                self._organization_dict = {}

            for organization in self.model.organizations:
                self._organization_dict[organization.id] = organization

            for organization_id in list(self._organization_dict.keys()):
                if not any(
                    organization.id == organization_id
                    for organization in self.model.organizations
                ):
                    del self._organization_dict[organization_id]

        return self._organization_dict

    async def get_organization_by_id(
        self, organization_id: UUID
    ) -> Optional[OrganizationsModel]:
        if not self._organization_dict:
            await self._init_organizations()

        return self._organization_dict.get(organization_id)

    # async def fetch_acl_groups(self, refresh: bool = False) -> None:
    #     await self.model.fetch_acl_groups(refresh)

    async def has_access_to_item(self, item_id: UUID, item_type: str) -> bool:
        return await self.model.has_access_to_item(item_id, item_type)


async def get_current_user(supabase: AsyncClient) -> User:
    session: Session = await supabase.auth.get_session()
    session_store: SessionStorage = get_storage(session.access_token)

    user: Optional[User] = session_store.get("user")

    if user is None:
        user = User(supabase, session.user.id)
        session_store.set("user", user)

    if not user.is_initialized:
        await user.initialize()

    return user
