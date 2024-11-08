import json
from datetime import datetime
from typing import List, Optional
import uuid
from lib.models.supabase.journey import JourneyItemType
from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, Json, field_validator  # Changed UUID to UUID
from supabase.client import AsyncClient


class JourneyTemplateModel(SupabaseModel):
    TABLE_NAME: str = "journey_template"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    current_version_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase)

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, self.id)

    @classmethod
    async def from_json(cls, data: dict, supabase: AsyncClient):
        # Extract the ID from the provided data
        existing_id = data.get("id")

        # Check if JourneyTemplateModel exists
        journey_template = cls(id=existing_id)
        if await journey_template.exists_in_supabase(supabase):
            journey_template = await journey_template.fetch_from_supabase(supabase)
            # Fetch the current version of JourneyTemplateVersionModel
            journey_template_version = (
                await JourneyTemplateVersionModel.fetch_current_version(
                    journey_template.current_version_id, supabase
                )
            )
        else:
            # Generate a new UUID for the template version using the existing ID
            template_version_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_version_{existing_id}"
            )

            # Save the new journey template to Supabase
            await journey_template.save_to_supabase(supabase)

            # Create a new JourneyTemplateVersionModel instance
            journey_template_version = (
                await JourneyTemplateVersionModel.create_new_version(
                    template_version_id, existing_id, data, supabase
                )
            )

            journey_template.current_version_id = template_version_id
            await journey_template.save_to_supabase(supabase)

        # Create or fetch JourneyTemplateItemModel instances
        items = await JourneyTemplateItemModel.create_or_fetch_items(data, supabase)

        # Create or fetch JourneyTemplateStructureModel instances
        structures = await JourneyTemplateStructureModel.create_or_fetch_structures(
            data, journey_template.current_version_id, supabase
        )

        return journey_template, journey_template_version, items, structures


class JourneyTemplateVersionModel(SupabaseModel):
    TABLE_NAME: str = "journey_template_version"
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
    async def fetch_current_version(cls, version_id: UUID, supabase: AsyncClient):
        version = cls(id=version_id)
        if await version.exists_in_supabase(supabase):
            return await version.fetch_from_supabase(supabase)
        return None

    @classmethod
    async def create_new_version(
        cls, version_id: UUID, template_id: UUID, data: dict, supabase: AsyncClient
    ):
        version = cls(
            id=version_id,
            template_id=template_id,
            name=data.get("title"),
            description=data.get("description"),
            version_of_id=template_id,
        )
        await version.save_to_supabase(supabase)
        return version


class JourneyTemplateItemModel(SupabaseModel):
    TABLE_NAME: str = "journey_template_item"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    name: str
    type: Optional[JourneyItemType] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @field_validator("data", mode="before")
    def validate_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @classmethod
    async def create_or_fetch_items(
        cls, data: dict, supabase: AsyncClient
    ) -> List["JourneyTemplateItemModel"]:
        items = []
        nodes = [data]

        while nodes:
            node = nodes.pop()
            item_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_item_{node.get('id')}"
            )
            item = cls(id=item_id, name=node.get("title"))

            if await item.exists_in_supabase(supabase):
                item = await item.fetch_from_supabase(supabase)
            else:
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
                await item.save_to_supabase(supabase)

            items.append(item)
            nodes.extend(node.get("children", []))

        return items


class JourneyTemplateStructureModel(SupabaseModel):
    TABLE_NAME: str = "journey_template_structure"
    id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    template_version_id: UUID  # Changed UUID to UUID
    journey_template_item_id: UUID  # Changed UUID to UUID
    parent_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    previous_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    next_id: Optional[UUID] = Field(default=None)  # Changed UUID to UUID
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @classmethod
    async def create_or_fetch_structures(
        cls, data: dict, template_version_id: UUID, supabase: AsyncClient
    ) -> List["JourneyTemplateStructureModel"]:
        structures = []
        nodes = [(data, None)]

        while nodes:
            node, parent_id = nodes.pop()
            children = node.get("children", [])
            for i, child in enumerate(children):
                structure_id = uuid.uuid5(
                    uuid.NAMESPACE_DNS, f"journey_template_structure_{child.get('id')}"
                )
                structure = cls(
                    id=structure_id,
                    template_version_id=template_version_id,
                    journey_template_item_id=uuid.uuid5(
                        uuid.NAMESPACE_DNS, f"journey_template_item_{child.get('id')}"
                    ),
                )

                if await structure.exists_in_supabase(supabase):
                    structure = await structure.fetch_from_supabase(supabase)
                else:
                    structure.parent_id = parent_id
                    structure.previous_id = (
                        uuid.uuid5(
                            uuid.NAMESPACE_DNS,
                            f"journey_template_item_{children[i - 1].get('id')}",
                        )
                        if i > 0
                        else None
                    )
                    structure.next_id = (
                        uuid.uuid5(
                            uuid.NAMESPACE_DNS,
                            f"journey_template_item_{children[i + 1].get('id')}",
                        )
                        if i < len(children) - 1
                        else None
                    )
                    await structure.save_to_supabase(supabase)

                structures.append(structure)
                nodes.append((child, structure.journey_template_item_id))

        return structures
