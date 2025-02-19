import datetime
import time
from typing import List, Tuple
from uuid import UUID, uuid4
from supabase import Client
from celery import group
from celery.result import AsyncResult
from app.core.supabase import get_sync_supabase_client

# from source.llm_exec.websource_exec import group_web_sources
from source.models.structures.web_source import WebSource
from source.models.structures.web_source_collection import WebSourceCollection
from source.models.supabase.panel import ProcessState, PanelDiscussion, PanelTranscript
from source.models.structures.panel import (
    PanelRequestData,
    custom_config,
    ConversationConfig,
)

from source.helpers.sources import (
    fetch_links,
    manage_news_sources,
)
from source.llm_exec.panel_exec import (
    transcript_combiner,
    transcript_summary_writer,
    transcript_translate,
)
from source.models.structures.user import UserIDs
from source.tasks.transcript import (
    generate_and_verify_transcript_task,
    serialize_sources,
)


def initialize_supabase_client(
    tokens: Tuple[str, str], supabase_client: Client = None
) -> Client:
    return supabase_client or get_sync_supabase_client(
        access_token=tokens[0], refresh_token=tokens[1]
    )


def fetch_panel_metadata_and_config(
    supabase_client: Client,
    panel_id: UUID | PanelDiscussion,
    request_data: PanelRequestData,
) -> Tuple[ConversationConfig, dict, PanelDiscussion]:
    panel = (
        panel_id
        if isinstance(panel_id, PanelDiscussion)
        else PanelDiscussion.fetch_from_supabase_sync(supabase_client, panel_id)
    )
    metadata = panel.metadata or {}
    base_conversation_config = metadata.get("conversation_config", {})

    config = {
        **custom_config,
        **base_conversation_config,
        **(request_data.conversation_config.model_dump() or {}),
    }
    if not isinstance(config.get("roles_person1", {}), dict):
        config["roles_person1"] = {"role": config.get("roles_person1", "")}

    if not isinstance(config.get("roles_person2", {}), dict):
        config["roles_person2"] = {"role": config.get("roles_person2", "")}

    conversation_config = ConversationConfig(**config)
    conversation_config.output_language = (
        conversation_config.output_language or "English"
    )
    return conversation_config, metadata, panel


def fetch_links_and_process_articles(
    supabase_client: Client,
    sources: List,
    user_ids: UserIDs = None,
    guidance="",
    max_items=5,
    tokens: tuple = None,
) -> List[WebSource | WebSourceCollection]:
    article_news_items = []
    for news_item in fetch_links(
        supabase_client,
        sources,
        user_ids=user_ids,
        guidance=guidance,
        max_items=max_items,
        tokens=tokens,
    ):
        article_news_items.append(news_item)
    return article_news_items


def construct_transcript_title(
    panel: PanelDiscussion,
    conversation_config: ConversationConfig,
    request_data: PanelRequestData,
) -> str:
    title_elements = [
        f"{panel.title} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        conversation_config.output_language,
        (
            f"{conversation_config.word_count} words"
            if conversation_config.word_count
            else None
        ),
        (
            f"Creativity: {conversation_config.creativity}"
            if conversation_config.creativity
            else None
        ),
        (
            f"Roles: {str(conversation_config.roles_person1)}, {str(conversation_config.roles_person2)}"
            if str(conversation_config.roles_person1)
            and str(conversation_config.roles_person2)
            else None
        ),
        (
            f"Structure: {', '.join(conversation_config.dialogue_structure)}"
            if conversation_config.dialogue_structure
            else None
        ),
        (
            f"Techniques: {', '.join(conversation_config.engagement_techniques)}"
            if conversation_config.engagement_techniques
            else None
        ),
        (
            f"[{', '.join(conversation_config.conversation_style)}]"
            if conversation_config.conversation_style
            else None
        ),
    ]
    title = " - ".join(filter(None, title_elements))
    if request_data.transcript_parent_id is not None:
        title = "Recurring-" + title
    return title


