import datetime
import json
import os
import tempfile
from typing import Optional, Tuple, Union, List
from uuid import UUID
from podcastfy.client import generate_podcast
from supabase import Client
from celery import Task
from celery.worker.request import Request

from pydantic import BaseModel

from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_client, get_sync_supabase_service_client
from source.helpers.news.google import GoogleNewsConfig, fetch_google_news_links

from source.models.data.news_item import NewsItem
from source.models.config.logging import logger
from source.helpers.news.yle import fetch_yle_news_links, YleNewsConfig
from source.helpers.communication import send_email_about_new_shows_task
from source.models.data.user import UserIDs
from source.models.supabase.panel import (
    ProcessState,
    PanelDiscussion,
    PanelTranscript,
    PanelAudio,
)


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
    update_cycle: Optional[int] = None
    owner_id: Optional[str] = None
    organization_id: Optional[str] = None

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


def create_panel(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    task_request: Request = None,
    supabase_client: Client = None,
) -> UUID:
    supabase_client = (
        supabase_client
        if supabase_client is not None
        else get_sync_supabase_client(access_token=tokens[0], refresh_token=tokens[1])
    )
    logger.debug(f"create public panel {tokens=}")
    try:
        supabase_client = get_sync_supabase_client(
            access_token=tokens[0], refresh_token=tokens[1]
        )
    except Exception as e:
        logger.error(e)

    logger.debug(f"supa sesssion {supabase_client.auth.get_session()=}")

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

    if request_data.google_news:
        metadata["google_news"] = request_data.google_news

    if request_data.yle_news:
        metadata["yle_news"] = request_data.yle_news

    panel: PanelDiscussion = PanelDiscussion(
        title=request_data.title,
        metadata=metadata,
        is_public=True,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    panel.create_sync(supabase=supabase_client)

    return panel.id


def create_panel_transcript(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    supabase_client: Client = None,
) -> UUID:
    supabase_client = (
        supabase_client
        if supabase_client is not None
        else get_sync_supabase_client(access_token=tokens[0], refresh_token=tokens[1])
    )

    # Retrieve panel metadata
    panel = PanelDiscussion.fetch_from_supabase_sync(
        supabase_client, request_data.panel_id
    )
    metadata = panel.metadata or {}

    # Load base conversation_config from PanelDiscussion metadata
    base_conversation_config = metadata.get("conversation_config", {})
    # Extend with conversation_config from request_data and apply custom_config defaults
    conversation_config = {
        **custom_config,
        **base_conversation_config,
        **(request_data.conversation_config or {}),
    }

    user_ids: UserIDs = None
    if request_data.organization_id is not None:
        user_ids = UserIDs(
            user_id=request_data.owner_id, organization_id=request_data.organization_id
        )

    # Fetch news links from GoogleNewsConfig instances
    # logger.debug(f"{metadata=}")
    google_news_configs_json = metadata.get("google_news", []) + (
        request_data.google_news or []
    )
    if not isinstance(google_news_configs_json, list):
        google_news_configs_json = [google_news_configs_json]

    # Deserialize JSON strings into GoogleNewsConfig objects
    google_news_configs = [
        GoogleNewsConfig.model_validate(config) for config in google_news_configs_json
    ]

    # logger.debug(f"{google_news_configs=}")

    article_contents = []
    article_news_items = []

    for config in google_news_configs:
        # if isinstance(
        #     config, GoogleNewsConfig
        # ):  # Ensure config is a GoogleNewsConfig instance
        for page, content in fetch_google_news_links(config):
            article_contents.append(content)

    # Fetch news links from YleNewsConfig instances
    yle_news_configs_json = metadata.get("yle_news", []) + (request_data.yle_news or [])
    if not isinstance(yle_news_configs_json, list):
        yle_news_configs_json = [yle_news_configs_json]

    yle_news_configs = [
        YleNewsConfig.model_validate(config) for config in yle_news_configs_json
    ]

    # print(f"{yle_news_configs_json=}")
    # print(f"{yle_news_configs=}")

    for config in yle_news_configs:
        news_item: NewsItem = None
        for news_item in fetch_yle_news_links(
            supabase_client, config, user_ids=user_ids
        ):
            article_contents.append(news_item.original_content)
            article_news_items.append(news_item)
            # print(f"{page=}")

    combined_sources = set()
    if request_data.input_source:
        combined_sources.update(
            request_data.input_source
            if isinstance(request_data.input_source, list)
            else [request_data.input_source]
        )
    if metadata.get("urls"):
        combined_sources.update(
            metadata["urls"]
            if isinstance(metadata["urls"], list)
            else [metadata["urls"]]
        )

    input_source = list(combined_sources)

    # logger.debug(f"{input_source=}")

    longform = (
        request_data.longform
        if request_data.longform is not None
        else metadata.get("longform", False)
    )
    input_text = request_data.input_text or metadata.get("input_text", "")

    # Concatenate article contents to input_text
    input_text += "\n\n" + "\n\n".join(article_contents)

    # Construct title
    title_elements = [
        f"{panel.title} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        conversation_config.get("output_language"),
        (
            f"{conversation_config.get('word_count')} words"
            if conversation_config.get("word_count")
            else None
        ),
        (
            f"Creativity: {conversation_config.get('creativity')}"
            if conversation_config.get("creativity")
            else None
        ),
        (
            f"Roles: {conversation_config.get('roles_person1')}, {conversation_config.get('roles_person2')}"
            if conversation_config.get("roles_person1")
            and conversation_config.get("roles_person2")
            else None
        ),
        (
            f"Structure: {', '.join(conversation_config.get('dialogue_structure', []))}"
            if conversation_config.get("dialogue_structure")
            else None
        ),
        (
            f"Techniques: {', '.join(conversation_config.get('engagement_techniques', []))}"
            if conversation_config.get("engagement_techniques")
            else None
        ),
        (
            f"[{', '.join(conversation_config.get('conversation_style', []))}]"
            if conversation_config.get("conversation_style")
            else None
        ),
    ]
    title = " - ".join(filter(None, title_elements))
    if request_data.transcript_parent_id is not None:
        title = "Recurring-" + title

    panel_transcript: PanelTranscript = PanelTranscript(
        panel_id=request_data.panel_id,
        title=title,
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        type="segment",
        metadata={
            "longform": longform,
            "conversation_config": conversation_config,
            # "max_output_tokens": request_data.max_output_tokens,
        },
        generation_interval=(
            request_data.update_cycle
            if request_data.update_cycle is None or request_data.update_cycle > 0
            else None
        ),  # Set generation_interval using update_cycle
        generation_parent=request_data.transcript_parent_id,
        is_public=True,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    panel_transcript.create_sync(supabase=supabase_client)

    for news_item in article_news_items:
        news_item.create_panel_transcript_source_reference_sync(
            supabase_client, panel_transcript
        )

    bucket_transcript_file: str = (
        f"panel_{request_data.panel_id}_{panel_transcript.id}_transcript.txt"
    )
    panel_transcript.file = bucket_transcript_file
    panel_transcript.update_sync(supabase=supabase_client)

    try:
        print(
            f"Creating {longform=} transcript for {input_source=} with {conversation_config=}"
        )
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
        panel_transcript.update_sync(supabase=supabase_client)
        raise RuntimeError("Failed to generate podcast transcript") from e

    with open(transcript_file, "rb") as transcript_src:
        supabase_client.storage.from_(request_data.bucket_name).upload(
            bucket_transcript_file, transcript_src
        )
    panel_transcript.process_state = ProcessState.done
    panel_transcript.update_sync(supabase=supabase_client)

    return panel_transcript.id


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


def create_panel_audio(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    supabase_client: Client = None,
) -> UUID:
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
    conversation_config = {
        **custom_config,
        **base_conversation_config,
        **(request_data.conversation_config or {}),
    }

    tts_model = request_data.tts_model or metadata.get("tts_model", "geminimulti")

    # Construct title
    default_voices = (
        conversation_config.get("text_to_speech", {})
        .get(tts_model, {})
        .get("default_voices", {})
    )
    title_elements = [
        f"{panel.title} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        conversation_config.get("output_language"),
        f"TTS Model: {tts_model}",
        (
            f"Voices: {default_voices.get('question')} (Q), {default_voices.get('answer')} (A)"
            if default_voices.get("question") and default_voices.get("answer")
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
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        metadata={"conversation_config": conversation_config},
        is_public=True,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    panel_audio.create_sync(supabase=supabase_client)
    bucket_audio_file: str = (
        f"panel_{panel_id}_{transcript_id}_{panel_audio.id}_audio.mp3"
    )
    panel_audio.file = bucket_audio_file

    try:
        audio_file: str = generate_podcast(
            transcript_file=transcript_file,
            tts_model=tts_model,
            conversation_config=conversation_config,
        )
    except Exception as e:
        panel_audio.process_state = ProcessState.failed
        panel_audio.process_fail_message = str(e)
        panel_audio.update_sync(supabase=supabase_client)
        raise RuntimeError("Failed to generate podcast audio") from e

    os.remove(transcript_file)
    with open(audio_file, "rb") as audio_src:
        supabase_client.storage.from_(request_data.bucket_name).upload(
            bucket_audio_file, audio_src
        )

    panel_audio.process_state = ProcessState.done
    panel_audio.update_sync(supabase=supabase_client)

    return panel_audio.id


@celery_app.task
def create_panel_audio_task(tokens: Tuple[str, str], request_data_json):
    request_data = PanelRequestData.model_validate_json(request_data_json)
    return create_panel_audio(tokens, request_data)


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

    # Fetch all PanelTranscripts with generation_interval set
    transcripts_with_interval = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase_client, filter={"generation_interval": {"neq": None}}
    )

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

    new_titles = []  # List to store titles of newly generated transcripts

    for transcript in transcripts_with_interval:
        transcript_id = transcript.id
        panel_id = transcript.panel_id
        latest_transcript: PanelTranscript = transcripts_by_parent.get(
            transcript_id, [None]
        )[0]

        if latest_transcript is None:
            latest_transcript = transcript

        if latest_transcript:
            now_aware = datetime.datetime.now(datetime.timezone.utc)
            time_since_creation = now_aware - latest_transcript.created_at
            if time_since_creation > datetime.timedelta(
                seconds=transcript.generation_interval
            ) - datetime.timedelta(minutes=10):
                # Fetch the matching PanelDiscussion model
                panel = PanelDiscussion.fetch_from_supabase_sync(
                    supabase_client, panel_id
                )
                metadata = (panel.metadata or {}) if panel is not None else {}

                # Extend the metadata with the PanelTranscript model
                transcript_metadata = (
                    (transcript.metadata or {}) if transcript is not None else {}
                )

                # Fetch the connected PanelAudio model
                audio = PanelAudio.fetch_from_supabase_sync(
                    supabase_client, transcript.id, id_column="transcript_id"
                )
                # logger.debug(f"{transcript.id=} {audio=}")
                audio_metadata = (audio.metadata or {}) if audio is not None else {}

                # Separate and extend conversation_config
                conversation_config: dict = metadata.get("conversation_config", {})
                conversation_config.update(
                    transcript_metadata.get("conversation_config", {})
                )
                metadata.update(transcript_metadata)
                metadata["conversation_config"] = conversation_config
                # metadata = transcript.metadata or {}

                new_transcript_data = PanelRequestData(
                    title=panel.title,
                    input_source=metadata.get("input_source", ""),
                    input_text=metadata.get("input_text", ""),
                    # tts_model=metadata.get("tts_model", "geminimulti"),
                    longform=metadata.get("longform", False),
                    bucket_name=metadata.get("bucket_name", "public_panels"),
                    conversation_config=metadata.get(
                        "conversation_config", custom_config
                    ),
                    panel_id=panel_id,
                    google_news=metadata.get("google_news", None),
                    yle_news=metadata.get("yle_news", None),
                    owner_id=str(panel.owner_id),
                    organization_id=str(panel.organization_id),
                    transcript_parent_id=str(transcript_id),
                )

                print(
                    f"Generating timed transcript for {transcript.id} after {time_since_creation}."
                )
                if tokens is not None:
                    transcript_id = create_panel_transcript(tokens, new_transcript_data)
                else:
                    transcript_id = create_panel_transcript(
                        tokens, new_transcript_data, supabase_client
                    )
                # Add the title and panelId of the newly generated transcript to the list
                new_titles.append(
                    f"{panel.id}: {panel.title} - {datetime.datetime.now().strftime('%Y-%m-%d')}"
                )

                metadata.update(audio_metadata)
                conversation_config.update(
                    audio_metadata.get("conversation_config", {})
                )
                metadata["conversation_config"] = conversation_config
                new_transcript_data.tts_model = audio_metadata.get(
                    "tts_model", "gemini"
                )

                new_transcript_data.transcript_id = transcript_id
                new_transcript_data.conversation_config = conversation_config
                # logger.debug(f"{transcript_id=} {new_transcript_data=}")
                if tokens is not None:
                    create_panel_audio(tokens, new_transcript_data)
                else:
                    create_panel_audio(tokens, new_transcript_data, supabase_client)
                new_transcripts_generated = True
                # Set flag to true if a new transcript is generated

            else:
                time_since_creation_str = str(time_since_creation).split(".")[
                    0
                ]  # Remove microseconds
                generation_interval_str = str(
                    datetime.timedelta(seconds=transcript.generation_interval)
                ).split(".")[
                    0
                ]  # Remove microseconds
                print(
                    f"Skip generation for {transcript.id} because time since creation is {time_since_creation_str} and minimum generation interval is {generation_interval_str}"
                )

    # After processing all transcripts, check the flag and send emails if needed
    if new_transcripts_generated:
        send_email_about_new_shows_task.delay(
            new_titles
        )  # Send emails with the new titles
