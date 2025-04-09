import re
from typing import List, Union
import os

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage

from source.prompts.base import BaseOutputParser, clean_tags
from source.models.config.default_env import DEFAULT_PATH


# Function to load fewshot examples from the file
def load_fewshot_examples(filename: str) -> str:
    file_path = os.path.join(DEFAULT_PATH, "fewshot_data", filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return "FEWSHOT EXAMPLES:\n" + file.read()
    except FileNotFoundError:
        print(f"Fewshot examples file not found: {file_path}")
        return ""


ROLES_PERSON_INSTRUCT = """
        When generating dialogue or content, use the roles defined in `Person N role` (provided in the user prompt) to shape the tone, style, and perspective of each speaker. Each role provides the following attributes:
        - **Name**: The speaker's name, which should be used to personalize the dialogue.
        - **Persona**: The speaker's personality traits or characteristics, which should influence their tone and style of speech.
        - **Role**: The speaker's functional or thematic role in the conversation, which should guide the content and focus of their contributions.

        **Application Guidelines:**
        1.  **Reflect Persona & Role:** Ensure the dialogue accurately reflects the unique persona and role of each speaker.
        2.  **Naming:** Person 1 should reference Person 2 by their Name, and Person 2 should reference Person 1 by their Name.
        3.  **Audience Address:** Both speakers should address the audience directly as "you."
        4.  **Alignment:** Ensure the content aligns with the specified conversation style and engagement techniques provided in the user prompt configuration.
        5.  **Consistency:** Apply roles consistently throughout the conversation for coherence and authenticity.
        """


class TranscriptParser(BaseOutputParser[str]):
    """Custom parser to process and validate podcast transcripts."""

    def _strip_tags(self, text: str, tag: str) -> str:
        """Remove specific tags but keep their content."""
        return re.sub(rf"</?{tag}.*?>", "", text, flags=re.IGNORECASE)

    @classmethod
    def split_blocks(cls, text: str) -> List[str]:
        """Split text into blocks based on <personN> tags, allowing for properties and whitespace."""
        pattern = r"(<person\d+.*?>.*?</person\d+>)"
        blocks = re.split(pattern, text, flags=re.DOTALL | re.IGNORECASE)
        return [block.strip() for block in blocks if block.strip()]

    @classmethod
    def fix_blocks(cls, blocks):
        corrected_blocks = []

        for block in blocks:
            match = re.match(
                r"<person(\d+)(.*?)>(.*?)</person\1>", block, re.DOTALL | re.IGNORECASE
            )
            if match:
                # Block is valid, so we add it back to the corrected_blocks list
                corrected_blocks.append(block)
            else:
                # Check for critical mismatches in block, e.g., nested mismatched tags
                if re.search(
                    r"<person(\d+)>.*?</person(\d+)>", block, re.DOTALL | re.IGNORECASE
                ):
                    tag_mismatches = re.findall(
                        r"<person(\d+)>.*?</person(\d+)>",
                        block,
                        re.DOTALL | re.IGNORECASE,
                    )
                    for opening, closing in tag_mismatches:
                        if opening != closing:
                            raise OutputParserException(
                                f"Critical mismatch in block tags:\n\n{block}"
                            )
                # Attempt to repair malformed blocks
                open_tags = re.findall(r"<person(\d+)>", block, re.IGNORECASE)
                close_tags = re.findall(r"</person(\d+)>", block, re.IGNORECASE)

                # Balance mismatched open and closing tags
                if len(open_tags) > len(close_tags):
                    for tag in open_tags[len(close_tags) :]:
                        block += f"</person{tag}>"
                elif len(close_tags) > len(open_tags):
                    for tag in close_tags[len(open_tags) :]:
                        block = f"<person{tag}>" + block

                # Verify after fixing
                fixed_match = re.match(
                    r"<person(\d+)(.*?)>(.*?)</person\1>",
                    block,
                    re.DOTALL | re.IGNORECASE,
                )
                if fixed_match:
                    corrected_blocks.append(block)
                else:
                    raise OutputParserException(
                        f"Unable to automatically fix malformed block. Be sure to use the correct structure `<Person1>...</Person1><Person2>...</Person2>`:\n\n{block}"
                    )

        return corrected_blocks

    @classmethod
    def validate_and_merge_blocks(cls, blocks: List[str]) -> List[str]:
        """Validate and merge consecutive blocks for the same speaker."""
        merged_blocks = []
        current_speaker = None
        current_content = []

        fixed_blocks = cls.fix_blocks(blocks)

        for block in fixed_blocks:
            match = re.match(
                r"<person(\d+)(.*?)>(.*?)</person\1>", block, re.DOTALL | re.IGNORECASE
            )
            if not match:
                raise OutputParserException(
                    f"Malformed block. Verify format and correct tags <person[N]></person[N]>:\n\n{block}"
                )

            speaker, properties, content = match.groups()
            content = content.strip()

            if speaker == current_speaker:
                current_content.append(content)
            else:
                if current_content:
                    merged_blocks.append(
                        f"<Person{current_speaker}{properties}>{' '.join(current_content)}</Person{current_speaker}>"
                    )
                current_speaker = speaker
                current_content = [content]

        if current_content:
            merged_blocks.append(
                f"<Person{current_speaker}{properties}>{' '.join(current_content)}</Person{current_speaker}>"
            )

        return merged_blocks

    def _ensure_alternating_speakers(self, blocks: List[str]) -> List[str]:
        """Ensure the transcript alternates between speakers."""
        if not blocks:
            return blocks

        first_speaker_match = re.match(r"<person(\d+)", blocks[0], re.IGNORECASE)
        last_speaker_match = re.match(r"<person(\d+)", blocks[-1], re.IGNORECASE)

        if not first_speaker_match or not last_speaker_match:
            raise OutputParserException(
                "Transcript must start and end with valid <personN> tags."
            )

        return blocks

    def parse(self, text: Union[str, BaseMessage]) -> str:
        """Parse input, handling both strings and BaseMessage objects."""
        if isinstance(text, BaseMessage):
            text = text.content
        elif not isinstance(text, (str, bytes)):
            raise TypeError(
                f"Expected string, bytes, or BaseMessage, got {type(text).__name__}"
            )

        if "xml" in text:
            xml_block = re.search(r"```xml\n(.*?)\n```", text, re.DOTALL)
            if xml_block:
                xml_string = xml_block.group(1).strip()

                print("Extracted XML string:", xml_string)
                text = xml_string

        # Step 1: Remove <think> and <reflection> tags and their content
        text = clean_tags(text, ["think", "reflection"])

        # Step 2: Remove <output> tags but keep their content
        text = self._strip_tags(text, "output")

        # Step 3: Split text into blocks and validate formatting
        blocks = self.split_blocks(text)

        # Step 4: Validate and merge consecutive blocks for the same speaker
        blocks = self.validate_and_merge_blocks(blocks)

        # Step 5: Ensure the transcript alternates between speakers
        blocks = self._ensure_alternating_speakers(blocks)

        return "\n".join(blocks)


transcript_template = {
    "identity": """
        **Role:** You are an international Oscar-winning screenwriter. You have worked with multiple award-winning podcasters.
    """,
    "identity_extend": """
        **Role:** You are a skilled writer specializing in adding depth, detail, and richness to content. Your expertise lies in expanding ideas, enhancing descriptions, and making content more engaging and comprehensive.
    """,
    "identity_reduce": """
        **Role:** You are a skilled writer with expertise in simplifying and condensing content effectively. Your focus is on maintaining clarity while making content concise, direct, and impactful.
    """,
    "instructions": {
        "rewriter": """
        **Primary Task:** Revise the provided transcript *only* to address the specific issues outlined in the `feedback` (provided in user prompt). Do NOT modify parts of the transcript not specified in the issues.

        **Core Revision Guidelines (Apply ONLY when fixing specified issues):**
        *   **Targeted Fixes:** Address *only* the issues detailed in the `feedback`. Leave all other sections of the transcript untouched.
        *   **Natural Integration:** Ensure your revisions blend seamlessly with the original transcript's flow, tone, and style.
        *   **Adhere to Rewrite Requirements:** If `feedback` includes specific rewrite instructions (e.g., adding conversational dynamics, humor), implement them precisely as requested, following the original configuration (`conversation_style`, `engagement_techniques`, etc. provided in user prompt).
        *   **Preserve Unchanged Sections:** It is critical that parts of the transcript *not* mentioned in the `feedback` remain identical to the original.
        *   **TTS Optimization:** Ensure changes maintain suitability for AI Text-To-Speech (TTS) pipelines and enhance natural engagement where revisions occur.
        *   **Conversational Elements (Targeted):** Incorporate disfluencies, interruptions, banter, etc., *only* in the sections specified by the `feedback`. Do not add these elements elsewhere.
        *   **Word Choice:** In revised sections, avoid overuse of common filler words ("totally," "absolutely," "exactly," "definitely") and vague phrases ("it's like," "[feel] like"). Make revised sections insightful. Avoid filler words.
        *   **Dialogue Structure:** Avoid simple question-answer patterns in revised sections; aim for dynamic discussion. Break up long monologues *only* if specified in the `feedback`.
        *   **Language:** Maintain the `output_language` (specified in user prompt).
        *   **Avoid Past Mistakes:** Do not repeat errors flagged in previous revision attempts (if applicable).
        *   **Main Item:** Highlight the `main_item` (specified in user prompt) *only* if the `feedback` requires adjustments related to it.
        *   **Intros/Conclusions:** Add introductions or conclusions *only* if explicitly requested by the `feedback`.
        *   **Contextual References:** Use `previous_episodes` (from user prompt) for context *only* if the `feedback` requires it.
        *   **Humor:** Use humor (witty comebacks, not "Ha ha") appropriately in revised sections, aligning with the topic. Omit humor for serious/tragic content. Avoid childish remarks.
        *   **Numbers:** Ensure all numbers are written out fully as text (e.g., 'ten' for 10, 'two thousand twenty-four' for 2024, 'first' for 1st, 'may fifth' for May 5th).
        *   **Abbreviations and Units:** Ensure all abbreviations and units are written out as words or natural vocalizations (e.g., 'five gee' for 5G, 'ten centimeters' for 10cm, 'and so on' for etc.), deducing the correct form from context.
        *   **Location Perspective:** Write revisions from the perspective of living in the specified `location` (from user prompt). If none, avoid US-centric assumptions.
        *   **No Arbitrary Changes:** Ensure all changes align strictly with the `feedback` and instructions; do not introduce modifications not requested.
        *   **Full Transcript Output:** ALWAYS return the complete transcript, including both unchanged and revised sections.
        """,
    },
    "length": {
        "maintain": """
        **Length Goal:** Maintain the original transcript's approximate word count.
        *   The output transcript must have at least the word count specified in the user prompt (`word_count`).
        *   Do not significantly reduce or increase the length of the conversation.
        *   Ensure the output transcript includes all content and segments from the input transcript.
        """,
        "extend": """
        **Length Goal:** Significantly expand the transcript to meet or exceed the target `word_count` (from user prompt).
        *   Use provided `content`, context, and feedback to enrich and lengthen the conversation substantially.
        *   Aim for a much longer transcript (e.g., potentially twice the original length or more), prioritizing depth and detail while maintaining coherence.
        *   Strive to utilize the available token limit effectively for maximum expansion without sacrificing quality.
        *   Ensure the output transcript includes all original segments, expanded as needed.
        """,
        "reduce": """
        **Length Goal:** Compress the transcript to fit within the target `word_count` (from user prompt).
        *   Focus on concise phrasing and eliminating redundancy while preserving *all* key content and meaning.
        *   Prioritize brevity to achieve the shortest possible version that still covers everything.
        *   Ensure the output transcript includes all essential information from the original segments.
        *   **Formatting Constraint:** Do not revert numbers/abbreviations back to symbols/digits during reduction. Maintain the text/vocalization format (e.g., 'ten', 'five gee').
        """,
    },
    "format": """
        **Output Format Requirements:**
        *   Structure: Use the `<Person1>...</Person1><Person2>...</Person2>` format.
        *   Tagging: Ensure all speaker tags are correctly opened and closed (e.g., `<Person1>` closed by `</Person1>`).
        *   Encapsulation: All spoken text must be enclosed within speaker tags.
        *   Sequence: The conversation must start with `<Person1>` and end with `<Person2>`.
        *   Numbers: Write all numbers fully as text (e.g., 'ten', 'two thousand twenty-four', 'first', 'may fifth').
        *   Abbreviations/Units: Write all abbreviations and units as words or natural vocalizations (e.g., 'five gee', 'ten centimeters', 'and so on').
        """,
}
