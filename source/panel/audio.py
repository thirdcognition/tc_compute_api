import os
import tempfile
import datetime
import time
from typing import Tuple
from uuid import UUID
from supabase import Client
from podcastfy.client import generate_podcast
from app.core.supabase import get_sync_supabase_client

from source.models.supabase.panel import (
    ProcessState,
    PanelDiscussion,
    PanelTranscript,
    PanelAudio,
)
from source.models.structures.panel import (
    PanelRequestData,
    custom_config,
    ConversationConfig,
)


def create_panel_audio(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    supabase_client: Client = None,
) -> UUID:
    print(f"Creating panel audio with request data: {request_data}")
    supabase_client = (
        supabase_client
        if supabase_client is not None
        else get_sync_supabase_client(access_token=tokens[0], refresh_token=tokens[1])
    )

    panel_id: UUID = request_data.panel_id
    transcript_id: UUID = request_data.transcript_id

    bucket_transcript_file: str = f"panel_{panel_id}_{transcript_id}_transcript.txt"

    # Retrieve panel metadata
    panel = PanelDiscussion.fetch_from_supabase_sync(supabase_client, panel_id)
    transcript = PanelTranscript.fetch_from_supabase_sync(
        supabase_client, transcript_id
    )
    metadata = transcript.metadata or {}

    # Load base conversation_config from PanelTranscript metadata
    base_conversation_config = metadata.get("conversation_config", {})
    # Extend with conversation_config from request_data and apply custom_config defaults
    conversation_config = ConversationConfig(
        **{
            **custom_config,
            **base_conversation_config,
            **(request_data.conversation_config.model_dump() or {}),
        }
    )

    tts_model = request_data.tts_model or metadata.get("tts_model", "geminimulti")

    lang_voices = (
        conversation_config.text_to_speech.get(transcript.lang.lower())
        if conversation_config.text_to_speech is not None
        else None
    )

    # Construct title
    default_voices = (
        conversation_config.text_to_speech.get(tts_model, {}).get("default_voices", {})
        if conversation_config.text_to_speech is not None
        else {}
    )
    title_voices = lang_voices if lang_voices else default_voices
    title_elements = [
        f"{panel.title} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        transcript.lang,
        f"Model: {tts_model}",
        (
            f"Q: {title_voices.get('question')}, A: {title_voices.get('answer')}"
            if title_voices.get("question") and title_voices.get("answer")
            else None
        ),
    ]
    title = " - ".join(filter(None, title_elements))

    response = supabase_client.storage.from_(request_data.bucket_name).download(
        bucket_transcript_file
    )

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response)
        transcript_file = tmp_file.name

    panel_audio: PanelAudio = PanelAudio(
        panel_id=panel_id,
        transcript_id=transcript_id,
        title=title,
        lang=transcript.lang,
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        metadata={
            "conversation_config": conversation_config.model_dump(),
            "tts_model": tts_model,
        },
        is_public=request_data.is_public,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    print(f"Panel Audio created with title: {title}")
    panel_audio.create_sync(supabase=supabase_client)
    print(f"Panel Audio ID: {panel_audio.id}")
    bucket_audio_file: str = (
        f"panel_{panel_id}_{transcript_id}_{panel_audio.id}_audio.mp3"
    )
    panel_audio.file = bucket_audio_file

    conv_conf = conversation_config.model_dump()

    conv_conf["text_to_speech"] = {}
    conv_conf["text_to_speech"][tts_model] = conversation_config.text_to_speech.get(
        tts_model, {}
    )
    if lang_voices:
        conv_conf["text_to_speech"][tts_model]["default_voices"] = lang_voices

    try:
        audio_file: str = generate_podcast(
            transcript_file=transcript_file,
            tts_model=tts_model,
            conversation_config=conv_conf,
        )
    except Exception as e:
        print(f"Error during audio generation: {e}")

        # Retry logic
        try:
            time.sleep(60)  # Wait for 60 seconds before retrying
            audio_file: str = generate_podcast(
                transcript_file=transcript_file,
                tts_model=tts_model,
                conversation_config=conv_conf,
            )
        except Exception as e:
            print(f"Error during second attempt of audio generation: {e}")
            panel_audio.process_state = ProcessState.failed
            panel_audio.process_state_message = str(e)
            panel_audio.update_sync(supabase=supabase_client)
            raise RuntimeError("Failed to generate podcast audio after retry") from e

    os.remove(transcript_file)
    with open(audio_file, "rb") as audio_src:
        supabase_client.storage.from_(request_data.bucket_name).upload(
            bucket_audio_file, audio_src
        )

    panel_audio.process_state = ProcessState.done
    panel_audio.update_sync(supabase=supabase_client)

    print(f"Uploading audio file: {audio_file} to bucket: {request_data.bucket_name}")
    return panel_audio.id
