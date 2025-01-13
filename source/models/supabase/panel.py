from datetime import datetime
from enum import Enum
from typing import ClassVar, Dict, Optional, List
from uuid import UUID
from pydantic import Field
from source.models.supabase.supabase_model import SupabaseModel


class ProcessState(str, Enum):
    none = "none"
    waiting = "waiting"
    processing = "processing"
    failed = "failed"
    done = "done"


class PanelAudio(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_audio"
    id: Optional[UUID] = Field(default=None)
    panel_id: UUID
    transcript_id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: str = Field(default="public_panels")
    process_state: Optional[ProcessState] = Field(default=None)
    process_fail_message: Optional[str] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)


class PanelDiscussion(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_discussion"
    id: Optional[UUID] = Field(default=None)
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)


class PanelTranscript(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_transcript"
    id: Optional[UUID] = Field(default=None)
    panel_id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: str = Field(default="public_panels")
    type: Optional[str] = Field(default=None)
    transcript: Optional[Dict] = Field(default=None)
    process_state: Optional[ProcessState] = Field(default=None)
    process_fail_message: Optional[str] = Field(default=None)
    generation_interval: Optional[int] = Field(default=None)
    generation_parent: Optional[UUID] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)


class PanelTranscriptOrder(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_transcript_order"
    id: Optional[UUID] = Field(default=None)
    panel_id: UUID
    transcript_id: Optional[UUID] = Field(default=None)
    before_id: Optional[UUID] = Field(default=None)
    after_id: Optional[UUID] = Field(default=None)
    data: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)


class PanelTranscriptSourceReference(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "panel_transcript_source_reference"
    id: Optional[UUID] = Field(default=None)
    transcript_id: UUID
    source_id: UUID
    type: Optional[str] = Field(default=None)
    data: Optional[Dict] = Field(default=None)
    is_public: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)
