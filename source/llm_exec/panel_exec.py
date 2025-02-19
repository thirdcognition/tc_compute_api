import re
from typing import List, Union
from datetime import datetime
from langchain_core.messages import BaseMessage
from langsmith import traceable
from source.chains.init import get_chain

# from source.helpers.translation import (
#     translate_transcript,
# )
from source.models.structures.web_source import WebSource
from source.models.structures.web_source_collection import WebSourceCollection
from source.models.structures.panel import ConversationConfig
from source.prompts.panel import (
    TranscriptQualityCheck,
    TranscriptSummary,
)


def count_words(text: str) -> int:
    cleaned_text = re.sub(r"</?person\d+>", "", text, flags=re.IGNORECASE)
    return len(cleaned_text.split())


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
            "output_language": conversation_config.output_language,
            "conversation_style": conversation_config.conversation_style,
            "roles_person1": str(conversation_config.roles_person1),
            "roles_person2": str(conversation_config.roles_person2),
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


def transcript_rewriter(
    content: str,
    orig_transcript: str,
    conversation_config: ConversationConfig = ConversationConfig(),
    word_count: int = 300,
    max_retries: int = 3,
    main_item: bool = False,
    orig_combined_transcript=None,
    previous_episodes: str = None,
):
    guidance = ""
    retry_count = 0
    check_passed = False
    change_length = True

    transcript_content = orig_transcript
    fallback_quality_check = TranscriptQualityCheck(pass_test=True, issues=[])
    previous_transcripts = (
        ""
        if orig_combined_transcript is None
        else "Original transcript:\n" + orig_combined_transcript
    )

    while (not check_passed or change_length) and retry_count < max_retries:
        change_length = False
        length_instructions = ""
        if word_count is not None:
            change_length_int, length_instructions = check_transcript_length(
                transcript_content,
                content,
                word_count,
            )
            change_length = change_length_int != 0

        retries = 3

        while change_length and change_length_int < 0 and retries > 0:
            retries -= 1
            save_content = transcript_content
            try:
                transcript_content = transcript_compress(
                    transcript=transcript_content,
                    conversation_config=conversation_config,
                )
                change_length_int = 0
            except ValueError as e:
                print(f"Error during transcript rewrite: {e}")
                transcript_content = save_content

            change_length_int, length_instructions = check_transcript_length(
                transcript_content,
                content,
                word_count,
            )
            change_length = change_length_int != 0

        print("Verify transcript quality...")
        quality_check = fallback_quality_check
        try:
            quality_check = verify_transcript_quality(
                transcript=transcript_content,
                content=content,
                conversation_config=conversation_config,
                main_item=main_item,
                length_instructions=(
                    length_instructions
                    if change_length
                    else "Transcript length is good."
                ),
                previous_episodes=previous_episodes,
            )
        except Exception as e:
            print(f"Error while verifying quality: {e}")
            quality_check = fallback_quality_check

        all_issues = sorted(
            (issue for issue in quality_check.issues if issue.severity >= 2),
            key=lambda issue: issue.severity,
            reverse=False,
        )

        quality_check.pass_test = len(all_issues) == 0
        check_passed = quality_check.pass_test

        guidance = ""
        prev_content = transcript_content
        prev_len = count_words(transcript_content)

        if not check_passed or change_length:
            while len(all_issues) > 0 or change_length:
                issues = (
                    []
                    if check_passed
                    else [all_issues.pop(0) for _ in range(min(5, len(all_issues)))]
                )
                change_length = False
                feedback = (
                    (length_instructions if change_length else "")
                    if check_passed
                    else "\n\n".join(
                        [
                            f"Issue {str(i + 1)}:\nTitle: {issue.title}\n Segments:\n{'\n\n'.join(issue.transcript_segments)}\nSuggested fix: {issue.suggestions}"
                            for i, issue in enumerate(issues)
                        ]
                    )
                )
                guidance += feedback + "\n"
                chain = (
                    "transcript_rewriter"
                    if change_length_int == 0
                    else (
                        "transcript_rewriter_extend"
                        if change_length_int == 1
                        else "transcript_rewriter_reduce"
                    )
                )

                print(
                    f"Rewrite transcript due to failed check (use chain {chain}).\n{feedback=}"
                )

                try:
                    transcript_content = _transcript_rewriter(
                        transcript=transcript_content,
                        content=content,
                        feedback=feedback,
                        conversation_config=conversation_config,
                        previous_transcripts=previous_transcripts,
                        previous_episodes=previous_episodes,
                        chain=chain,
                        word_count=word_count,
                    )
                    change_length_int = 0
                except ValueError as e:
                    print(f"Error during transcript rewrite: {e}")
                    transcript_content = prev_content

            print(f"Rewritten transcript ({count_words(transcript_content)=})")
            # previous_transcripts += (
            #     f"\n\n{'Retry ' + str(retry_count) if retry_count > 0 else 'First version'}:\n"
            #     f"Input:\n{prev_content}\n\nIssues:\n{guidance}"
            # )
            if (
                check_passed
                and (prev_len * 1.05) > count_words(transcript_content)
                and retry_count > 2
            ):
                transcript_content = prev_content
                retry_count = max_retries + 1

        retry_count += 1

    return transcript_content


