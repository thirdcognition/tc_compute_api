from typing import List, Union

from langchain_core.messages import BaseMessage
from langsmith import traceable

from source.chains import get_chain
from source.models.structures.panel import (
    ConversationConfig,
    OutputLanguageOptions,
    SummaryReference,
    TranscriptSummary,
)
from source.models.structures.web_source import WebSource
from source.models.structures.web_source_collection import WebSourceCollection

# Relative import from the same package
from .base import count_words


@traceable(
    run_type="llm",
    name="Write transcript summary",
)
def transcript_summary_writer(
    transcript: str,
    sources: List[Union[WebSource, WebSourceCollection, str]],
    conversation_config: ConversationConfig = ConversationConfig(),
) -> TranscriptSummary:
    print(
        f"transcript_summary_writer - Starting with transcript ({count_words(transcript)} words)"
    )

    # subjects = "- " + "\n- ".join(
    #     [
    #         source.title or (source.source_model.title if source.source_model else "")
    #         for source in sources
    #         if isinstance(source, (WebSource, WebSourceCollection))
    #     ]
    # )

    retries = 3
    result = None
    while not result and retries > 0:
        retries -= 1
        try:
            result: TranscriptSummary = get_chain(
                "transcript_summary_formatter_sync"  # Assuming this chain exists and is correctly named
            ).invoke(
                {
                    "transcript": transcript,
                    "subjects": "\n\n".join(
                        [
                            (
                                source.short_string()
                                if isinstance(source, (WebSource, WebSourceCollection))
                                else str(source or "")
                            )
                            for source in sources
                        ]
                    ),
                    "podcast_name": conversation_config.podcast_name,
                    "podcast_tagline": conversation_config.podcast_tagline,
                    "output_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ].value,
                }
            )
        except Exception as e:
            print(f"Error invoking transcript_summary_formatter_sync chain: {e}")
            result = None  # Ensure result is None on error
            continue  # Try again if retries left

        if isinstance(result, BaseMessage):
            print("Generation failed: Received a BaseMessage. Retrying...")
            result = None  # Reset result to trigger retry
            continue

        # Basic validation if needed (e.g., check if essential fields are present)
        if not result or not result.title or not result.subjects:
            print("Generation failed: Summary missing essential fields. Retrying...")
            result = None
            continue

    if not result:
        raise ValueError("Failed to generate transcript summary after retries.")

    # Process references
    for item in result.subjects:
        if item.references:
            new_references = []
            processed_ids = (
                set()
            )  # Keep track of processed source IDs to avoid duplicates
            for reference_input in item.references:
                reference_id = None
                if isinstance(reference_input, SummaryReference):
                    reference_id = reference_input.id
                elif isinstance(
                    reference_input, str
                ):  # Handle if reference is just an ID string
                    reference_id = reference_input
                else:
                    # Handle unexpected reference types if necessary
                    print(
                        f"Warning: Unexpected reference type in summary: {type(reference_input)}"
                    )
                    continue

                if not reference_id:
                    continue

                for source in sources:
                    if isinstance(source, str):
                        continue  # Skip plain string sources for matching

                    match = source.find_match(reference_id)
                    if match:
                        # Use a unique identifier for the match to avoid duplicates
                        match_unique_id = match.source_id or (
                            match.source_model.id if match.source_model else None
                        )
                        if match_unique_id and match_unique_id not in processed_ids:
                            new_references.append(
                                SummaryReference(
                                    id=match_unique_id,
                                    title=match.title,
                                    image=match.image,
                                    url=match.get_url(),
                                    publish_date=match.publish_date,
                                )
                            )
                            processed_ids.add(match_unique_id)
                        # Break inner loop once a match is found for this reference_id
                        # Assuming one reference ID maps to one source match
                        break
            item.references = new_references

    print("transcript_summary_writer - Completed.")
    return result
