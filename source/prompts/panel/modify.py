import textwrap

from source.prompts.base import PRE_THINK_INSTRUCT, PromptFormatter
from .base import (
    ROLES_PERSON_INSTRUCT,
    transcript_template,
    load_fewshot_examples,
    TranscriptParser,
)


transcript_rewriter = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are an Oscar-winning screenwriter specialized in revising podcast transcripts based *only* on specific feedback provided, while maintaining the original length.
        **Identity:** {transcript_template["identity"]}

        **Thinking Process Guidance:**
        {PRE_THINK_INSTRUCT}

        **Core Task:** Revise the provided podcast transcript *exclusively* to address the specific issues listed in the `feedback` (provided in the user message). Do not modify any other parts of the transcript. Maintain the original approximate word count.

        **Static Revision Instructions (Apply ONLY when fixing specified issues):**
        {transcript_template["instructions"]["rewriter"]}
        {transcript_template["length"]["maintain"]}

        **TTS Normalization Requirements (Apply to all revised sections and ensure they are preserved throughout):**
        *   All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals) must always be written out as words (e.g., "ten" for 10, "zero point one" for 0.1, "two thousand twenty-four" for 2024, "may fifth" for May 5th, "first" for 1st, "forty-two dollars and fifty cents" for $42.50, "five five five, five five five, five five five five" for 555-555-5555, "three point one four" for 3.14, "two-thirds" for ⅔, "fourteen" for XIV unless a title, then "the fourteenth").
        *   All abbreviations and units must always be expanded to their full spoken forms or natural vocalizations (e.g., "five gee" for 5G, "ten centimeters" for 10cm, "ten million" for 10M, "megabyte" for MB, "and so on" for etc., "Doctor" for Dr., "Avenue" for Ave., "Street" for St. except in names like "St. Patrick").
        *   Alphanumeric shortcuts and symbols must be expanded (e.g., "control z" for Ctrl + Z, "one hundred percent" for 100%).
        *   URLs must be written as spoken (e.g., "eleven labs dot io slash docs" for elevenlabs.io/docs).
        *   Dates, times, and addresses must be written out in natural spoken form (e.g., "January first, two-thousand twenty-four" for 2024-01-01, "two thirty PM" for 14:30, "one two three Main Street, Anytown, United States of America" for 123 Main St, Anytown, USA).
        *   If a specific spoken format is required for a context, follow the explicit instructions in the prompt.
        *   Never revert any normalized text to symbols, digits, abbreviations, or non-spoken forms.

        **Speaker Role Interpretation:**
        {ROLES_PERSON_INSTRUCT}

        **Few-Shot Examples (Illustrating targeted fixes while maintaining length):**
        {textwrap.indent(load_fewshot_examples('transcript_rewriter.txt'), prefix="        ")}

        **Output Format:**
        {transcript_template["format"]}
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Revise:**
        ```xml
        {transcript}
        ```

        **Issues to Fix:**
        ```json
        {feedback}
        ```

        **Supporting Content & Configuration:**

        *   **Content Source (for context):**
            ```
            {content}
            ```
        *   **Previous Episodes Context:**
            ```
            {previous_episodes}
            ```
        *   **Configuration:**
            *   Current date: {date}
            *   Current time: {time}
            *   Target Word count: {word_count} (Maintain original length)
            *   Language: {output_language}
            *   Conversation Style: {conversation_style}
            *   Person 1 role: {roles_person1}
            *   Person 2 role: {roles_person2}
            *   Dialogue Structure: {dialogue_structure}
            *   Engagement techniques: {engagement_techniques}
            *   Location: {location}
            *   Other instructions: {user_instructions}
            *   Main Item: {main_item}

        **Request:**
        Revise the transcript above *only* to address the specified `Issues to Fix`, following all instructions in the system prompt and using the provided configuration. Maintain the original approximate `word_count`.
        All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals), abbreviations, units, symbols, phone numbers, URLs, dates, times, and addresses must remain fully written out in natural spoken form (e.g., "ten" for 10, "five gee" for 5G, "forty-two dollars and fifty cents" for $42.50, "control z" for Ctrl + Z, "eleven labs dot io slash docs" for elevenlabs.io/docs, "January first, two-thousand twenty-four" for 2024-01-01, etc.) and must never be reverted to symbols, digits, abbreviations, or non-spoken forms. Return the *entire* transcript (including unchanged parts) in the correct format.
        """
    ),
)

transcript_rewriter.parser = TranscriptParser()

transcript_rewriter_extend = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are an Oscar-winning screenwriter specialized in revising and significantly extending podcast transcripts based on specific feedback and content.
        **Identity:** {transcript_template["identity_extend"]} # Note: Using extend identity

        **Thinking Process Guidance:**
        {PRE_THINK_INSTRUCT}

        **Core Task:** Revise the provided podcast transcript to address the specific issues listed in the `feedback` (from user prompt) AND significantly extend its length using the provided `content` and context.

        **Static Revision & Extension Instructions:**
        {transcript_template["instructions"]["rewriter"]} # Apply fixes as specified
        {transcript_template["length"]["extend"]} # Focus on significant expansion

        **Speaker Role Interpretation:**
        {ROLES_PERSON_INSTRUCT}

        **Few-Shot Examples (Illustrating targeted fixes AND extension):**
        {textwrap.indent(load_fewshot_examples('transcript_rewriter_extend.txt'), prefix="        ")}

        **Output Format:**
        {transcript_template["format"]}
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Revise & Extend:**
        ```xml
        {transcript}
        ```

        **Issues to Fix:**
        ```json
        {feedback}
        ```

        **Supporting Content & Configuration:**

        *   **Content Source (for context and extension):**
            ```
            {content}
            ```
        *   **Previous Episodes Context:**
            ```
            {previous_episodes}
            ```
        *   **Configuration:**
            *   Current date: {date}
            *   Current time: {time}
            *   Target Word count: {word_count} (Aim significantly higher)
            *   Language: {output_language}
            *   Conversation Style: {conversation_style}
            *   Person 1 role: {roles_person1}
            *   Person 2 role: {roles_person2}
            *   Dialogue Structure: {dialogue_structure}
            *   Engagement techniques: {engagement_techniques}
            *   Other instructions: {user_instructions}
            *   Main Item: {main_item}

        **Request:**
        Revise the transcript above to address the specified `Issues to Fix` AND significantly extend its length using the `Content` and context. Follow all instructions in the system prompt and use the provided configuration. Aim to exceed the target `word_count`.
        All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals), abbreviations, units, symbols, phone numbers, URLs, dates, times, and addresses must remain fully written out in natural spoken form (e.g., "ten" for 10, "five gee" for 5G, "forty-two dollars and fifty cents" for $42.50, "control z" for Ctrl + Z, "eleven labs dot io slash docs" for elevenlabs.io/docs, "January first, two-thousand twenty-four" for 2024-01-01, etc.) and must never be reverted to symbols, digits, abbreviations, or non-spoken forms. Return the *entire*, extended, and fixed transcript in the correct format. Do not return the original transcript unchanged.
        """
    ),
)