def create_and_update_panel_transcript(
    supabase_client: Client,
    request_data: PanelRequestData,
    title: str,
    conversation_config: ConversationConfig,
    longform: bool,
    language: str = "english",
    parent_id: str = None,
) -> PanelTranscript:
    panel_transcript = PanelTranscript(
        panel_id=request_data.panel_id,
        title=title,
        lang=language,
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        type="segment",
        metadata={
            "longform": longform,
            "conversation_config": conversation_config.model_dump(),
        },
        generation_cronjob=request_data.cronjob,
        transcript_parent_id=parent_id or request_data.transcript_parent_id,
        is_public=request_data.is_public,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    panel_transcript.create_sync(supabase=supabase_client)
    return panel_transcript


def generate_transcripts(
    conversation_config: ConversationConfig,
    input_text: str,
    sources: List[WebSourceCollection],
    longform: bool,
    previous_episodes: str = None,
) -> Tuple[List[str], str]:
    all_transcripts = []
    combined_sources = []
    total_count = len(sources) + 1
    # Prepare tasks for parallel execution
    tasks = []

    if longform:
        if input_text:
            task_id = str(uuid4())  # Generate a unique ID for the task
            task = generate_and_verify_transcript_task.s(
                conversation_config_json=conversation_config.model_dump(),
                content=input_text,
                sources_json=None,
                previous_transcripts=None,
                previous_episodes=previous_episodes,
                total_count=total_count,
            ).set(
                task_id=task_id
            )  # Set the task ID
            tasks.append(task)
            combined_sources.append(input_text)

        for source_collection in sources:
            serialized = serialize_sources(source_collection)
            task_id = str(uuid4())  # Generate a unique ID for the task
            task = generate_and_verify_transcript_task.s(
                conversation_config_json=conversation_config.model_dump(),
                content=None,
                sources_json=serialized,
                previous_transcripts=None,
                previous_episodes=previous_episodes,
                total_count=total_count,
            ).set(
                task_id=task_id
            )  # Set the task ID
            tasks.append(task)
            combined_sources.append(source_collection)

    else:
        combined_sources = [input_text] + sources if input_text else sources
        serialized = serialize_sources(combined_sources)

        task_id = str(uuid4())  # Generate a unique ID for the task
        task = generate_and_verify_transcript_task.s(
            conversation_config_json=conversation_config.model_dump(),
            content=None,
            sources_json=serialized,
            previous_transcripts=None,
            previous_episodes=previous_episodes,
            total_count=1,
        ).set(
            task_id=task_id
        )  # Set the task ID
        tasks.append(task)

    # Execute tasks in parallel using Celery group
    task_group = group(tasks)
    async_result: AsyncResult = task_group.apply_async(disable_sync_subtasks=False)
    start_time = time.time()
    timeout = 30 * 60
    elapsed_time = 0
    while not async_result.ready() and elapsed_time < timeout:
        elapsed_time = time.time() - start_time
        print(
            f"Build transcripts: Waiting for tasks to complete ({elapsed_time:.2f}s)..."
        )
        time.sleep(30)  # Sleep for 5 seconds to avoid busy-waiting

    if not async_result.ready() and elapsed_time >= timeout:
        print("Timeout reached! Revoking pending tasks...")
        for task in task_group:
            if task is None or task.id is None:
                continue
            async_task_result = AsyncResult(task.id)
            task_state = async_task_result.state
            if task_state == "PENDING":
                async_task_result.revoke(terminate=False)  # Only cancel pending tasks
                print(f"Task {task.id} revoked (state: {task_state}).")
            else:
                print(f"Task {task.id} not revoked (state: {task_state}).")

    results = None
    # Process results asynchronously
    if async_result.successful():
        results = async_result.get(disable_sync_subtasks=False)
    else:
        raise Exception("Error while generating transcripts...")

    # Collect results
    for result in results:
        if result:  # Ensure the task succeeded
            all_transcripts.append(result)

    return all_transcripts, combined_sources


def upload_transcript_to_supabase(
    supabase_client: Client,
    panel_transcript: PanelTranscript,
    final_transcript: str,
    bucket_name: str,
):
    bucket_transcript_file = (
        f"panel_{panel_transcript.panel_id}_{panel_transcript.id}_transcript.txt"
    )
    supabase_client.storage.from_(bucket_name).upload(
        path=bucket_transcript_file, file=final_transcript.encode("utf-8")
    )
    panel_transcript.file = bucket_transcript_file
    panel_transcript.process_state = ProcessState.done
    panel_transcript.update_sync(supabase=supabase_client)


def create_panel_transcript(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    supabase_client: Client = None,
) -> list[UUID]:
    supabase_client = initialize_supabase_client(tokens, supabase_client)
    conversation_config, metadata, panel = fetch_panel_metadata_and_config(
        supabase_client, request_data.panel_id, request_data
    )

    title = construct_transcript_title(panel, conversation_config, request_data)
    panel_transcript = create_and_update_panel_transcript(
        supabase_client, request_data, title, conversation_config, request_data.longform
    )
    transcript_ids = []
    try:
        user_ids = (
            UserIDs(
                user_id=request_data.owner_id,
                organization_id=request_data.organization_id,
            )
            if request_data.organization_id
            else None
        )

        sources = manage_news_sources(request_data, metadata)

        input_sources = set()

        if request_data.input_source:
            input_sources = (
                request_data.input_source
                if isinstance(request_data.input_source, list)
                else [request_data.input_source]
            )

        if metadata.get("input_source"):
            metadata_sources = (
                metadata["input_source"]
                if isinstance(metadata["input_source"], list)
                else [metadata["input_source"]]
            )
            input_sources.update(metadata_sources)

        if metadata.get("urls"):
            metadata_urls = (
                metadata["urls"]
                if isinstance(metadata["urls"], list)
                else [metadata["urls"]]
            )
            input_sources.update(metadata_urls)

        if len(input_sources) > 0:
            sources.extend(list(input_sources))

        ordered_groups = fetch_links_and_process_articles(
            supabase_client,
            sources,
            user_ids,
            guidance=request_data.news_guidance,
            max_items=request_data.news_items,
            tokens=tokens,
        )

        for item in ordered_groups:
            item.create_panel_transcript_source_reference_sync(
                supabase_client, panel_transcript
            )

        # ordered_groups = group_web_sources(web_sources)

        previous_transcripts_with_content = load_last_transcripts_with_content(
            supabase_client, request_data.panel_id, 5
        )

        previous_episodes = ""

        for transcript, content in previous_transcripts_with_content:
            previous_episodes = f"Episode {transcript.created_at.strftime('%Y-%m-%d (%a) %H:%M:%S')}:\nTitle: {transcript.title}\nTranscript:\n{content}\n\n"
            print(
                f"Episode {transcript.created_at.strftime('%Y-%m-%d (%a) %H:%M:%S')}:\nTitle: {transcript.title}"
            )

        all_transcripts, combined_sources = generate_transcripts(
            conversation_config,
            (
                request_data.input_text
                if request_data.input_text
                else metadata.get("input_text", "")
            ),
            ordered_groups,
            request_data.longform,
            previous_episodes=previous_episodes,
        )
        if len(combined_sources) > 1:
            try:
                final_transcript = transcript_combiner(
                    all_transcripts,
                    combined_sources,
                    conversation_config,
                    previous_episodes=previous_episodes,
                )
            except ValueError as e:
                print(f"Skipping transcript combination due to error: {e}")
                final_transcript = "\n\n".join(all_transcripts)
        else:
            final_transcript = "\n\n".join(all_transcripts)

        transcript_summaries = transcript_summary_writer(
            final_transcript, combined_sources, conversation_config
        )

        panel_transcript.title = transcript_summaries.title
        panel_transcript.metadata["subjects"] = transcript_summaries.subjects
        panel_transcript.metadata["description"] = transcript_summaries.description

        if "images" not in panel_transcript.metadata:
            panel_transcript.metadata["images"] = []

        panel_transcript.metadata["images"] = [
            str(web_source.image)
            for collection in combined_sources
            if isinstance(collection, WebSourceCollection)
            for web_source in collection.web_sources
            if isinstance(web_source, WebSource) and web_source.image
        ]

        transcript_ids.append(panel_transcript.id)

        upload_transcript_to_supabase(
            supabase_client,
            panel_transcript,
            final_transcript,
            request_data.bucket_name,
        )

        if metadata.get("languages"):
            languages = metadata.get("languages")
            for language in languages:
                transcript_ids.append(
                    create_panel_transcript_translation(
                        request_data=request_data,
                        panel=panel,
                        parent_transcript=panel_transcript,
                        transcript=final_transcript,
                        language=language,
                        sources=ordered_groups,
                        combined_sources=combined_sources,
                        supabase_client=supabase_client,
                    )
                )
    except Exception as e:
        panel_transcript.process_state = ProcessState.failed
        panel_transcript.process_state_message = str(e)
        panel_transcript.update_sync(supabase=supabase_client)
        raise RuntimeError("Failed to generate podcast transcript") from e

    return transcript_ids


def create_panel_transcript_translation(
    request_data: PanelRequestData,
    panel: PanelDiscussion,
    parent_transcript: PanelTranscript,
    transcript: str,
    language: str,
    sources: List[WebSource | WebSourceCollection],
    combined_sources: str = "",
    supabase_client: Client = None,
) -> UUID:
    conversation_config, metadata, panel = fetch_panel_metadata_and_config(
        supabase_client, panel, request_data
    )

    conversation_config = conversation_config.model_copy()
    conversation_config.output_language = language

    title = construct_transcript_title(panel, conversation_config, request_data)
    panel_transcript = create_and_update_panel_transcript(
        supabase_client,
        request_data,
        title,
        conversation_config,
        request_data.longform,
        language=language,
        parent_id=parent_transcript.id,
    )

    try:
        for item in sources:
            item.create_panel_transcript_source_reference_sync(
                supabase_client, panel_transcript
            )

        # ordered_groups = group_web_sources(web_sources)

        final_transcript = transcript_translate(
            transcript, language, sources, conversation_config
        )

        transcript_summaries = transcript_summary_writer(
            final_transcript, combined_sources, conversation_config
        )

        panel_transcript.title = transcript_summaries.title
        panel_transcript.metadata["subjects"] = transcript_summaries.subjects
        panel_transcript.metadata["description"] = transcript_summaries.description

        if "images" not in panel_transcript.metadata:
            panel_transcript.metadata["images"] = []

        panel_transcript.metadata["images"] = [
            str(web_source.image)
            for collection in combined_sources
            if isinstance(collection, WebSourceCollection)
            for web_source in collection.web_sources
            if isinstance(web_source, WebSource) and web_source.image
        ]

        upload_transcript_to_supabase(
            supabase_client,
            panel_transcript,
            final_transcript,
            request_data.bucket_name,
        )
    except Exception as e:
        panel_transcript.process_state = ProcessState.failed
        panel_transcript.process_state_message = str(e)
        panel_transcript.update_sync(supabase=supabase_client)
        raise RuntimeError("Failed to generate podcast transcript") from e

    return panel_transcript.id


def load_last_transcripts_with_content(
    supabase_client: Client, panel_id: UUID, num_transcripts: int
) -> List[Tuple[PanelTranscript, str]]:
    """
    Load the last N transcripts for a given panelId from Supabase, including their content.

    Args:
        supabase_client (Client): The Supabase client instance.
        panel_id (UUID): The ID of the panel.
        num_transcripts (int): The number of transcripts to fetch.

    Returns:
        List[Tuple[PanelTranscript, str]]: A list of tuples, each containing a transcript object and its content.
    """
    # Fetch transcripts for the given panel_id
    transcripts = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase_client,
        filter={"panel_id": str(panel_id)},
    )

    # Sort by updated_at in descending order and limit to num_transcripts
    transcripts = [t for t in transcripts if t.process_state == ProcessState.done]
    transcripts.sort(key=lambda t: t.updated_at)
    transcripts = transcripts[:num_transcripts]

    # Load content from Supabase storage for each transcript
    transcript_tuples = []
    for transcript in transcripts:
        bucket_name = transcript.bucket_id
        file_path = transcript.file

        # Download the file content from Supabase storage
        try:
            print(
                f"Load transcript: {transcript.title}, from {bucket_name} with name {file_path}"
            )
            response = supabase_client.storage.from_(bucket_name).download(file_path)
            transcript_content = response.decode("utf-8")  # Decode the content
        except Exception as e:
            print(f"Failed to load transcript {transcript.title} because {repr(e)}")
            continue

        # Append the tuple (transcript, content) to the result list
        transcript_tuples.append((transcript, transcript_content))

    return transcript_tuples
