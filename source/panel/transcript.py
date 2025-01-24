import datetime
from json import dumps, loads
from typing import List, Tuple, Union, Type
from uuid import UUID
from supabase import Client

from app.core.supabase import get_sync_supabase_client
from source.chains.init import get_chain
from source.models.data.web_source import WebSource
from source.models.structures.web_source_structure import WebSourceCollection
from source.models.supabase.panel import ProcessState, PanelDiscussion, PanelTranscript
from source.models.structures.panel import PanelRequestData, custom_config

from source.helpers.sources import (
    GoogleNewsConfig,
    YleNewsConfig,
    TechCrunchNewsConfig,
    HackerNewsConfig,
    fetch_links,
)
from source.llm_exec.panel_exec import (
    generate_and_verify_transcript,
    transcript_combiner,
    transcript_summary_writer,
)
from source.models.data.user import UserIDs
from source.prompts.web_source import WebSourceGrouping


def initialize_supabase_client(
    tokens: Tuple[str, str], supabase_client: Client = None
) -> Client:
    return supabase_client or get_sync_supabase_client(
        access_token=tokens[0], refresh_token=tokens[1]
    )


def fetch_panel_metadata_and_config(
    supabase_client: Client, panel_id: UUID, request_data: PanelRequestData
) -> Tuple[dict, dict, PanelDiscussion]:
    panel = PanelDiscussion.fetch_from_supabase_sync(supabase_client, panel_id)
    metadata = panel.metadata or {}
    base_conversation_config = metadata.get("conversation_config", {})
    conversation_config = {
        **custom_config,
        **base_conversation_config,
        **(request_data.conversation_config or {}),
    }
    conversation_config["output_language"] = (
        conversation_config["output_language"] or "English"
    )
    return conversation_config, metadata, panel


def deduplicate_and_validate_configs(
    configs_json: List[dict],
    config_class: Union[
        Type[GoogleNewsConfig],
        Type[YleNewsConfig],
        Type[TechCrunchNewsConfig],
        Type[HackerNewsConfig],
    ],
) -> List:
    unique_configs = list(
        {
            dumps(
                (
                    config.model_dump(mode="json")
                    if isinstance(config, config_class)
                    else config
                ),
                sort_keys=True,
            )
            for config in configs_json
        }
    )
    return [config_class.model_validate(loads(config)) for config in unique_configs]


def fetch_links_and_process_articles(
    supabase_client: Client, sources: List, user_ids: UserIDs = None
) -> List[WebSource]:
    article_news_items = []
    for news_item in fetch_links(supabase_client, sources, user_ids=user_ids):
        article_news_items.append(news_item)
    return article_news_items


def construct_transcript_title(
    panel: PanelDiscussion, conversation_config: dict, request_data: PanelRequestData
) -> str:
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
    return title


