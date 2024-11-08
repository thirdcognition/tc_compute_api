from uuid import UUID
from supabase.client import AsyncClient
from datetime import datetime
from typing import Dict, Optional, Union
from postgrest import APIResponse

from lib.models.supabase.organization import (
    OrganizationsModel,
)


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
    def id(self) -> UUID:
        """
        Returns the ID of the organization.

        Returns
        -------
        UUID
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
    def logo(self) -> Optional[str]:
        """
        Returns the logo of the organization.

        Returns
        -------
        Optional[str]
            The logo of the organization.
        """
        return self.model.logo

    @property
    def metadata(self) -> Optional[Dict]:
        """
        Returns the metadata of the organization.

        Returns
        -------
        Optional[Dict]
            The metadata of the organization.
        """
        return self.model.metadata

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
    def owner_id(self) -> Optional[UUID]:
        """
        Returns the ID of the organization's owner.

        Returns
        -------
        Optional[UUID]
            The ID of the organization's owner.
        """
        return self.model.owner_id

    def to_json(self) -> str:
        """
        Convert the organization data into a JSON format.

        Returns
        -------
        str
            The organization data in JSON format.
        """
        return self.model.model_dump_json()


async def get_organization(
    supabase: AsyncClient, organization: Union[OrganizationsModel, UUID]
) -> Organization:
    """
    Retrieve an organization from Supabase.

    Args:
        supabase (AsyncClient): The Supabase client.
        organization (Union[OrganizationsModel, UUID]): The organization model or its ID.

    Returns:
        Organization: The retrieved organization.

    Raises:
        ValueError: If the organization type is invalid.
    """
    if isinstance(organization, OrganizationsModel):
        organization_model = organization
    elif isinstance(organization, UUID):
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
