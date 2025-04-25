from datetime import datetime
from typing import List, Union

from langchain_core.messages import BaseMessage
from langsmith import traceable

from source.chains import get_chain
from source.models.structures.panel import (
    ConversationConfig,
    OutputLanguageOptions,
    TranscriptQualityCheck,
)
from source.models.structures.web_source import WebSource
from source.models.structures.web_source_collection import WebSourceCollection

# Relative imports from the same package
from .base import count_words, is_near, check_transcript_length, RangeCheck
from .quality import verify_transcript_quality


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

    # Ensure word_count is treated as int if possible
    if isinstance(word_count, str):
        try:
            word_count = int(word_count)
        except ValueError:
            print(f"Warning: Invalid word_count '{word_count}', using default logic.")
            word_count = None  # Or handle error appropriately

    if word_count is not None:
        content_word_count = count_words(content)
        if content_word_count > 0:
            word_count = min(
                word_count,
                content_word_count // 1.25 if content_word_count > 0 else 300,
            )
        else:
            word_count = 300  # Default if content is empty

    while (not check_passed or change_length) and retry_count < max_retries:
        change_length = False
        length_instructions = ""
        change_length_int = 0  # Initialize change_length_int

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
                # change_length_int = 0 # Reset after attempt
            except ValueError as e:
                print(f"Error during transcript length adjustment: {e}")
                length_change_fail = True
                transcript_content = save_content  # Revert on error

            if transcript_content != save_content and word_count is not None:
                # Re-check length only if content changed
                (
                    new_change_length_int,
                    new_length_instructions,
                ) = check_transcript_length(
                    transcript_content,
                    content,
                    word_count,
                )
                # Update change_length only if the direction is still the same or now within range
                if (
                    new_change_length_int == 0
                    or new_change_length_int == change_length_int
                ):
                    change_length_int = new_change_length_int
                    length_instructions = new_length_instructions
                change_length = change_length_int != 0
            elif transcript_content == save_content:
                # If content didn't change (e.g., due to error or no compression/extension happened)
                # stop trying to change length in this inner loop iteration
                change_length = False

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
                    if change_length  # Use instructions only if length change is still needed
                    else "Transcript length is good."
                ),
                previous_episodes=previous_episodes,
            )
        except Exception as e:
            print(f"Error while verifying quality: {e}")
            quality_check = fallback_quality_check  # Use fallback on error

        all_issues = sorted(
            (issue for issue in quality_check.issues if issue.severity >= 2),
            key=lambda issue: issue.severity,
            reverse=False,  # Severity low to high
        )

        quality_check.pass_test = len(all_issues) == 0
        check_passed = quality_check.pass_test

        # guidance = "" # Reset guidance for this retry loop

        if not check_passed or change_length:
            # Determine the chain based on the *current* length needs
            chain = (
                "transcript_rewriter"
                if change_length_int == 0
                else (
                    "transcript_rewriter_extend"
                    if change_length_int > 0  # Needs extension
                    else "transcript_rewriter_reduce"  # Needs reduction
                )
            )

            # Construct feedback message
            feedback_parts = []
            if change_length:
                feedback_parts.append(length_instructions)
            if not check_passed:
                issues_to_address = [
                    all_issues.pop(0) for _ in range(min(5, len(all_issues)))
                ]
                issue_feedback = "\n\n".join(
                    [
                        f"Issue {str(i + 1)}:\nTitle: {issue.title}\nCoverage: {issue.issue_coverage.value}\nSegments:\n{'\n----\n'.join(issue.transcript_segments) if len(issue.transcript_segments) > 0 else ''}\nSuggested fix:\n{issue.suggestions}"
                        for i, issue in enumerate(issues_to_address)
                    ]
                )
                feedback_parts.append(issue_feedback)

            feedback = "\n\n".join(filter(None, feedback_parts))

            if feedback:  # Only rewrite if there's feedback (length or quality issues)
                print(
                    f"Rewrite transcript due to failed check or length issue (use chain {chain}).\n{feedback=}"
                )
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
                        main_item=main_item,  # Pass main_item here
                    )
                    # After rewrite, reset length check variables for the next outer loop iteration
                    # change_length_int = 0 # Assume rewrite addressed length unless re-checked
                    # change_length = False # Assume rewrite addressed length unless re-checked
                except ValueError as e:
                    print(f"Error during transcript rewrite: {e}")
                    transcript_content = prev_content  # Revert on error
                    check_passed = False  # Force re-evaluation if rewrite failed
                    # change_length = True # Assume length issue might persist if rewrite failed
            else:
                # If no feedback (somehow passed quality and length checks here), break inner loop?
                # This case might indicate logic error, but safer to assume checks passed.
                check_passed = True
                change_length = False

            # Re-evaluate length after rewrite attempt
            if word_count is not None:
                (
                    new_change_length_int,
                    new_length_instructions,
                ) = check_transcript_length(
                    transcript_content,
                    content,
                    word_count,
                )
                # Only consider length change needed if rewrite didn't revert and target not met
                if transcript_content != prev_content:
                    change_length_int = new_change_length_int
                    length_instructions = new_length_instructions
                    change_length = change_length_int != 0
                else:  # If reverted, keep original length status
                    change_length_int, length_instructions = check_transcript_length(
                        prev_content, content, word_count
                    )
                    change_length = change_length_int != 0

            # previous_transcripts += (
            #     f"\n\n{'Retry ' + str(retry_count) if retry_count > 0 else 'First version'}:\n"
            #     f"Input:\n{prev_content}\n\nIssues:\n{guidance}" # Guidance needs update if used
            # )

            length_change_fail = False  # Reset length change fail flag for next retry

        retry_count += 1
        # Loop continues if !check_passed or change_length

    # Final check after loop
    if not check_passed:
        print(
            f"Warning: Transcript rewrite finished after {max_retries} retries but quality check may not have passed."
        )
    if change_length:
        print(
            f"Warning: Transcript rewrite finished after {max_retries} retries but length target may not have been met."
        )

    print(f"Rewritten transcript final length: ({count_words(transcript_content)=})")
    return transcript_content


