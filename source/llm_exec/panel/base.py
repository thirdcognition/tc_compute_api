import re
from enum import Enum


def count_words(text: str) -> int:
    cleaned_text = re.sub(r"</?person\d+>", "", text, flags=re.IGNORECASE)
    return len(cleaned_text.split())


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
    if target is None or number is None:
        # Handle cases where target or number might be None
        return RangeCheck.WITHIN  # Or raise an error, depending on desired behavior

    # Ensure target is not zero to avoid division by zero
    if target == 0:
        if number == 0:
            return RangeCheck.WITHIN
        elif number < 0:
            return RangeCheck.BELOW
        else:
            return RangeCheck.ABOVE

    margin = abs(target * (percentage / 100))  # Use abs to handle negative targets
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
            multiplier = (
                target_word_count / word_count_in_transcript
                if word_count_in_transcript > 0
                else float("inf")
            )
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
