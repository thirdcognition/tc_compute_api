import asyncio
from typing import Dict, List, Optional
from lib.models.supabase.organization import (
    OrganizationRoleModel,
    OrganizationTeamModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel,
    OrganizationsModel,
    UserProfileModel,
)
from lib.models.supabase.acl import (
    ACLGroupUsersModel,
    ACLGroupUsersWithItems,
    ACLGroupModel,
    UserACL,
)
from uuid import UUID
from postgrest import APIResponse
from supabase.client import AsyncClient
from supabase_auth.types import UserResponse, AdminUserAttributes
from app.core.supabase import get_supabase_service_client
from pydantic import BaseModel


class CreateOrganizationUserRequestData(BaseModel):
    email: Optional[str] = None
    auth_id: Optional[UUID] = None
    metadata: Optional[Dict] = None
    is_admin: bool = False


class UserData:
    def __init__(
        self,
        supabase: AsyncClient,
        auth_id: UUID,
        user_data: Optional[UserProfileModel] = None,
    ):
        """
        Initialize a UserData object.

        :param supabase: The Supabase client. Used for making API calls to Supabase.
        :type supabase: AsyncClient
        :param auth_id: The authentication ID of the user. Used to fetch user-specific data.
        :type auth_id: UUID
        :param user_data: The user data, defaults to None. If provided, it is used to initialize the profile attribute.
        :type user_data: Optional[UserProfile], optional
        """
        self.auth_id: UUID = auth_id
        self.supabase: AsyncClient = supabase
        self.profile: Optional[UserProfileModel] = user_data
        # The organizations the user is a part of. Initialized as None and fetched when needed.
        self.organizations: Optional[List[OrganizationsModel]] = None
        # The teams the user is a part of, organized by organization ID. Initialized as None and fetched when needed.
        self.teams: Optional[Dict[UUID, List[OrganizationTeamModel]]] = None
        # The roles the user has in the organizations they are a part of, organized by organization ID. Initialized as None and fetched when needed.
        self.roles: Optional[Dict[UUID, List[OrganizationRoleModel]]] = None
        # The memberships the user has in the teams they are a part of, organized by organization ID. Initialized as None and fetched when needed.
        self.memberships: Optional[
            Dict[UUID, List[OrganizationTeamMembersModel]]
        ] = None
        # The user's relationship with the organizations they are a part of, organized by organization ID. Initialized as None and fetched when needed.
        self.as_user: Optional[Dict[UUID, OrganizationUsersModel]] = None
        # The ACL groups the user is a part of. Initialized as None and fetched when needed.
        self.user_in_acl_group: Optional[List[ACLGroupUsersModel]] = None
        # The ACL group models the user is a part of. Initialized as None and fetched when needed.
        self.acl_group: Optional[List[ACLGroupModel]] = None

    @staticmethod
    async def create_organization_user(
        supabase: AsyncClient,
        organization_id: UUID,
        request_data: CreateOrganizationUserRequestData,
    ) -> OrganizationUsersModel:
        """
        Add a user to an organization in Supabase.

        Args:
            supabase (AsyncClient): The Supabase client.
            organization_id (UUID): The ID of the organization.
            request_data (CreateOrganizationUserRequestData): User data.

        Raises:
            ValueError: If neither email nor auth_id is provided.
            ValueError: If the user is already a member of the organization.
        """

        if not await OrganizationsModel.exists_in_supabase(supabase, organization_id):
            raise ValueError(f"Invalid organization id: {organization_id}")

        service_client: AsyncClient = None
        auth_id = None
        user_profile = None
        # Check if the user already exists
        if request_data.email is not None:
            if await UserProfileModel.exists_in_supabase(
                supabase, request_data.email, id_column="email"
            ):
                user_profile = await UserProfileModel.fetch_from_supabase(
                    supabase, value=request_data.email, id_column="email"
                )
                auth_id = user_profile.auth_id
            else:
                service_client: AsyncClient = (
                    service_client or await get_supabase_service_client()
                )
                user_data = await service_client.rpc(
                    "get_user_id_by_email", {"email": request_data.email}
                ).execute()
                if len(user_data.data) > 0:
                    auth_id = user_data.data[0]["id"]

        elif request_data.auth_id is not None:
            # Check existence directly with the class method using auth_id
            if await UserProfileModel.exists_in_supabase(
                supabase, request_data.auth_id, id_column="auth_id"
            ):
                user_profile: UserProfileModel = (
                    await UserProfileModel.fetch_from_supabase(
                        supabase, value=request_data.auth_id, id_column="auth_id"
                    )
                )
                auth_id = request_data.auth_id
            else:
                service_client: AsyncClient = (
                    service_client or await get_supabase_service_client()
                )
                user_data = await service_client.auth.admin.get_user_by_id(
                    request_data.auth_id
                )
                auth_id = (
                    user_data.user.id
                    if (user_data.user and user_data.user.id)
                    else None
                )
        else:
            raise ValueError("Either email or auth_id must be provided")

        if auth_id:
            # user_profile = await UserProfileModel.fetch_from_supabase(
            #     supabase, request_data.auth_id, id_column="auth_id"
            # )
            if await OrganizationUsersModel.exists_in_supabase(
                supabase,
                value={"auth_id": auth_id, "organization_id": organization_id},
                id_column="auth_id",
            ):
                raise ValueError("User is already a member of the organization")
            else:
                # If the user is not a member of the organization, add them as a member

                organization_user = OrganizationUsersModel(
                    auth_id=auth_id,
                    organization_id=organization_id,
                    is_admin=request_data.is_admin,
                    user_id=user_profile.id if user_profile else None,
                )
                await organization_user.create(supabase)
                return organization_user
        else:
            service_client: AsyncClient = (
                service_client or await get_supabase_service_client()
            )
            resp: UserResponse = await service_client.auth.admin.create_user(
                AdminUserAttributes(
                    email=request_data.email,
                    email_confirm=True,
                    data={
                        "organization_id": organization_id,
                        "is_admin": request_data.is_admin,
                    },
                )
            )

            organization_user = await OrganizationUsersModel.fetch_from_supabase(
                supabase,
                value={"auth_id": resp.user.id, "organization_id": organization_id},
                id_column="auth_id",
            )
            return organization_user

    async def save_all_to_supabase(self, supabase: AsyncClient):
        """
        Save all data to Supabase.

        :param supabase: The Supabase client.
        :type supabase: AsyncClient
        """

        # Separate lists for different model types
        profiles_to_upsert: List[UserProfileModel] = []
        organizations_to_upsert: List[OrganizationsModel] = []
        teams_to_upsert: List[OrganizationTeamModel] = []
        roles_to_upsert: List[OrganizationRoleModel] = []
        memberships_to_upsert: List[OrganizationTeamMembersModel] = []
        users_to_upsert: List[OrganizationUsersModel] = []

        # Collect instances
        if self.profile:
            profiles_to_upsert.append(self.profile)

        if self.organizations:
            organizations_to_upsert.extend(self.organizations)

        if self.teams:
            for teams in self.teams.values():
                teams_to_upsert.extend(teams)

        if self.roles:
            for roles in self.roles.values():
                roles_to_upsert.extend(roles)

        if self.memberships:
            for memberships in self.memberships.values():
                memberships_to_upsert.extend(memberships)

        if self.as_user:
            users_to_upsert.extend(self.as_user.values())

        # Prepare upsert tasks
        upsert_tasks = []

        if profiles_to_upsert:
            upsert_tasks.append(
                profiles_to_upsert[0].upsert_to_supabase(supabase, profiles_to_upsert)
            )

        if organizations_to_upsert:
            upsert_tasks.append(
                organizations_to_upsert[0].upsert_to_supabase(
                    supabase, organizations_to_upsert
                )
            )

        if teams_to_upsert:
            upsert_tasks.append(
                teams_to_upsert[0].upsert_to_supabase(supabase, teams_to_upsert)
            )

        if roles_to_upsert:
            upsert_tasks.append(
                roles_to_upsert[0].upsert_to_supabase(supabase, roles_to_upsert)
            )

        if memberships_to_upsert:
            upsert_tasks.append(
                memberships_to_upsert[0].upsert_to_supabase(
                    supabase, memberships_to_upsert
                )
            )

        if users_to_upsert:
            upsert_tasks.append(
                users_to_upsert[0].upsert_to_supabase(supabase, users_to_upsert)
            )

        # Run all upsert operations concurrently
        await asyncio.gather(*upsert_tasks)

    async def fetch_user_profile(
        self, refresh: bool = False
    ) -> Optional[UserProfileModel]:
        """
        Fetch the user profile from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The user profile
        :rtype: Optional[UserProfile]
        """
        if not self.profile or refresh:
            self.profile = await UserProfileModel.fetch_from_supabase(
                self.supabase, value={"auth_id": str(self.auth_id)}
            )
        return self.profile if self.profile else None

    async def fetch_organizations(
        self, refresh: bool = False
    ) -> List[OrganizationsModel]:
        """
        Fetch the organizations the user is a part of from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The list of organizations the user is a part of
        :rtype: List[Organizations]
        """
        if not self.organizations or refresh:
            response: APIResponse = (
                await self.supabase.from_("organizations")
                .select("*, organization_users(auth_id)")
                .eq("auth_id", str(self.auth_id))
                .execute()
            )
            self.organizations = [OrganizationsModel(**data) for data in response.data]
        return self.organizations

    async def fetch_teams(
        self, refresh: bool = False
    ) -> Dict[UUID, List[OrganizationTeamModel]]:
        """
        Fetch the teams the user is a part of from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The dictionary of teams the user is a part of, organized by organization ID
        :rtype: Dict[UUID, List[OrganizationTeam]]
        """
        if not self.teams or refresh:
            # Fetch organizations if not already fetched
            if not self.organizations:
                await self.fetch_organizations()

            # If organizations are available, fetch teams for each organization
            if self.organizations:
                self.teams = {}
                for organization in self.organizations:
                    self.teams[
                        organization.id
                    ] = await OrganizationTeamModel.fetch_existing_from_supabase(
                        self.supabase,
                        filter={"organization_id": str(organization.id)},
                    )
        return self.teams

    async def fetch_roles(
        self, refresh: bool = False
    ) -> Dict[UUID, List[OrganizationRoleModel]]:
        """
        Fetch the roles the user has in the organizations they are a part of from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The dictionary of roles the user has in the organizations they are a part of, organized by organization ID
        :rtype: Dict[UUID, List[OrganizationRole]]
        """
        if not self.roles or refresh:
            # Fetch organizations if not already fetched
            if not self.organizations:
                await self.fetch_organizations()

            # If organizations are available, fetch roles for each organization
            if self.organizations:
                self.roles = {}
                for organization in self.organizations:
                    self.roles[
                        organization.id
                    ] = await OrganizationRoleModel.fetch_existing_from_supabase(
                        self.supabase,
                        filter={"organization_id": str(organization.id)},
                    )
        return self.roles

    async def fetch_memberships(
        self, refresh: bool = False
    ) -> Dict[UUID, List[OrganizationTeamMembersModel]]:
        """
        Fetch the memberships the user has in the teams they are a part of from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The dictionary of memberships the user has in the teams they are a part of, organized by organization ID
        :rtype: Dict[UUID, List[OrganizationTeamMembers]]
        """
        if not self.memberships or refresh:
            self.memberships = {}
            memberships = (
                await OrganizationTeamMembersModel.fetch_existing_from_supabase(
                    self.supabase, filter={"auth_id": str(self.auth_id)}
                )
            )
            for membership in memberships:
                organization_id = membership.organization_id
                if organization_id not in self.memberships:
                    self.memberships[organization_id] = []
                self.memberships[organization_id].append(membership)
        return self.memberships

    async def fetch_as_user(
        self, refresh: bool = False
    ) -> Dict[UUID, OrganizationUsersModel]:
        """
        Fetch the user's relationship with the organizations they are a part of from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The dictionary of the user's relationship with the organizations they are a part of, organized by organization ID
        :rtype: Dict[UUID, List[OrganizationUsers]]
        """
        if not self.as_user or refresh:
            self.as_user = {}
            users = await OrganizationUsersModel.fetch_existing_from_supabase(
                self.supabase, filter={"auth_id": str(self.auth_id)}
            )
            for user in users:
                organization_id = user.organization_id
                self.as_user[organization_id] = user
        return self.as_user

    async def fetch_acl(self, refresh: bool = False) -> List[ACLGroupUsersModel]:
        """
        Fetch the ACL groups the user is a part of from Supabase.

        :param refresh: Whether to refresh the data from Supabase, defaults to False
        :type refresh: bool, optional
        :return: The list of ACL groups the user is a part of
        :rtype: List[ACLGroupUsersModel]
        """
        if not self.user_in_acl_group or refresh:
            self.user_in_acl_group = (
                await ACLGroupUsersModel.fetch_existing_from_supabase(
                    self.supabase, filter={"auth_id": str(self.auth_id)}
                )
            )
            acl_group_ids = [group.acl_group_id for group in self.user_in_acl_group]
            self.acl_group = await ACLGroupModel.fetch_existing_from_supabase(
                self.supabase, values=acl_group_ids, id_column="id"
            )
        return self.user_in_acl_group

    async def in_acl_group(self, acl_group_id: UUID) -> bool:
        """
        Check if the user is in a specific ACL group.

        :param acl_group_id: The ID of the ACL group
        :type acl_group_id: UUID
        :return: True if the user is in the specified ACL group, False otherwise
        :rtype: bool
        """
        if not self.user_in_acl_group:
            await self.fetch_acl()
        return any(
            group.acl_group_id == acl_group_id for group in self.user_in_acl_group
        )

    async def has_access_to_item(self, item_id: UUID, item_type: str) -> bool:
        """
        Check if the user has access to a specific item based on their ACL groups.

        :param item_id: The ID of the item
        :type item_id: UUID
        :param item_type: The type of the item
        :type item_type: str
        :return: True if the user has access to the item, False otherwise
        :rtype: bool
        """
        return await ACLGroupUsersWithItems.exists_in_supabase(
            self.supabase,
            value={
                "auth_id": str(self.auth_id),
                "item_id": str(item_id),
                "item_type": item_type,
            },
        )

    async def connect_with_acl_group(
        self, organization_id: UUID, acl_group_id: UUID, acl: UserACL
    ) -> None:
        """
        Connect the user to an ACL group with specified ACL level.

        :param acl_group_id: The ID of the ACL group
        :type acl_group_id: UUID
        :param acl: The ACL level
        :type acl: UserACL
        """
        await self.as_user[organization_id].connect_with_acl_group(
            self.supabase, acl_group_id, acl
        )
        await self.fetch_acl(refresh=True)

    async def disconnect_from_acl_group(
        self, organization_id: UUID, acl_group_id: UUID
    ) -> None:
        """
        Connect the user to an ACL group with specified ACL level.

        :param acl_group_id: The ID of the ACL group
        :type acl_group_id: UUID
        :param acl: The ACL level
        :type acl: UserACL
        """
        await self.as_user[organization_id].disconnect_with_acl_group(
            self.supabase, acl_group_id
        )
        await self.fetch_acl(refresh=True)

    async def get_teams_by_organization(
        self, organization_id: UUID
    ) -> List[OrganizationTeamModel]:
        """
        Get the teams the user is a part of in a specific organization.

        :param organization_id: The ID of the organization
        :type organization_id: UUID
        :return: The list of teams the user is a part of in the specified organization
        :rtype: List[OrganizationTeam]
        """
        if not self.teams:
            await self.fetch_teams()
        return self.teams.get(organization_id, [])

    async def get_roles_by_organization(
        self, organization_id: UUID
    ) -> List[OrganizationRoleModel]:
        """
        Get the roles the user has in a specific organization.

        :param organization_id: The ID of the organization
        :type organization_id: UUID
        :return: The list of roles the user has in the specified organization
        :rtype: List[OrganizationRole]
        """
        if not self.roles:
            await self.fetch_roles()
        return self.roles.get(organization_id, [])

    async def get_memberships_by_organization(
        self, organization_id: UUID
    ) -> List[OrganizationTeamMembersModel]:
        """
        Get the memberships the user has in the teams of a specific organization.

        :param organization_id: The ID of the organization
        :type organization_id: UUID
        :return: The list of memberships the user has in the teams of the specified organization
        :rtype: List[OrganizationTeamMembers]
        """
        if not self.memberships:
            await self.fetch_memberships()
        return self.memberships.get(organization_id, [])

    async def in_organization(self, organization_id: UUID) -> bool:
        """
        Check if the user is a part of a specific organization.

        :param organization_id: The ID of the organization
        :type organization_id: UUID
        :return: True if the user is a part of the specified organization, False otherwise
        :rtype: bool
        """
        if not self.organizations:
            await self.fetch_organizations()
        return any(
            organization.id == organization_id for organization in self.organizations
        )

    async def is_admin_in_organization(self, organization_id: UUID) -> bool:
        """
        Check if the user is an admin in a specific organization.

        :param organization_id: The ID of the organization
        :type organization_id: UUID
        :return: True if the user is an admin in the specified organization, False otherwise
        :rtype: bool
        """
        if not self.organizations:
            await self.fetch_organizations()
        if not self.as_user:
            await self.fetch_as_user()

        # Check if the user is the owner of the organization
        if any(
            organization.id == organization_id and organization.owner_id == self.auth_id
            for organization in self.organizations
        ):
            return True

        # Check if the user has the is_admin flag set to True in the OrganizationUsers table
        if organization_id in self.as_user:
            return self.as_user[organization_id].is_admin
        return False