@traceable(
    run_type="llm",
    name="Rewrite transcript (Internal)",
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
) -> str:  # Return type should be str, not bool
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    orig_len = count_words(transcript)

    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        try:
            result = get_chain(chain).invoke(
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
                    "word_count": (
                        word_count * 1.2 if word_count else 500
                    ),  # Provide a default/calculated value
                    "location": conversation_config.location or "Finland",
                }
            )
        except Exception as e:
            print(f"Error invoking chain '{chain}': {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

        if (
            not isinstance(result, BaseMessage) and result
        ):  # Check if result is a non-empty string
            result_len = count_words(result)
            target_check = None
            if "extend" in chain:
                target_check = (
                    RangeCheck.BELOW
                )  # Expect result to be longer than original
            elif "reduce" in chain:
                target_check = (
                    RangeCheck.ABOVE
                )  # Expect result to be shorter than original

            # If a target direction exists, check if the result moved in the wrong direction significantly
            if (
                target_check is not None
                and is_near(result_len, orig_len, 10) == target_check
            ):
                print(
                    f"_transcript_rewriter ({chain}): Transcript length moved significantly opposite to target: (orig: {orig_len}, new: {result_len}). Retrying..."
                )
                result = ""  # Reset result to trigger retry
        elif isinstance(result, BaseMessage):
            print(f"_transcript_rewriter ({chain}): Received BaseMessage. Retrying...")
            result = ""  # Reset result to trigger retry

    if isinstance(result, BaseMessage) or not result:  # Check if failed after retries
        raise ValueError(
            f"Generation failed for chain '{chain}' after multiple retries."
        )

    print(f"_transcript_rewriter ({chain}): LLM result {count_words(result)=}")

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
        f"transcript_compress - Starting with transcript ({count_words(transcript)}), target={target}, config={conversation_config}"
    )
    retries = 3
    is_near_fail_count = 0  # Tracks failures specific to `is_near`
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    prev_result = transcript
    final_success = False  # Track if target was met

    while retries > 0:
        retries -= 1
        prev_count = count_words(prev_result)

        # Check if already below or at target
        if target is not None and prev_count <= target:
            print(
                f"transcript_compress - Already at or below target ({prev_count} <= {target}). Skipping."
            )
            final_success = True
            break

        try:
            result = get_chain("transcript_compress").invoke(
                {
                    "transcript": prev_result,
                    "output_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ],
                    "conversation_style": conversation_config.conversation_style,
                    "person_roles": "\n".join(
                        [
                            f"Person {key}: {str(role)}"
                            for key, role in conversation_config.person_roles.items()
                        ]
                        if conversation_config.person_roles
                        else ""
                    ),
                    "user_instructions": conversation_config.user_instructions,
                    "date": current_date,
                    "time": current_time,
                }
            )
        except Exception as e:
            print(f"Error invoking transcript_compress chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

        if isinstance(result, BaseMessage) or not result:
            print("Received a BaseMessage or empty result. Retrying...")
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
                f"transcript_compress - New result length ({result_count}) is not significantly smaller than previous ({prev_count}) by {min_reduce_percentage}%; ignoring."
            )
            is_near_fail_count += 1
            # Stop if `is_near` fails more than 1 time (allow one failure)
            if is_near_fail_count >= 2:
                print("Failed to compress transcript sufficiently after 2 attempts.")
                break  # Exit loop, keep prev_result
        else:
            print(
                f"transcript_compress - Reduced by ({prev_count - result_count}). Current length: {result_count}, Target: {target}"
            )
            prev_result = result  # Accept the new compressed result
            is_near_fail_count = 0  # Reset failure count for valid compression

            # Check if target met after successful compression
            if target is not None and result_count <= target:
                print(f"transcript_compress - Target {target} met.")
                final_success = True
                break  # Exit loop

    if isinstance(prev_result, BaseMessage):  # Should not happen if loop exits normally
        print("Generation failed: Ended with a BaseMessage.")
        return transcript, False  # Return original and failure

    final_count = count_words(prev_result)
    print(f"transcript_compress - Completed with result ({final_count})")

    # Final check against target if target was provided
    if target is not None:
        final_success = (
            is_near(final_count, target, 10) != RangeCheck.ABOVE
        )  # Success if not significantly above target

    return prev_result, final_success


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
        f"transcript_extend - Starting with transcript ({count_words(transcript)}), target={target}, config={conversation_config}"
    )
    retries = 3
    is_near_fail_count = 0  # Tracks failures specific to `is_near`
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    prev_result = transcript
    final_success = False  # Track if target was met

    while retries > 0:
        retries -= 1
        prev_count = count_words(prev_result)

        # Check if already at or above target
        if target is not None and prev_count >= target:
            print(
                f"transcript_extend - Already at or above target ({prev_count} >= {target}). Skipping."
            )
            final_success = True
            break

        try:
            result = get_chain("transcript_extend").invoke(
                {
                    "transcript": prev_result,
                    "content": content,
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
                    "podcast_name": conversation_config.podcast_name,
                    "podcast_tagline": conversation_config.podcast_tagline,
                    "date": current_date,
                    "time": current_time,
                }
            )
        except Exception as e:
            print(f"Error invoking transcript_extend chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

        if isinstance(result, BaseMessage) or not result:
            print("Received a BaseMessage or empty result. Retrying...")
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
                f"transcript_extend - New result length ({result_count}) is not significantly larger than previous ({prev_count}) by {min_extend_percentage}%; ignoring."
            )
            is_near_fail_count += 1
            # Stop if `is_near` fails more than 1 time
            if is_near_fail_count >= 2:
                print(
                    "Failed to generate a sufficiently larger result after 2 attempts."
                )
                break  # Exit loop, keep prev_result
        else:
            print(
                f"transcript_extend - Extended by ({result_count - prev_count}). Current length: {result_count}, Target: {target}"
            )
            prev_result = result  # Accept the new result
            is_near_fail_count = 0  # Reset failure count for meaningful growth

            # Check if target met after successful extension
            if target is not None and result_count >= target:
                print(f"transcript_extend - Target {target} met.")
                final_success = True
                break  # Exit loop

    if isinstance(prev_result, BaseMessage):  # Should not happen
        print("Generation failed: Ended with a BaseMessage.")
        return transcript, False  # Return original and failure

    final_count = count_words(prev_result)
    print(f"transcript_extend - Completed with result ({final_count})")

    # Final check against target if target was provided
    if target is not None:
        final_success = (
            is_near(final_count, target, 10) != RangeCheck.BELOW
        )  # Success if not significantly below target

    return prev_result, final_success


