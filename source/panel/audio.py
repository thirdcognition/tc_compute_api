import datetime
import time
from typing import Dict, Tuple
from uuid import UUID
from io import BytesIO
from supabase import Client
from pydub import AudioSegment
from app.core.supabase import get_sync_supabase_client
from transcript_to_audio.schemas import TTSConfig, SpeakerConfig
from transcript_to_audio.text_to_speech import TextToSpeech

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

    tts_model = request_data.tts_model or metadata.get("tts_model", "elevenlabs")
    tts_config = request_data.tts_config or metadata.get("tts_config", None)
    if tts_config is not None:
        tts_config = {
            key: TTSConfig(**value) if isinstance(value, dict) else value
            for key, value in tts_config.items()
        }
    else:
        raise ValueError(f"Text to speech configs are missing! {request_data=}")

    voice_configs: Dict[int, SpeakerConfig] = {}
    for key, role in conversation_config.person_roles.items():
        voice_configs[key] = role.voice_config.get(
            transcript.lang, next(iter(role.voice_config.values()))
        )

    lang_tts_config = tts_config.get(transcript.lang, next(iter(tts_config.values())))

    # Construct title
    title_elements = [
        f"{panel.title} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        transcript.lang,
        f"Model: {tts_model}",
        (
            " | ".join([f"{key}: {value}" for key, value in voice_configs.items()])
            if len(voice_configs.keys()) > 0
            else None
        ),
    ]
    title = " - ".join(filter(None, title_elements))

    # Download transcript as string
    response = supabase_client.storage.from_(request_data.bucket_name).download(
        bucket_transcript_file
    )
    transcript_text = (
        response.decode("utf-8") if isinstance(response, bytes) else response
    )

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
            "tts_config": {
                key: value.model_dump() if hasattr(value, "model_dump") else value
                for key, value in tts_config.items()
            },
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

    # Prepare TTS
    tts = TextToSpeech(provider=tts_model, tts_config=lang_tts_config)

    # Try TTS conversion: returns (updated_transcript_path, audio_segment)
    # audio_segment is a pydub.AudioSegment object
    try:
        audio_segment: AudioSegment = None
        updated_transcript_path, audio_segment = tts.convert_to_speech(
            transcript_text, None, save_file=False
        )
    except Exception as e:
        print(f"Error during audio generation: {e}")
        # Retry logic
        try:
            time.sleep(60)  # Wait for 60 seconds before retrying
            updated_transcript_path, audio_segment = tts.convert_to_speech(
                transcript_text, voice_configs, None, save_file=False
            )
        except Exception as e:
            print(f"Error during second attempt of audio generation: {e}")
            panel_audio.process_state = ProcessState.failed
            panel_audio.process_state_message = str(e)
            panel_audio.update_sync(supabase=supabase_client)
            raise RuntimeError("Failed to generate podcast audio after retry") from e

    # Upload new transcript file to bucket (replace previous)
    with open(updated_transcript_path, "rb") as new_transcript_file:
        supabase_client.storage.from_(request_data.bucket_name).upload(
            bucket_transcript_file, new_transcript_file, overwrite=True
        )

    # Export audio_segment (pydub.AudioSegment) to BytesIO and upload directly
    audio_buffer = BytesIO()
    audio_segment.export(audio_buffer, format="mp3")
    audio_buffer.seek(0)
    supabase_client.storage.from_(request_data.bucket_name).upload(
        bucket_audio_file, audio_buffer
    )

    panel_audio.process_state = ProcessState.done
    panel_audio.update_sync(supabase=supabase_client)

    print(
        f"Uploading audio file: {bucket_audio_file} to bucket: {request_data.bucket_name}"
    )
    return panel_audio.id
