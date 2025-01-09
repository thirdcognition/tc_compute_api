from enum import Enum
import json
from typing import Dict, List, Optional, Tuple
import uuid
from pydantic import BaseModel, Field, Json, field_validator
from source.helpers.journey import load_journey_template


class JourneyItemType(str, Enum):
    JOURNEY = "journey"
    SECTION = "section"
    MODULE = "module"
    ACTION = "action"


class JourneyTemplateModel(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    name: str
    description: Optional[str] = Field(default=None)
    items: List["JourneyTemplateItemModel"]
    structures: List["JourneyTemplateStructureModel"]

    @classmethod
    async def from_json(
        cls, data: dict = None, template_id: str = None
    ) -> "JourneyTemplateModel":
        if data is None and template_id:
            data = await load_journey_template(template_id)
        elif data is None and template_id is None:
            raise ValueError("Either template_id or data must be defined.")

        template_id = data.get("id")
        items = JourneyTemplateItemModel.items_from_json(data, template_id)
        structures = JourneyTemplateStructureModel.structures_from_json(
            data, template_id
        )
        journey_template = cls(
            id=template_id,
            name=data.get("title"),
            description=data.get("description"),
            items=items,
            structures=structures,
        )

        return journey_template


class JourneyTemplateItemModel(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    template_id: uuid.UUID
    name: str
    type: Optional[JourneyItemType] = Field(default=None)
    data: Optional[Json] = Field(default=None)

    @field_validator("data", mode="before")
    def validate_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v

    @classmethod
    def items_from_json(
        cls, data: dict = None, template_id: uuid.UUID = None
    ) -> List["JourneyTemplateItemModel"]:
        items_to_create: List["JourneyTemplateItemModel"] = []
        nodes = [data]
        while nodes:
            node = nodes.pop()
            item_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_item_{node.get('id')}"
            )
            item = cls(
                id=item_id,
                name=node.get("title"),
                template_id=template_id,
            )
            relevant_data = {
                "end_of_day": node.get("end_of_day"),
                "length_in_days": node.get("length_in_days"),
                "action": node.get("action"),
                "description": node.get("description"),
                "content_instructions": node.get("content_instructions"),
                "icon": node.get("icon"),
            }
            item.type = JourneyItemType(node.get("type")) if node.get("type") else None
            item.data = relevant_data
            items_to_create.append(item)
            nodes.extend(node.get("children", []))
        return items_to_create


class JourneyTemplateStructureModel(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    template_id: uuid.UUID
    template_item_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = Field(default=None)
    previous_id: Optional[uuid.UUID] = Field(default=None)
    next_id: Optional[uuid.UUID] = Field(default=None)

    @classmethod
    def structures_from_json(
        cls, data: Dict, template_id: uuid.UUID
    ) -> List["JourneyTemplateStructureModel"]:
        structures_to_create: List["JourneyTemplateStructureModel"] = []
        nodes: List[Tuple[Dict, Optional[uuid.UUID]]] = [(data, None)]
        while nodes:
            node, parent_id = nodes.pop()
            children = node.get("children", [])
            node_id = uuid.uuid5(
                uuid.NAMESPACE_DNS, f"journey_template_structure_{node.get('id')}"
            )
            new_structure = cls(
                id=node_id,
                template_id=template_id,
                parent_id=parent_id,
                template_item_id=uuid.uuid5(
                    uuid.NAMESPACE_DNS, f"journey_template_item_{node.get('id')}"
                ),
            )
            structures_to_create.append(new_structure)
            for child in children:
                nodes.append((child, node_id))

        # Update sibling relationships
        for structure in structures_to_create:
            parent_id = structure.parent_id
            siblings: List["JourneyTemplateStructureModel"] = [
                s for s in structures_to_create if s.parent_id == parent_id
            ]

            for i, sibling in enumerate(siblings):
                if sibling.id == structure.id:
                    prev_id = siblings[i - 1].id if i > 0 else None
                    next_id = siblings[i + 1].id if i < len(siblings) - 1 else None
                    structure.previous_id = prev_id
                    structure.next_id = next_id

        return structures_to_create
