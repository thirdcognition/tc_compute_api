import datetime
from typing import Tuple
from uuid import UUID
from celery import Task
from supabase import Client
from croniter import croniter

from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_client, get_sync_supabase_service_client
from source.panel.panel import create_panel
from source.panel.transcript import create_panel_transcript
from source.panel.audio import create_panel_audio
from source.helpers.communication import send_email_about_new_shows_task
from source.models.structures.panel import PanelRequestData
from source.models.supabase.panel import PanelTranscript, PanelDiscussion, PanelAudio
from source.models.structures.panel import custom_config


@celery_app.task
def create_panel_transcription_task(tokens: Tuple[str, str], request_data_json):
    request_data = PanelRequestData.model_validate_json(request_data_json)
    return create_panel_transcript(tokens, request_data)


@celery_app.task(bind=True)
def create_panel_w_transcript_task(
    self: Task, tokens: Tuple[str, str], request_data_json
) -> Tuple[UUID, UUID]:
    request_data = PanelRequestData.model_validate_json(request_data_json)
    panel_id = create_panel(tokens, request_data, self.request)
    request_data.panel_id = panel_id

    transcript_id = create_panel_transcript(tokens, request_data)

    return panel_id, transcript_id


@celery_app.task
def create_panel_audio_task(tokens: Tuple[str, str], request_data_json):
    request_data = PanelRequestData.model_validate_json(request_data_json)
    audio_id = create_panel_audio(tokens, request_data)

    if audio_id:
        send_email_about_new_shows_task([str(request_data.transcript_id)])

    return audio_id


@celery_app.task(bind=True)
def create_panel_task(
    self: Task, tokens: Tuple[str, str], request_data_json
) -> Tuple[UUID, UUID, UUID]:
    request_data = PanelRequestData.model_validate_json(request_data_json)
    panel_id = create_panel(tokens, request_data, self.request)
    request_data.panel_id = panel_id

    transcript_id = create_panel_transcript(tokens, request_data)
    request_data.transcript_id = transcript_id

    audio_id = create_panel_audio(tokens, request_data)

    return panel_id, transcript_id, audio_id


@celery_app.task(bind=True)
def generate_transcripts_task(
    self: Task,
    tokens: Tuple[str, str],
    use_service_account=False,
    supabase_client: Client = None,
):
    if use_service_account and supabase_client is None:
        supabase_client = get_sync_supabase_service_client()
    elif supabase_client is None:
        supabase_client = get_sync_supabase_client(
            access_token=tokens[0], refresh_token=tokens[1]
        )

    # Fetch all PanelTranscripts with generation_cronjob set
    transcripts_with_cronjob = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase_client, filter={"generation_cronjob": {"neq": None}}
    )

    # Skip entries with empty string as generation_cronjob
    transcripts_with_cronjob = [
        transcript
        for transcript in transcripts_with_cronjob
        if transcript.generation_cronjob != ""
    ]

    # Fetch all PanelTranscripts and map them by panelId
    all_transcripts_with_parent = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase_client, filter={"generation_parent": {"neq": None}}
    )

    transcripts_by_parent: dict[str, PanelTranscript] = {}
    for transcript in all_transcripts_with_parent:
        if transcript.generation_parent not in transcripts_by_parent:
            transcripts_by_parent[transcript.generation_parent] = []
        transcripts_by_parent[transcript.generation_parent].append(transcript)

    # Sort each list of transcripts by updated_at, newest first
    for transcript_id in transcripts_by_parent:
        transcripts_by_parent[transcript_id].sort(
            key=lambda x: x.updated_at, reverse=True
        )

    new_transcripts_generated = False  # Flag to track new transcript generation

    new_transcript_ids = []  # List to store IDs of newly generated transcripts

    for transcript in transcripts_with_cronjob:
        transcript_id = transcript.id
        panel_id = transcript.panel_id
        latest_transcript: PanelTranscript = transcripts_by_parent.get(
            transcript_id, [None]
        )[0]

        if latest_transcript is None:
            latest_transcript = transcript

        if latest_transcript:
            now_aware = datetime.datetime.now(datetime.timezone.utc)
            cron = croniter(
                transcript.generation_cronjob,
                latest_transcript.created_at.astimezone(datetime.timezone.utc),
            )
            prev_scheduled_time = datetime.datetime.fromtimestamp(
                cron.get_prev(float)
            ).astimezone(datetime.timezone.utc)
            next_scheduled_time = datetime.datetime.fromtimestamp(
                cron.get_next(float)
            ).astimezone(datetime.timezone.utc)

            print(
                f"Debug: Transcript {transcript.id} - now: {now_aware}, "
                f"next: {next_scheduled_time}, prev: {prev_scheduled_time}, "
                f"created_at: {latest_transcript.created_at}"
            )
            if (
                now_aware
                >= next_scheduled_time
                # and latest_transcript.created_at <= prev_scheduled_time
            ):
                # Fetch the matching PanelDiscussion model
                panel = PanelDiscussion.fetch_from_supabase_sync(
                    supabase_client, panel_id
                )
                metadata = (panel.metadata or {}) if panel is not None else {}

                # Call the helper function to process transcript generation
                transcript_id = process_transcript_generation(
                    tokens, transcript, panel, metadata, supabase_client
                )
                new_transcript_ids.append(str(transcript_id))
                new_transcripts_generated = True

            else:
                time_since_creation_str = str(
                    now_aware - latest_transcript.created_at
                ).split(".")[
                    0
                ]  # Remove microseconds
                print(
                    f"Skip generation for {transcript.id} because time since creation is {time_since_creation_str}, "
                    f"current time is {now_aware}, next scheduled time is {next_scheduled_time}, "
                    f"and previous scheduled time is {prev_scheduled_time}"
                )

    # After processing all transcripts, check the flag and send emails if needed
    if new_transcripts_generated:
        send_email_about_new_shows_task.delay(new_transcript_ids)


