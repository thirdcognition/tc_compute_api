import os
import json
from typing import Optional, Union, List
from uuid import UUID
from pydantic import BaseModel
from source.helpers.sources import (
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


class PanelRequestData(BaseModel):
    title: str = "New public morning show"
    input_source: Union[str, List[str]] = ""
    input_text: Optional[str] = ""
    tts_model: str = "geminimulti"
    longform: bool = False
    bucket_name: str = "public_panels"
    conversation_config: Optional[dict] = custom_config
    panel_id: Optional[UUID] = None
    transcript_parent_id: Optional[str] = None
    transcript_id: Optional[UUID] = None
    google_news: Optional[Union[GoogleNewsConfig, List[GoogleNewsConfig]]] = None
    yle_news: Optional[Union[YleNewsConfig, List[YleNewsConfig]]] = None
    techcrunch_news: Optional[
        Union[TechCrunchNewsConfig, List[TechCrunchNewsConfig]]
    ] = None
    hackernews: Optional[Union[HackerNewsConfig, List[HackerNewsConfig]]] = None
    cronjob: Optional[str] = None
    owner_id: Optional[str] = None
    organization_id: Optional[str] = None

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)
