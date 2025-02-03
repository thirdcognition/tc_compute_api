import re
from typing import List, Union
from langchain_core.messages import BaseMessage
from source.chains.init import get_chain
from source.models.data.web_source import WebSource
from source.models.structures.web_source_structure import WebSourceCollection
from source.prompts.panel import TranscriptSummary


def count_words(text: str) -> int:
    cleaned_text = re.sub(r"</?person\d+>", "", text, flags=re.IGNORECASE)
    return len(cleaned_text.split())


def verify_transcript_quality(
    transcript: str,
    content: str,
    conversation_config: dict = {},
    main_item: bool = False,
    length_instructions: str = "",
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
            "main_item": (
                "This is the main item of the episode. Make sure to emphasise it."
                if main_item
                else "False"
            ),
            "transcript_length": length_instructions,
        }
    )

    if isinstance(result, BaseMessage):
        raise ValueError("Generation failed: Received a BaseMessage.")

    passed: bool = False
    response: str = None
    if isinstance(result, tuple):
        passed, response = result

    print(f"LLM result {passed=}")

    return passed, response


def transcript_rewriter(
    transcript: str,
    content: str,
    feedback: str,
    conversation_config: dict = {},
    previous_transcript="",
    chain: str = "transcript_rewriter",
    main_item: bool = False,
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
                "main_item": (
                    "This is the main item of the episode. Make sure to emphasise it."
                    if main_item
                    else "False"
                ),
            }
        )

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"LLM result {count_words(result)=}")

    return result


def transcript_writer(
    content: str, conversation_config: dict = {}, main_item=False
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
                "main_item": (
                    "This is the main item of the episode. Make sure to emphasise it."
                    if main_item
                    else "False"
                ),
            }
        )

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"transcript_writer - Completed with result ({count_words(result)})")

    return result


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

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"transcript_bridge_writer - Completed with result ({count_words(result)})")

    return result


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

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"transcript_intro_writer - Completed with result ({count_words(result)})")

    return result


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

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    print(
        f"transcript_conclusion_writer - Completed with result ({count_words(result)})"
    )

    return result


def transcript_summary_writer(
    transcript: str,
    sources: List[Union[WebSource, WebSourceCollection, str]],
    conversation_config: dict = {},
) -> TranscriptSummary:
    print(
        f"transcript_summary_writer - Starting with transcript ({count_words(transcript)} words)"
    )

    subjects = "- " + "\n- ".join(
        [
            source.title
            for source in sources
            if isinstance(source, WebSource) or isinstance(source, WebSourceCollection)
        ]
    )

    retries = 3
    result = None
    while not result and retries > 0:
        retries -= 1
        result = get_chain("transcript_summary_formatter_sync").invoke(
            {
                "transcript": transcript,
                "subjects": subjects,
                "podcast_name": conversation_config.get("podcast_name", ""),
                "podcast_tagline": conversation_config.get("podcast_tagline", ""),
                "output_language": conversation_config.get("output_language", ""),
            }
        )

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    if not result:
        raise ValueError("Failed to generate transcript summary after retries.")

    print("transcript_summary_writer - Completed.")
    return result