def create_and_update_panel_transcript(
    supabase_client: Client,
    request_data: PanelRequestData,
    title: str,
    conversation_config: dict,
    longform: bool,
) -> PanelTranscript:
    panel_transcript = PanelTranscript(
        panel_id=request_data.panel_id,
        title=title,
        bucket_id=request_data.bucket_name,
        process_state=ProcessState.processing,
        type="segment",
        metadata={
            "longform": longform,
            "conversation_config": conversation_config,
        },
        generation_interval=(
            request_data.update_cycle
            if request_data.update_cycle is None or request_data.update_cycle > 0
            else None
        ),
        generation_parent=request_data.transcript_parent_id,
        is_public=True,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    panel_transcript.create_sync(supabase=supabase_client)
    return panel_transcript


def generate_transcripts(
    conversation_config: dict,
    input_text: str,
    sources: List[WebSourceCollection],
    longform: bool,
) -> Tuple[List[str], str]:
    all_transcripts = []
    combined_sources = []
    total_count = len(sources) + 1

    if longform:
        if input_text:
            transcript = generate_and_verify_transcript(
                conversation_config=conversation_config,
                content=input_text,
                urls=[],
                total_count=total_count,
            )
            combined_sources.append(input_text)
            all_transcripts.append(transcript)

        for source_collection in sources:
            transcript = generate_and_verify_transcript(
                conversation_config=conversation_config,
                source=source_collection,
                urls=[],
                total_count=total_count,
            )
            all_transcripts.append(transcript)
            combined_sources.append(source_collection)
    else:
        combined_sources = sources
        all_transcripts = [
            generate_and_verify_transcript(
                conversation_config=conversation_config,
                sources=sources,
                urls=[],
                total_count=1,
            )
        ]

    return all_transcripts, combined_sources


def group_web_sources(web_sources: List[WebSource]) -> List[WebSourceCollection]:
    # Create a list of source IDs as strings
    source_ids = {str(source.source_id) for source in web_sources}

    grouping: WebSourceGrouping = get_chain("group_web_sources_sync").invoke(
        {
            "web_sources": "\n\n".join(
                source.to_simple_str() for source in web_sources
            ),
            "start_with": "Humor or funny topic if available",
            "end_with": "Lighthearted, or funny topic if available",
        }
    )

    source_collections: List[WebSourceCollection] = []
    main_item = int(grouping.main_group)
    i = 0
    for group in grouping.ordered_groups:
        # Convert group IDs to strings
        filtered_sources = [
            source for source in web_sources if str(source.source_id) in group
        ]
        # Remove used IDs from the list
        source_ids -= {str(source.source_id) for source in filtered_sources}
        coll = WebSourceCollection(filtered_sources)
        if i == main_item:
            coll.main_item = True
        source_collections.append(coll)
        i += 1

    # print(f"Missing ids {source_ids=}, grouping ids {grouping.all_ids=}")

    # Handle any remaining IDs that were not grouped
    for remaining_id in source_ids:
        remaining_source = next(
            (source for source in web_sources if str(source.source_id) == remaining_id),
            None,
        )
        if remaining_source:
            source_collections.append(WebSourceCollection([remaining_source]))

    return source_collections


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
) -> UUID:
    supabase_client = initialize_supabase_client(tokens, supabase_client)
    conversation_config, metadata, panel = fetch_panel_metadata_and_config(
        supabase_client, request_data.panel_id, request_data
    )

    user_ids = (
        UserIDs(
            user_id=request_data.owner_id, organization_id=request_data.organization_id
        )
        if request_data.organization_id
        else None
    )

    sources = []
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("google_news", []) + (request_data.google_news or []),
            GoogleNewsConfig,
        )
    )
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("yle_news", []) + (request_data.yle_news or []), YleNewsConfig
        )
    )
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("techcrunch_news", []) + (request_data.techcrunch_news or []),
            TechCrunchNewsConfig,
        )
    )
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("hackernews", []) + (request_data.hackernews or []),
            HackerNewsConfig,
        )
    )

    if request_data.input_source:
        sources.extend(
            request_data.input_source
            if isinstance(request_data.input_source, list)
            else [request_data.input_source]
        )
    if metadata.get("urls"):
        sources.extend(
            metadata["urls"]
            if isinstance(metadata["urls"], list)
            else [metadata["urls"]]
        )

    web_sources = fetch_links_and_process_articles(supabase_client, sources, user_ids)
    title = construct_transcript_title(panel, conversation_config, request_data)
    panel_transcript = create_and_update_panel_transcript(
        supabase_client, request_data, title, conversation_config, request_data.longform
    )

    for source in web_sources:
        source.create_panel_transcript_source_reference_sync(
            supabase_client, panel_transcript
        )

    ordered_groups = group_web_sources(web_sources)

    # for col in ordered_groups:
    #     print(str(col))

    try:
        all_transcripts, combined_sources = generate_transcripts(
            conversation_config,
            request_data.input_text or "",
            ordered_groups,
            request_data.longform,
        )
        final_transcript = transcript_combiner(
            all_transcripts, combined_sources, conversation_config
        )

        transcript_summaries = transcript_summary_writer(final_transcript)

        panel_transcript.title = transcript_summaries.title
        panel_transcript.metadata["subjects"] = transcript_summaries.subjects
        panel_transcript.metadata["description"] = transcript_summaries.description

        # New code to add images to metadata
        if "images" not in panel_transcript.metadata:
            panel_transcript.metadata["images"] = []

        panel_transcript.metadata["images"] = [
            str(web_source.image)
            for collection in combined_sources
            for web_source in collection.web_sources
            if web_source.image
        ]

        upload_transcript_to_supabase(
            supabase_client,
            panel_transcript,
            final_transcript,
            request_data.bucket_name,
        )
    except Exception as e:
        panel_transcript.process_state = ProcessState.failed
        panel_transcript.process_fail_message = str(e)
        panel_transcript.update_sync(supabase=supabase_client)
        raise RuntimeError("Failed to generate podcast transcript") from e

    return panel_transcript.id
