from datetime import datetime
from langchain_core.messages import BaseMessage
from langsmith import traceable

from source.chains import get_chain
from source.models.structures.panel import (
    ConversationConfig,
    OutputLanguageOptions,
    TranscriptQualityCheck,
)


@traceable(
    run_type="llm",
    name="Verify transcript quality",
)
def verify_transcript_quality(
    transcript: str,
    content: str,
    conversation_config: ConversationConfig = ConversationConfig(),
    main_item: bool = False,
    length_instructions: str = "",
    previous_episodes: str = None,
) -> TranscriptQualityCheck:
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")

    result: TranscriptQualityCheck = get_chain("verify_transcript_quality").invoke(
        {
            "content": content,
            "transcript": transcript,
            "output_language": OutputLanguageOptions[
                conversation_config.output_language
            ].value,
            "conversation_style": conversation_config.conversation_style,
            "person_roles": "\n".join(
                [
                    f"Person {key}: {str(role)}"
                    for key, role in conversation_config.person_roles.items()
                ]
                if conversation_config.person_roles
                else ""
            ),
            "dialogue_structure": conversation_config.dialogue_structure,
            "engagement_techniques": conversation_config.engagement_techniques,
            "user_instructions": conversation_config.user_instructions,
            "main_item": (
                "This is the main item of the episode. Make sure to emphasise it."
                if main_item
                else "False"
            ),
            "transcript_length": length_instructions,
            "previous_episodes": (
                previous_episodes if previous_episodes is not None else ""
            ),
            "date": current_date,
            "time": current_time,
        }
    )

    if isinstance(result, BaseMessage):
        raise ValueError("Generation failed: Received a BaseMessage.")

    # print(f"LLM result {result=}")

    return result
