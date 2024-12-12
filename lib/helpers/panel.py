import os
import tempfile
from typing import Tuple, Union, List
from uuid import UUID
from podcastfy.client import generate_podcast
from celery import Task  # Import Task for typing
from supabase import AsyncClient

# from app.core.celery_app import celery_app, async_task  # Import the Celery app
from app.core.supabase import get_supabase_service_client
from lib.models.supabase.public_panel import (
    ProcessState,
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)
from pydantic import BaseModel


class PublicPanelRequestData(BaseModel):
    input_source: Union[str, List[str]]
    tts_model: str = "geminimulti"
    longform: bool = False
    bucket_name: str = "public_panels"


# @async_task(celery_app, bind=True)
async def create_public_panel_transcript(
    self: Task,
    supabase: AsyncClient,
    panel_id: UUID,
    input_source: Union[str, List[str]],
    longform: bool = False,
    bucket_name: str = "public_panels",
) -> UUID:
    """
    Creates a panel transcript from the given input source and saves it as a temporary file.

    Args:
        panel_id (uuid): The ID of the panel discussion.
        input_source (str or list): The input source for the panel (e.g., URL, text, PDF path).
        longform (bool): Whether to generate a longform panel.

    Returns:
        str: The path to the transcript file.
    """

    bucket_transcript_file: str = f"panel_{panel_id}_transcript.txt"

    # Create a new PublicPanelTranscript instance
    panel_transcript: PublicPanelTranscript = PublicPanelTranscript(
        public_panel_id=panel_id,
        title="Panel Transcript",
        bucket_id=bucket_name,
        process_state=ProcessState.processing,
        file=bucket_transcript_file,
        type="segment",
    )
    await panel_transcript.create(supabase=supabase)

    transcript_file: str = generate_podcast(
        urls=input_source if isinstance(input_source, list) else [input_source],
        transcript_only=True,
        longform=longform,
    )
    panel_transcript.process_state = ProcessState.done
    await panel_transcript.update(supabase=supabase)

    with open(transcript_file, "rb") as transcript_src:
        await supabase.storage.from_(bucket_name).upload(
            bucket_transcript_file, transcript_src
        )

    return panel_transcript.id


# @async_task(celery_app, bind=True)
async def create_public_panel_audio(
    self: Task,
    supabase: AsyncClient,
    panel_id: UUID,
    transcript_id: UUID,
    tts_model: str = "geminimulti",
    bucket_name: str = "public_panels",
) -> None:
    """
    Creates a panel audio file from the given transcript file and saves it as a temporary file.

    Args:
        panel_id (UUID): The ID of the panel discussion.
        transcript_file (str): The path to the transcript file.
        tts_model (str): The text-to-speech model to use for audio generation.
    """
    bucket_transcript_file: str = f"panel_{panel_id}_transcript.txt"
    bucket_audio_file: str = f"panel_{panel_id}_audio.mp3"

    # Download the transcript file from Supabase
    response = await supabase.storage.from_(bucket_name).download(
        bucket_transcript_file
    )

    # Save transcript to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response)
        transcript_file = tmp_file.name

    # Create a new PublicPanelAudio instance
    panel_audio: PublicPanelAudio = PublicPanelAudio(
        public_panel_id=panel_id,
        public_transcript_id=transcript_id,
        title="Panel Audio",
        bucket_id=bucket_name,
        process_state=ProcessState.processing,
        file=bucket_audio_file,
    )
    await panel_audio.create(supabase=supabase)

    # Generate the panel audio file
    audio_file: str = generate_podcast(
        transcript_file=transcript_file,
        tts_model=tts_model,
    )

    panel_audio.process_state = ProcessState.done
    await panel_audio.update(supabase=supabase)

    # Delete the temporary transcript file
    os.remove(transcript_file)
    # Upload the audio file
    with open(audio_file, "rb") as audio_src:
        await supabase.storage.from_(bucket_name).upload(bucket_audio_file, audio_src)


# @async_task(celery_app, bind=True)
async def create_public_panel(
    self: Task, supabase: AsyncClient, request_data: PublicPanelRequestData
) -> Tuple[UUID, str]:
    """
    Creates a panel audio file from the given input source and saves it as a temporary file.

    Args:
        request_data (PublicPanelRequestData): The request data containing input source, tts_model, longform, and bucket_name.

    Returns:
        tuple: The panel ID and the Celery task ID.
    """
    service_client: AsyncClient = await get_supabase_service_client()
    # Create a new PublicPanelDiscussion instance
    panel_discussion: PublicPanelDiscussion = PublicPanelDiscussion(
        title="New Panel Discussion",
        # metadata={"task_id": self.request.id},
    )
    await panel_discussion.create(supabase=service_client)
    panel_id = panel_discussion.id

    transcript_id = await create_public_panel_transcript(
        self,
        service_client,
        panel_id,
        request_data.input_source,
        request_data.longform,
        request_data.bucket_name,
    )

    await create_public_panel_audio(
        self,
        service_client,
        panel_id,  # panel_discussion.id,
        transcript_id,
        request_data.tts_model,
        request_data.bucket_name,
    )

    return panel_id, "test"  # self.request.id