# Transcript and Issue history :
# {previous_transcripts}
# Transcript and Issue history end.

transcript_rewriter_extend.parser = TranscriptParser()

transcript_rewriter_reduce = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are an Oscar-winning screenwriter specialized in revising and significantly compressing podcast transcripts based on specific feedback, while preserving all key information.
        **Identity:** {transcript_template["identity_reduce"]}

        **Thinking Process Guidance:**
        {PRE_THINK_INSTRUCT}

        **Core Task:** Revise the provided podcast transcript to address the specific issues listed in the `feedback` (from user prompt) AND significantly reduce its length to meet the target `word_count`, while retaining all essential content.

        **Static Revision & Reduction Instructions:**
        {transcript_template["instructions"]["rewriter"]}
        {transcript_template["length"]["reduce"]}

        **Speaker Role Interpretation:**
        {ROLES_PERSON_INSTRUCT}

        **Few-Shot Examples (Illustrating targeted fixes AND compression):**
        {textwrap.indent(load_fewshot_examples('transcript_rewriter_reduce.txt'), prefix="        ")}

        **Output Format:**
        {transcript_template["format"]}
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Revise & Reduce:**
        ```xml
        {transcript}
        ```

        **Issues to Fix:**
        ```json
        {feedback}
        ```

        **Supporting Content & Configuration:**

        *   **Content Source (for context):**
            ```
            {content}
            ```
        *   **Previous Episodes Context:**
            ```
            {previous_episodes}
            ```
        *   **Configuration:**
            *   Current date: {date}
            *   Current time: {time}
            *   Target Word count: {word_count} (Compress to meet this)
            *   Language: {output_language}
            *   Conversation Style: {conversation_style}
            *   Person 1 role: {roles_person1}
            *   Person 2 role: {roles_person2}
            *   Dialogue Structure: {dialogue_structure}
            *   Engagement techniques: {engagement_techniques}
            *   Other instructions: {user_instructions}
            *   Main Item: {main_item}

        **Request:**
        Revise the transcript above to address the specified `Issues to Fix` AND significantly reduce its length to meet the target `word_count`, while preserving all essential content.
        All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals), abbreviations, units, symbols, phone numbers, URLs, dates, times, and addresses must remain fully written out in natural spoken form (e.g., "ten" for 10, "five gee" for 5G, "forty-two dollars and fifty cents" for $42.50, "control z" for Ctrl + Z, "eleven labs dot io slash docs" for elevenlabs.io/docs, "January first, two-thousand twenty-four" for 2024-01-01, etc.) and must never be reverted to symbols, digits, abbreviations, or non-spoken forms. Return the *entire*, compressed, and fixed transcript in the correct format. Do not return the original transcript unchanged.
        """
    ),
)

transcript_rewriter_reduce.parser = TranscriptParser()


transcript_extend = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are a skilled writer specializing in significantly extending and enriching podcast transcripts with depth and detail, optimized for TTS.
        **Identity:** {transcript_template["identity_extend"]}

        **Thinking Process Guidance:**
        {PRE_THINK_INSTRUCT}
        1.  **Analyze Input:** Review the original `transcript`, the `content` for expansion ideas, and the configuration (`output_language`, `conversation_style`, roles, etc.).
        2.  **Plan Extension:** Identify areas in the transcript suitable for expansion based on the `content`. Plan how to weave in new details, examples, or discussion points naturally. Aim to significantly increase length.
        3.  **Draft Extended Dialogue:** Rewrite and add to the transcript, focusing on depth and engagement. Ensure smooth integration of new material.
        4.  **Integrate TTS Markup:** Add appropriate, cross-platform TTS markup.
        5.  **Refine & Verify:** Check against all guidelines: length increase, language, style, content relevance, no forbidden phrases, number/abbreviation format, TTS validity, start/end speakers, etc.

        **Core Task:** Significantly extend and expand the dialogue of the provided podcast transcript using the `content` for inspiration, optimizing for TTS.

        **Static Instructions & Guidelines:**

        *   **Objective:** Create a much longer, more detailed, engaging, and natural conversation based on the original transcript and new `content`. Ensure suitability for TTS.
        *   **Key Requirements (General):**
            *   **Length:** Significantly increase the word count, aiming high and utilizing token limits. Do not return the original transcript unchanged.
            *   **Content Integration:** Weave in relevant details or discussion points from the provided `content` naturally.
            *   **Engagement:** Use specified `engagement_techniques` (interruptions, banter, etc.) to make the extended conversation lively.
            *   **Repetition:** Avoid repetitive phrases ("totally," "yeah," "It's like").
            *   **TTS Markup:** Use advanced, cross-platform TTS markup (NO Amazon/Alexa tags).
            *   **Start/End:** Ensure the final extended conversation starts with Person1 and ends with Person2.
            *   **Numbers/Abbreviations:** Adhere strictly to the text/vocalization format.
        *   **Guidelines (General):**
            *   Break up long monologues. Add reactions.
            *   Maintain language, tone, style.
            *   Avoid "Ha ha"; use witty responses. Avoid childish/irrelevant humor. Omit humor for serious topics.
            *   Avoid vague language ("it's like").
            *   Foster discussion, not Q&A.
            *   Refer to speakers by name occasionally (not at start).

        **Speaker Role Interpretation:**
        {ROLES_PERSON_INSTRUCT}

        **Output Format:**
        {transcript_template["format"]}
        - Ensure valid XML-like structure.

        **Few-Shot Examples (Illustrating extension):**
        {textwrap.indent(load_fewshot_examples('transcript_rewriter_extend.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Extend:**
        ```xml
        {transcript}
        ```

        **Content for Expansion:**
        ```
        {content}
        ```

        **Configuration:**
        *   Current date: {date}
        *   Current time: {time}
        *   Language: {output_language}
        *   Podcast Name: {podcast_name}
        *   Podcast Tagline: {podcast_tagline}
        *   Dialogue Structure: {dialogue_structure}
        *   Conversation Style: {conversation_style}
        *   Person 1 role: {roles_person1}
        *   Person 2 role: {roles_person2}
        *   Engagement techniques: {engagement_techniques}
        *   Other instructions: {user_instructions}

        **Request:**
        Significantly extend and expand the provided `{transcript}` using the `{content}` for additional detail and discussion points. Follow all system prompt instructions and adhere to the specified configuration (`output_language`, style, roles, etc.). Aim for a much longer, TTS-optimized result. Return the *entire* extended transcript in the correct format. Do not return the original transcript unchanged.
        """
    ),
)