def check_transcript_length(
    transcript: str,
    content: str,
    total_count: int,
    word_count: str | int,
) -> tuple[bool, str]:
    # Compare with specified word_count and update user_instructions
    change_length = False
    length_instruction = ""
    content_word_count = count_words(content)

    print(f"Word count: Check transcript length: {word_count=} {content_word_count=}")
    if word_count is not None:
        word_count_in_transcript = count_words(transcript)
        change_length = True
        target_word_count = int(word_count) // total_count // 1.25
        print(
            f"Word count: Checking for target word count: {word_count_in_transcript=} {target_word_count=}"
        )
        # if (
        #     content_word_count < target_word_count
        #     and word_count_in_transcript > (content_word_count // 1.25)
        # ) and (
        #     content_word_count > target_word_count
        #     and word_count_in_transcript < (content_word_count * 1.25)
        # ):
        #     print("Word count: Length suffices.")
        #     return False, ""
        multiplier = target_word_count / word_count_in_transcript
        if multiplier > 1.15:
            if multiplier > 2:
                length_instruction = "The transcript is too short. It should be at least three times as long. Give extensive feedback on the possible ways to extend the transcript."
                #  Try to extend on details, content, considerations and explanation. The transcript needs to be considerably longer. The transcript is too short, add more details. Write a longer version of the transcript. Do not return the same transcript. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            elif multiplier > 1.5:
                length_instruction = "The transcript is too short. It should be at least twice as long. Give feedback on the possible ways to extend the transcript."

                # Try to extend on details from content and discussion of the topic. The transcript needs to be longer. The transcript is too short, write a longer version of it. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            else:
                length_instruction = "The transcript is too short. It should be slightly longer. Give feedback on how to extend the dialogue."
            # conversation_config["user_instructions"] = (
            #     f"{orig_user_instr} {length_instruction}."
            # )
        elif multiplier < 0.85:
            if multiplier < 0.33:
                length_instruction = "The transcript is too long. It should be at least three times shorter. Give extensive feedback on the possible ways to shorten the transcript."
                #  Try to extend on details, content, considerations and explanation. The transcript needs to be considerably longer. The transcript is too short, add more details. Write a longer version of the transcript. Do not return the same transcript. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            elif multiplier < 0.5:
                length_instruction = "The transcript is too long. It should be half the length. Give feedback on the possible ways to shorten the transcript."

                # Try to extend on details from content and discussion of the topic. The transcript needs to be longer. The transcript is too long, write a longer version of it. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            else:
                length_instruction = "The transcript is too long. It should be slightly shorter. Give feedback on how to shorten the dialogue."
        else:
            print("Word count: Matches target")
            return False, ""
    return change_length, length_instruction


def generate_and_verify_transcript(
    # config: dict,
    conversation_config: dict,
    content: str = None,
    source: WebSource | WebSourceCollection | str = None,
    urls: list = None,
    total_count=1,
    sources: List[WebSource | WebSourceCollection | str] = None,
) -> str:
    """
    Generate a podcast transcript and verify its quality.

    :param conversation_config: Configuration for the conversation.
    :param content: The content to be used for generating the transcript.
    :param urls: List of URLs to be included in the transcript generation.
    :return: The path to the generated transcript file.
    """
    urls = urls or []
    max_count = 6 if total_count == 1 else 3
    guidance = ""

    if content is None:
        content = ""
        if source is not None:
            content = str(source)
        elif sources is not None:
            content = "\n\n".join(map(str, sources))

    print(f"Generate transcript with: {conversation_config=}")

    main_item = False
    if source is not None and (
        isinstance(source, WebSource) or isinstance(source, WebSourceCollection)
    ):
        main_item = source.main_item

    orig_transcript_content = transcript_writer(content, conversation_config, main_item)

    # print(f"Resulting initial transcript: {orig_transcript_content=}")

    transcript_content = orig_transcript_content

    retry_count = 0
    check_passed = False
    change_length = True

    while (not check_passed or change_length) and retry_count < max_count:
        length_instructions = ""
        if conversation_config.get("word_count") is not None:
            change_length, length_instructions = check_transcript_length(
                transcript_content,
                content,
                total_count,
                int(conversation_config.get("word_count"))
                * (1 if not main_item else 2),
            )

        check_passed, guidance = verify_transcript_quality(
            transcript=transcript_content,
            content=content,
            conversation_config=conversation_config,
            main_item=main_item,
            length_instructions=(
                length_instructions if change_length else "Transcript length is good."
            ),
        )

        if not check_passed or change_length:
            feedback = (
                (length_instructions if change_length else "")
                if check_passed
                else guidance
            )
            # Rewrite the transcript if verification fails
            print(f"Rewrite transcript due to failed check. {feedback=}")
            prev_content = transcript_content
            prev_len = count_words(transcript_content)
            transcript_content = transcript_rewriter(
                transcript=transcript_content,
                content=content,
                feedback=feedback,
                conversation_config=conversation_config,
                previous_transcript=(
                    orig_transcript_content
                    if transcript_content is not orig_transcript_content
                    else ""
                ),
            )
            print(f"Rewritten transcript ({count_words(transcript_content)=})")
            if (
                check_passed
                and (prev_len * 1.05) > count_words(transcript_content)
                and retry_count > 2
            ):
                transcript_content = prev_content
                retry_count = max_count + 1

        retry_count += 1

    # Ensure the final transcript is saved after the last rewrite attempt
    # with open(transcript_file.replace(".txt", "_final.txt"), "w") as final_transcript:
    #     final_transcript.write(transcript_content)

    return transcript_content


