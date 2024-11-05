from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Any
from lib.models.supabase.supabase_model import SupabaseModel
from pydantic import UUID4, Field, Json
from supabase.client import AsyncClient


class JourneyModel(SupabaseModel):
    id: UUID4 | None = None
    template_id: UUID4
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    current_version_id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey", self.id)


class JourneyVersionModel(SupabaseModel):
    id: UUID4 | None = None
    journey_id: UUID4
    template_version_id: UUID4
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    version_of_id: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_version", self.id)


class JourneyStepModel(SupabaseModel):
    id: UUID4 | None = None
    journey_id: UUID4
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    current_version_id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_step")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_step", self.id)


class JourneyStepVersionModel(SupabaseModel):
    id: UUID4 | None = None
    journey_id: UUID4
    template_step_id: Optional[UUID4] = None
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    data: Optional[dict] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    version_of_id: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_step_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_step_version", self.id
        )


class JourneyStructureModel(SupabaseModel):
    id: UUID4 | None = None
    journey_id: UUID4
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    current_version_id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_structure")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_structure", self.id)


class JourneyStructureVersionModel(SupabaseModel):
    id: UUID4 | None = None
    journey_id: UUID4
    step_id: UUID4
    child_id: Optional[UUID4] = None
    child_journey_id: Optional[UUID4] = None
    next_step_id: Optional[UUID4] = None
    previous_step_id: Optional[UUID4] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    owner_id: Optional[UUID4] = None
    organization_id: UUID4
    version_of_id: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_structure_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_structure_version", self.id
        )


class JourneyProgressModel(SupabaseModel):
    id: UUID4 | None = None
    journey_id: UUID4
    journey_version_id: UUID4
    current_step_id: UUID4
    current_step_version_id: UUID4
    progress_percentage: Decimal = Field(..., gt=0, lt=100)
    completed_at: Optional[datetime]
    created_at: Optional[datetime]
    owner_id: Optional[UUID4]
    organization_id: UUID4
    state: Literal["active", "ended", "paused"]

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_progress")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_progress", self.id)


class JourneyProgressLLMConversationMessagesModel(SupabaseModel):
    step_progress_id: UUID4
    message_id: UUID4
    created_at: Optional[datetime]
    owner_id: Optional[UUID4]
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(
            supabase,
            "journey_progress_llm_conversation_messages",
            ["step_progress_id", "message_id"],
        )

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase,
            "journey_progress_llm_conversation_messages",
            {"step_progress_id": self.step_progress_id, "message_id": self.message_id},
        )


class JourneyProgressLLMConversationsModel(SupabaseModel):
    progress_id: UUID4
    conversation_id: UUID4
    created_at: Optional[datetime]
    owner_id: Optional[UUID4]
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
            "journey_progress_llm_conversation_messages",
            {"progress_id": self.progress_id, "conversation_id": self.conversation_id},
        )


class JourneyStepProgressModel(SupabaseModel):
    id: UUID4 | None = None
    journey_progress_id: UUID4
    journey_step_id: UUID4
    journey_step_version_id: UUID4
    progress_percentage: Decimal = Field(..., gt=0, lt=100)
    state: Literal["active", "ended", "paused"]
    data: Optional[Any]
    created_at: Optional[datetime]
    owner_id: Optional[UUID4]
    organization_id: UUID4

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_step_progress")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_step_progress", self.id
        )


class JourneyTemplateModel(SupabaseModel):
    id: UUID4 | None = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    current_version_id: Optional[UUID4] = None
    updated_at: Optional[datetime] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(supabase, "journey_template", self.id)


class JourneyTemplateStepModel(SupabaseModel):
    id: UUID4 | None = None
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    prompt: Optional[str] = None
    data: Optional[Json] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template_step")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_template_step", self.id
        )


class JourneyTemplateStructureModel(SupabaseModel):
    id: UUID4 | None = None
    template_version_id: UUID4
    step_id: UUID4
    parent_id: Optional[UUID4] = None
    child_id: Optional[UUID4] = None
    child_journey_id: Optional[UUID4] = None
    previous_step_id: Optional[UUID4] = None
    next_step_id: Optional[UUID4] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template_structure")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_template_structure", self.id
        )


class JourneyTemplateVersionModel(SupabaseModel):
    id: UUID4 | None = None
    template_id: UUID4
    name: str
    description: Optional[str] = None
    disabled: bool = False
    disabled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    version_of_id: Optional[UUID4] = None

    async def save_to_supabase(self, supabase: AsyncClient):
        await super().save_to_supabase(supabase, "journey_template_version")

    async def fetch_from_supabase(self, supabase: AsyncClient):
        return await super().fetch_from_supabase(
            supabase, "journey_template_version", self.id
        )
