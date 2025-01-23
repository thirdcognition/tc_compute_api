# import os
import re
from typing import List
from source.chains.init import get_chain

# from podcastfy.client import generate_podcast

# from source.load_env import SETTINGS


def count_words(text: str) -> int:
    """
    Count the number of words in a given text, excluding special tags like <person1> or <person2>.

    :param text: The input text to count words in.
    :return: The word count as an integer.
    """
    cleaned_text = re.sub(r"</?person\d+>", "", text, flags=re.IGNORECASE)
    return len(cleaned_text.split())


def verify_transcript_quality(
    transcript: str, content: str, conversation_config: dict = {}
) -> tuple[bool, str]:
    result = get_chain("verify_transcript_quality").invoke(
        {
            "content": content,
            "transcript": transcript,
            "output_language": conversation_config.get("output_language", ""),
            "conversation_style": conversation_config.get("conversation_style", ""),
            "roles_person1": conversation_config.get("roles_person1", ""),
            "roles_person2": conversation_config.get("roles_person2", ""),
            "dialogue_structure": conversation_config.get("dialogue_structure", ""),
            "engagement_techniques": conversation_config.get(
                "engagement_techniques", ""
            ),
            "user_instructions": conversation_config.get("user_instructions"),
        }
    )

    passed: bool = False
    response: str = None
    if isinstance(result, tuple):
        passed, response = result

    print(f"LLM result {passed=}")

    return passed, response  # Pass supabase


def transcript_rewriter(
    transcript: str,
    content: str,
    feedback: str,
    conversation_config: dict = {},
    previous_transcript="",
    chain: str = "transcript_rewriter",
) -> bool:
    retries = 3
    result = ""
    while result == "" and retries > 0:
        retries -= 1
        result = get_chain(chain).invoke(
            {
                "content": content,
                "transcript": transcript,
                "output_language": conversation_config.get("output_language", ""),
                "conversation_style": conversation_config.get("conversation_style", ""),
                "roles_person1": conversation_config.get("roles_person1", ""),
                "roles_person2": conversation_config.get("roles_person2", ""),
                "dialogue_structure": conversation_config.get("dialogue_structure", ""),
                "engagement_techniques": conversation_config.get(
                    "engagement_techniques", ""
                ),
                "user_instructions": conversation_config.get("user_instructions"),
                "feedback": feedback,
                "previous_transcript": previous_transcript,
                "podcast_name": conversation_config.get("podcast_name", ""),
                "podcast_tagline": conversation_config.get("podcast_tagline", ""),
            }
        )

    print(f"LLM result {count_words(result)=}")

    return result  # Pass supabase


