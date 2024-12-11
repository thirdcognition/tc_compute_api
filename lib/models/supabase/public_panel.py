from datetime import datetime, time
from typing import ClassVar, Optional, List
from uuid import UUID
from pydantic import Field, Json
from lib.models.supabase.supabase_model import SupabaseModel
from enum import Enum


class ProcessState(str, Enum):
    none = "none"
    waiting = "waiting"
    processing = "processing"
    failed = "failed"
    done = "done"


class PublicPanelAudio(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "public_panel_audio"
    id: UUID
    public_panel_id: UUID
    public_transcript_id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: str = Field(default="public_panels")
    process_state: Optional[ProcessState] = Field(default=None)
    process_fail_message: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)


class PublicPanelDiscussion(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "public_panel_discussion"
    id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)


class PublicPanelTranscript(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "public_panel_transcript"
    id: UUID
    public_panel_id: UUID
    title: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: str = Field(default="public_panels")
    type: Optional[str] = Field(default=None)
    transcript: Optional[Json] = Field(default=None)
    process_state: Optional[ProcessState] = Field(default=None)
    process_fail_message: Optional[str] = Field(default=None)
    metadata: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)


class PublicPanelTranscriptSourceReference(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "public_panel_transcript_source_reference"
    id: UUID
    public_transcript_id: UUID
    source_version_id: UUID
    type: Optional[str] = Field(default=None)
    data: Optional[Json] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    started_at: Optional[time] = Field(default=None)
    completed_at: Optional[time] = Field(default=None)
