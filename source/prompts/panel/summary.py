import textwrap

from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage

from source.models.structures.panel import TranscriptSummary
from source.prompts.base import PromptFormatter
from .base import load_fewshot_examples


transcript_summary_parser = PydanticOutputParser(pydantic_object=TranscriptSummary)


class TranscriptSummaryValidator:
    def parse(self, raw_input: str) -> TranscriptSummary:
        # Clean the <think> and <reflection> tags
        cleaned_input = raw_input
        if isinstance(raw_input, BaseMessage):
            cleaned_input = raw_input.content

        # cleaned_input = self.cleaner.parse(raw_input)

        # Parse the cleaned input into a WebSourceGrouping object
        parsed_response = transcript_summary_parser.parse(cleaned_input)

        return parsed_response


transcript_summary_formatter = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are an expert summarizer analyzing podcast transcripts.

        **Task:** Analyze the provided transcript and generate a structured summary containing:
        1.  **Title:** Concise and engaging (max 90 chars), summarizing specific subjects. Avoid generalizations.
        2.  **Main Subject:** Identify the single most important subject discussed.
        3.  **Subjects List:** List all key subjects/topics covered, with brief details for each.
        4.  **Description:** A 2-3 sentence summary of the entire transcript's discussion.

        **Static Guidelines:**
        *   Do not include the `podcast_name` or `podcast_tagline` (from user prompt) in your generated title, subjects, or description.
        *   Ensure all generated text adheres to the number/abbreviation text/vocalization format.

        **Few-Shot Examples (Illustrating title/subject generation):**
        {textwrap.indent(load_fewshot_examples('transcript_summary_formatter.txt'), prefix="        ")}

        **Output Format:**
        Strictly adhere to the JSON schema provided below.
        {transcript_summary_parser.get_format_instructions()}
        """
    ),
    user=textwrap.dedent(
        """
        **Input for Summary:**

        *   **Transcript to Summarize:**
            ```xml
            {transcript}
            ```
        *   **Subject Hints (Optional):**
            ```
            {subjects}
            ```
        *   **Configuration:**
            *   Language: {output_language}
            *   Podcast name: {podcast_name} (Do NOT use in output)
            *   Podcast tagline: {podcast_tagline} (Do NOT use in output)

        **Request:**
        Analyze the `{transcript}` using the optional `{subjects}` hints and the specified `{output_language}`. Generate the title, main subject, subjects list, and description according to the system prompt instructions and the required JSON format.
        """
    ),
)

transcript_summary_formatter.parser = TranscriptSummaryValidator()
