import json
import os
import tempfile
from typing import Optional, Tuple, Union, List
from uuid import UUID
from podcastfy.client import generate_podcast
from supabase import Client
from celery import Task
from celery.worker.request import Request

from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_service_client
from lib.models.supabase.public_panel import (
    ProcessState,
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)
from pydantic import BaseModel

# Load custom_config from environment variables with defaults
custom_config = {
    "word_count": int(os.getenv("panel_defaults_word_count", 200)),
    "conversation_style": os.getenv(
        "panel_defaults_conversation_style", "casual,humorous"
    ).split(","),
    "podcast_name": os.getenv("panel_defaults_podcast_name", "Morning Show"),
    "podcast_tagline": os.getenv(
        "panel_defaults_podcast_tagline", "Your Personal Morning Podcast"
    ),
    "creativity": float(os.getenv("panel_defaults_creativity", 0.7)),
}


class PublicPanelRequestData(BaseModel):
    title: str = "New public morning show"
    input_source: Union[str, List[str]] = ""
    input_text: Optional[str] = ""
    tts_model: str = "geminimulti"
    longform: bool = False
    bucket_name: str = "public_panels"
    conversation_config: Optional[dict] = custom_config
    panel_id: Optional[UUID] = None
    transcript_id: Optional[UUID] = None

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


def create_public_panel(
    access_token: str,
    request_data: PublicPanelRequestData,
    task_request: Request = None,
) -> UUID:
    service_client: Client = get_sync_supabase_service_client()

    # Initialize metadata with task_id if available
    metadata = {"task_id": task_request.id} if task_request else {}

    # Add additional fields to metadata if they are defined
    if request_data.conversation_config:
        metadata["conversation_config"] = request_data.conversation_config
    if request_data.tts_model:
        metadata["tts_model"] = request_data.tts_model
    if request_data.input_source:
        metadata["urls"] = request_data.input_source
    if request_data.longform is not None:
        metadata["longform"] = request_data.longform
    if request_data.input_text:
        metadata["input_text"] = request_data.input_text

    panel: PublicPanelDiscussion = PublicPanelDiscussion(
        title=request_data.title,
        metadata=metadata,
    )
    panel.create_sync(supabase=service_client)

    return panel.id


def create_public_panel_transcript(
    access_token: str, request_data: PublicPanelRequestData
) -> UUID:
    supabase: Client = get_sync_supabase_service_client()

    # Retrieve panel metadata
    panel = PublicPanelDiscussion.get_sync(supabase, request_data.panel_id)
    metadata = panel.metadata or {}

    # Use values from metadata if not defined in request_data
    conversation_config = request_data.conversation_config or metadata.get(
        "conversation_config", custom_config
    )
    conversation_config["podcast_name"] = custom_config["podcast_name"]
    conversation_config["podcast_tagline"] = custom_config["podcast_tagline"]
    input_source = request_data.input_source or metadata.get("urls", "")
    longform = (
        request_data.longform
        if request_data.longform is not None
        else metadata.get("longform", False)
    )
    input_text = request_data.input_text or metadata.get("input_text", "")

    bucket_transcript_file: str = f"panel_{request_data.panel_id}_transcript.txt"

    panel_transcript: PublicPanelTranscript = PublicPanelTranscript(
        public_panel_id=request_data.panel_id,
        title="Panel Transcript",
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        file=bucket_transcript_file,
        type="segment",
        metadata={"conversation_config": conversation_config},
    )
    panel_transcript.create_sync(supabase=supabase)

    try:
        transcript_file: str = generate_podcast(
            urls=(input_source if isinstance(input_source, list) else [input_source]),
            transcript_only=True,
            longform=longform,
            conversation_config=conversation_config,
            text=input_text,
        )
    except Exception as e:
        panel_transcript.process_state = ProcessState.failed
        panel_transcript.process_fail_message = str(e)
        panel_transcript.update_sync(supabase=supabase)
        raise RuntimeError("Failed to generate podcast transcript") from e

    with open(transcript_file, "rb") as transcript_src:
        supabase.storage.from_(request_data.bucket_name).upload(
            bucket_transcript_file, transcript_src
        )
    panel_transcript.process_state = ProcessState.done
    panel_transcript.update_sync(supabase=supabase)

    return panel_transcript.id


