import hashlib
import re
from typing import Union
import os
from lxml import etree as ET

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage

# Removed: from langchain_core.output_parsers.xml import XMLOutputParser

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
    """Custom parser to process and validate podcast transcripts using lxml."""

    def _strip_tags(self, text: str, tag: str) -> str:
        """Remove specific tags but keep their content."""
        return re.sub(rf"</?{tag}.*?>", "", text, flags=re.IGNORECASE)

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

        # print("Cleaned text for parsing:", text)

        # Ensure the text is wrapped in a root element if it isn't already
        if not text.strip().startswith("<root>"):
            if re.match(r"^\s*<Person\d+", text.strip(), re.IGNORECASE):
                text = f"<root>{text}</root>"
            else:
                print(
                    "Warning: Input text doesn't start with <root> or <PersonN>. Wrapping in <root>."
                )
                text = f"<root>{text}</root>"

        # Step 4: Parse XML using lxml.etree
        try:
            # Use lxml's parser with recovery enabled
            # Encode string to bytes for lxml parser
            if isinstance(text, str):
                text_bytes = text.strip().encode("utf-8")
            elif isinstance(text, bytes):
                text_bytes = text.strip()
            else:
                # Should not happen due to earlier type check, but safety first
                raise TypeError(
                    f"Unexpected type for text before parsing: {type(text).__name__}"
                )

            # Configure parser for security and recovery
            # no_network=True prevents external DTD/entity resolution
            # recover=True attempts to parse even with errors
            # resolve_entities=False prevents entity expansion (important for security)
            parser = ET.XMLParser(
                recover=True, no_network=True, resolve_entities=False, encoding="utf-8"
            )
            root = ET.fromstring(text_bytes, parser=parser)

            # Check if recovery actually happened and if the root is None (indicates severe error)
            if root is None:
                # Access parser error log if needed
                error_log = parser.error_log
                raise OutputParserException(
                    f"XML parsing failed severely, unable to recover a root element. Error log: {error_log}\nInput text:\n{text}"
                )

        except ET.XMLSyntaxError as e:
            # lxml provides detailed syntax errors
            raise OutputParserException(
                f"XML parsing failed: {e}\n"
                f"Error details: {e.msg}\n"
                f"Line: {e.lineno}, Column: {e.offset}\n"
                f"Input text:\n{text}"
            )
        except Exception as e:  # Catch other potential exceptions
            raise OutputParserException(
                f"An unexpected error occurred during XML parsing: {e}\nInput text:\n{text}"
            )

        blocks = []

        # Step 5: Process parsed elements and reconstruct tags
        for element in root:
            tag = element.tag
            # Ensure attributes are strings, handle potential None values gracefully
            attrs = {
                k: str(v) if v is not None else "" for k, v in element.attrib.items()
            }
            text_content = (element.text or "").strip()

            # Generate 'id' attribute based on text_content if it's not set and tag starts with 'Person'
            if "id" not in attrs and tag.lower().startswith("person") and text_content:
                id_hash = hashlib.md5(text_content.encode("utf-8")).hexdigest()[:8]
                attrs["id"] = f"{id_hash}"

            # Join attributes into a tag string, ensuring proper quoting
            attrs_string = " ".join(f'{k}="{v}"' for k, v in attrs.items())

            # Reconstruct the tag string
            if attrs_string:
                tag_string = f"<{tag} {attrs_string}>{text_content}</{tag}>"
            else:
                tag_string = f"<{tag}>{text_content}</{tag}>"

            if tag_string:
                blocks.append(tag_string)

        # Commented out sections remain unchanged

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
        *   **Normalization Constraint:** During reduction, all text-to-speech normalization must be strictly maintained. Do not revert any of the following to symbols, digits, abbreviations, or non-spoken forms:
            - Numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals) must always be written out as words (e.g., "ten" for 10, "zero point one" for 0.1, "two thousand twenty-four" for 2024, "may fifth" for May 5th, "first" for 1st, "forty-two dollars and fifty cents" for $42.50, "five five five, five five five, five five five five" for 555-555-5555, "three point one four" for 3.14, "two-thirds" for ⅔, "fourteen" for XIV unless a title, then "the fourteenth").
            - Abbreviations and units must always be expanded to their full spoken forms or natural vocalizations (e.g., "five gee" for 5G, "ten centimeters" for 10cm, "ten million" for 10M, "megabyte" for MB, "and so on" for etc., "Doctor" for Dr., "Avenue" for Ave., "Street" for St. except in names like "St. Patrick").
            - Alphanumeric shortcuts and symbols must be expanded (e.g., "control z" for Ctrl + Z, "one hundred percent" for 100%).
            - URLs must be written as spoken (e.g., "eleven labs dot io slash docs" for elevenlabs.io/docs).
            - Dates, times, and addresses must be written out in natural spoken form (e.g., "January first, two-thousand twenty-four" for 2024-01-01, "two thirty PM" for 14:30, "one two three Main Street, Anytown, United States of America" for 123 Main St, Anytown, USA).
        *   If a specific spoken format is required for a context, follow the explicit instructions in the prompt.
        *   **Flow Constraint:** Ensure the flow of discussion is maintained at all times. Avoid abrupt changes of subject or phrasing that could cause the listener to lose track of what has been discussed. Transitions should be smooth and preserve coherence throughout.
        """,
    },
    "format": """
        **Output Format Requirements:**
        *   Structure: Use the `<Person1>...</Person1><Person2>...</Person2>` format.
        *   Each <PersonN>-tag can have `emote`, `id` args. If they're defined in the input, then they must be kept.
        *   `emote` argument can contain text to speech friendly description of how the person expresses his line. E.g. `"He spoke with excitement and a cheerful tone"`. Emote must match the person's profile and persona. If multiple tags are rewritten as one, rewrite the emote description to match. The description should be limited to voice and speech style, characteristics, and dynamics.
        *   `id` will be an id to refer the tag instance with. If there's none defined, do not define one, otherwise keep the one which has been previously defined. If multiple tags are rewritten as one, take the first id.
        *   Tagging: Ensure all speaker tags are correctly opened and closed (e.g., `<Person1>` closed by `</Person1>`).
        *   Encapsulation: All spoken text must be enclosed within speaker tags.
        *   Sequence: The conversation must start with `<Person1>` and end with `<Person2>`.
        *   A person may have multiple tags after one another if there's a clear change in subject or it's otherwise needed.

        **TTS Normalization Requirements:**
        *   Convert all output text into a format suitable for text-to-speech. Ensure that numbers, symbols, and abbreviations are expanded for clarity when read aloud.
        *   Expand all abbreviations to their full spoken forms.
        *   Normalize the following cases:
            - Cardinal numbers: `123` → "one hundred twenty-three"
            - Ordinal numbers: `2nd` → "second"
            - Monetary values: `$45.67` → "forty-five dollars and sixty-seven cents"
            - Phone numbers: `123-456-7890` → "one two three, four five six, seven eight nine zero"
            - Decimals & Fractions: `3.5` → "three point five", `⅔` → "two-thirds"
            - Roman numerals: `XIV` → "fourteen" (or "the fourteenth" if a title)
            - Abbreviations: `Dr.` → "Doctor", `Ave.` → "Avenue", `St.` → "Street" (but "St. Patrick" should remain)
            - Alphanumeric shortcuts: `Ctrl + Z` → "control z"
            - Abbreviations for units: `100km` → "one hundred kilometers"
            - Symbols: `100%` → "one hundred percent"
            - URLs: `elevenlabs.io/docs` → "eleven labs dot io slash docs"
            - Calendar events: `2024-01-01` → "January first, two-thousand twenty-four"
            - Addresses: `123 Main St, Anytown, USA` → "one two three Main Street, Anytown, United States of America"
            - Time: `14:30` → "two thirty PM"
            - Dates: `01/02/2023` → "January second, two-thousand twenty-three" or "the first of February, two-thousand twenty-three", depending on locale
        *   If a specific spoken format is required for a context, follow the explicit instructions in the prompt.
        *   See these examples for reference:
            - `"$42.50"` → "forty-two dollars and fifty cents"
            - `"£1,001.32"` → "one thousand and one pounds and thirty-two pence"
            - `"1234"` → "one thousand two hundred thirty-four"
            - `"3.14"` → "three point one four"
            - `"555-555-5555"` → "five five five, five five five, five five five five"
            - `"2nd"` → "second"
            - `"XIV"` → "fourteen" (unless a title, then "the fourteenth")
            - `"3.5"` → "three point five"
            - `"⅔"` → "two-thirds"
            - `"Dr."` → "Doctor"
            - `"Ave."` → "Avenue"
            - `"St."` → "Street" (but "St. Patrick" should remain)
            - `"Ctrl + Z"` → "control z"
            - `"100km"` → "one hundred kilometers"
            - `"100%"` → "one hundred percent"
            - `"elevenlabs.io/docs"` → "eleven labs dot io slash docs"
            - `"2024-01-01"` → "January first, two-thousand twenty-four"
            - `"123 Main St, Anytown, USA"` → "one two three Main Street, Anytown, United States of America"
            - `"14:30"` → "two thirty PM"
            - `"01/02/2023"` → "January second, two-thousand twenty-three" or "the first of February, two-thousand twenty-three", depending on locale

        *If you encounter edge cases, use your best judgment to produce the most natural and clear spoken form for TTS.*
        """,
}