@traceable(
    run_type="llm",
    name="Rewrite transcript",
)
def _transcript_rewriter(
    transcript: str,
    content: str,
    feedback: str,
    conversation_config: ConversationConfig = ConversationConfig(),
    previous_transcripts="",
    previous_episodes: str = None,
    chain: str = "transcript_rewriter",
    main_item: bool = False,
    word_count: int = None,
) -> bool:
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        result = get_chain(chain).invoke(
            {
                "content": content,
                "transcript": transcript,
                "output_language": conversation_config.output_language,
                "conversation_style": conversation_config.conversation_style,
                "roles_person1": str(conversation_config.roles_person1),
                "roles_person2": str(conversation_config.roles_person2),
                "dialogue_structure": conversation_config.dialogue_structure,
                "engagement_techniques": conversation_config.engagement_techniques,
                "user_instructions": conversation_config.user_instructions,
                "feedback": feedback,
                "previous_transcripts": previous_transcripts,
                "previous_episodes": (
                    previous_episodes if previous_episodes is not None else ""
                ),
                "podcast_name": conversation_config.podcast_name,
                "podcast_tagline": conversation_config.podcast_tagline,
                "main_item": (
                    "This is the main item of the episode. Make sure to emphasise it."
                    if main_item
                    else "False"
                ),
                "date": current_date,
                "time": current_time,
                "word_count": word_count * 1.2,
            }
        )

    if isinstance(result, BaseMessage):
        raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"LLM result {count_words(result)=}")

    return result


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
) -> bool:
    print(
        f"transcript_writer - Starting with content ({count_words(content)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        result = get_chain("transcript_writer").invoke(
            {
                "content": content,
                "output_language": conversation_config.output_language,
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
            }
        )

    if isinstance(result, BaseMessage):
        raise ValueError("Generation failed: Received a BaseMessage.")

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
) -> bool:
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
        result = get_chain("transcript_bridge_writer").invoke(
            {
                "transcript1": transcript_1,
                "transcript2": transcript_2,
                "output_language": conversation_config.output_language,
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

    if isinstance(result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return ""

    print(f"transcript_bridge_writer - Completed with result ({count_words(result)})")

    return result


@traceable(
    run_type="llm",
    name="Write transcript intro",
)
def transcript_intro_writer(
    content: str,
    conversation_config: ConversationConfig = ConversationConfig(),
    previous_episodes: str = None,
) -> bool:
    print(
        f"transcript_intro_writer - Starting with content ({count_words(content)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        result = get_chain("transcript_intro_writer").invoke(
            {
                "content": content,
                "output_language": conversation_config.output_language,
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

    if isinstance(result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return ""

    print(f"transcript_intro_writer - Completed with result ({count_words(result)})")

    return result


@traceable(
    run_type="llm",
    name="Write transcript conclusion",
)
def transcript_conclusion_writer(
    previous_dialogue: str,
    conversation_config: ConversationConfig = ConversationConfig(),
) -> bool:
    print(
        f"transcript_conclusion_writer - Starting with previous_dialogue ({count_words(previous_dialogue)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        result = get_chain("transcript_conclusion_writer").invoke(
            {
                "previous_dialogue": previous_dialogue,
                "output_language": conversation_config.output_language,
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

    if isinstance(result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return ""

    print(
        f"transcript_conclusion_writer - Completed with result ({count_words(result)})"
    )

    return result


@traceable(
    run_type="llm",
    name="Compress transcript",
)
def transcript_compress(
    transcript: str,
    conversation_config: ConversationConfig = ConversationConfig(),
) -> bool:
    print(
        f"transcript_compress - Starting with transcript ({count_words(transcript)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        result = get_chain("transcript_compress").invoke(
            {
                "transcript": transcript,
                "output_language": conversation_config.output_language,
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

    if isinstance(result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return ""

    print(f"transcript_compress - Completed with result ({count_words(result)})")

    return result


@traceable(
    run_type="llm",
    name="Translate transcript",
)
def _transcript_translate(
    transcript: str,
    target_language: str,
    conversation_config: ConversationConfig = ConversationConfig(),
) -> bool:
    print(
        f"transcript_translate - Starting with transcript ({count_words(transcript)}), conversation_config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        result = get_chain("transcript_translate").invoke(
            {
                "transcript": transcript,
                "source_language": conversation_config.output_language,
                "target_language": target_language,
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

    if isinstance(result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return ""

    print(f"transcript_translate - Completed with result ({count_words(result)})")

    return result


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
                "podcast_name": conversation_config.podcast_name,
                "podcast_tagline": conversation_config.podcast_tagline,
                "output_language": conversation_config.output_language,
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
    word_count: str | int,
) -> tuple[int, str]:
    # Compare with specified word_count and update user_instructions
    change_length = 0
    length_instruction = ""
    content_word_count = count_words(content)

    print(f"Word count: Check transcript length: {word_count=} {content_word_count=}")
    if word_count is not None:
        word_count_in_transcript = count_words(transcript)
        target_word_count = max(int(word_count), 300)
        print(
            f"Word count: Checking for target word count: {word_count_in_transcript=} {target_word_count=}"
        )
        multiplier = target_word_count / word_count_in_transcript
        if multiplier > 1.25:
            change_length = 1
            if multiplier > 2:
                length_instruction = "The transcript is too short. It should be at least three times as long. Give extensive feedback on the possible ways to extend the transcript."
                #  Try to extend on details, content, considerations and explanation. The transcript needs to be considerably longer. The transcript is too short, add more details. Write a longer version of the transcript. Do not return the same transcript. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            elif multiplier > 1.5:
                length_instruction = "The transcript is too short. It should be at least twice as long. Give feedback on the possible ways to extend the transcript."

                # Try to extend on details from content and discussion of the topic. The transcript needs to be longer. The transcript is too short, write a longer version of it. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            else:
                length_instruction = "The transcript is too short. It should be slightly longer. Give feedback on how to extend the dialogue."
            # conversation_config.user_instructions = (
            #     f"{orig_user_instr} {length_instruction}."
            # )
        elif multiplier < 0.75:
            change_length = -1
            if multiplier < 0.33:
                length_instruction = "The transcript is too long. It should be at least three times shorter. Give extensive feedback on the possible ways to shorten the transcript."
                #  Try to extend on details, content, considerations and explanation. The transcript needs to be considerably longer. The transcript is too short, add more details. Write a longer version of the transcript. Do not return the same transcript. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            elif multiplier < 0.5:
                length_instruction = "The transcript is too long. It should be half the length. Give feedback on the possible ways to shorten the transcript."

                # Try to extend on details from content and discussion of the topic. The transcript needs to be longer. The transcript is too long, write a longer version of it. Rewrite the transcript to be longer. Add more dialogue. Add more considerations. Add more insights. Add more details.
            else:
                length_instruction = "The transcript is too long. It should be slightly shorter. Give feedback on how to shorten the dialogue."
        else:
            print(
                f"Word count: Matches target close enough. {target_word_count=} {word_count_in_transcript=}"
            )
            return 0, ""
    return change_length, length_instruction


@traceable(
    run_type="llm",
    name="Generate Transcript",
)
def generate_and_verify_transcript(
    # config: dict,
    conversation_config: ConversationConfig = ConversationConfig(),
    content: str = None,
    source: WebSource | WebSourceCollection | str = None,
    urls: list = None,
    total_count=1,
    sources: List[WebSource | WebSourceCollection | str] = None,
    previous_transcripts: List[str] = None,
    previous_episodes: str = None,
) -> str:
    """
    Generate a podcast transcript and verify its quality.

    :param conversation_config: Configuration for the conversation.
    :param content: The content to be used for generating the transcript.
    :param urls: List of URLs to be included in the transcript generation.
    :return: The path to the generated transcript file.
    """
    urls = urls or []

    if isinstance(sources, WebSource) or isinstance(sources, WebSourceCollection):
        if sources is None:
            source = sources
            sources = None
        else:
            sources = [source, sources]
            source = None

    if content is None:
        content = ""
        if source is not None:
            content = str(source)

        if isinstance(sources, list):
            content += "\n\n".join(map(str, sources))

    main_item = False
    if source is not None and (
        isinstance(source, WebSource) or isinstance(source, WebSourceCollection)
    ):
        main_item = source.main_item

    orig_transcript_content = ""
    if (sources or isinstance(source, WebSourceCollection)) and total_count == 1:
        for item in sources if sources else source.web_sources:
            try:
                orig_transcript_content += transcript_writer(
                    str(item),
                    conversation_config,
                    main_item,
                    previous_transcripts,
                    previous_episodes=previous_episodes,
                )
            except Exception as e:
                print(f"Error while writing transcript: {e}")
    else:
        try:
            orig_transcript_content = transcript_writer(
                content,
                conversation_config,
                main_item,
                previous_transcripts,
                previous_episodes=previous_episodes,
            )
        except Exception as e:
            print(f"Error while writing transcript: {e}")

    # print(f"Resulting initial transcript: {orig_transcript_content=}")

    transcript_content = orig_transcript_content

    if total_count > 1:
        word_count = int(conversation_config.word_count) // (
            (total_count - 1) + (-(total_count / 4) if main_item else (total_count / 4))
        )
    else:
        word_count = int(conversation_config.word_count)

    try:
        transcript_content = transcript_rewriter(
            content=content,
            orig_transcript=transcript_content,
            conversation_config=conversation_config,
            word_count=word_count,
            max_retries=4 if total_count == 1 else 2,
            main_item=False,
            previous_episodes=previous_episodes,
        )
    except Exception as e:
        print(f"Failed to rewrite the transcript: {e}")
        transcript_content = orig_transcript_content or ""

    return transcript_content or orig_transcript_content


@traceable(
    run_type="llm",
    name="Combine transcript segments",
)
def transcript_combiner(
    transcripts: List[str],
    sources: List[WebSource | WebSourceCollection | str],
    conversation_config: ConversationConfig = ConversationConfig(),
    previous_episodes: str = None,
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
            # combined_transcripts.append(f"Topic {str(i + 1)}:\n\n{transcripts[i]}")
            combined_transcripts.append(transcripts[i])

            bridge = transcript_bridge_writer(
                transcript_1=transcripts[i],
                transcript_2=transcripts[i + 1],
                conversation_config=conversation_config,
            )

            # combined_transcripts.append(
            #     f"Bridge for Topic {str(i + 1)} and Topic {str(i + 2)}:\n\n{bridge}"
            # )
            combined_transcripts.append(bridge)
        except ValueError as e:
            print(
                f"Skipping bridge generation for topics {i + 1} and {i + 2} due to error: {e}"
            )
            continue

    if transcripts:
        # combined_transcripts.append(
        #     f"Topic {str(len(transcripts))}:\n\n{transcripts[-1]}"
        # )
        combined_transcripts.append(transcripts[-1])
    else:
        print("Error: No transcripts provided to combine.")
        raise ValueError("No transcripts provided to combine.")

    combined_transcripts.append(
        transcript_conclusion_writer(
            "\n\n".join(combined_transcripts), conversation_config
        )
    )

    orig_transcript = "\n".join(combined_transcripts)
    transcript_content = orig_transcript

    word_count = conversation_config.word_count
    word_count = (
        (word_count * article_count) // 2
        if word_count is not None and conversation_config.longform
        else word_count
    )

    try:
        transcript_content = transcript_rewriter(
            content=content,
            orig_transcript=transcript_content,
            conversation_config=conversation_config,
            word_count=word_count,
            max_retries=6,
            main_item=False,
            orig_combined_transcript=orig_transcript,
            previous_episodes=previous_episodes,
        )
    except Exception as e:
        print(f"Failed to rewrite the transcript: {e}")
        raise

    return transcript_content


@traceable(
    run_type="llm",
    name="Translate generated transcript",
)
def transcript_translate(
    transcript_content: str,
    target_language: str,
    sources: List[WebSource | WebSourceCollection | str],
    conversation_config: ConversationConfig = ConversationConfig(),
) -> str:
    content = ""
    article_count = 1
    if sources is not None:
        content = "\n\n".join(map(str, sources))
        article_count = len(sources)
    else:
        raise ValueError("Sources needed for combining resulting transcripts.")

    word_count = conversation_config.word_count
    word_count = (
        (word_count * article_count) // 2
        if word_count is not None and conversation_config.longform
        else word_count
    )

    # translated_transcript = translate_transcript(transcript_content, target_language)

    translated_transcript = _transcript_translate(
        transcript_content,
        target_language,
        conversation_config,
    )

    conversation_config_copy = conversation_config.model_copy()
    conversation_config_copy.output_language = target_language

    try:
        transcript_content = transcript_rewriter(
            content=content,
            orig_transcript=translated_transcript,
            conversation_config=conversation_config_copy,
            word_count=word_count,
            max_retries=6,
            main_item=False,
            orig_combined_transcript=transcript_content,
        )
    except Exception as e:
        print(f"Failed to translate the transcript: {e}")
        raise

    return transcript_content
