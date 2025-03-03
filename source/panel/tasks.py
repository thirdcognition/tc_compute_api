import datetime
from typing import Tuple
from uuid import UUID
from celery import Task, chord
from supabase import Client
from croniter import croniter

from app.core.celery_app import celery_app
from app.core.supabase import (
    get_sync_supabase_client,
    get_sync_supabase_service_client,
)
from source.panel.panel import create_panel
from source.panel.transcript import create_panel_transcript
from source.panel.audio import create_panel_audio
from source.helpers.communication import send_email_about_new_shows_task
from source.models.structures.panel import (
    PanelRequestData,
    ConversationConfig,
)
from source.models.supabase.panel import PanelTranscript, PanelDiscussion, PanelAudio
from source.tasks.utils import collect_results


@celery_app.task
def create_panel_transcription_task(tokens: Tuple[str, str], request_data_json):
    request_data = PanelRequestData.model_validate_json(request_data_json)
    return create_panel_transcript(tokens, request_data)


@celery_app.task(bind=True)
def create_panel_w_transcript_task(
    self: Task, tokens: Tuple[str, str], request_data_json
) -> Tuple[UUID, list[UUID]]:
    request_data = PanelRequestData.model_validate_json(request_data_json)
    panel_id = create_panel(tokens, request_data, self.request)
    request_data.panel_id = panel_id

    transcript_ids = create_panel_transcript(tokens, request_data)

    return panel_id, transcript_ids


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
) -> Tuple[UUID, list[UUID], list[UUID]]:
    request_data = PanelRequestData.model_validate_json(request_data_json)
    panel_id = create_panel(tokens, request_data, self.request)
    request_data.panel_id = panel_id

    transcript_ids = create_panel_transcript(tokens, request_data)
    audio_ids = []
    for transcript_id in transcript_ids:
        audio_request_data = request_data.model_copy()
        audio_request_data.transcript_id = transcript_id
        audio_ids.append(create_panel_audio(tokens, audio_request_data))

    return panel_id, transcript_ids, audio_ids


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

    # Create a chord to execute tasks in parallel and collect results
    chord(
        process_transcript_task.s(transcript.id, tokens, use_service_account)
        for transcript in transcripts_with_cronjob
    )(collect_results.s() | handle_transcript_cron_results.s())


@celery_app.task
def handle_transcript_cron_results(new_transcript_ids):
    """
    Handle the results of the collect_results task and send emails if needed.

    :param new_transcript_ids: List of new transcript IDs.
    """
    if new_transcript_ids:
        send_email_about_new_shows_task.delay(new_transcript_ids)


@celery_app.task
def process_transcript_task(
    transcript_id: UUID, tokens: Tuple[str, str], use_service_account=False
):
    supabase_client = (
        get_sync_supabase_service_client()
        if use_service_account
        else get_sync_supabase_client(access_token=tokens[0], refresh_token=tokens[1])
    )

    # Fetch the transcript from the database
    transcript = PanelTranscript.fetch_from_supabase_sync(
        supabase_client, transcript_id
    )
    if not transcript:
        raise ValueError(f"Transcript with ID {transcript_id} not found.")

    panel_id = transcript.panel_id
    latest_transcript = transcript  # Default to the current transcript

    # Fetch the latest transcript if available
    all_transcripts_with_parent = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase_client, filter={"transcript_parent_id": {"neq": None}}
    )
    transcripts_by_parent = {}
    for t in all_transcripts_with_parent:
        if t.transcript_parent_id not in transcripts_by_parent:
            transcripts_by_parent[t.transcript_parent_id] = []
        transcripts_by_parent[t.transcript_parent_id].append(t)

    if transcript_id in transcripts_by_parent:
        transcripts_by_parent[transcript_id].sort(
            key=lambda x: x.updated_at, reverse=True
        )
        latest_transcript = transcripts_by_parent[transcript_id][0]

    now_aware = datetime.datetime.now(datetime.timezone.utc)
    cron = croniter(
        transcript.generation_cronjob,
        latest_transcript.created_at.astimezone(datetime.timezone.utc),
    )
    next_scheduled_time = datetime.datetime.fromtimestamp(
        cron.get_next(float)
    ).astimezone(datetime.timezone.utc)

    if now_aware >= next_scheduled_time:
        panel = PanelDiscussion.fetch_from_supabase_sync(supabase_client, panel_id)
        metadata = (panel.metadata or {}) if panel else {}

        # Process transcript generation
        transcript_ids = process_transcript_generation(
            tokens, transcript, panel, metadata, supabase_client
        )
        ret_ids = []
        for transcript_id in transcript_ids:
            if isinstance(transcript_id, list):
                ret_ids.extend([str(id) for id in transcript_id])
            else:
                ret_ids.append(str(transcript_id))

        return ret_ids
        # return [str(transcript_id) for transcript_id in transcript_ids ]
    else:
        return None


