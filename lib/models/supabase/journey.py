from datetime import datetime
import json
from typing import ClassVar, Optional, List
from lib.models.supabase.journey_template import (
    JourneyItemType,
    JourneyTemplateItemModel,
    JourneyTemplateStructureModel,
    JourneyTemplateVersionModel,
)
from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, Json, field_validator
from supabase.client import AsyncClient
import uuid


class JourneyModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey"
    id: Optional[UUID] = Field(default=None)
    template_id: UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    @classmethod
    async def create_from_template(
        cls,
        supabase: AsyncClient,
        template_version_id: UUID,
        owner_id: UUID,
        organization_id: UUID,
    ):
        # Create a new JourneyModel instance
        journey_id = uuid.uuid4()
        journey = cls(
            id=journey_id,
            template_id=template_version_id,
            owner_id=owner_id,
            organization_id=organization_id,
        )
        await journey.create(supabase)

        # Create a new JourneyVersionModel instance using values from JourneyTemplateVersion
        journey_version = await JourneyVersionModel.create_new_version(
            supabase, journey_id, template_version_id, owner_id, organization_id
        )

        # Create JourneyItemModel and JourneyItemVersionModel instances
        (
            journey_items,
            journey_item_versions,
        ) = await JourneyItemModel.create_items_from_template(
            supabase, journey_id, template_version_id, owner_id, organization_id
        )

        # Create JourneyStructureModel and JourneyStructureVersionModel instances
        (
            journey_structures,
            journey_structure_versions,
        ) = await JourneyStructureModel.create_structures_from_template(
            supabase,
            journey_id,
            template_version_id,
            journey_items,
            owner_id,
            organization_id,
        )

        return (
            journey,
            journey_version,
            journey_items,
            journey_item_versions,
            journey_structures,
            journey_structure_versions,
        )


class JourneyVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_version"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    template_version_id: UUID
    name: str
    description: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    version_of_id: Optional[UUID] = Field(default=None)

    @field_validator("metadata", mode="before")
    def validate_metadata(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v

    @classmethod
    async def create_new_version(
        cls,
        supabase: AsyncClient,
        journey_id: UUID,
        template_version_id: UUID,
        owner_id: UUID,
        organization_id: UUID,
    ):
        # Fetch template version details
        template_version = await JourneyTemplateVersionModel.fetch_current_version(
            supabase, template_version_id
        )

        version_id = uuid.uuid4()
        version = cls(
            id=version_id,
            journey_id=journey_id,
            template_version_id=template_version_id,
            name=template_version.name,
            description=template_version.description,
            owner_id=owner_id,
            organization_id=organization_id,
            version_of_id=journey_id,
        )
        await version.create(supabase)
        return version


class JourneyItemModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_item"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    template_item_id: Optional[UUID] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    @classmethod
    async def create_items_from_template(
        cls,
        supabase: AsyncClient,
        journey_id: UUID,
        template_version_id: UUID,
        owner_id: UUID,
        organization_id: UUID,
    ):
        # Fetch template items and create journey items
        template_items = await JourneyTemplateItemModel.fetch_existing_from_supabase(
            supabase, filter=template_version_id, id_column="template_version_id"
        )

        journey_items = []
        journey_item_versions = []
        for template_item in template_items:
            item_id = uuid.uuid4()
            journey_item = cls(
                id=item_id,
                journey_id=journey_id,
                owner_id=owner_id,
                organization_id=organization_id,
                template_item_id=template_item.id,
            )
            journey_items.append(journey_item)

            # Create corresponding JourneyItemVersionModel
            version_id = uuid.uuid4()
            item_version = JourneyItemVersionModel(
                id=version_id,
                journey_id=journey_id,
                name=template_item.name,
                type=template_item.type,
                data=template_item.data,
                owner_id=owner_id,
                organization_id=organization_id,
                version_of_id=item_id,
            )

            journey_item_versions.append(item_version)

        if journey_items:
            await cls.upsert_to_supabase(supabase, journey_items)
        if journey_item_versions:
            await JourneyItemVersionModel.upsert_to_supabase(
                supabase, journey_item_versions
            )
        return journey_items, journey_item_versions


class JourneyItemVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_item_version"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    name: str
    type: Optional[JourneyItemType] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    version_of_id: Optional[UUID] = Field(default=None)

    @field_validator("metadata", "data", mode="before")
    def validate_json_fields(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class JourneyStructureModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_structure"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    @classmethod
    async def create_structures_from_template(
        cls,
        supabase: AsyncClient,
        journey_id: UUID,
        template_version_id: UUID,
        journey_items: List[JourneyItemModel],
        owner_id: UUID,
        organization_id: UUID,
    ):
        # Fetch template structures and create journey structures
        template_structures = (
            await JourneyTemplateStructureModel.fetch_existing_from_supabase(
                supabase, filter=template_version_id, id_column="template_version_id"
            )
        )
        journey_structures = []
        journey_structure_versions: List[JourneyStructureVersionModel] = []
        journey_item_map = {item.template_item_id: item.id for item in journey_items}
        structure_template_map = {
            item.id: item.template_item_id for item in journey_items
        }

        # Create a map to hold the structure version IDs
        structure_version_map = {}

        for template_structure in template_structures:
            structure_id = uuid.uuid4()
            journey_structure = cls(
                id=structure_id,
                journey_id=journey_id,
                owner_id=owner_id,
                organization_id=organization_id,
            )
            journey_structures.append(journey_structure)

            version_id = uuid.uuid4()
            structure_version = JourneyStructureVersionModel(
                id=version_id,
                journey_id=journey_id,
                journey_item_id=journey_item_map.get(
                    template_structure.journey_template_item_id
                ),
                version_id=structure_id,
                owner_id=owner_id,
                organization_id=organization_id,
                version_of_id=structure_id,
            )

            journey_structure_versions.append(structure_version)

            # Map the structure version ID
            structure_version_map[template_structure.id] = structure_version.id

            journey_structure.current_version_id = structure_version.id

        if journey_structures:
            await cls.upsert_to_supabase(supabase, journey_structures)

        if journey_structure_versions:
            await JourneyItemVersionModel.upsert_to_supabase(
                supabase, journey_structure_versions
            )

        for structure_version in journey_structure_versions:
            template_structure_id = structure_template_map.get(
                structure_version.journey_item_id
            )
            template_structure = next(
                (ts for ts in template_structures if ts.id == template_structure_id),
                None,
            )
            if template_structure:
                structure_version.parent_id = structure_version_map.get(
                    template_structure.parent_id
                )
                structure_version.next_id = structure_version_map.get(
                    template_structure.next_id
                )
                structure_version.previous_id = structure_version_map.get(
                    template_structure.previous_id
                )

        if journey_structure_versions:
            await JourneyItemVersionModel.upsert_to_supabase(
                supabase, journey_structure_versions
            )

        return journey_structures, journey_structure_versions


class JourneyStructureVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_structure_version"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    journey_item_id: UUID
    version_id: UUID
    parent_id: Optional[UUID] = Field(default=None)
    next_id: Optional[UUID] = Field(default=None)
    previous_id: Optional[UUID] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    version_of_id: Optional[UUID] = Field(default=None)
