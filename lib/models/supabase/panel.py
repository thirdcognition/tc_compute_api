from datetime import datetime, time
from typing import ClassVar, Optional, List
from uuid import UUID
from pydantic import Field, Json
from lib.models.supabase.supabase_model import SupabaseModel
from lib.models.supabase.public_panel import ProcessState


class PanelAudio(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_audio"
    id: Optional[UUID] = Field(default=None)
    panel_id: UUID
    transcript_id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: Optional[str] = Field(default=None)
    process_state: Optional[ProcessState] = Field(default=None)
    process_fail_message: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)


class PanelDiscussion(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_discussion"
    id: Optional[UUID] = Field(default=None)
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)


class PanelTranscript(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_transcript"
    id: Optional[UUID] = Field(default=None)
    panel_id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    type: Optional[str] = Field(default=None)
    transcript: Optional[Json] = Field(default=None)
    process_state: Optional[ProcessState] = Field(default=None)
    process_fail_message: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)


class PanelTranscriptOrder(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_transcript_order"
    id: Optional[UUID] = Field(default=None)
    panel_id: UUID
    transcript_id: Optional[UUID] = Field(default=None)
    public_transcript_id: Optional[UUID] = Field(default=None)
    before_id: Optional[UUID] = Field(default=None)
    after_id: Optional[UUID] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID


class PanelTranscriptSourceReference(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_transcript_source_reference"
    id: Optional[UUID] = Field(default=None)
    transcript_id: UUID
    source_version_id: UUID
    type: Optional[str] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: UUID
