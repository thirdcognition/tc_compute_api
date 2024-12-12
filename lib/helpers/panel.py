import json
import os
import tempfile
from typing import Optional, Tuple, Union, List
from uuid import UUID
from podcastfy.client import generate_podcast
from supabase import AsyncClient
from celery.worker.request import Request

from app.core.supabase import get_supabase_service_client
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
    # "text_to_speech": {
    #     "gemini": {
    #         "default_voices": {
    #             "question": "en-US-Studio-O",  # "en-US-Journey-D",
    #             "answer": "en-GB-Studio-C",  # "en-US-Journey-O",
    #         }
    #     },
    # },
}


class PublicPanelRequestData(BaseModel):
    title: str = "New public morning show"
    input_source: Union[str, List[str]]
    input_text: Optional[str]
    tts_model: str = "geminimulti"
    longform: bool = False
    bucket_name: str = "public_panels"

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


# @async_task(celery_app, bind=True)
async def create_public_panel_transcript(
    supabase: AsyncClient,
    panel_id: UUID,
    input_source: Union[str, List[str]],
    input_text: str = None,
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

    try:
        transcript_file: str = generate_podcast(
            urls=input_source if isinstance(input_source, list) else [input_source],
            transcript_only=True,
            longform=longform,
            conversation_config=custom_config,
            text=input_text,
        )
    except Exception as e:
        panel_transcript.process_state = ProcessState.failed
        panel_transcript.process_fail_message = str(e)
        await panel_transcript.update(supabase=supabase)
        raise RuntimeError("Failed to generate podcast transcript") from e

    with open(transcript_file, "rb") as transcript_src:
        await supabase.storage.from_(bucket_name).upload(
            bucket_transcript_file, transcript_src
        )
    panel_transcript.process_state = ProcessState.done
    await panel_transcript.update(supabase=supabase)

    return panel_transcript.id


# @async_task(celery_app, bind=True)
async def create_public_panel_audio(
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

    try:
        # Generate the panel audio file
        audio_file: str = generate_podcast(
            transcript_file=transcript_file,
            tts_model=tts_model,
            conversation_config=custom_config,
        )
    except Exception as e:
        panel_audio.process_state = ProcessState.failed
        panel_audio.process_fail_message = str(e)
        await panel_audio.update(supabase=supabase)
        raise RuntimeError("Failed to generate podcast audio") from e

    # Delete the temporary transcript file
    os.remove(transcript_file)
    # Upload the audio file
    with open(audio_file, "rb") as audio_src:
        await supabase.storage.from_(bucket_name).upload(bucket_audio_file, audio_src)

    panel_audio.process_state = ProcessState.done
    await panel_audio.update(supabase=supabase)


# @async_task(celery_app, bind=True)
async def create_public_panel(
    access_token: str,
    request_data: PublicPanelRequestData,
    task_request: Request = None,
) -> Tuple[UUID, str]:
    """
    Creates a panel audio file from the given input source and saves it as a temporary file.

    Args:
        request_data_json (str): The JSON-serialized request data containing input source, tts_model, longform, and bucket_name.

    Returns:
        tuple: The panel ID and the Celery task ID.
    """

    # Deserialize the JSON string back into a PublicPanelRequestData object using Pydantic V2

    print(f"{task_request=}", f"{request_data=}", f"{access_token=}")

    service_client: AsyncClient = await get_supabase_service_client()
    # Create a new PublicPanelDiscussion instance
    panel_discussion: PublicPanelDiscussion = PublicPanelDiscussion(
        title=request_data.title,
        metadata={"task_id": task_request.id},
    )
    await panel_discussion.create(supabase=service_client)
    panel_id = panel_discussion.id

    transcript_id = await create_public_panel_transcript(
        service_client,
        panel_id,
        request_data.input_source,
        request_data.input_text,
        request_data.longform,
        request_data.bucket_name,
    )
    # panel_id = UUID("f2027a96-c17e-4e73-ad21-9e3ac26d6ee6")
    # transcript_id = UUID("f7bcde51-3a8f-415c-b3fb-171fdfc57abf")

    await create_public_panel_audio(
        service_client,
        panel_id,  # panel_discussion.id,
        transcript_id,
        request_data.tts_model,
        request_data.bucket_name,
    )

    return panel_id