def transcript_combiner(
    transcripts: List[str],
    sources: List[WebSource | WebSourceCollection | str],
    conversation_config: dict = {},
) -> str:
    combined_transcripts = []
    content = ""
    article_count = 1
    if sources is not None:
        content = "\n\n".join(map(str, sources))
        article_count = len(sources)
    else:
        raise ValueError("Sources needed for combining resulting transcripts.")

    combined_transcripts.append(transcript_intro_writer(content, conversation_config))

    for i in range(len(transcripts) - 1):
        try:
            combined_transcripts.append(f"Topic {str(i + 1)}:\n\n{transcripts[i]}")

            bridge = transcript_bridge_writer(
                transcript_1=transcripts[i],
                transcript_2=transcripts[i + 1],
                conversation_config=conversation_config,
            )

            combined_transcripts.append(
                f"Bridge for Topic {str(i + 1)} and Topic {str(i + 2)}:\n\n{bridge}"
            )
        except ValueError as e:
            print(
                f"Skipping bridge generation for topics {i + 1} and {i + 2} due to error: {e}"
            )
            continue

    if transcripts:
        combined_transcripts.append(
            f"Topic {str(len(transcripts))}:\n\n{transcripts[-1]}"
        )
    else:
        print("Error: No transcripts provided to combine.")
        raise ValueError("No transcripts provided to combine.")

    combined_transcripts.append(
        transcript_conclusion_writer(
            "\n\n".join(combined_transcripts), conversation_config
        )
    )

    orig_transcript = "\n".join(combined_transcripts)

    print(
        f"Combine transcripts ({len(transcripts)=} = {count_words(orig_transcript)=} chars) into one with: {conversation_config=}"
    )

    try:
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

        if isinstance(transcript_content, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    except ValueError as e:
        print(f"Error during transcript combination: {e}")
        raise

    print("Combiner result:")
    print(f"Input ({count_words(orig_transcript)=})")
    print(f"Output ({count_words(transcript_content)=})")

    max_count = 6
    retry_count = 0
    check_passed = False
    change_length = True
    word_count = conversation_config.get("word_count")
    word_count = (
        (word_count * article_count) // 2
        if word_count is not None and conversation_config.get("longform", False)
        else word_count
    )
    while (not check_passed or change_length) and retry_count < max_count:
        change_length = False
        if word_count is not None:
            change_length, length_instructions = check_transcript_length(
                transcript_content,
                content,
                1,
                word_count,
            )

        check_passed, guidance = verify_transcript_quality(
            transcript=transcript_content,
            content=content,
            conversation_config=conversation_config,
            length_instructions=(
                length_instructions if change_length else "Transcript length is good."
            ),
        )

        if not check_passed or change_length:
            feedback = (
                (length_instructions if change_length else "")
                if check_passed
                else guidance
            )
            print(f"Rewrite transcript due to failed check. {feedback=}")
            prev_content = transcript_content
            prev_len = count_words(transcript_content)

            try:
                transcript_content = transcript_rewriter(
                    transcript=transcript_content,
                    content=content,
                    feedback=feedback,
                    conversation_config=conversation_config,
                    previous_transcript=(
                        orig_transcript
                        if transcript_content is not orig_transcript
                        else ""
                    ),
                    chain="transcript_combined_rewriter",
                )
            except ValueError as e:
                print(f"Error during transcript rewrite: {e}")
                transcript_content = prev_content

            print(f"Rewritten transcript ({count_words(transcript_content)=})")
            if (
                check_passed
                and (prev_len * 1.05) > count_words(transcript_content)
                and retry_count > 2
            ):
                transcript_content = prev_content
                retry_count = max_count + 1

        retry_count += 1

    return transcript_content