@traceable(
    run_type="llm",
    name="Translate transcript (Internal)",
)
def _transcript_translate(
    transcript: str,
    target_language: str,
    conversation_config: ConversationConfig = ConversationConfig(),
) -> str:  # Return type str, not bool
    print(
        f"_transcript_translate - Starting with transcript ({count_words(transcript)}), target={target_language}, config={conversation_config}"
    )
    retries = 3
    result = ""
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d (%a)")
    current_time = current_datetime.strftime("%H:%M:%S")
    while (result == "" or isinstance(result, BaseMessage)) and retries > 0:
        retries -= 1
        try:
            result = get_chain("transcript_translate").invoke(
                {
                    "transcript": transcript,
                    "source_language": OutputLanguageOptions[
                        conversation_config.output_language
                    ].value,
                    "target_language": OutputLanguageOptions[target_language].value,
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
                    "podcast_name": conversation_config.podcast_name,
                    "podcast_tagline": conversation_config.podcast_tagline,
                    "date": current_date,
                    "time": current_time,
                }
            )
        except Exception as e:
            print(f"Error invoking transcript_translate chain: {e}")
            result = ""  # Ensure result is reset on error
            continue  # Try again if retries left

    if isinstance(result, BaseMessage) or not result:
        raise ValueError(
            "Generation failed for transcript_translate after multiple retries."
        )

    print(f"_transcript_translate - Completed with result ({count_words(result)})")

    return result