@celery_app.task
def create_public_panel_transcription_task(access_token, request_data_json):
    request_data = PublicPanelRequestData.model_validate_json(request_data_json)
    return create_public_panel_transcript(access_token, request_data)


@celery_app.task(bind=True)
def create_public_panel_w_transcript_task(
    self: Task, access_token, request_data_json
) -> Tuple[UUID, UUID]:
    request_data = PublicPanelRequestData.model_validate_json(request_data_json)
    panel_id = create_public_panel(access_token, request_data, self.request)
    request_data.panel_id = panel_id

    transcript_id = create_public_panel_transcript(access_token, request_data)

    return panel_id, transcript_id


def create_public_panel_audio(
    access_token: str,
    request_data: PublicPanelRequestData,
) -> UUID:
    panel_id: UUID = request_data.panel_id
    transcript_id: UUID = request_data.transcript_id

    bucket_transcript_file: str = f"panel_{panel_id}_transcript.txt"
    bucket_audio_file: str = f"panel_{panel_id}_audio.mp3"

    supabase: Client = get_sync_supabase_service_client()

    # Retrieve panel metadata
    panel = PublicPanelDiscussion.get_sync(supabase, panel_id)
    metadata = panel.metadata or {}

    # Use values from metadata if not defined in request_data
    conversation_config = request_data.conversation_config or metadata.get(
        "conversation_config", custom_config
    )
    conversation_config["podcast_name"] = custom_config["podcast_name"]
    conversation_config["podcast_tagline"] = custom_config["podcast_tagline"]
    tts_model = request_data.tts_model or metadata.get("tts_model", "geminimulti")

    response = supabase.storage.from_(request_data.bucket_name).download(
        bucket_transcript_file
    )

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response)
        transcript_file = tmp_file.name

    panel_audio: PublicPanelAudio = PublicPanelAudio(
        public_panel_id=panel_id,
        public_transcript_id=transcript_id,
        title="Panel Audio",
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        file=bucket_audio_file,
        metadata={"conversation_config": conversation_config},
    )
    panel_audio.create_sync(supabase=supabase)

    try:
        audio_file: str = generate_podcast(
            transcript_file=transcript_file,
            tts_model=tts_model,
            conversation_config=conversation_config,
        )
    except Exception as e:
        panel_audio.process_state = ProcessState.failed
        panel_audio.process_fail_message = str(e)
        panel_audio.update_sync(supabase=supabase)
        raise RuntimeError("Failed to generate podcast audio") from e

    os.remove(transcript_file)
    with open(audio_file, "rb") as audio_src:
        supabase.storage.from_(request_data.bucket_name).upload(
            bucket_audio_file, audio_src
        )

    panel_audio.process_state = ProcessState.done
    panel_audio.update_sync(supabase=supabase)

    return panel_audio.id


@celery_app.task
def create_public_panel_audio_task(self: Task, access_token, request_data_json):
    request_data = PublicPanelRequestData.model_validate_json(request_data_json)
    return create_public_panel_audio(access_token, request_data)


@celery_app.task(bind=True)
def create_public_panel_task(
    self: Task, access_token, request_data_json
) -> Tuple[UUID, UUID, UUID]:
    request_data = PublicPanelRequestData.model_validate_json(request_data_json)
    panel_id = create_public_panel(access_token, request_data, self.request)
    request_data.panel_id = panel_id

    transcript_id = create_public_panel_transcript(access_token, request_data)
    request_data.transcript_id = transcript_id

    audio_id = create_public_panel_audio(access_token, request_data)

    return panel_id, transcript_id, audio_id
