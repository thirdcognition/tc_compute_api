from typing import Dict, List, Optional
from lib.models.organization import Organization
from lib.models.supabase.organization import (
    OrganizationRoleModel,
    OrganizationTeamModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel,
    OrganizationsModel,
    UserProfileModel,
)
from uuid import UUID
from postgrest import APIResponse
from supabase.client import AsyncClient


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
        self._organization_dict: Optional[Dict[UUID, Organization]] = None

    async def save_all_to_supabase(self, supabase: AsyncClient):
        """
        Save all data to Supabase.

        :param supabase: The Supabase client.
        :type supabase: AsyncClient
        """
        if self.profile:
            await self.profile.save_to_supabase(supabase)
        if self.organizations:
            for organization in self.organizations:
                await organization.save_to_supabase(supabase)
        if self.teams:
            for organization_id, teams in self.teams.items():
                for team in teams:
                    await team.save_to_supabase(supabase)
        if self.roles:
            for organization_id, roles in self.roles.items():
                for role in roles:
                    await role.save_to_supabase(supabase)
        if self.memberships:
            for organization_id, memberships in self.memberships.items():
                for membership in memberships:
                    await membership.save_to_supabase(supabase)
        if self.as_user:
            for organization_id, user in self.as_user.items():
                await user.save_to_supabase(supabase)

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
            response: APIResponse = (
                await self.supabase.table("user_profile")
                .select("*")
                .eq("auth_id", str(self.auth_id))
                .execute()
            )
            # Assuming that there is only one profile per auth_id, we can directly assign the first item of the list
            if response.count > 0:
                self.profile = UserProfileModel(**response.data[0])
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
                await self.supabase.from_("organization_users")
                .select("organization_id, organizations(*)")
                .eq("auth_id", str(self.auth_id))
                .execute()
            )
            self.organizations = [
                OrganizationsModel(**data["organizations"]) for data in response.data
            ]
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
                    response: APIResponse = (
                        await self.supabase.table("organization_teams")
                        .select("*")
                        .eq("organization_id", str(organization.id))
                        .execute()
                    )
                    self.teams[organization.id] = [
                        OrganizationTeamModel(**data) for data in response.data
                    ]
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
                    response: APIResponse = (
                        await self.supabase.table("organization_roles")
                        .select("*")
                        .eq("organization_id", str(organization.id))
                        .execute()
                    )
                    self.roles[organization.id] = [
                        OrganizationRoleModel(**data) for data in response.data
                    ]
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
            response: APIResponse = (
                await self.supabase.table("organization_team_members")
                .select("*")
                .eq("auth_id", str(self.auth_id))
                .execute()
            )
            self.memberships = {}
            for data in response.data:
                organization_id = data["organization_id"]
                if organization_id not in self.memberships:
                    self.memberships[organization_id] = []
                self.memberships[organization_id].append(
                    OrganizationTeamMembersModel(**data)
                )
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
            response: APIResponse = (
                await self.supabase.table("organization_users")
                .select("*")
                .eq("auth_id", str(self.auth_id))
                .execute()
            )
            self.as_user = {}
            for data in response.data:
                organization_id = data["organization_id"]
                self.as_user[organization_id] = OrganizationUsersModel(**data)
        return self.as_user

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
