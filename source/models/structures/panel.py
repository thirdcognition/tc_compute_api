from datetime import datetime
from enum import Enum
import os
import json
from typing import Dict, Optional, Union, List
from uuid import UUID
from pydantic import BaseModel, Field

# Import TTSConfig from the new library
from transcript_to_audio.schemas import TTSConfig, SpeakerConfig
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
    voice_config: Optional[Dict[str, SpeakerConfig]] = None

    def to_string(self) -> str:
        return f"Name: {self.name}, Role: {self.role}, Persona: {self.persona}"


class OutputLanguageOptions(Enum):
    en = "English"
    fi = "Finnish"
    sv = "Swedish"
    da = "Danish"
    de = "German"
    fr = "French"
    nl = "Dutch"
    es = "Spanish"
    pt = "Portuguese"
    it = "Italian"
    el = "Greek"
    zh = "Chinese"
    ja = "Japanese"
    ru = "Russian"
    ar = "Arabic"


class ConversationConfig(BaseModel):
    output_language: Optional[str] = "en"
    conversation_style: Optional[List[str]] = custom_config["conversation_style"]
    person_roles: Optional[Dict[Union[int, str], HostProfile]] = None
    dialogue_structure: Optional[List[str]] = None
    engagement_techniques: Optional[List[str]] = None
    user_instructions: Optional[str] = None
    podcast_name: Optional[str] = None
    podcast_tagline: Optional[str] = None
    creativity: Optional[float] = custom_config["creativity"]
    word_count: Optional[int] = custom_config["word_count"]
    longform: Optional[bool] = False
    location: Optional[str] = "Finland"
    short_intro_and_conclusion: Optional[bool] = False
    disable_intro_and_conclusion: Optional[bool] = False


class PanelRequestData(BaseModel):
    title: str = "New public morning show"
    input_source: Union[str, List[str]] = ""
    input_text: Optional[str] = ""
    tts_model: str = "elevenlabs"
    longform: bool = False
    bucket_name: str = "public_panels"
    display_tag: Optional[str] = ""
    podcast_name: Optional[str] = custom_config["podcast_name"]
    podcast_tagline: Optional[str] = custom_config["podcast_tagline"]
    conversation_config: Optional[ConversationConfig] = ConversationConfig()
    tts_config: Optional[Dict[str, TTSConfig]] = None
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
    id: Optional[Union[str | UUID]] = None
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


class TranscriptIssueCoverage(str, Enum):
    WHOLE_TRANSCRIPT = "whole transcript"
    MULTIPLE_SEGMENTS = "multiple segments"
    SINGLE_SEGMENT = "single segment"


class TranscriptQualityIssue(BaseModel):
    title: str = Field(..., title="Title", description="Title describing the issue.")
    details: str = Field(
        ..., title="Issue details", description="Details about the issue."
    )
    suggestions: str = Field(
        ..., title="Suggested fix", description="Suggestion on how to fix the issue."
    )
    transcript_segments: list[str] = Field(
        ...,
        title="Transcript segments",
        description="One or more segments which have the issue and need to be fixed. Format should match original content: <personN>...</personN><personM>...</personM>",
        min_length=1,
    )
    severity: int = Field(
        ...,
        title="Issue severity",
        description="How severe is this issue with a scale from 1 to 5. 5 being most severe.",
        min=1,
        max=5,
    )
    issue_coverage: TranscriptIssueCoverage = Field(
        ...,
        title="Issue coverage",
        description="Coverage for the issue impacting the transcript: 'whole transcript', 'multiple segments', or 'single segment'.",
    )


class TranscriptQualityCheck(BaseModel):
    pass_test: bool = Field(
        ...,
        title="Valid transcript",
        description="Boolean indicating whether the transcript passes the quality check. Set to True only if no issues are present.",
    )
    issues: List[TranscriptQualityIssue] = Field(
        ...,
        title="Issues",
        description="List of issues for the transcript, if any.",
    )


class PanelMetadata(BaseModel):
    title: Optional[str] = None
    input_source: Optional[Union[str, List[str]]] = None
    input_text: Optional[str] = None
    tts_model: Optional[str] = None
    longform: Optional[bool] = None
    display_tag: Optional[str] = None
    conversation_config: Optional[ConversationConfig] = None
    tts_config: Optional[Dict[str, TTSConfig]] = None
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
        None, title="Images", description="List of image URLs."
    )
    longform: Optional[bool] = Field(
        None, title="Longform", description="Indicates if it's long-form content."
    )
    subjects: Optional[List[SummarySubject]] = Field(
        None,
        title="Subjects",
        description="List of subjects with descriptions and references.",
    )
    description: Optional[str] = Field(
        None, title="Description", description="Summary of the segment's discussion."
    )
    conversation_config: Optional[ConversationConfig] = Field(
        None,
        title="Conversation Configuration",
        description="Details for panel setup and dialogue.",
    )
    tts_config: Optional[Dict[str, TTSConfig]] = Field(
        None,
        title="TTS Configuration",
        description="Text to speech configuration",
    )
    tts_model: Optional[str] = Field(
        None,
        title="TTS model",
        description="Text to speech model name",
    )


# New metadata class for panels


class AudioMetadata(BaseModel):
    tts_model: Optional[str] = None
    conversation_config: Optional[ConversationConfig] = None
    tts_config: Optional[Dict[str, TTSConfig]] = None
