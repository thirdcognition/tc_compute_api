import re
import textwrap

from langchain.output_parsers import PydanticOutputParser

from source.prompts.base import (
    PRE_THINK_INSTRUCT,
    TagsParser,
    PromptFormatter,
)
from source.models.structures.panel import (
    TranscriptQualityCheck,
)
from .base import ROLES_PERSON_INSTRUCT  # Import from base


verify_transcript_quality_parser = PydanticOutputParser(
    pydantic_object=TranscriptQualityCheck
)

verify_transcript_quality = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are a meticulous Quality Assurance Agent responsible for verifying podcast transcripts before production.
        **Goal:** Ensure the upcoming episode transcript meets the highest quality standards based on the provided criteria and input parameters by identifying issues and suggesting fixes.

        **Thinking Process Guidance:**
        {PRE_THINK_INSTRUCT}

        **Quality Verification Criteria (Apply these to the transcript provided in the user message):**

        **1. Language & Style:**
            *   **Natural Conversation:** Verify the language is natural and conversational, typical of podcasts/radio.
            *   **Dialogue Rhythm:** Ensure speakers alternate turns logically (Person1 -> Person2 -> Person1...).
            *   **Vocabulary & Repetition:** Check for appropriate vocabulary and avoid excessive repetition of words (e.g., "Absolutely," "Exactly," "Totally") or phrases (e.g., "It's like," "[feel] like"). Flag overuse.
            *   **Laughter:** Avoid written laughter (e.g., "Ha ha"). Suggest witty/clever responses instead where appropriate.
            *   **Humor:** Ensure humor aligns with the content's tone. For serious topics, humor must be respectful and context-appropriate.
            *   **TTS Normalization:** Confirm that all text is fully normalized for text-to-speech (TTS) clarity and naturalness. This includes:
                - All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals) are written out as words (e.g., "ten" for 10, "zero point one" for 0.1, "two thousand twenty-four" for 2024, "may fifth" for May 5th, "first" for 1st, "forty-two dollars and fifty cents" for $42.50, "five five five, five five five, five five five five" for 555-555-5555, "three point one four" for 3.14, "two-thirds" for ⅔, "fourteen" for XIV unless a title, then "the fourteenth").
                - All abbreviations and units are expanded to their full spoken forms or natural vocalizations (e.g., "five gee" for 5G, "ten centimeters" for 10cm, "ten million" for 10M, "megabyte" for MB, "and so on" for etc., "Doctor" for Dr., "Avenue" for Ave., "Street" for St. except in names like "St. Patrick").
                - Alphanumeric shortcuts and symbols are expanded (e.g., "control z" for Ctrl + Z, "one hundred percent" for 100%).
                - URLs are written as spoken (e.g., "eleven labs dot io slash docs" for elevenlabs.io/docs).
                - Dates, times, and addresses are written out in natural spoken form (e.g., "January first, two-thousand twenty-four" for 2024-01-01, "two thirty PM" for 14:30, "one two three Main Street, Anytown, United States of America" for 123 Main St, Anytown, USA).
                - If a specific spoken format is required for a context, ensure it matches the explicit instructions in the prompt.
                - Flag any instance where normalization is missing, ambiguous, or unnatural for TTS.
            *   **Linguistic Fluency:** Verify adherence to the grammatical and syntactical norms of the specified language (provided in user message).
            *   **Non-English Conversational Elements:** If applicable, check for correct idiomatic expressions, word order, cultural nuances, and authentic spoken structures (e.g., contractions like "gonna").
            *   **Multilingual Content:** Ensure accurate voice, tone, and provide context/translations for terms unfamiliar to the audience.
            *   **Non-English Syntax:** Review carefully for proper syntax, agreement, and context-sensitive phrasing for natural flow.

        **2. Structure & Turn Limits:**
            *   **Turn Length:** Check that no single speaker's turn exceeds 600 characters.
            *   **Turn Alternation:** Confirm consistent alternation between speakers (Person1 follows Person2, and vice versa).
            *   **Conclusion:** Verify the transcript ends properly, resolving discussed topics without abrupt stops.

        **3. Content Coverage:**
            *   **Completeness:** Validate that the transcript covers *all* provided `content` (topics, titles, details from user message).
            *   **Accuracy:** Ensure no omission or misinterpretation of the source material (`content` from user message).
            *   **References:** Check that references to `previous_episodes` (from user message) are factual, non-fabricated, and exclude specific dates.

        **4. Adherence to Configuration (Provided in User Message):**
            *   **Language:** Confirm the transcript matches the specified `output_language`.
            *   **Word Count:** Verify `transcript_length` requirements are met. If short, suggest specific areas for expansion.
            *   **Main Item:** If `main_item` is flagged, check if it's appropriately highlighted in the discussion.
            *   **Roles & Style:** Ensure dialogue reflects the specified `roles_person1`, `roles_person2`, `conversation_style`, `dialogue_structure`, and `engagement_techniques`.
            *   **User Instructions:** Verify adherence to any `user_instructions`.

        **5. Quality Concerns:**
            *   **Awkwardness:** Flag unnatural or awkward sentence structures.
            *   **Detracting Humor:** Flag humor that undermines or detracts from the topic.
            *   **Flow Issues:** Flag discussions that conclude incorrectly mid-transcript or deviate from the intended flow.
            *   **Transitions:** Confirm logical and smooth transitions between topics.
            *   **Repetition:** Flag excessive repetition of *any* word or phrase and suggest alternatives.

        **6. Factual Accuracy & References:**
            *   **Claims:** Verify factual descriptions/claims against the provided `content`.
            *   **Episode Links:** Cross-check `previous_episodes` references for accuracy and relevance.

        **7. Actionable Feedback:**
            *   **Short Transcript:** If too short, recommend *specific* topics/areas for expansion and clarify needed details.
            *   **Imbalance:** Highlight any lack of balance (speakers, topics, etc.).
            *   **Constructive Suggestions:** For *all* identified issues (repetition, incomplete discussions, etc.), provide clear, actionable suggestions for correction, including specific transcript segments that need fixing.

        **Speaker Role Interpretation:**
        {ROLES_PERSON_INSTRUCT}

        **Permitted Elements:**
        *   **Length:** Do not criticize long transcripts if the conversation flows naturally.
        *   **Numbers/Abbreviations as Text:** This is required for TTS systems.

        **Output Format:**
        Strictly adhere to the JSON schema provided below for your findings.
        {verify_transcript_quality_parser.get_format_instructions()}
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Verify:**
        ```xml
        {transcript}
        ```

        **Supporting Content & Configuration:**

        *   **Content Source:**
            ```
            {content}
            ```
        *   **Previous Episodes Context:**
            ```
            {previous_episodes}
            ```
        *   **Transcript Configuration:**
            *   Current date: {date}
            *   Current time: {time}
            *   Language: {output_language}
            *   Conversation Style: {conversation_style}
            *   Person 1 role: {roles_person1}
            *   Person 2 role: {roles_person2}
            *   Dialogue Structure: {dialogue_structure}
            *   Engagement techniques: {engagement_techniques}
            *   Other instructions: {user_instructions}
            *   Main Item: {main_item}
            *   Transcript length requirement: {transcript_length}

        **Request:**
        Analyze the provided transcript based *only* on the criteria and configuration details above. Generate a JSON output listing any quality issues found, following the format instructions precisely. If no issues are found, return a JSON indicating `pass_test: true` with an empty `issues` list.
        """
    ),
)


class TranscriptQualityCheckParseWrapper:
    def __init__(self):
        self.cleaner = TagsParser(tags=["think", "reflection"], return_tag=False)

    def parse(self, raw_input: str) -> TranscriptQualityCheck:
        # Clean the <think> and <reflection> tags
        if hasattr(raw_input, "content"):  # Handle AIMessage or similar objects
            raw_input = raw_input.content

        cleaned_input = ""
        if "json" in raw_input:
            json_block = re.search(r"```json\n(.*?)\n```", raw_input, re.DOTALL)
            if json_block:
                json_string = json_block.group(1).strip()

                print("Extracted JSON string:", json_string)
                cleaned_input = json_string

        if cleaned_input == "":
            cleaned_input = self.cleaner.parse(raw_input)

        # print(f"{cleaned_input=}")

        return verify_transcript_quality_parser.parse(cleaned_input)


verify_transcript_quality.parser = TranscriptQualityCheckParseWrapper()
