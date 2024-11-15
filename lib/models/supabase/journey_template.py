import json
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Tuple
import uuid
from lib.models.supabase.journey import JourneyItemType
from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, Json, field_validator  # Changed UUID to UUID
from supabase.client import AsyncClient


class JourneyTemplateModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_template"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    current_version_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID

    @classmethod
    async def from_json(cls, supabase: AsyncClient, data: dict) -> Tuple[UUID, UUID]:
        # Extract the ID from the provided data
        existing_id = data.get("id")

        # Check if JourneyTemplateModel exists
        if await cls.exists_in_supabase(supabase, existing_id):
            journey_template = await cls.fetch_from_supabase(supabase, existing_id)
            # Fetch the current version of JourneyTemplateVersionModel
            journey_template_version = (
                await JourneyTemplateVersionModel.fetch_current_version(
                    supabase, journey_template.current_version_id
                )
            )
        else:
            journey_template = cls(id=existing_id)
            # Generate a new UUID for the template version using the existing ID
            template_version_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_version_{existing_id}"
            )

            # Save the new journey template to Supabase
            print(f"{supabase=}")
            await journey_template.create(supabase)

            # Create a new JourneyTemplateVersionModel instance
            journey_template_version = (
                await JourneyTemplateVersionModel.create_new_version(
                    supabase, template_version_id, existing_id, data
                )
            )

            journey_template.current_version_id = template_version_id
            await journey_template.update(supabase)

        # Create or fetch JourneyTemplateItemModel instances
        # items =
        await JourneyTemplateItemModel.create_or_fetch_items(
            supabase, data, journey_template.current_version_id
        )

        # Create or fetch JourneyTemplateStructureModel instances
        # structures =
        await JourneyTemplateStructureModel.create_or_fetch_structures(
            supabase, data, journey_template.current_version_id
        )

        return (
            journey_template.id,
            journey_template_version.id,
        )  # journey_template, journey_template_version, items, structures


class JourneyTemplateVersionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_template_version"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    template_id: UUID  # Changed UUID to UUID
    name: str
    description: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    version_of_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID

    @classmethod
    async def fetch_current_version(cls, supabase: AsyncClient, version_id: UUID):
        if await cls.exists_in_supabase(supabase, version_id):
            # version = cls(id=version_id)
            return await cls.fetch_from_supabase(supabase, version_id)
        return None

    @classmethod
    async def create_new_version(
        cls, supabase: AsyncClient, version_id: UUID, template_id: UUID, data: dict
    ):
        version = cls(
            id=version_id,
            template_id=template_id,
            name=data.get("title"),
            description=data.get("description"),
            version_of_id=template_id,
        )
        await version.create(supabase)
        return version


class JourneyTemplateItemModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_template_item"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    template_version_id: UUID  # Changed UUID to UUID
    name: str
    type: Optional[JourneyItemType] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    # disabled: bool = Field(default=False)
    # disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator("data", mode="before")
    def validate_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v

    @classmethod
    async def create_or_fetch_items(
        cls, supabase: AsyncClient, data: dict, template_version_id: UUID
    ) -> List["JourneyTemplateItemModel"]:
        # Step 1: Fetch existing items using node_ids as values
        existing_items = await cls.fetch_existing_from_supabase(
            supabase,
            filter=template_version_id,
            id_column="template_version_id",
        )

        # Convert existing items into a dictionary for quick lookup
        existing_items_dict = {item.id: item for item in existing_items}

        items_to_create: List["JourneyTemplateItemModel"] = []
        updated_items: List["JourneyTemplateItemModel"] = []

        nodes = [data]
        while nodes:
            node = nodes.pop()
            item_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_item_{node.get('id')}"
            )

            if str(item_id) in existing_items_dict:
                # Update the fields if the item exists
                item = existing_items_dict[str(item_id)]
                relevant_data = {
                    "end_of_day": node.get("end_of_day"),
                    "length_in_days": node.get("length_in_days"),
                    "action": node.get("action"),
                    "description": node.get("description"),
                    "content_instructions": node.get("content_instructions"),
                    "logo": node.get("logo"),
                }
                item.type = (
                    JourneyItemType(node.get("type")) if node.get("type") else None
                )
                item.data = {"item_details": relevant_data}
                updated_items.append(item)
            else:
                # Create a new item if it does not exist
                item = cls(
                    id=item_id,
                    name=node.get("title"),
                    template_version_id=template_version_id,
                )
                relevant_data = {
                    "end_of_day": node.get("end_of_day"),
                    "length_in_days": node.get("length_in_days"),
                    "action": node.get("action"),
                    "description": node.get("description"),
                    "content_instructions": node.get("content_instructions"),
                    "logo": node.get("logo"),
                }
                item.type = (
                    JourneyItemType(node.get("type")) if node.get("type") else None
                )
                item.data = {"item_details": relevant_data}
                items_to_create.append(item)

            nodes.extend(node.get("children", []))

        # Step 2: Persist new items and updated items
        if items_to_create:
            await cls.upsert_to_supabase(supabase, items_to_create)
        if updated_items:
            await cls.upsert_to_supabase(supabase, updated_items)

        # Collect all items
        all_items = items_to_create + updated_items

        return all_items


class JourneyTemplateStructureModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "journey_template_structure"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    template_version_id: UUID  # Changed UUID to UUID
    journey_template_item_id: UUID  # Changed UUID to UUID
    parent_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    previous_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    next_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    async def update_structure(
        self,
        supabase: AsyncClient,
        parent_id: Optional[UUID],
        prev_id: Optional[UUID],
        next_id: Optional[UUID],
        update=True,
    ) -> None:
        self.parent_id = parent_id
        self.previous_id = prev_id
        self.next_id = next_id
        if update:
            await self.update(supabase)

    @classmethod
    async def create_or_fetch_structures(
        cls, supabase: AsyncClient, data: Dict, template_version_id: UUID
    ) -> List["JourneyTemplateStructureModel"]:
        # Step 1: Fetch existing structures using template_version_id
        existing_structures = await cls.fetch_existing_from_supabase(
            supabase, filter=template_version_id, id_column="template_version_id"
        )

        # Convert existing structures into a dictionary for quick lookup
        existing_structures_dict = {
            structure.id: structure for structure in existing_structures
        }

        structures_to_create: List["JourneyTemplateStructureModel"] = []
        updated_structures: List["JourneyTemplateStructureModel"] = []
        nodes: List[Tuple[Dict, Optional[UUID]]] = [(data, None)]

        while nodes:
            node, parent_id = nodes.pop()
            children = node.get("children", [])

            # Determine if the node exists
            node_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_structure_{node.get('id')}"
            )  # Assume each node has a unique identifier or key
            if node_id in existing_structures_dict:
                # If it exists, update the fields
                structure = existing_structures_dict[node_id]

                # Manually update fields
                structure.parent_id = parent_id or structure.parent_id
                updated_structures.append(structure)
            else:
                # Create a new structure
                new_structure = cls(
                    id=uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        f"journey_template_structure_{node.get('id')}",
                    ),
                    template_version_id=template_version_id,
                    parent_id=parent_id,
                    journey_template_item_id=uuid.uuid5(
                        uuid.NAMESPACE_DNS, f"journey_template_item_{node.get('id')}"
                    ),
                )
                structures_to_create.append(new_structure)

            # Add children nodes for processing
            for child in children:
                nodes.append(
                    (child, node_id)
                )  # Pass the node's current ID as parent ID

        # Step 2: Persist new structures and updated structures
        if structures_to_create:
            await cls.upsert_to_supabase(supabase, structures_to_create)

        if updated_structures:
            await cls.upsert_to_supabase(supabase, updated_structures)

        # Collect all structures to handle sibling updates
        all_structures = structures_to_create + updated_structures

        if all_structures:
            await cls.upsert_to_supabase(supabase, all_structures)

        # Update sibling relationships
        for structure in all_structures:
            parent_id = structure.parent_id
            siblings: List["JourneyTemplateStructureModel"] = [
                s for s in all_structures if s.parent_id == parent_id
            ]

            for i, sibling in enumerate(siblings):
                if sibling.id == structure.id:
                    prev_id = siblings[i - 1].id if i > 0 else None
                    next_id = siblings[i + 1].id if i < len(siblings) - 1 else None
                    await sibling.update_structure(
                        supabase, parent_id, prev_id, next_id, False
                    )

        # Final persist after updating sibling relationships if any changes
        if all_structures:
            await cls.upsert_to_supabase(supabase, all_structures)

        return all_structures
