from enum import Enum
from datetime import datetime
import json
from typing import Optional
from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, Json, field_validator


class JourneyModel(SupabaseModel):
    TABLE_NAME: str = "journey"
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


class JourneyVersionModel(SupabaseModel):
    TABLE_NAME: str = "journey_version"
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
        return v


class JourneyItemModel(SupabaseModel):
    TABLE_NAME: str = "journey_item"
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


class JourneyItemType(str, Enum):
    JOURNEY = "journey"
    SECTION = "section"
    MODULE = "module"
    ACTION = "action"


class JourneyItemVersionModel(SupabaseModel):
    TABLE_NAME: str = "journey_item_version"
    id: Optional[UUID] = Field(default=None)
    journey_id: UUID
    template_item_id: Optional[UUID] = Field(default=None)
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
        return v


class JourneyStructureModel(SupabaseModel):
    TABLE_NAME: str = "journey_structure"
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


class JourneyStructureVersionModel(SupabaseModel):
    TABLE_NAME: str = "journey_structure_version"
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
