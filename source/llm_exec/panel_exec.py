from enum import Enum
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
from source.models.structures.panel import (
    ConversationConfig,
    OutputLanguageOptions,
    SummaryReference,
)
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
            "output_language": OutputLanguageOptions[
                conversation_config.output_language
            ].value,
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
    # orig_combined_transcript=None,
    previous_episodes: str = None,
):
    # guidance = ""
    retry_count = 0
    check_passed = False
    change_length = True

    transcript_content = orig_transcript
    fallback_quality_check = TranscriptQualityCheck(pass_test=True, issues=[])
    # previous_transcripts = (
    #     ""
    #     if orig_combined_transcript is None
    #     else "Original transcript:\n" + orig_combined_transcript
    # )

    length_change_fail = False

    if content is None or len(content) < 1:
        raise ValueError("Content is empty, unable to continue generation.")

    word_count = min(word_count, count_words(content) // 1.25)

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
        prev_content = transcript_content

        while not length_change_fail and change_length and retries > 0:
            retries -= 1
            save_content = transcript_content
            try:
                if change_length_int < 0:
                    transcript_content, length_change_fail = transcript_compress(
                        transcript=transcript_content,
                        conversation_config=conversation_config,
                        target=word_count,
                    )
                elif change_length_int > 0:
                    transcript_content, length_change_fail = transcript_extend(
                        transcript=transcript_content,
                        content=content,
                        conversation_config=conversation_config,
                        target=word_count,
                    )
                change_length_int = 0
            except ValueError as e:
                print(f"Error during transcript rewrite: {e}")
                length_change_fail = True
                transcript_content = save_content

            if transcript_content != save_content:
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

        # guidance = ""

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
                            f"Issue {str(i + 1)}:\nTitle: {issue.title}\nCoverage: {issue.issue_coverage.value}\nSegments:\n{'\n----\n'.join(issue.transcript_segments) if len(issue.transcript_segments) > 0 else ''}\nSuggested fix:\n{issue.suggestions}"
                            for i, issue in enumerate(issues)
                        ]
                    )
                )
                # guidance += feedback + "\n"
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

                if feedback:
                    try:
                        transcript_content = _transcript_rewriter(
                            transcript=transcript_content,
                            content=content,
                            feedback=feedback,
                            conversation_config=conversation_config,
                            # previous_transcripts=previous_transcripts,
                            previous_episodes=previous_episodes,
                            chain=chain,
                            word_count=word_count,
                        )
                        change_length_int = 0
                    except ValueError as e:
                        print(f"Error during transcript rewrite: {e}")
                        transcript_content = prev_content
                else:
                    check_passed = True

            # previous_transcripts += (
            #     f"\n\n{'Retry ' + str(retry_count) if retry_count > 0 else 'First version'}:\n"
            #     f"Input:\n{prev_content}\n\nIssues:\n{guidance}"
            # )

            change_length = False
            prev_content_len = count_words(prev_content)
            transcript_content_len = count_words(transcript_content)
            if word_count is not None:
                change_length_int, length_instructions = check_transcript_length(
                    transcript_content,
                    content,
                    word_count,
                )
                change_length = (
                    change_length_int != 0
                    and is_near(prev_content_len, transcript_content_len, 10)
                    != RangeCheck.WITHIN
                )

            if check_passed and not change_length:
                print(f"Rewritten transcript ({count_words(transcript_content)=})")
                break
            else:
                length_change_fail = False

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
    # previous_transcripts="",
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
        orig_len = count_words(transcript)
        result = get_chain(chain).invoke(
            {
                "content": content,
                "transcript": transcript,
                "output_language": OutputLanguageOptions[
                    conversation_config.output_language
                ].value,
                "conversation_style": conversation_config.conversation_style,
                "roles_person1": str(conversation_config.roles_person1),
                "roles_person2": str(conversation_config.roles_person2),
                "dialogue_structure": conversation_config.dialogue_structure,
                "engagement_techniques": conversation_config.engagement_techniques,
                "user_instructions": conversation_config.user_instructions,
                "feedback": feedback,
                # "previous_transcripts": previous_transcripts,
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
                "location": conversation_config.location or "Finland",
            }
        )

        if not isinstance(result, BaseMessage):
            result_len = count_words(result)
            target = (
                RangeCheck.BELOW
                if "extend" in chain
                else RangeCheck.ABOVE
                if "reduce" in chain
                else None
            )
            if is_near(result_len, orig_len, 10) == target:
                print(
                    f"transcript_rewriter: Transcript length considerably outside of target: ({str(orig_len - result_len)})"
                )
                result = ""

    if isinstance(result, BaseMessage):
        raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"transcript_rewriter: LLM result {count_words(result)=}")

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
    if content is None or len(content) < 1:
        raise ValueError("Content is empty, unable to continue generation.")

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
    transcript: str,
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
        result = get_chain(
            "transcript_short_intro_writer"
            if conversation_config.short_intro_and_conclusion
            else "transcript_intro_writer"
        ).invoke(
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
        result = get_chain(
            "transcript_short_conclusion_writer"
            if conversation_config.short_intro_and_conclusion
            else "transcript_conclusion_writer"
        ).invoke(
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
    target: int = None,
    conversation_config: ConversationConfig = ConversationConfig(),
    min_reduce_percentage: int = 10,
) -> tuple[str, bool]:
    print(
        f"transcript_compress - Starting with transcript ({count_words(transcript)}), conversation_config={conversation_config}"
    )
    retries = 3
    is_near_fail_count = 0  # Tracks failures specific to `is_near`
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    prev_result = transcript

    while (
        (result == "" or isinstance(result, BaseMessage))
        or (target is not None and target < count_words(prev_result))
    ) and retries > 0:
        retries -= 1
        prev_count = count_words(prev_result)
        result = get_chain("transcript_compress").invoke(
            {
                "transcript": prev_result,
                "output_language": OutputLanguageOptions[
                    conversation_config.output_language
                ].value,
                "roles_person1": str(conversation_config.roles_person1),
                "roles_person2": str(conversation_config.roles_person2),
                "user_instructions": conversation_config.user_instructions,
                "date": current_date,
                "time": current_time,
            }
        )

        if isinstance(result, BaseMessage):
            print("Received a BaseMessage. Retrying...")
            continue

        result_count = count_words(result)

        # Validate compression using `is_near`
        compression_check = is_near(
            result_count,
            prev_count,
            percentage=min_reduce_percentage,
        )
        if compression_check != RangeCheck.BELOW:
            print(
                f"transcript_compress - New result length is longer or within {str(min_reduce_percentage)}% of the previous result; ignoring."
            )
            is_near_fail_count += 1
            # Stop if `is_near` fails more than 2 times
            if is_near_fail_count >= 2:
                print("Failed to compress transcript sufficiently after 2 attempts.")
                break
        else:
            print(
                f"transcript_compress - Reduced by ({str(prev_count - result_count)} missing target by: {str(result_count - target)})"
            )
            prev_result = result  # Accept the new compressed result
            is_near_fail_count = 0  # Reset failure count for valid compression

    if isinstance(prev_result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return transcript

    print(f"transcript_compress - Completed with result ({count_words(prev_result)})")

    result_count = count_words(prev_result)

    return prev_result, is_near(result_count, target, 10) == RangeCheck.WITHIN


@traceable(
    run_type="llm",
    name="Extend transcript",
)
def transcript_extend(
    transcript: str,
    content: str,
    target: int = None,
    conversation_config: ConversationConfig = ConversationConfig(),
    min_extend_percentage: int = 10,
) -> tuple[str, bool]:
    print(
        f"transcript_extend - Starting with transcript ({count_words(transcript)}), conversation_config={conversation_config}"
    )
    retries = 3
    is_near_fail_count = 0  # Tracks failures specific to `is_near`
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    prev_result = transcript

    while (
        retries > 0
        and (result == "" or isinstance(result, BaseMessage))
        or (target is not None and target > count_words(prev_result))
    ):
        retries -= 1
        prev_count = count_words(prev_result)
        result = get_chain("transcript_extend").invoke(
            {
                "transcript": prev_result,
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
                "date": current_date,
                "time": current_time,
            }
        )

        if isinstance(result, BaseMessage):
            print("Received a BaseMessage. Retrying...")
            continue

        result_count = count_words(result)

        growth_check = is_near(
            result_count,
            prev_count,
            percentage=min_extend_percentage,
        )
        # Validate growth using `is_near`
        if growth_check != RangeCheck.ABOVE:
            print(
                f"transcript_extend - New result length is less or within {str(min_extend_percentage)}% of the previous result; ignoring."
            )
            is_near_fail_count += 1
            # Stop if `is_near` fails more than 2 times
            if is_near_fail_count >= 2:
                print(
                    "Failed to generate a sufficiently larger result after 2 attempts."
                )
                break
        else:
            print(
                f"transcript_extend - Extended with ({str(result_count - prev_count)} missing target by: {str(target - result_count)})"
            )
            prev_result = result  # Accept the new result
            is_near_fail_count = 0  # Reset failure count for meaningful growth

    if isinstance(prev_result, BaseMessage):
        print("Generation failed: Received a BaseMessage.")
        return transcript

    print(f"transcript_extend - Completed with result ({count_words(prev_result)})")

    result_count = count_words(prev_result)

    return prev_result, is_near(result_count, target, 10) == RangeCheck.WITHIN


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
                "source_language": OutputLanguageOptions[
                    conversation_config.output_language
                ].value,
                "target_language": OutputLanguageOptions[target_language].value,
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
        raise ValueError("Generation failed: Received a BaseMessage.")

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
        result: TranscriptSummary = get_chain(
            "transcript_summary_formatter_sync"
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

        if isinstance(result, BaseMessage):
            raise ValueError("Generation failed: Received a BaseMessage.")

    if not result:
        raise ValueError("Failed to generate transcript summary after retries.")

    for item in result.subjects:
        if item.references:
            new_references = []
            for reference in item.references:
                if isinstance(reference, SummaryReference):
                    reference = reference.id

                for source in sources:
                    if isinstance(source, str):
                        continue

                    match = source.find_match(reference)
                    if match:
                        new_references.append(
                            SummaryReference(
                                id=match.source_id
                                or (
                                    match.source_model.id if match.source_model else ""
                                ),
                                title=match.title,
                                image=match.image,
                                url=match.get_url(),
                                publish_date=match.publish_date,
                            )
                        )
            item.references = new_references

    print("transcript_summary_writer - Completed.")
    return result


class RangeCheck(Enum):
    BELOW = -1
    WITHIN = 0
    ABOVE = 1

    def __bool__(self):
        return self == RangeCheck.WITHIN


def is_near(number, target, percentage) -> RangeCheck:
    """
    Check if 'number' is near 'target' by a specified percentage.

    :param number: The number to check.
    :param target: The reference number.
    :param percentage: The percentage for proximity (e.g., 10 for 10%).
    :return:
        RangeCheck.BELOW if 'number' is below the range,
        RangeCheck.WITHIN if 'number' is within the range,
        RangeCheck.ABOVE if 'number' is above the range.
    """
    margin = target * (percentage / 100)  # Convert percentage to a fraction
    lower_bound = target - margin
    upper_bound = target + margin
    if number < lower_bound:
        return RangeCheck.BELOW
    elif number > upper_bound:
        return RangeCheck.ABOVE
    return RangeCheck.WITHIN


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
        comparison_result = is_near(
            word_count_in_transcript, target_word_count, 25
        )  # 25% margin

        if comparison_result == RangeCheck.BELOW:  # Too short
            multiplier = target_word_count / word_count_in_transcript
            change_length = 1
            if multiplier > 2:
                length_instruction = (
                    "The transcript is too short. It should be at least three times as long. "
                    "Give extensive feedback on the possible ways to extend the transcript."
                )
            elif multiplier > 1.5:
                length_instruction = (
                    "The transcript is too short. It should be at least twice as long. "
                    "Give feedback on the possible ways to extend the transcript."
                )
            else:
                length_instruction = (
                    "The transcript is too short. It should be slightly longer. "
                    "Give feedback on how to extend the dialogue."
                )
        elif comparison_result == RangeCheck.ABOVE:  # Too long
            multiplier = word_count_in_transcript / target_word_count
            change_length = -1
            if multiplier > 3:
                length_instruction = (
                    "The transcript is too long. It should be at least three times shorter. "
                    "Give extensive feedback on the possible ways to shorten the transcript."
                )
            elif multiplier > 2:
                length_instruction = (
                    "The transcript is too long. It should be half the length. "
                    "Give feedback on the possible ways to shorten the transcript."
                )
            else:
                length_instruction = (
                    "The transcript is too long. It should be slightly shorter. "
                    "Give feedback on how to shorten the dialogue."
                )
        else:  # Near target
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
    add_detail: bool = False,
) -> str:
    """
    Generate a podcast transcript and verify its quality.

    :param conversation_config: Configuration for the conversation.
    :param content: The content to be used for generating the transcript.
    :param urls: List of URLs to be included in the transcript generation.
    :return: The path to the generated transcript file.
    """
    urls = urls or []

    if isinstance(sources, (WebSource, WebSourceCollection)):
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
            content += "\n\n".join([src for src in map(str, sources) if src])
        elif sources is not None:
            content += str(sources)

    main_item = False
    if source is not None and (isinstance(source, (WebSource, WebSourceCollection))):
        main_item = source.main_item

    orig_transcript_content = ""
    if (sources or isinstance(source, WebSourceCollection)) and add_detail:
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
        if isinstance(sources, list):
            content += "\n\n".join([src for src in map(str, sources) if src])
        else:
            content += str(sources)
        article_count = len(sources)
    else:
        raise ValueError("Sources needed for combining resulting transcripts.")

    if content is None or len(content) < 1:
        raise ValueError("Content is empty, unable to generate transcript.")

    if not conversation_config.disable_intro_and_conclusion:
        combined_transcripts.append(
            transcript_intro_writer(
                "\n".join(transcripts), content, conversation_config, previous_episodes
            )
        )

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

    if not conversation_config.disable_intro_and_conclusion:
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
            orig_transcript=orig_transcript,
            conversation_config=conversation_config,
            word_count=word_count,
            max_retries=6,
            main_item=False,
            # orig_combined_transcript=orig_transcript,
            previous_episodes=previous_episodes,
        )
    except Exception as e:
        print(f"Failed to rewrite the transcript: {e}")
        return orig_transcript

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
        if isinstance(sources, list):
            content += "\n\n".join([src for src in map(str, sources) if src])
        else:
            content += str(sources)
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
            # orig_combined_transcript=transcript_content,
        )
    except Exception as e:
        print(f"Failed to translate the transcript: {e}")
        raise

    return transcript_content
