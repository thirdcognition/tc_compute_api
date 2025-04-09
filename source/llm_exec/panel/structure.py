from datetime import datetime
from typing import List, Union

from langchain_core.messages import BaseMessage
from langsmith import traceable

from source.chains import get_chain
from source.models.structures.panel import (
    ConversationConfig,
    OutputLanguageOptions,
)
from source.models.structures.web_source import WebSource
from source.models.structures.web_source_collection import WebSourceCollection

# Relative imports from the same package
from .base import count_words
from .modify import transcript_rewriter


@traceable(
    run_type="llm",
    name="Write transcript",
)
def transcript_writer(
    content: str,
    conversation_config: ConversationConfig = ConversationConfig(),
    main_item=False,
    previous_transcripts: List[str] = None,
    previous_episodes: str = None,
) -> str:  # Return type str, not bool
    print(
        f"transcript_writer - Starting with content ({count_words(content)}), conversation_config={conversation_config}"
    )
    if content is None or len(content) < 1:
        raise ValueError("Content is empty, unable to continue generation.")

    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        try:
            result = get_chain("transcript_writer").invoke(
                {
                    "content": content,
                    "output_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ].value,
                    "conversation_style": conversation_config.conversation_style,
                    "roles_person1": str(conversation_config.roles_person1),
                    "roles_person2": str(conversation_config.roles_person2),
                    "dialogue_structure": conversation_config.dialogue_structure,
                    "engagement_techniques": conversation_config.engagement_techniques,
                    "user_instructions": conversation_config.user_instructions,
                    "podcast_name": conversation_config.podcast_name,
                    "podcast_tagline": conversation_config.podcast_tagline,
                    "main_item": (
                        "This is the main item of the episode. Make sure to emphasise it."
                        if main_item
                        else "False"
                    ),
                    "date": current_date,
                    "time": current_time,
                    "previous_transcripts": (
                        ""
                        if previous_transcripts is None
                        else "\n\n".join(previous_transcripts)
                    ),
                    "previous_episodes": (
                        previous_episodes if previous_episodes is not None else ""
                    ),
                    "word_count": (
                        conversation_config.word_count * 1.2
                        if conversation_config.word_count
                        else ""
                    ),
                    "location": conversation_config.location or "Finland",
                }
            )
        except Exception as e:
            print(f"Error invoking transcript_writer chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

    if isinstance(result, BaseMessage) or not result:
        raise ValueError(
            "Generation failed for transcript_writer after multiple retries."
        )

    print(f"transcript_writer - Completed with result ({count_words(result)})")

    return result


@traceable(
    run_type="llm",
    name="Write transcript bridge",
)
def transcript_bridge_writer(
    transcript_1: str,
    transcript_2: str,
    conversation_config: ConversationConfig = ConversationConfig(),
) -> str:  # Return type str, not bool
    print(
        f"transcript_bridge_writer - Starting with transcript_1 ({count_words(transcript_1)}), transcript_2 ({count_words(transcript_2)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        try:
            result = get_chain("transcript_bridge_writer").invoke(
                {
                    "transcript1": transcript_1,
                    "transcript2": transcript_2,
                    "output_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ].value,
                    "conversation_style": conversation_config.conversation_style,
                    "roles_person1": str(conversation_config.roles_person1),
                    "roles_person2": str(conversation_config.roles_person2),
                    "dialogue_structure": conversation_config.dialogue_structure,
                    "engagement_techniques": conversation_config.engagement_techniques,
                    "user_instructions": conversation_config.user_instructions,
                    "date": current_date,
                    "time": current_time,
                }
            )
        except Exception as e:
            print(f"Error invoking transcript_bridge_writer chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

    if isinstance(result, BaseMessage):  # Check if failed after retries
        print("Generation failed for transcript_bridge_writer: Received a BaseMessage.")
        return ""  # Return empty string on failure

    print(f"transcript_bridge_writer - Completed with result ({count_words(result)})")

    return result


@traceable(
    run_type="llm",
    name="Write transcript intro",
)
def transcript_intro_writer(
    transcript: str,
    content: str,
    conversation_config: ConversationConfig = ConversationConfig(),
    previous_episodes: str = None,
) -> str:  # Return type str, not bool
    print(
        f"transcript_intro_writer - Starting with content ({count_words(content)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    chain_name = (
        "transcript_short_intro_writer"
        if conversation_config.short_intro_and_conclusion
        else "transcript_intro_writer"
    )
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        try:
            result = get_chain(chain_name).invoke(
                {
                    "transcript": transcript,
                    "content": content,
                    "output_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ].value,
                    "conversation_style": conversation_config.conversation_style,
                    "roles_person1": str(conversation_config.roles_person1),
                    "roles_person2": str(conversation_config.roles_person2),
                    "dialogue_structure": conversation_config.dialogue_structure,
                    "engagement_techniques": conversation_config.engagement_techniques,
                    "user_instructions": conversation_config.user_instructions,
                    "podcast_name": conversation_config.podcast_name,
                    "podcast_tagline": conversation_config.podcast_tagline,
                    "previous_episodes": (
                        previous_episodes if previous_episodes is not None else ""
                    ),
                    "date": current_date,
                    "time": current_time,
                }
            )
        except Exception as e:
            print(f"Error invoking {chain_name} chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

    if isinstance(result, BaseMessage):  # Check if failed after retries
        print(f"Generation failed for {chain_name}: Received a BaseMessage.")
        return ""  # Return empty string on failure

    print(
        f"transcript_intro_writer ({chain_name}) - Completed with result ({count_words(result)})"
    )

    return result


@traceable(
    run_type="llm",
    name="Write transcript conclusion",
)
def transcript_conclusion_writer(
    previous_dialogue: str,
    conversation_config: ConversationConfig = ConversationConfig(),
) -> str:  # Return type str, not bool
    print(
        f"transcript_conclusion_writer - Starting with previous_dialogue ({count_words(previous_dialogue)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    chain_name = (
        "transcript_short_conclusion_writer"
        if conversation_config.short_intro_and_conclusion
        else "transcript_conclusion_writer"
    )
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        try:
            result = get_chain(chain_name).invoke(
                {
                    "previous_dialogue": previous_dialogue,
                    "output_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ].value,
                    "conversation_style": conversation_config.conversation_style,
                    "roles_person1": str(conversation_config.roles_person1),
                    "roles_person2": str(conversation_config.roles_person2),
                    "dialogue_structure": conversation_config.dialogue_structure,
                    "engagement_techniques": conversation_config.engagement_techniques,
                    "user_instructions": conversation_config.user_instructions,
                    "podcast_name": conversation_config.podcast_name,
                    "podcast_tagline": conversation_config.podcast_tagline,
                    "date": current_date,
                    "time": current_time,
                }
            )
        except Exception as e:
            print(f"Error invoking {chain_name} chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

    if isinstance(result, BaseMessage):  # Check if failed after retries
        print(f"Generation failed for {chain_name}: Received a BaseMessage.")
        return ""  # Return empty string on failure

    print(
        f"transcript_conclusion_writer ({chain_name}) - Completed with result ({count_words(result)})"
    )

    return result


@traceable(
    run_type="llm",
    name="Generate Transcript (Core)",
)
def generate_and_verify_transcript(
    # config: dict,
    conversation_config: ConversationConfig = ConversationConfig(),
    content: str = None,
    source: Union[WebSource, WebSourceCollection, str] = None,  # Added Union
    urls: list = None,
    total_count=1,
    sources: List[Union[WebSource, WebSourceCollection, str]] = None,  # Added Union
    previous_transcripts: List[str] = None,
    previous_episodes: str = None,
    add_detail: bool = False,
) -> str:
    """
    Generate a podcast transcript segment and verify its quality.

    :param conversation_config: Configuration for the conversation.
    :param content: The content to be used for generating the transcript.
    :param source: A single primary source (optional).
    :param urls: List of URLs (legacy, likely unused if sources are provided).
    :param total_count: Total number of segments being generated in the batch.
    :param sources: List of all sources for context (optional if single source provided).
    :param previous_transcripts: Context from previously generated transcripts in the same session.
    :param previous_episodes: Context from previous episodes.
    :param add_detail: Flag to generate detailed segments per source item (if applicable).
    :return: The generated and potentially rewritten transcript segment.
    """
    urls = urls or []
    all_sources = []

    # Consolidate sources
    if source:
        all_sources.append(source)
    if sources:
        all_sources.extend(sources)

    # Build content string if not provided
    if content is None:
        content = "\n\n".join([str(s) for s in all_sources if s])

    if not content:
        print("Warning: No content provided for transcript generation.")
        # Decide behavior: return empty string, raise error, or proceed with minimal context?
        # Returning empty for now, assuming rewrite might handle it if context exists elsewhere.
        # return ""
        # Or try to generate based only on config/previous context if that's intended
        pass  # Let it proceed to writer, which might fail gracefully or use other context

    main_item = False
    # Determine main_item status from the first source if available
    if all_sources and isinstance(all_sources[0], (WebSource, WebSourceCollection)):
        main_item = all_sources[0].main_item

    orig_transcript_content = ""
    # Handle detailed generation based on 'add_detail' flag
    if add_detail and all_sources:
        # Determine the list of items to iterate over
        items_to_process = []
        for s in all_sources:
            if isinstance(s, WebSourceCollection):
                items_to_process.extend(s.web_sources)
            elif isinstance(s, WebSource):
                items_to_process.append(s)
            # Ignore string sources for detailed generation? Or treat them as single items?
            # Assuming we only do detailed generation for WebSource/WebSourceCollection items
            # else: items_to_process.append(s) # Uncomment to include string sources

        generated_segments = []
        for item in items_to_process:
            try:
                # Determine main_item status for this specific item
                item_main_item = (
                    getattr(item, "main_item", False)
                    if isinstance(item, (WebSource, WebSourceCollection))
                    else False
                )

                segment = transcript_writer(
                    str(item),  # Use string representation of the item as content
                    conversation_config,
                    item_main_item,  # Pass item's main_item status
                    previous_transcripts=(previous_transcripts or [])
                    + generated_segments,  # Provide context of prior segments in this run
                    previous_episodes=previous_episodes,
                )
                generated_segments.append(segment)
            except Exception as e:
                print(f"Error while writing detailed transcript segment: {e}")
        orig_transcript_content = "\n".join(generated_segments)  # Combine segments
    else:
        # Standard generation using combined content
        try:
            orig_transcript_content = transcript_writer(
                content,  # Use the combined content string
                conversation_config,
                main_item,  # Use overall main_item status
                previous_transcripts,
                previous_episodes=previous_episodes,
            )
        except Exception as e:
            print(f"Error while writing transcript: {e}")
            # Decide fallback: return empty, raise error?
            orig_transcript_content = ""  # Fallback to empty string

    # print(f"Resulting initial transcript: {orig_transcript_content=}")

    transcript_content = orig_transcript_content

    # Calculate word count target for rewriting
    word_count_target = None
    if conversation_config.word_count is not None:
        base_word_count = int(conversation_config.word_count)
        if total_count > 1:
            # Adjust word count based on total segments and main item status
            # This logic seems complex and might need refinement.
            # It divides the total word count, potentially unevenly.
            adjustment_factor = (total_count - 1) + (
                -total_count / 4 if main_item else total_count / 4
            )
            if adjustment_factor > 0:
                word_count_target = base_word_count // adjustment_factor
            else:
                word_count_target = (
                    base_word_count  # Fallback if factor is zero or negative
                )
        else:
            word_count_target = base_word_count

        # Ensure a minimum word count?
        word_count_target = (
            max(word_count_target, 150) if word_count_target is not None else 150
        )  # Example minimum

    # Proceed with rewriting if initial transcript exists
    if transcript_content:
        try:
            transcript_content = transcript_rewriter(
                content=content,  # Provide full content context for rewrite
                orig_transcript=transcript_content,
                conversation_config=conversation_config,
                word_count=word_count_target,  # Pass calculated target
                max_retries=(
                    4 if total_count == 1 else 2
                ),  # Adjust retries based on context
                main_item=main_item,  # Pass main_item status
                previous_episodes=previous_episodes,
            )
        except Exception as e:
            print(f"Failed to rewrite the transcript: {e}")
            # Fallback to original content if rewrite fails
            # transcript_content = orig_transcript_content # Keep the original if rewrite fails
            pass  # Keep the potentially modified content from writer if rewrite fails
    elif not orig_transcript_content:
        print("Skipping rewrite because initial transcript generation failed.")

    # Return the final content, which might be the original or the rewritten version
    return transcript_content


@traceable(
    run_type="llm",
    name="Combine transcript segments",
)
def transcript_combiner(
    transcripts: List[str],
    sources: List[Union[WebSource, WebSourceCollection, str]],  # Added Union
    conversation_config: ConversationConfig = ConversationConfig(),
    previous_episodes: str = None,
) -> str:
    combined_transcripts_parts = []
    content = ""
    article_count = 0  # Initialize count

    if sources:
        content = "\n\n".join([str(src) for src in sources if src])
        article_count = len(sources)
    # else: # Removed redundant else block
    # raise ValueError("Sources needed for combining resulting transcripts.") # Consider if sources are truly mandatory

    if not content:
        print("Warning: Combining transcripts without source content context.")
        # raise ValueError("Content is empty, unable to generate transcript.") # Optional

    if not transcripts:
        print("Error: No transcripts provided to combine.")
        raise ValueError("No transcripts provided to combine.")

    # Add Intro
    if not conversation_config.disable_intro_and_conclusion:
        try:
            intro = transcript_intro_writer(
                transcripts[0],  # Provide context from the first segment for intro
                content,
                conversation_config,
                previous_episodes,
            )
            combined_transcripts_parts.append(intro)
        except Exception as e:
            print(f"Error generating intro: {e}. Skipping intro.")

    # Add Transcripts and Bridges
    for i, transcript_segment in enumerate(transcripts):
        combined_transcripts_parts.append(transcript_segment)

        # Add bridge if not the last segment
        if i < len(transcripts) - 1:
            try:
                bridge = transcript_bridge_writer(
                    transcript_1=transcript_segment,  # End of current segment
                    transcript_2=transcripts[i + 1],  # Start of next segment
                    conversation_config=conversation_config,
                )
                combined_transcripts_parts.append(bridge)
            except ValueError as e:
                print(
                    f"Skipping bridge generation between segments {i + 1} and {i + 2} due to error: {e}"
                )
                continue  # Skip bridge on error

    # Add Conclusion
    if not conversation_config.disable_intro_and_conclusion:
        try:
            # Provide context from the combined parts so far for the conclusion
            conclusion_context = "\n".join(combined_transcripts_parts)
            conclusion = transcript_conclusion_writer(
                conclusion_context, conversation_config
            )
            combined_transcripts_parts.append(conclusion)
        except Exception as e:
            print(f"Error generating conclusion: {e}. Skipping conclusion.")

    orig_transcript = "\n".join(combined_transcripts_parts)
    transcript_content = orig_transcript

    # Calculate word count for final rewrite
    word_count_target = conversation_config.word_count
    if (
        word_count_target is not None
        and conversation_config.longform
        and article_count > 0
    ):
        word_count_target = (word_count_target * article_count) // 2

    # Final Rewrite of the combined transcript
    try:
        transcript_content = transcript_rewriter(
            content=content,  # Provide full content context
            orig_transcript=orig_transcript,
            conversation_config=conversation_config,
            word_count=word_count_target,  # Pass calculated target
            max_retries=6,  # Allow more retries for final combination
            main_item=False,  # Assume main_item less relevant for combined rewrite
            # orig_combined_transcript=orig_transcript, # Optional: pass original combined for context
            previous_episodes=previous_episodes,
        )
    except Exception as e:
        print(f"Failed to rewrite the combined transcript: {e}")
        return orig_transcript  # Return the combined-but-not-rewritten version on error

    return transcript_content
