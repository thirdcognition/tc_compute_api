from datetime import datetime
import json
from typing import ClassVar, Optional, List, Dict

from source.models.structures.journey_template import (
    JourneyItemType,
    JourneyTemplateModel,
)
from source.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, field_validator
from supabase.client import AsyncClient
import uuid


class JourneyModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey"
    id: Optional[UUID] = Field(default=None)
    template_id: Optional[UUID] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    @classmethod
    async def copy_from(
        cls,
        supabase: AsyncClient,
        journey_id: UUID = None,
        journey_version_id: Optional[UUID] = None,
    ):
        existing_journey = None
        existing_version = None
        if journey_id is not None:
            # Fetch the existing journey
            existing_journey = await cls.fetch_from_supabase(supabase, journey_id)
            if not existing_journey:
                raise ValueError("Journey not found")

            # Determine the version to copy
            journey_version_id = (
                journey_version_id or existing_journey.current_version_id
            )
            if not journey_version_id:
                raise ValueError(
                    "No version specified and no current version available"
                )

        if journey_version_id is not None:
            # Fetch the existing journey version
            existing_version = await JourneyVersionModel.fetch_from_supabase(
                supabase, journey_version_id
            )
            if not existing_version:
                raise ValueError("Journey version not found")

            if existing_journey is None:
                journey_id = existing_version.journey_id

                existing_journey = await cls.fetch_from_supabase(supabase, journey_id)
                if not existing_journey:
                    raise ValueError("Journey not found")

        # Create a new JourneyModel instance
        new_journey_id = uuid.uuid4()
        new_journey = cls(
            id=new_journey_id,
            template_id=existing_journey.template_id,
        )
        await new_journey.create(supabase)

        # Create a new JourneyVersionModel instance
        new_version = await JourneyVersionModel.create_new_version(
            supabase, new_journey_id, old_version=existing_version
        )

        # Copy JourneyItemModel and JourneyItemVersionModel instances
        (
            journey_items,
            journey_item_versions,
            item_map,
        ) = await JourneyItemModel.copy_items_from_journey(
            supabase, new_journey_id, journey_id
        )

        # Copy JourneyStructureModel and JourneyStructureVersionModel instances
        (
            journey_structures,
            journey_structure_versions,
        ) = await JourneyStructureModel.copy_structures_from_journey(
            supabase, new_journey_id, journey_id, item_map
        )

        return (
            new_journey,
            new_version,
            journey_items,
            journey_item_versions,
            journey_structures,
            journey_structure_versions,
        )

    @classmethod
    async def create_from_template(
        cls,
        supabase: AsyncClient,
        template_name: str,
    ):
        template = await JourneyTemplateModel.from_json(template_id=template_name)
        template_id = template.id

        # Create a new JourneyModel instance
        journey_id = uuid.uuid4()
        print(f"{journey_id=} {template_id=}")
        journey = cls(
            id=journey_id,
            template_id=template_id,
        )
        await journey.create(supabase)

        # Create a new JourneyVersionModel instance using values from JourneyTemplateVersion
        journey_version = await JourneyVersionModel.create_new_version(
            supabase, journey_id, template
        )

        # Create JourneyItemModel and JourneyItemVersionModel instances
        (
            journey_items,
            journey_item_versions,
        ) = await JourneyItemModel.create_items_from_template(
            supabase, journey_id, template
        )

        # Create JourneyStructureModel and JourneyStructureVersionModel instances
        (
            journey_structures,
            journey_structure_versions,
        ) = await JourneyStructureModel.create_structures_from_template(
            supabase,
            journey_id,
            template,
            journey_items,
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
    template_id: Optional[UUID] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
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
        template: JourneyTemplateModel = None,
        old_version: "JourneyVersionModel" = None,
    ):
        # Fetch template version details

        version_id = uuid.uuid4()
        version = cls(
            id=version_id,
            journey_id=journey_id,
            template_id=template.id if template else old_version.id,
            name=template.name if template else old_version.name,
            description=template.description if template else old_version.description,
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
    organization_id: Optional[UUID] = Field(default=None)
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    @classmethod
    async def copy_items_from_journey(
        cls,
        supabase: AsyncClient,
        new_journey_id: UUID,
        old_journey_id: UUID,
    ):
        # Fetch existing journey items
        existing_items = await cls.fetch_existing_from_supabase(
            supabase, filter=old_journey_id, id_column="journey_id"
        )
        # Fetch all item versions
        existing_item_versions = (
            await JourneyItemVersionModel.fetch_existing_from_supabase(
                supabase, filter=old_journey_id, id_column="journey_id"
            )
        )

        journey_items: List[JourneyItemModel] = []
        journey_item_versions = []
        item_map = {}
        for existing_item in existing_items:
            # Only copy items that are set in current_version_id
            if existing_item.current_version_id:
                item_id = uuid.uuid4()
                journey_item = cls(
                    id=item_id,
                    journey_id=new_journey_id,
                    template_item_id=existing_item.template_item_id,
                )
                journey_items.append(journey_item)
                item_map[existing_item.id] = item_id

                # Filter the corresponding item version
                item_version = next(
                    (
                        version
                        for version in existing_item_versions
                        if version.id == existing_item.current_version_id
                    ),
                    None,
                )
                if item_version:
                    version_id = uuid.uuid4()
                    new_item_version = JourneyItemVersionModel(
                        id=version_id,
                        journey_id=new_journey_id,
                        name=item_version.name,
                        type=item_version.type,
                        data=item_version.data,
                        version_of_id=item_id,
                    )
                    journey_item_versions.append(new_item_version)

                    # Update the current_version_id in the new journey item
                    # journey_item.current_version_id = version_id
                    item_map[item_version.id] = version_id
                    item_map[item_id] = version_id

        if journey_items:
            await cls.upsert_to_supabase(supabase, journey_items)
        if journey_item_versions:
            await JourneyItemVersionModel.upsert_to_supabase(
                supabase, journey_item_versions
            )
        if journey_items:
            for journey_item in journey_items:
                journey_item.current_version_id = item_map[journey_item.id]

            await cls.upsert_to_supabase(supabase, journey_items)

        return journey_items, journey_item_versions, item_map

    @classmethod
    async def create_items_from_template(
        cls, supabase: AsyncClient, journey_id: UUID, template: JourneyTemplateModel
    ):
        # Fetch template items and create journey items
        template_items = template.items

        journey_items: List[cls] = []
        journey_item_versions: List[JourneyItemVersionModel] = []
        item_map = {}
        for template_item in template_items:
            item_id = uuid.uuid4()
            journey_item = cls(
                id=item_id,
                journey_id=journey_id,
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
                version_of_id=item_id,
            )
            item_map[item_id] = version_id
            journey_item_versions.append(item_version)

        if journey_items:
            await cls.upsert_to_supabase(supabase, journey_items)
        if journey_item_versions:
            await JourneyItemVersionModel.upsert_to_supabase(
                supabase, journey_item_versions
            )
        if journey_items:
            for journey_item in journey_items:
                journey_item.current_version_id = item_map[journey_item.id]
            await cls.upsert_to_supabase(supabase, journey_items)

        return journey_items, journey_item_versions


class JourneyItemVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_item_version"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    name: str
    type: Optional[JourneyItemType] = Field(default=None)
    data: Optional[Dict] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
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
    organization_id: Optional[UUID] = Field(default=None)
    current_version_id: Optional[UUID] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)

    @classmethod
    async def copy_structures_from_journey(
        cls,
        supabase: AsyncClient,
        new_journey_id: UUID,
        old_journey_id: UUID,
        item_map: Dict[UUID, UUID],
    ):
        # Fetch existing journey structures
        existing_structures = await cls.fetch_existing_from_supabase(
            supabase, filter=old_journey_id, id_column="journey_id"
        )
        # Fetch all structure versions
        existing_structure_versions = (
            await JourneyStructureVersionModel.fetch_existing_from_supabase(
                supabase, filter=old_journey_id, id_column="journey_id"
            )
        )

        journey_structures: List[cls] = []
        journey_structure_versions: List[JourneyStructureVersionModel] = []
        structure_version_map = {}

        for existing_structure in existing_structures:
            # Only copy structures that are set in current_version_id
            if existing_structure.current_version_id:
                structure_id = uuid.uuid4()
                journey_structure = cls(
                    id=structure_id,
                    journey_id=new_journey_id,
                )
                journey_structures.append(journey_structure)
                structure_version_map[existing_structure.id] = structure_id

                # Filter the corresponding structure version
                structure_version = next(
                    (
                        version
                        for version in existing_structure_versions
                        if version.id == existing_structure.current_version_id
                    ),
                    None,
                )
                if structure_version:
                    version_id = uuid.uuid4()
                    new_structure_version = JourneyStructureVersionModel(
                        id=version_id,
                        journey_id=new_journey_id,
                        journey_item_id=item_map.get(structure_version.journey_item_id),
                        journey_item_version_id=item_map.get(
                            structure_version.journey_item_version_id
                        ),
                        version_of_id=structure_id,
                    )
                    journey_structure_versions.append(new_structure_version)

                    # Map the structure version ID
                    structure_version_map[
                        structure_version.id
                    ] = new_structure_version.id

                    # Update the current_version_id in the new journey structure
                    structure_version_map[structure_id] = version_id
                    # journey_structure.current_version_id = version_id

        if journey_structures:
            await cls.upsert_to_supabase(supabase, journey_structures)

        if journey_structure_versions:
            await JourneyStructureVersionModel.upsert_to_supabase(
                supabase, journey_structure_versions
            )

        if journey_structures:
            for journey_structure in journey_structures:
                journey_structure.current_version_id = structure_version_map[
                    journey_structure.id
                ]
            await cls.upsert_to_supabase(supabase, journey_structures)

        # Update parent_id, next_id, and previous_id for the new structure versions
        for structure_version in journey_structure_versions:
            original_version = next(
                (
                    version
                    for version in existing_structure_versions
                    if version.id == structure_version.version_of_id
                ),
                None,
            )
            if original_version:
                structure_version.parent_id = structure_version_map.get(
                    original_version.parent_id
                )
                structure_version.next_id = structure_version_map.get(
                    original_version.next_id
                )
                structure_version.previous_id = structure_version_map.get(
                    original_version.previous_id
                )

        if journey_structure_versions:
            await JourneyStructureVersionModel.upsert_to_supabase(
                supabase, journey_structure_versions
            )

        return journey_structures, journey_structure_versions

    @classmethod
    async def create_structures_from_template(
        cls,
        supabase: AsyncClient,
        journey_id: UUID,
        template: JourneyTemplateModel,
        journey_items: List[JourneyItemModel],
    ):
        # Fetch template structures and create journey structures
        template_structures = template.structures
        journey_structures: List[JourneyStructureModel] = []
        journey_structure_versions: List[JourneyStructureVersionModel] = []
        journey_item_map = {item.template_item_id: item.id for item in journey_items}
        journey_item_version_map = {
            item.template_item_id: item.current_version_id for item in journey_items
        }
        structure_template_map = {
            item.id: item.template_item_id for item in journey_items
        }

        # Create a map to hold the structure version IDs
        structure_version_map = {}
        structure_version_map = {}

        for template_structure in template_structures:
            structure_id = uuid.uuid4()
            journey_structure = cls(
                id=structure_id,
                journey_id=journey_id,
            )
            journey_structures.append(journey_structure)

            version_id = uuid.uuid4()
            structure_version = JourneyStructureVersionModel(
                id=version_id,
                journey_id=journey_id,
                journey_item_id=journey_item_map.get(
                    template_structure.template_item_id
                ),
                journey_item_version_id=journey_item_version_map.get(
                    template_structure.template_item_id
                ),
                version_of_id=structure_id,
            )

            journey_structure_versions.append(structure_version)

            # Map the structure version ID
            structure_version_map[template_structure.id] = structure_version.id
            structure_version_map[journey_structure.id] = structure_version.id

            # journey_structure.current_version_id = structure_version.id

        if journey_structures:
            await cls.upsert_to_supabase(supabase, journey_structures)

        if journey_structure_versions:
            await JourneyStructureVersionModel.upsert_to_supabase(
                supabase, journey_structure_versions
            )

        for structure in journey_structures:
            structure.current_version_id = structure_version_map[journey_structure.id]

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

        if journey_structures:
            await cls.upsert_to_supabase(supabase, journey_structures)

        if journey_structure_versions:
            await JourneyStructureVersionModel.upsert_to_supabase(
                supabase, journey_structure_versions
            )

        return journey_structures, journey_structure_versions


class JourneyStructureVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_structure_version"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    journey_item_id: UUID
    journey_item_version_id: UUID
    parent_id: Optional[UUID] = Field(default=None)
    next_id: Optional[UUID] = Field(default=None)
    previous_id: Optional[UUID] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
    version_of_id: Optional[UUID] = Field(default=None)
