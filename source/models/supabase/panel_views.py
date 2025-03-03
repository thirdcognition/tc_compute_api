from typing import ClassVar, Dict, Optional
from uuid import UUID
from pydantic import Field
from datetime import datetime
from source.models.supabase.supabase_model import SupabaseModel


class ViewUserPanelDiscussionModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "view_user_panel_discussion"
    user_data_id: Optional[UUID] = Field(default=None)
    panel_discussion_id: Optional[UUID] = Field(default=None)
    auth_id: Optional[UUID] = Field(default=None)
    title: Optional[str] = Field(default=None)
    tags: Optional[list[str]] = Field(default=None)
    item: Optional[str] = Field(default=None)
    user_data_data: Optional[Dict] = Field(default=None)
    panel_discussion_metadata: Optional[Dict] = Field(default=None)
    user_data_created_at: Optional[datetime] = Field(default=None)
    user_data_updated_at: Optional[datetime] = Field(default=None)


class ViewUserPanelTranscriptModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "view_user_panel_transcript"
    user_data_id: Optional[UUID] = Field(default=None)
    panel_transcript_id: Optional[UUID] = Field(default=None)
    auth_id: Optional[UUID] = Field(default=None)
    item: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    lang: Optional[str] = Field(default=None)
    transcript: Optional[Dict] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    user_data_data: Optional[Dict] = Field(default=None)
    panel_transcript_metadata: Optional[Dict] = Field(default=None)
    user_data_created_at: Optional[datetime] = Field(default=None)
    user_data_updated_at: Optional[datetime] = Field(default=None)


class ViewUserPanelAudioModel(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "view_user_panel_audio"
    user_data_id: Optional[UUID] = Field(default=None)
    panel_audio_id: Optional[UUID] = Field(default=None)
    auth_id: Optional[UUID] = Field(default=None)
    item: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    lang: Optional[str] = Field(default=None)
    file: Optional[str] = Field(default=None)
    bucket_id: Optional[str] = Field(default=None)
    user_data_data: Optional[Dict] = Field(default=None)
    panel_audio_metadata: Optional[Dict] = Field(default=None)
    user_data_created_at: Optional[datetime] = Field(default=None)
    user_data_updated_at: Optional[datetime] = Field(default=None)
