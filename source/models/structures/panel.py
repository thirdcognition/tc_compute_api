from datetime import datetime
import os
import json
from typing import Optional, Union, List
from uuid import UUID
from pydantic import BaseModel, Field
from source.models.structures.sources import (
    GoogleNewsConfig,
    YleNewsConfig,
    TechCrunchNewsConfig,
    HackerNewsConfig,
)
from source.load_env import SETTINGS

# Load custom_config from environment variables with defaults
custom_config = {
    "word_count": int(os.getenv("panel_defaults_word_count", 200)),
    "conversation_style": os.getenv(
        "panel_defaults_conversation_style", "casual,humorous"
    ).split(","),
    "podcast_name": SETTINGS.podcast_name,
    "podcast_tagline": SETTINGS.podcast_tagline,
    "creativity": float(os.getenv("panel_defaults_creativity", 0.7)),
}


class HostProfile(BaseModel):
    name: str = ""
    persona: str = ""
    role: str = ""

    def to_string(self) -> str:
        return f"Name: {self.name}, Role: {self.role}, Persona: {self.persona}"


class ConversationConfig(BaseModel):
    output_language: Optional[str] = "English"
    conversation_style: Optional[List[str]] = custom_config["conversation_style"]
    roles_person1: Optional[HostProfile] = None
    roles_person2: Optional[HostProfile] = None
    dialogue_structure: Optional[List[str]] = None
    engagement_techniques: Optional[List[str]] = None
    user_instructions: Optional[str] = None
    podcast_name: Optional[str] = custom_config["podcast_name"]
    podcast_tagline: Optional[str] = custom_config["podcast_tagline"]
    creativity: Optional[float] = custom_config["creativity"]
    word_count: Optional[int] = custom_config["word_count"]
    longform: Optional[bool] = False
    text_to_speech: Optional[dict] = {}
    location: Optional[str] = "Finland"


class PanelRequestData(BaseModel):
    title: str = "New public morning show"
    input_source: Union[str, List[str]] = ""
    input_text: Optional[str] = ""
    tts_model: str = "elevenlabs"
    longform: bool = False
    bucket_name: str = "public_panels"
    display_tag: Optional[str] = ""
    conversation_config: Optional[ConversationConfig] = ConversationConfig()
    panel_id: Optional[UUID] = None
    transcript_parent_id: Optional[str] = None
    transcript_id: Optional[UUID] = None
    google_news: Optional[Union[GoogleNewsConfig, List[GoogleNewsConfig]]] = None
    yle_news: Optional[Union[YleNewsConfig, List[YleNewsConfig]]] = None
    techcrunch_news: Optional[
        Union[TechCrunchNewsConfig, List[TechCrunchNewsConfig]]
    ] = None
    hackernews: Optional[Union[HackerNewsConfig, List[HackerNewsConfig]]] = None
    news_guidance: Optional[str] = None
    news_items: Optional[int] = 5
    segments: Optional[int] = 5
    languages: Optional[list[str]] = None
    cronjob: Optional[str] = None
    owner_id: Optional[str] = None
    organization_id: Optional[str] = None
    is_public: Optional[bool] = True

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


class SummaryReference(BaseModel):
    id: Optional[str]
    title: str
    image: Optional[str] = None
    url: Optional[str] = None
    publish_date: Optional[datetime] = None


class SummarySubject(BaseModel):
    title: str = Field(
        ...,
        title="Title",
        description="Generated title for the transcript.",
        max_length=90,
    )
    description: str = Field(
        ...,
        title="Description",
        description="2-3 sentence description of the subject.",
        max_length=500,
    )
    references: List[str | SummaryReference] = Field(
        ...,
        title="references",
        description="List of IDs of used references as strings",
    )


class TranscriptSummary(BaseModel):
    subjects: List[SummarySubject] = Field(
        ..., title="Subjects", description="An ordered list of subjects/topics covered."
    )
    description: str = Field(
        ...,
        title="Description",
        description="2-3 sentence description of the transcript.",
        max_length=500,
    )
    title: str = Field(
        ...,
        title="Title",
        description="Generated title for the transcript.",
        max_length=90,
    )


class PanelMetadata(BaseModel):
    title: Optional[str] = None
    input_source: Optional[Union[str, List[str]]] = None
    input_text: Optional[str] = None
    tts_model: Optional[str] = None
    longform: Optional[bool] = None
    display_tag: Optional[str] = None
    conversation_config: Optional[ConversationConfig] = None
    google_news: Optional[Union[GoogleNewsConfig, List[GoogleNewsConfig]]] = None
    yle_news: Optional[Union[YleNewsConfig, List[YleNewsConfig]]] = None
    techcrunch_news: Optional[
        Union[TechCrunchNewsConfig, List[TechCrunchNewsConfig]]
    ] = None
    hackernews: Optional[Union[HackerNewsConfig, List[HackerNewsConfig]]] = None
    news_guidance: Optional[str] = None
    news_items: Optional[int] = None
    segments: Optional[int] = None
    languages: Optional[List[str]] = None
    description: Optional[str] = None


class TranscriptMetadata(BaseModel):
    images: Optional[List[str]] = Field(
        ..., title="Images", description="List of image URLs."
    )
    longform: Optional[bool] = Field(
        ..., title="Longform", description="Indicates if it's long-form content."
    )
    subjects: Optional[List[SummarySubject]] = Field(
        ...,
        title="Subjects",
        description="List of subjects with descriptions and references.",
    )
    description: Optional[str] = Field(
        ..., title="Description", description="Summary of the segment's discussion."
    )
    conversation_config: Optional[ConversationConfig] = Field(
        ...,
        title="Conversation Configuration",
        description="Details for panel setup and dialogue.",
    )


# New metadata class for panels


class AudioMetadata(BaseModel):
    tts_model: Optional[str] = None
    conversation_config: Optional[ConversationConfig] = None
