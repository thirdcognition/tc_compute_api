import json
from app.core.celery_app import celery_app
from source.models.structures.web_source_collection import WebSourceCollection
from source.models.structures.web_source import WebSource
from source.models.structures.panel import ConversationConfig
from source.llm_exec.panel.structure import generate_and_verify_transcript


def serialize_sources(item):
    """
    Serialize a single WebSource, WebSourceCollection, or str object into a JSON-compatible format.
    """
    if isinstance(item, list):
        # print(f"Serialize Sources: Detected list with {len(item)} items")
        return [serialize_sources(i) for i in item]
    elif isinstance(item, (WebSource, WebSourceCollection)):
        # print(f"Serialize Sources: Detected {type(item)}")
        return json.dumps(item.model_dump(), default=str)
    elif isinstance(item, str):
        # print(f"Serialize Sources: Detected {type(item)}")
        return item
    else:
        raise ValueError(f"Unsupported item type: {type(item)}")


def deserialize_sources(item_json):
    """
    Deserialize a single JSON-compatible object into a WebSource, WebSourceCollection, or str.
    """
    # print(
    #     f"Deserialize Sources: Starting deserialization for item of type {type(item_json)}"
    # )

    if isinstance(item_json, list):
        # print(f"Deserialize Sources: Detected list with {len(item_json)} items")
        return [deserialize_sources(i) for i in item_json]
    elif isinstance(item_json, dict) and "web_sources" in item_json:
        # print(
        #     "Deserialize Sources: Detected dictionary with 'web_sources' key, parsing as WebSourceCollection"
        # )
        return WebSourceCollection.model_validate(item_json)
    elif isinstance(item_json, dict):
        # print(
        #     "Deserialize Sources: Detected dictionary without 'web_sources' key, parsing as WebSource"
        # )
        return WebSource.model_validate(item_json)
    elif isinstance(item_json, str):
        # print("Deserialize Sources: Detected string")
        try:
            # Attempt to parse the string as JSON
            parsed_json = json.loads(item_json)
            # print("Deserialize Sources: Successfully parsed string as JSON")
            # Recursively deserialize the parsed JSON
            return deserialize_sources(parsed_json)
        except json.JSONDecodeError as e:
            print("Deserialize Sources: Failed to decode JSON: " + repr(e))
            # Return the original string if parsing fails
            return item_json
    else:
        error_message = f"Unsupported item type: {type(item_json)}"
        print(f"Deserialize Sources: {error_message}")
        raise ValueError(error_message)


@celery_app.task
def generate_and_verify_transcript_task(
    conversation_config_json,
    content=None,
    sources_json=None,
    previous_transcripts=None,
    previous_episodes=None,
    total_count=1,
):
    """
    Celery task to generate and verify a transcript.

    :param conversation_config_json: Serialized ConversationConfig.
    :param content: Content for the transcript.
    :param sources_json: Serialized list of WebSource objects.
    :param previous_transcripts: List of previous transcripts.
    :param previous_episodes: Serialized previous episodes.
    :return: Serialized result of the transcript generation.
    """
    # Deserialize arguments
    if isinstance(conversation_config_json, dict):
        conversation_config = ConversationConfig.model_validate(
            conversation_config_json, strict=True
        )
    else:
        conversation_config = ConversationConfig.model_validate_json(
            conversation_config_json, strict=True
        )
    sources = None
    if sources_json:
        sources = deserialize_sources(sources_json)
    previous_transcripts = previous_transcripts or []

    # Call the function
    try:
        result = generate_and_verify_transcript(
            conversation_config=conversation_config,
            content=content,
            sources=sources,
            previous_transcripts=previous_transcripts,
            previous_episodes=previous_episodes,
            total_count=total_count,
        )
    except Exception as e:
        raise ValueError(f"Task failed: {e}")

    # Serialize and return the result
    return result