def transcript_writer(
    content: str,
    conversation_config: dict = {},
) -> bool:
    print(
        f"transcript_writer - Starting with content ({count_words(content)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    while result == "" and retries > 0:
        retries -= 1
        result = get_chain("transcript_writer").invoke(
            {
                "content": content,
                "output_language": conversation_config.get("output_language", ""),
                "conversation_style": conversation_config.get("conversation_style", ""),
                "roles_person1": conversation_config.get("roles_person1", ""),
                "roles_person2": conversation_config.get("roles_person2", ""),
                "dialogue_structure": conversation_config.get("dialogue_structure", ""),
                "engagement_techniques": conversation_config.get(
                    "engagement_techniques", ""
                ),
                "user_instructions": conversation_config.get("user_instructions", ""),
                "podcast_name": conversation_config.get("podcast_name", ""),
                "podcast_tagline": conversation_config.get("podcast_tagline", ""),
            }
        )

    print(f"transcript_writer - Completed with result ({count_words(result)})")

    return result  # Pass supabase


def transcript_bridge_writer(
    transcript_1: str, transcript_2: str, conversation_config: dict = {}
) -> bool:
    print(
        f"transcript_bridge_writer - Starting with transcript_1 ({count_words(transcript_1)}), transcript_2 ({count_words(transcript_2)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    while result == "" and retries > 0:
        retries -= 1
        result = get_chain("transcript_bridge_writer").invoke(
            {
                "transcript1": transcript_1,
                "transcript2": transcript_2,
                "output_language": conversation_config.get("output_language", ""),
                "conversation_style": conversation_config.get("conversation_style", ""),
                "roles_person1": conversation_config.get("roles_person1", ""),
                "roles_person2": conversation_config.get("roles_person2", ""),
                "dialogue_structure": conversation_config.get("dialogue_structure", ""),
                "engagement_techniques": conversation_config.get(
                    "engagement_techniques", ""
                ),
                "user_instructions": conversation_config.get("user_instructions"),
            }
        )

    print(f"transcript_bridge_writer - Completed with result ({count_words(result)})")

    return result  # Pass supabase


def transcript_intro_writer(
    content: str,
    conversation_config: dict = {},
) -> bool:
    print(
        f"transcript_intro_writer - Starting with content ({count_words(content)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    while result == "" and retries > 0:
        retries -= 1
        result = get_chain("transcript_intro_writer").invoke(
            {
                "content": content,
                "output_language": conversation_config.get("output_language", ""),
                "conversation_style": conversation_config.get("conversation_style", ""),
                "roles_person1": conversation_config.get("roles_person1", ""),
                "roles_person2": conversation_config.get("roles_person2", ""),
                "dialogue_structure": conversation_config.get("dialogue_structure", ""),
                "engagement_techniques": conversation_config.get(
                    "engagement_techniques", ""
                ),
                "user_instructions": conversation_config.get("user_instructions", ""),
                "podcast_name": conversation_config.get("podcast_name", ""),
                "podcast_tagline": conversation_config.get("podcast_tagline", ""),
            }
        )

    print(f"transcript_intro_writer - Completed with result ({count_words(result)})")

    return result  # Pass supabase


def transcript_conclusion_writer(
    previous_dialogue: str,
    conversation_config: dict = {},
) -> bool:
    print(
        f"transcript_conclusion_writer - Starting with previous_dialogue ({count_words(previous_dialogue)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    while result == "" and retries > 0:
        retries -= 1
        result = get_chain("transcript_conclusion_writer").invoke(
            {
                "previous_dialogue": previous_dialogue,
                "output_language": conversation_config.get("output_language", ""),
                "conversation_style": conversation_config.get("conversation_style", ""),
                "roles_person1": conversation_config.get("roles_person1", ""),
                "roles_person2": conversation_config.get("roles_person2", ""),
                "dialogue_structure": conversation_config.get("dialogue_structure", ""),
                "engagement_techniques": conversation_config.get(
                    "engagement_techniques", ""
                ),
                "user_instructions": conversation_config.get("user_instructions", ""),
                "podcast_name": conversation_config.get("podcast_name", ""),
                "podcast_tagline": conversation_config.get("podcast_tagline", ""),
            }
        )

    print(
        f"transcript_conclusion_writer - Completed with result ({count_words(result)})"
    )

    return result  # Pass supabase


def check_transcript_length(
    transcript: str,
    content: str,
    total_count: int,
    word_count: str | int,
) -> tuple[bool, str]:
    # Compare with specified word_count and update user_instructions
    make_longer = False
    length_instruction = ""
    content_word_count = count_words(content)

    print(f"Word count: Check transcript length: {word_count=} {content_word_count=}")
    if word_count is not None:
        word_count_in_transcript = count_words(transcript)
        make_longer = True
        target_word_count = int(word_count) // total_count // 1.25
        print(
            f"Word count: Checking for target word count: {word_count_in_transcript=} {target_word_count=}"
        )
        if content_word_count < target_word_count and word_count_in_transcript > (
            content_word_count // 1.25
        ):
            print("Word count: Length suffices.")
            return False, ""
        if word_count_in_transcript < target_word_count:
            multiplier = target_word_count / word_count_in_transcript
            if multiplier > 2:
                length_instruction = "Make the transcript at least three times longer. Try to extend on details, content, considerations and explanation."
            elif multiplier > 1.5:
                length_instruction = "Make the transcript twice as long. Try to extend on details from content and discussion of the topic."
            else:
                length_instruction = "Make the transcript slightly longer. Try to extend on conversation and dialogue."
            # conversation_config["user_instructions"] = (
            #     f"{orig_user_instr} {length_instruction}."
            # )
        print(f"Word count: Resulting instructions: {length_instruction=}")
    return make_longer, length_instruction


def generate_and_verify_transcript(
    # config: dict,
    conversation_config: dict,
    content: str = "",
    urls: list = None,
    total_count=1,
) -> str:
    """
    Generate a podcast transcript and verify its quality.

    :param conversation_config: Configuration for the conversation.
    :param content: The content to be used for generating the transcript.
    :param urls: List of URLs to be included in the transcript generation.
    :return: The path to the generated transcript file.
    """
    urls = urls or []
    max_count = 3
    guidance = ""

    print(f"Generate transcript with: {conversation_config=}")

    # Generate the initial transcript - unable to configure open ai so it's google.
    # transcript_file: str = generate_podcast(
    #     urls=urls,
    #     transcript_only=True,
    #     longform=conversation_config.get("longform", False),
    #     config=config,
    #     conversation_config=conversation_config,
    #     text=content,
    # )

    # # Read the transcript file once
    # with open(transcript_file, "r") as transcript_src:
    #     orig_transcript_content = transcript_src.read()

    orig_transcript_content = transcript_writer(content, conversation_config)

    print(f"Resulting initial transcript: {orig_transcript_content=}")

    transcript_content = orig_transcript_content

    retry_count = 0
    check_passed = False

    while not check_passed and retry_count < max_count:
        check_passed, guidance = verify_transcript_quality(
            transcript=transcript_content,
            content=content,
            conversation_config=conversation_config,
        )

        make_longer = False
        if conversation_config.get("word_count") is not None:
            make_longer, length_instructions = check_transcript_length(
                transcript_content,
                content,
                total_count,
                conversation_config.get("word_count"),
            )

        if not check_passed or make_longer:
            # Rewrite the transcript if verification fails
            print(
                f"Rewrite transcript due to failed check. {length_instructions=}, {guidance=}"
            )
            transcript_content = transcript_rewriter(
                transcript=transcript_content,
                content=content,
                feedback=("" if check_passed else guidance)
                + " "
                + (length_instructions if make_longer else ""),
                conversation_config=conversation_config,
                previous_transcript=(
                    orig_transcript_content
                    if transcript_content is not orig_transcript_content
                    else ""
                ),
            )
            print(
                f"Rewritten transcript ({count_words(transcript_content)=}): {transcript_content=}"
            )
        retry_count += 1

    # Ensure the final transcript is saved after the last rewrite attempt
    # with open(transcript_file.replace(".txt", "_final.txt"), "w") as final_transcript:
    #     final_transcript.write(transcript_content)

    return transcript_content


def transcript_combiner(
    transcripts: List[str], content: str, conversation_config: dict = {}
) -> str:
    # Initialize a list to hold the combined transcripts with bridges
    combined_transcripts = []

    combined_transcripts.append(transcript_intro_writer(content, conversation_config))

    # Iterate through the transcripts and add bridges between them
    for i in range(len(transcripts) - 1):
        # Add the current transcript
        combined_transcripts.append(f"Topic {str(i + 1)}:\n\n{transcripts[i]}")

        # Generate a bridge between the current and the next transcript
        bridge = transcript_bridge_writer(
            transcript_1=transcripts[i],
            transcript_2=transcripts[i + 1],
            conversation_config=conversation_config,
        )

        # Add the generated bridge
        combined_transcripts.append(
            f"Bridge for Topic {str(i + 1)} and Topic {str(i + 2)}:\n\n{bridge}"
        )

    # Add the last transcript (no bridge needed after the last one)
    if transcripts:
        combined_transcripts.append(
            f"Topic {str(len(transcripts))}:\n\n{transcripts[-1]}"
        )
    else:
        print("Error: No transcripts provided to combine.")
        return "Error: No transcripts provided to combine."

    combined_transcripts.append(
        transcript_conclusion_writer(
            "\n\n".join(combined_transcripts), conversation_config
        )
    )

    # Combine all transcripts and bridges into a single string
    orig_transcript = "\n".join(combined_transcripts)

    print(
        f"Combine transcripts ({len(transcripts)=} = {count_words(orig_transcript)=} chars) into one with: {conversation_config=}"
    )

    # Process the combined transcript using the transcript_combiner chain
    transcript_content = get_chain("transcript_combiner").invoke(
        {
            "content": content,
            "transcript": orig_transcript,
            "output_language": conversation_config.get("output_language", ""),
            "conversation_style": conversation_config.get("conversation_style", ""),
            "roles_person1": conversation_config.get("roles_person1", ""),
            "roles_person2": conversation_config.get("roles_person2", ""),
            "dialogue_structure": conversation_config.get("dialogue_structure", ""),
            "engagement_techniques": conversation_config.get(
                "engagement_techniques", ""
            ),
            "user_instructions": conversation_config.get("user_instructions"),
            "podcast_name": conversation_config.get("podcast_name", ""),
            "podcast_tagline": conversation_config.get("podcast_tagline", ""),
        }
    )

    print("Combiner result:")
    print(f"Input ({count_words(orig_transcript)=}): {orig_transcript}")
    print(f"Output ({count_words(transcript_content)=}): {transcript_content}")

    max_count = 5
    retry_count = 0
    check_passed = False

    while not check_passed and retry_count < max_count:
        check_passed, guidance = verify_transcript_quality(
            transcript=transcript_content,
            content=content,
            conversation_config=conversation_config,
        )

        word_count = conversation_config.get("word_count")
        make_longer = False
        if word_count is not None:
            make_longer, length_instructions = check_transcript_length(
                transcript_content,
                content,
                1,
                word_count,
            )

        if not check_passed or make_longer:
            # Rewrite the transcript if verification fails
            print(
                f"Rewrite transcript due to failed check. {length_instructions=} {guidance=}"
            )
            transcript_content = transcript_rewriter(
                transcript=transcript_content,
                content=content,
                feedback=("" if check_passed else guidance)
                + " "
                + (length_instructions if make_longer else ""),
                conversation_config=conversation_config,
                previous_transcript=(
                    orig_transcript if transcript_content is not orig_transcript else ""
                ),
                chain="transcript_combined_rewriter",
            )
            print(
                f"Rewritten transcript ({count_words(transcript_content)=}): {transcript_content=}"
            )
        retry_count += 1

    # print(f"LLM result {count_words(transcript_content)=}")

    return transcript_content  # Pass supabase