def process_transcript_generation(tokens, transcript, panel, metadata, supabase_client):
    # Extend the metadata with the PanelTranscript model
    transcript_metadata = (transcript.metadata or {}) if transcript is not None else {}

    # Fetch the connected PanelAudio model
    audio = PanelAudio.fetch_from_supabase_sync(
        supabase_client, transcript.id, id_column="transcript_id"
    )
    audio_metadata = (audio.metadata or {}) if audio is not None else {}

    # Separate and extend conversation_config
    conversation_config: dict = metadata.get("conversation_config", {})
    conversation_config.update(transcript_metadata.get("conversation_config", {}))
    metadata.update(transcript_metadata)
    metadata["conversation_config"] = conversation_config

    new_transcript_data = PanelRequestData(
        title=panel.title,
        input_source=metadata.get("input_source", ""),
        input_text=metadata.get("input_text", ""),
        longform=metadata.get("longform", False),
        bucket_name=metadata.get("bucket_name", "public_panels"),
        conversation_config=metadata.get("conversation_config", custom_config),
        panel_id=panel.id,
        google_news=metadata.get("google_news", None),
        yle_news=metadata.get("yle_news", None),
        techcrunch_news=metadata.get("techcrunch_news", None),
        hackernews=metadata.get("hackernews", None),
        owner_id=str(panel.owner_id),
        organization_id=str(panel.organization_id),
        transcript_parent_id=str(transcript.id),
    )

    print(f"Generating timed transcript for {transcript.id}.")
    if tokens is not None:
        transcript_id = create_panel_transcript(tokens, new_transcript_data)
    else:
        transcript_id = create_panel_transcript(
            tokens, new_transcript_data, supabase_client
        )

    metadata.update(audio_metadata)
    conversation_config.update(audio_metadata.get("conversation_config", {}))
    metadata["conversation_config"] = conversation_config
    new_transcript_data.tts_model = audio_metadata.get("tts_model", "gemini")

    new_transcript_data.transcript_id = transcript_id
    new_transcript_data.conversation_config = conversation_config
    if tokens is not None:
        create_panel_audio(tokens, new_transcript_data)
    else:
        create_panel_audio(tokens, new_transcript_data, supabase_client)

    return transcript_id
