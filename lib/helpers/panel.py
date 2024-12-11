import asyncio

from typing import Union, List
from podcastfy.client import generate_podcast
from celery import Task  # Import Task for typing
from supabase import AsyncClient
from app.core.celery_app import app  # Import the Celery app
from lib.models.supabase.public_panel import (
    ProcessState,
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)


@app.task(bind=True)
async def create_public_panel(
    self: Task,
    supabase: AsyncClient,
    input_source: Union[str, List[str]],
    tts_model: str = "geminimulti",
    longform: bool = False,
    bucket_name: str = "public_panels",
) -> str:
    """
    Creates a panel audio file from the given input source and saves it as a temporary file.

    Args:
        input_source (str or list): The input source for the panel (e.g., URL, text, PDF path).
        tts_model (str): The text-to-speech model to use for audio generation.
        longform (bool): Whether to generate a longform panel.

    Returns:
        str: The Celery task ID.
    """

    # Create a new PublicPanelDiscussion instance
    panel_discussion: PublicPanelDiscussion = PublicPanelDiscussion(
        title="New Panel Discussion",
        metadata={"task_id": self.request.id},
    )
    await panel_discussion.create(supabase=supabase)
    bucket_transcript_file: str = f"panel_{panel_discussion.id}_transcript.txt"
    bucket_audio_file: str = f"panel_{panel_discussion.id}_audio.mp3"

    # Create a new PublicPanelTranscript instance
    panel_transcript: PublicPanelTranscript = PublicPanelTranscript(
        public_panel_id=panel_discussion.id,
        title="Panel Transcript",
        bucket_id=bucket_name,
        process_state=ProcessState.processing,
        file=bucket_transcript_file,
    )
    await panel_transcript.create(supabase=supabase)

    transcript_file: str = generate_podcast(
        urls=input_source if isinstance(input_source, list) else [input_source],
        transcript_only=True,
        longform=longform,
    )
    panel_transcript.process_state = ProcessState.done
    await panel_transcript.update(supabase=supabase)

    # Create a new PublicPanelAudio instance
    panel_audio: PublicPanelAudio = PublicPanelAudio(
        public_panel_id=panel_discussion.id,
        public_transcript_id=panel_transcript.id,
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

    # Upload the audio and transcript files
    with (
        open(audio_file, "rb") as audio_src,
        open(transcript_file, "rb") as transcript_source,
    ):
        audio_task = supabase.storage.from_(bucket_name).upload(
            bucket_audio_file, audio_src
        )
        transcript_task = supabase.storage.from_(bucket_name).upload(
            bucket_transcript_file, transcript_source
        )

        await asyncio.gather(audio_task, transcript_task)

    return self.request.id  # Return the Celery task ID


# Example usage
# asyncio.run(check_task_status("your_task_id"))
