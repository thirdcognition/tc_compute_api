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

custom_config = {
    "word_count": 200,
    "conversation_style": ["casual", "humorous"],
    "podcast_name": "Morning Show",
    "podcast_tagline": "Your Personal Morning Podcast",
    "creativity": 0.7,
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
    panel_discussion: PublicPanelDiscussion = PublicPanelDiscussion(
        title=request_data.title,
        metadata={"task_id": task_request.id},
    )
    panel_discussion.create_sync(supabase=service_client)

    return panel_discussion.id


def create_public_panel_transcript(
    access_token: str, request_data: PublicPanelRequestData
) -> UUID:
    supabase: Client = get_sync_supabase_service_client()

    conversation_config = request_data.conversation_config or custom_config

    bucket_transcript_file: str = f"panel_{request_data.panel_id}_transcript.txt"

    panel_transcript: PublicPanelTranscript = PublicPanelTranscript(
        public_panel_id=request_data.panel_id,
        title="Panel Transcript",
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        file=bucket_transcript_file,
        type="segment",
    )
    panel_transcript.create_sync(supabase=supabase)

    try:
        transcript_file: str = generate_podcast(
            urls=(
                request_data.input_source
                if isinstance(request_data.input_source, list)
                else [request_data.input_source]
            ),
            transcript_only=True,
            longform=request_data.longform,
            conversation_config=conversation_config,
            text=request_data.input_text,
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
def create_public_panel_transcription_task(
    access_token, panel_id: UUID, request_data_json
):
    request_data = PublicPanelRequestData.model_validate_json(request_data_json)
    return create_public_panel_transcript(access_token, panel_id, request_data)


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

    conversation_config = request_data.conversation_config or custom_config

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
    )
    panel_audio.create_sync(supabase=supabase)

    try:
        audio_file: str = generate_podcast(
            transcript_file=transcript_file,
            tts_model=request_data.tts_model,
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