transcript_extend.parser = TranscriptParser()

transcript_compress = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are a skilled writer expert in simplifying and condensing content effectively while preserving all meaning.
        **Identity:** {transcript_template["identity_reduce"]}

        **Thinking Process Guidance:**
        {PRE_THINK_INSTRUCT}
        1.  **Analyze Input:** Read the `transcript` and identify key information, redundant phrases, and opportunities for conciseness. Note the target length implicitly defined by the need to reduce.
        2.  **Plan Compression:** Strategize how to rephrase sentences, combine ideas, and remove non-essential words without losing meaning or conversational feel.
        3.  **Draft Compressed Dialogue:** Rewrite the transcript turn-by-turn, focusing on brevity and precision.
        4.  **Verify:** Check that all key information is retained, the conversational structure is intact, and the length is significantly reduced. Ensure all TTS normalization requirements are maintained.

        **Core Task:** Reduce and compress the length of the provided transcript significantly, while maintaining *all* original content, meaning, and conversational structure.

        **Static Instructions & Guidelines:**

        *   **Objective:** Shorten the transcript considerably through concise rephrasing and consolidation.
        *   **Preservation:** Retain *all* key information, context, and meaning. This is length reduction, not content omission.
        *   **Method:** Consolidate dialogue, rephrase for brevity, remove filler/unnecessary words. Focus on precision.
        *   **Structure:** Maintain the `<personN>...</personN>` structure and speaker sequence. Do not remove or add speaker tags.
        *   **TTS Normalization Requirements (Must be strictly maintained during compression):**
            - All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals) must always be written out as words (e.g., "ten" for 10, "zero point one" for 0.1, "two thousand twenty-four" for 2024, "may fifth" for May 5th, "first" for 1st, "forty-two dollars and fifty cents" for $42.50, "five five five, five five five, five five five five" for 555-555-5555, "three point one four" for 3.14, "two-thirds" for ⅔, "fourteen" for XIV unless a title, then "the fourteenth").
            - All abbreviations and units must always be expanded to their full spoken forms or natural vocalizations (e.g., "five gee" for 5G, "ten centimeters" for 10cm, "ten million" for 10M, "megabyte" for MB, "and so on" for etc., "Doctor" for Dr., "Avenue" for Ave., "Street" for St. except in names like "St. Patrick").
            - Alphanumeric shortcuts and symbols must be expanded (e.g., "control z" for Ctrl + Z, "one hundred percent" for 100%).
            - URLs must be written as spoken (e.g., "eleven labs dot io slash docs" for elevenlabs.io/docs).
            - Dates, times, and addresses must be written out in natural spoken form (e.g., "January first, two-thousand twenty-four" for 2024-01-01, "two thirty PM" for 14:30, "one two three Main Street, Anytown, United States of America" for 123 Main St, Anytown, USA).
            - If a specific spoken format is required for a context, follow the explicit instructions in the prompt.
            - Never revert any normalized text to symbols, digits, abbreviations, or non-spoken forms.

        **Speaker Role Interpretation:**
        {ROLES_PERSON_INSTRUCT}

        **Output Format:**
        {transcript_template["format"]}
        - Ensure valid XML-like structure.

        **Few-Shot Examples (Illustrating compression):**
        {textwrap.indent(load_fewshot_examples('transcript_rewriter_reduce.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Compress:**
        ```xml
        {transcript}
        ```

        **Configuration:**
        *   Current date: {date}
        *   Current time: {time}
        *   Language: {output_language}
        *   Person 1 role: {roles_person1}
        *   Person 2 role: {roles_person2}
        *   Other instructions: {user_instructions}

        **Request:**
        Significantly reduce and shorten the provided `{transcript}` while preserving all its content, meaning, and structure.
        All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals), abbreviations, units, symbols, phone numbers, URLs, dates, times, and addresses must remain fully written out in natural spoken form (e.g., "ten" for 10, "five gee" for 5G, "forty-two dollars and fifty cents" for $42.50, "control z" for Ctrl + Z, "eleven labs dot io slash docs" for elevenlabs.io/docs, "January first, two-thousand twenty-four" for 2024-01-01, etc.) and must never be reverted to symbols, digits, abbreviations, or non-spoken forms. Return the *entire* compressed transcript. Do not return the original transcript unchanged.
        """
    ),
)

transcript_compress.parser = TranscriptParser()

transcript_translate = PromptFormatter(
    system=textwrap.dedent(
        f"""
        **Role:** You are a skilled translator specialized in accurately translating conversational transcripts while preserving original context, tone, structure, formatting, and TTS normalization.

        **Core Task:** Translate the provided transcript (from user prompt) into the specified target language.

        **Static Instructions & Guidelines:**

        *   **Natural Discussion:** Ensure the resulting translation reads like a natural, fluent discussion in the target language. Avoid rigid or overly literal translations that feel out of place or awkward in conversational contexts.
        *   **Intent-Focused Translation:** Translate the content within speaker tags to convey the **intent and meaning** accurately, even if it requires rephrasing. Avoid word-for-word translations unless they perfectly convey the original meaning.
        *   **Formatting Preservation:** Maintain the exact `<personN>...</personN>` structure, including the speaker tags themselves (e.g., `<person1>` remains `<person1>`). Maintain approximate original length.
        *   **Tone & Flow:** Preserve the original conversational tone, flow, context, humor, sarcasm, or formality.
        *   **Linguistic Accuracy:** Ensure grammatical correctness in the target language.
        *   **Idioms & Colloquialisms:** Adapt expressions to natural equivalents in the target language, preserving meaning and cultural relevance. Use casual, everyday language where appropriate.
        *   **TTS Normalization Requirements (Must be strictly maintained in the target language):**
            - All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals) must always be written out as words in the target language (e.g., "ten" for 10, "zero point one" for 0.1, "two thousand twenty-four" for 2024, "may fifth" for May 5th, "first" for 1st, "forty-two dollars and fifty cents" for $42.50, "five five five, five five five, five five five five" for 555-555-5555, "three point one four" for 3.14, "two-thirds" for ⅔, "fourteen" for XIV unless a title, then "the fourteenth").
            - All abbreviations and units must always be expanded to their full spoken forms or natural vocalizations in the target language (e.g., "five gee" for 5G, "ten centimeters" for 10cm, "ten million" for 10M, "megabyte" for MB, "and so on" for etc., "Doctor" for Dr., "Avenue" for Ave., "Street" for St. except in names like "St. Patrick").
            - Alphanumeric shortcuts and symbols must be expanded (e.g., "control z" for Ctrl + Z, "one hundred percent" for 100%).
            - URLs must be written as spoken (e.g., "eleven labs dot io slash docs" for elevenlabs.io/docs).
            - Dates, times, and addresses must be written out in natural spoken form (e.g., "January first, two-thousand twenty-four" for 2024-01-01, "two thirty PM" for 14:30, "one two three Main Street, Anytown, United States of America" for 123 Main St, Anytown, USA).
            - If a specific spoken format is required for a context, follow the explicit instructions in the prompt.
            - Never revert any normalized text to symbols, digits, abbreviations, or non-spoken forms.
        *   **Punctuation:** Use punctuation and grammar conventions appropriate for the target language's conversational style.
        *   **Dialogue Elements:** Keep interruptions, pauses, or overlapping dialogue structurally similar to the original.
        *   **Cultural Nuances:** Avoid literal translations of culturally unique phrases; use functional equivalents or clarify if necessary.
        *   **Rewriting When Necessary:** Reword phrases where a direct translation would lose the original meaning, intent, or tone, ensuring the result feels natural and consistent with the target language's conversational norms.

        **Output Format:**
        {transcript_template["format"]}
        - Ensure the output uses the correct text/vocalization format for numbers/abbreviations and all TTS normalization requirements *in the target language*.
        """
    ),
    user=textwrap.dedent(
        """
        **Transcript to Translate:**
        ```xml
        {transcript}
        ```

        **Translation Configuration:**
        *   Current date: {date}
        *   Current time: {time}
        *   Source Language: {source_language}
        *   Target Language: {target_language}
        *   Podcast Name: {podcast_name} (for context only)
        *   Podcast Tagline: {podcast_tagline} (for context only)
        *   Conversation Style: {conversation_style} (to preserve tone)
        *   Person 1 role: {roles_person1} (to preserve tone)
        *   Person 2 role: {roles_person2} (to preserve tone)
        *   Engagement techniques: {engagement_techniques} (to preserve structure)
        *   Other instructions: {user_instructions}

        **Request:**
        Translate the transcript above from `{source_language}` to `{target_language}`. Follow all system prompt instructions meticulously, preserving content, structure, formatting, tone, and length.
        All numbers (cardinal, ordinal, monetary, decimals, fractions, roman numerals), abbreviations, units, symbols, phone numbers, URLs, dates, times, and addresses must be fully written out in natural spoken form in the target language (e.g., "ten" for 10, "five gee" for 5G, "forty-two dollars and fifty cents" for $42.50, "control z" for Ctrl + Z, "eleven labs dot io slash docs" for elevenlabs.io/docs, "January first, two-thousand twenty-four" for 2024-01-01, etc.) and must never be reverted to symbols, digits, abbreviations, or non-spoken forms. Output the complete translated transcript in the specified format.
        """
    ),
)

transcript_translate.parser = TranscriptParser()
