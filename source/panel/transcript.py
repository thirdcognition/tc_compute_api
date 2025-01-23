import datetime
from json import dumps, loads
from typing import List, Tuple
from uuid import UUID
from supabase import Client

from app.core.supabase import get_sync_supabase_client
from source.models.data.web_source import WebSource
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
    count_words,
    generate_and_verify_transcript,
    transcript_combiner,
)
from source.models.data.user import UserIDs

# from source.models.config.logging import logger


# content_gen_config = {
#     "llm_model": "gemini-1.5-pro-latest",
#     "meta_llm_model": "gemini-1.5-pro-latest",
#     "max_output_tokens": 8192,
#     "prompt_template": "souzatharsis/podcastfy_multimodal_cleanmarkup",
#     "prompt_commit": "b2365f11",
#     "longform_prompt_template": "souzatharsis/podcastfy_longform",
#     "longform_prompt_commit": "acfdbc91",
#     "cleaner_prompt_template": "souzatharsis/podcastfy_longform_clean",
#     "cleaner_prompt_commit": "8c110a0b",
#     "rewriter_prompt_template": "souzatharsis/podcast_rewriter",
#     "rewriter_prompt_commit": "8ee296fb",
# }


def create_panel_transcript(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    supabase_client: Client = None,
) -> UUID:
    print(f"Creating panel transcript with request data: {request_data}")
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

    # Combine all news configurations and URLs
    sources = []

    google_news_configs_json = metadata.get("google_news", []) + (
        request_data.google_news or []
    )
    if not isinstance(google_news_configs_json, list):
        google_news_configs_json = [google_news_configs_json]

    # Deduplicate configurations
    # Debug: Log initial configurations

    unique_google_news_configs = list(
        {
            dumps(
                (
                    config.model_dump(mode="json")
                    if isinstance(config, GoogleNewsConfig)
                    else config
                ),
                sort_keys=True,
            )
            for config in google_news_configs_json
        }
    )

    # Debug: Log deduplicated configurations
    google_news_configs = [
        GoogleNewsConfig.model_validate(loads(config))
        for config in unique_google_news_configs
    ]

    sources.extend(google_news_configs)

    yle_news_configs_json = metadata.get("yle_news", []) + (request_data.yle_news or [])
    if not isinstance(yle_news_configs_json, list):
        yle_news_configs_json = [yle_news_configs_json]

    # Deduplicate configurations
    # Debug: Log initial configurations

    unique_yle_news_configs = list(
        {
            dumps(
                (
                    config.model_dump(mode="json")
                    if isinstance(config, YleNewsConfig)
                    else config
                ),
                sort_keys=True,
            )
            for config in yle_news_configs_json
        }
    )

    # Debug: Log deduplicated configurations
    yle_news_configs = [
        YleNewsConfig.model_validate(loads(config))
        for config in unique_yle_news_configs
    ]

    sources.extend(yle_news_configs)

    techcrunch_news_configs_json = metadata.get("techcrunch_news", []) + (
        request_data.techcrunch_news or []
    )
    if not isinstance(techcrunch_news_configs_json, list):
        techcrunch_news_configs_json = [techcrunch_news_configs_json]

    # Deduplicate configurations
    # Debug: Log initial configurations

    unique_techcrunch_news_configs = list(
        {
            dumps(
                (
                    config.model_dump(mode="json")
                    if isinstance(config, TechCrunchNewsConfig)
                    else config
                ),
                sort_keys=True,
            )
            for config in techcrunch_news_configs_json
        }
    )

    # Debug: Log deduplicated configurations
    techcrunch_news_configs = [
        TechCrunchNewsConfig.model_validate(loads(config))
        for config in unique_techcrunch_news_configs
    ]

    sources.extend(techcrunch_news_configs)

    hackernews_configs_json = metadata.get("hackernews", []) + (
        request_data.hackernews or []
    )
    if not isinstance(hackernews_configs_json, list):
        hackernews_configs_json = [hackernews_configs_json]

    # Deduplicate configurations
    # Debug: Log initial configurations

    unique_hackernews_configs = list(
        {
            dumps(
                (
                    config.model_dump(mode="json")
                    if isinstance(config, HackerNewsConfig)
                    else config
                ),
                sort_keys=True,
            )
            for config in hackernews_configs_json
        }
    )

    # Debug: Log deduplicated configurations
    hackernews_configs = [
        HackerNewsConfig.model_validate(loads(config))
        for config in unique_hackernews_configs
    ]

    sources.extend(hackernews_configs)

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

    # Fetch all links using the updated fetch_links method
    article_contents: List[str] = []
    article_news_items: List[WebSource] = []
    for news_item in fetch_links(supabase_client, sources, user_ids=user_ids):
        article_contents.append(
            news_item.formatted_content
            if news_item.formatted_content is not None
            else news_item.original_content
        )
        article_news_items.append(news_item)

    longform = (
        request_data.longform
        if request_data.longform is not None
        else metadata.get("longform", False)
    )
    input_text = request_data.input_text or metadata.get("input_text", "")

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
    print(f"Panel Transcript created with title: {title}")
    panel_transcript.create_sync(supabase=supabase_client)
    print(f"Panel Transcript ID: {panel_transcript.id}")

    for news_item in article_news_items:
        news_item.create_panel_transcript_source_reference_sync(
            supabase_client, panel_transcript
        )

    bucket_transcript_file: str = (
        f"panel_{request_data.panel_id}_{panel_transcript.id}_transcript.txt"
    )
    panel_transcript.file = bucket_transcript_file
    panel_transcript.update_sync(supabase=supabase_client)
    # final_transcript_content: str = None

    combined_content = ""

    all_transcripts = []
    try:
        total_count = len(article_contents) + (1 if input_text else 0)
        # Collect all generated transcript contents

        # first = True

        # Generate transcript for each input source, input text, and article content
        if input_text:
            # content_gen_config["prompt_template"] = (
            #     "heurekalabs/podcastfy_multimodal_cleanmarkup_middle"
            #     if not first
            #     else "heurekalabs/podcastfy_multimodal_cleanmarkup_beginning"
            # )
            # content_gen_config["prompt_commit"] = (
            #     "4433a387" if not first else "5be2e760"
            # )
            transcript = generate_and_verify_transcript(
                # config={"content_generator": content_gen_config},
                conversation_config=conversation_config,
                content=input_text,
                urls=[],
                total_count=total_count,
            )
            # first = False
            combined_content += input_text + "\n\n"
            all_transcripts.append(transcript)

        # i = 0

        for content in article_contents:
            # i += 1
            # last = i == (total_count - 1)
            if content:
                # if first and not last:
                #     content_gen_config["prompt_template"] = (
                #         "heurekalabs/podcastfy_multimodal_cleanmarkup_middle"
                #         if not first
                #         else "heurekalabs/podcastfy_multimodal_cleanmarkup_beginning"
                #     )
                #     content_gen_config["prompt_commit"] = (
                #         "4433a387" if not first else "5be2e760"
                #     )
                #     first = False
                # elif not first:
                #     content_gen_config["prompt_template"] = (
                #         "heurekalabs/podcastfy_multimodal_cleanmarkup_middle"
                #         if not last
                #         else "heurekalabs/podcastfy_multimodal_cleanmarkup_ending"
                #     )
                #     content_gen_config["prompt_commit"] = (
                #         "4433a387" if not first else "f107708c"
                #     )
                transcript = generate_and_verify_transcript(
                    # config={"content_generator": content_gen_config},
                    conversation_config=conversation_config,
                    content=content,
                    urls=[],
                    total_count=total_count,
                )
                print(
                    f"Append transcript ({len(all_transcripts)}): {count_words(transcript)} words"
                )
                all_transcripts.append(transcript)
                combined_content += content + "\n\n"

        # Join all transcripts into a single content

        # combined_transcript =

        print(
            f"Combined transcript {len(all_transcripts)=}: Total words: {sum(count_words(t) for t in all_transcripts)}"
        )

    except Exception as e:
        panel_transcript.process_state = ProcessState.failed
        panel_transcript.process_fail_message = str(e)
        panel_transcript.update_sync(supabase=supabase_client)
        print(f"Error during transcript generation: {e}")
        raise RuntimeError("Failed to generate podcast transcript") from e

    final_transcript = transcript_combiner(
        all_transcripts, combined_content, conversation_config
    )

    print(f"Final transcript total words: {count_words(final_transcript)}")
    print(
        f"Uploading transcript file: {bucket_transcript_file} to bucket: {request_data.bucket_name}"
    )
    supabase_client.storage.from_(request_data.bucket_name).upload(
        path=bucket_transcript_file, file=final_transcript.encode("utf-8")
    )
    panel_transcript.process_state = ProcessState.done
    panel_transcript.update_sync(supabase=supabase_client)
    print("Panel Transcript process state updated to done.")

    return panel_transcript.id
