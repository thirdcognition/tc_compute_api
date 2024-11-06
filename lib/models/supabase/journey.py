from enum import Enum
from datetime import datetime
from typing import Optional
from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import UUID4, Field, Json
from supabase.client import AsyncClient


class JourneyModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    template_id: UUID4
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    current_version_id: Optional[UUID4] = Field(default=None)
    updated_by: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey", self.id)


class JourneyVersionModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_id: UUID4
    template_version_id: UUID4
    name: str
    description: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    version_of_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_version", self.id)


class JourneyItemModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_id: UUID4
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    current_version_id: Optional[UUID4] = Field(default=None)
    updated_by: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_item")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_item", self.id)


class JourneyItemType(str, Enum):
    JOURNEY = "Journey"
    SECTION = "Section"
    MODULE = "Module"
    ACTION = "Action"


class JourneyItemVersionModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_id: UUID4
    template_item_id: Optional[UUID4] = Field(default=None)
    name: str
    type: Optional[JourneyItemType] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    version_of_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_item_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_item_version", self.id
        )


class JourneyStructureModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_id: UUID4
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    current_version_id: Optional[UUID4] = Field(default=None)
    updated_by: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_structure")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_structure", self.id)


class JourneyStructureVersionModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_id: UUID4
    journey_item_id: UUID4
    version_id: UUID4
    parent_id: Optional[UUID4] = Field(default=None)
    next_id: Optional[UUID4] = Field(default=None)
    previous_id: Optional[UUID4] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    version_of_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_structure_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_structure_version", self.id
        )


class JourneyProgressModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_id: UUID4
    journey_version_id: UUID4
    assigned_at: Optional[datetime] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_progress")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_progress", self.id)


class JourneyProgressLLMConversationMessagesModel(SupabaseModel):
    journey_item_progress_id: UUID4
    message_id: UUID4
    conversation_id: UUID4
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase,
            "journey_progress_llm_conversation_messages",
            ["journey_item_progress_id", "message_id"],
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "journey_progress_llm_conversation_messages",
            {
                "journey_item_progress_id": self.journey_item_progress_id,
                "message_id": self.message_id,
            },
        )


class JourneyProgressLLMConversationsModel(SupabaseModel):
    progress_id: UUID4
    conversation_id: UUID4
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase,
            "journey_progress_llm_conversations",
            ["progress_id", "conversation_id"],
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "journey_progress_llm_conversations",
            {"progress_id": self.progress_id, "conversation_id": self.conversation_id},
        )


class JourneyItemProgressModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    journey_progress_id: UUID4
    journey_item_id: UUID4
    journey_item_version_id: UUID4
    data: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID4] = Field(default=None)
    organization_id: UUID4
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_item_progress")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_item_progress", self.id
        )


class JourneyTemplateModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    current_version_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_template", self.id)


class JourneyTemplateItemModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    name: str
    type: Optional[str] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template_item")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_template_item", self.id
        )


class JourneyTemplateStructureModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    template_version_id: UUID4
    journey_template_item_id: UUID4
    parent_id: Optional[UUID4] = Field(default=None)
    previous_id: Optional[UUID4] = Field(default=None)
    next_id: Optional[UUID4] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template_structure")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_template_structure", self.id
        )


class JourneyTemplateVersionModel(SupabaseModel):
    id: Optional[UUID4] = Field(default=None)
    template_id: UUID4
    name: str
    description: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    version_of_id: Optional[UUID4] = Field(default=None)

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_template_version", self.id
        )