@traceable(
    run_type="llm",
    name="Translate generated transcript",
)
def transcript_translate(
    transcript_content: str,
    target_language: str,
    sources: List[Union[WebSource, WebSourceCollection, str]],  # Added Union type hint
    conversation_config: ConversationConfig = ConversationConfig(),
) -> str:
    content = ""
    article_count = 1
    if sources is not None:
        if isinstance(sources, list):
            content += "\n\n".join(
                [str(src) for src in sources if src]
            )  # Simplified content joining
            article_count = len(sources)
        # else: # Removed redundant else block, handled by list check
        #     content += str(sources)
        #     article_count = 1 # This was likely incorrect, should be based on source type if not list
    else:
        # Consider if raising an error is always correct, maybe allow translation without sources?
        print("Warning: Translating transcript without source context.")
        # raise ValueError("Sources needed for combining resulting transcripts.") # Optional: uncomment if sources are mandatory

    word_count = conversation_config.word_count
    if word_count is not None and conversation_config.longform and article_count > 0:
        word_count = (word_count * article_count) // 2

    # translated_transcript = translate_transcript(transcript_content, target_language) # Assuming this helper is removed/replaced

    try:
        translated_transcript = _transcript_translate(
            transcript_content,
            target_language,
            conversation_config,
        )
    except ValueError as e:
        print(f"Failed to translate the transcript initially: {e}")
        raise  # Re-raise the error if initial translation fails

    conversation_config_copy = conversation_config.model_copy(
        deep=True
    )  # Use deep copy
    conversation_config_copy.output_language = target_language

    try:
        # Use the main transcript_rewriter function for post-translation refinement
        final_transcript_content = transcript_rewriter(
            content=content,  # Provide content for context during rewrite
            orig_transcript=translated_transcript,
            conversation_config=conversation_config_copy,  # Use copied config with target language
            word_count=word_count,  # Pass calculated word count
            max_retries=6,
            main_item=False,  # Assuming main_item is not relevant for translation rewrite
            # orig_combined_transcript=transcript_content, # Pass original for context if needed by rewriter logic
        )
    except Exception as e:
        print(f"Failed to rewrite the translated transcript: {e}")
        # Decide whether to return the raw translation or raise error
        # Returning raw translation might be acceptable in some cases
        print("Returning raw translated transcript due to rewrite failure.")
        return translated_transcript
        # raise # Or re-raise the exception

    return final_transcript_content
