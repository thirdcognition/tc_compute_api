from source.chains.init import get_chain


def verify_transcript_quality(transcript: str, content: str, config: dict = {}) -> bool:
    result, response = get_chain("verify_transcript_quality").invoke(
        {
            "content": content,
            "transcript": transcript,
            "output_language": config.get("output_language", ""),
            "conversation_style": config.get("conversation_style", ""),
            "roles_person1": config.get("roles_person1", ""),
            "roles_person2": config.get("roles_person2", ""),
            "dialogue_structure": config.get("dialogue_structure", ""),
            "engagement_techniques": config.get("engagement_techniques", ""),
            "word_count": config.get("word_count", ""),
        }
    )

    print(f"LLM result {result=}, response {response=}")

    return result, response  # Pass supabase