def process_transcript_generation(
    tokens: Tuple,
    transcript: PanelTranscript,
    panel: PanelDiscussion,
    metadata: dict,
    supabase_client: Client,
) -> list[UUID]:
    # Extend the metadata with the PanelTranscript model
    transcript_metadata = (transcript.metadata or {}) if transcript is not None else {}

    # Fetch the connected PanelAudio model
    audio = PanelAudio.fetch_from_supabase_sync(
        supabase_client, transcript.id, id_column="transcript_id"
    )
    audio_metadata = (audio.metadata or {}) if audio is not None else {}

    # Separate and extend conversation_config
    conversation_config_data = metadata.get("conversation_config", {})
    conversation_config = ConversationConfig.model_validate(conversation_config_data)

    # Extend conversation_config with transcript_metadata
    conversation_config = conversation_config.model_copy(
        update=transcript_metadata.get("conversation_config", {})
    )

    metadata.update(transcript_metadata)
    metadata["conversation_config"] = conversation_config.model_dump()

    new_transcript_request = PanelRequestData(
        title=panel.title,
        input_source=metadata.get("input_source", ""),
        input_text=metadata.get("input_text", ""),
        longform=metadata.get("longform", False),
        bucket_name=metadata.get("bucket_name", "public_panels"),
        conversation_config=conversation_config,
        panel_id=panel.id,
        google_news=metadata.get("google_news", None),
        yle_news=metadata.get("yle_news", None),
        techcrunch_news=metadata.get("techcrunch_news", None),
        hackernews=metadata.get("hackernews", None),
        news_guidance=metadata.get("news_guidance", None),
        news_items=metadata.get("news_items", 5),
        segments=metadata.get("segments", 5),
        languages=metadata.get("languages", None),
        owner_id=str(panel.owner_id),
        organization_id=str(panel.organization_id),
        transcript_parent_id=str(transcript.id),
        is_public=bool(panel.is_public),
    )

    print(f"Generating timed transcript for {transcript.id}.")
    if tokens is not None:
        transcript_ids = create_panel_transcript(tokens, new_transcript_request)
    else:
        transcript_ids = create_panel_transcript(
            tokens, new_transcript_request, supabase_client
        )

    metadata.update(audio_metadata)
    conversation_config = conversation_config.model_copy(
        update=audio_metadata.get("conversation_config", {})
    )
    metadata["conversation_config"] = conversation_config.model_dump()
    new_transcript_request.tts_model = audio_metadata.get("tts_model", "elevenlabs")
    new_transcript_request.conversation_config = conversation_config

    for transcript_id in transcript_ids:
        audio_transcript_request = new_transcript_request.model_copy()
        audio_transcript_request.transcript_id = transcript_id
        if tokens is not None:
            create_panel_audio(tokens, audio_transcript_request)
        else:
            create_panel_audio(tokens, audio_transcript_request, supabase_client)

    return transcript_ids
