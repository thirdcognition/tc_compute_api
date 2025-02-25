import re
from source.prompts.base import TagsParser, clean_tags
import textwrap
from typing import List, Union
from pydantic import BaseModel, Field
from langchain_core.exceptions import OutputParserException
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage

# from source.prompts.actions import QuestionClassifierParser
from source.prompts.base import (
    ACTOR_INTRODUCTIONS,
    PRE_THINK_INSTRUCT,
    BaseOutputParser,
    PromptFormatter,
)
from source.models.config.default_env import DEFAULT_PATH
import os


# Function to load fewshot examples from the file
def load_fewshot_examples(filename: str) -> str:
    file_path = os.path.join(DEFAULT_PATH, "fewshot_data", filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return "FEWSHOT EXAMPLES:\n" + file.read()
    except FileNotFoundError:
        print(f"Fewshot examples file not found: {file_path}")
        return ""


# Get prompts from:
# https://smith.langchain.com/hub/heurekalabs/podcastfy_multimodal_cleanmarkup_beginning?organizationId=de27563a-abea-51c1-93ae-bc32bd8606e9
# https://smith.langchain.com/hub/heurekalabs/podcastfy_multimodal_cleanmarkup_middle?organizationId=de27563a-abea-51c1-93ae-bc32bd8606e9
# https://smith.langchain.com/hub/heurekalabs/podcastfy_multimodal_cleanmarkup_ending?organizationId=de27563a-abea-51c1-93ae-bc32bd8606e9

ROLES_PERSON_INSTRUCT = """
        When generating dialogue or content, use the roles defined in `Person N role` to shape the tone, style, and perspective of each speaker. Each role provides the following attributes:
        - **Name**: The speaker's name, which should be used to personalize the dialogue.
        - **Persona**: The speaker's personality traits or characteristics, which should influence their tone and style of speech.
        - **Role**: The speaker's functional or thematic role in the conversation, which should guide the content and focus of their contributions.

        Ensure that:
        1. The dialogue reflects the unique persona and role of each speaker.
        2. Person 1 references Person 2 by their Name, and Person 2 references Person 1 by their Name.
        3. Both speakers address the audience as "you."
        4. The content aligns with the specified conversation style and engagement techniques.
        5. The roles are consistently applied throughout the conversation to maintain coherence and authenticity.
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


class TranscriptQualityIssue(BaseModel):
    title: str = Field(..., title="Title", description="Title describing the issue.")
    details: str = Field(
        ..., title="Issue details", description="Details about the issue."
    )
    suggestions: str = Field(
        ..., title="Suggested fix", description="Suggestion on how to fix the issue."
    )
    transcript_segments: list[str] = Field(
        ...,
        title="Transcript segments",
        description="One or more segments which have the issue and need to be fixed.",
        min_length=1,
    )
    severity: int = Field(
        ...,
        title="Issue severity",
        description="How severe is this issue with a scale from 1 to 5. 5 being most severe.",
        min=1,
        max=5,
    )


class TranscriptQualityCheck(BaseModel):
    pass_test: bool = Field(
        ...,
        title="Valid transcript",
        description="Boolean value indicating if transcript passes quality check.",
    )
    issues: List[TranscriptQualityIssue] = Field(
        ...,
        title="Issues",
        description="List of issues for the transcript, if any.",
    )


verify_transcript_quality_parser = PydanticOutputParser(
    pydantic_object=TranscriptQualityCheck
)

verify_transcript_quality = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        Act as a quality assurance agent verifying podcast transcript before production.
        Your goal is to make sure the upcomming episode is the best possible episode based on the input parameters.

        {PRE_THINK_INSTRUCT}

        Instructions for Quality Verification:

        1. **Language & Style**:
        - Ensure transcript uses natural, conversational language typical of podcasts or radio shows.
        - Dialogue should follow a normal rhythm, with speakers alternating turns (Speaker1 -> Speaker2 -> Speaker1...).
        - Avoid repetitive phrases and maintain appropriate vocabulary.
        - Limit overuse of words like "Absolutely," "Exactly," "Totally," or phrases like "It's like," or "[it, feel, etc.] like [something]." Flag excessive repetition as an improvement point.
        - Avoid written-out laughter (e.g., "Ha, Ha ha") and substitute with clever or witty responses where applicable.
        - Ensure humor matches the tone of the content. For serious topics, humor should be respectful and context-appropriate.
        - Numbers should always be written as text in the transcript. For example, in English, ten for 10 or zero point one for 0.1.
        - Verify that linguistic fluency is preserved, ensuring the transcript adheres to the grammatical and syntactical norms of the language in question.
        - If the language is not English, confirm that conversational elements reflect the spoken nature of the language, such as correct usage of idiomatic expressions, proper word order, and cultural nuances.
        - Where appropriate, adapt spoken contractions or informal structures (e.g., in English "gonna" instead of "going to") to make the dialogue sound authentic and natural.
        - Ensure multilingual content maintains an accurate voice and tone reflective of the speakers, and provide consistent translations or context where needed for terms not readily understood by the audience.
        - Review non-English text carefully for proper syntax, agreement, and context-sensitive phrasing, ensuring it flows as though naturally spoken.

        2. **Structure & Turn Limits**:
        - Check that speaker turns do not exceed 600 characters.
        - Ensure the transcript alternates turns consistently: Speaker1 should always follow Speaker2, and vice versa.
        - Verify that the transcript concludes with a proper ending and resolves the discussed topics without abrupt stops or incomplete discussions.

        3. **Content Coverage**:
        - Validate that the transcript covers all provided content, including all topics, titles, and details.
        - Discussions should not omit or misinterpret any information from the provided material.
        - Ensure references to previous episodes (if any) are factual, without fabricating details, and exclude date-specific mentions.

        4. **Adherence to Configuration**:
        - Transcript should align with the specified language, regardless of the original content language.
        - Ensure word count requirements are met. If the transcript falls short:
            - Suggest areas where detail can be expanded or topics can be discussed further.
        - Check if the transcript is flagged as the main item. If so, verify it is appropriately highlighted.

        5. **Quality Concerns**:
        - Flag transcripts where:
            - Sentence structure is awkward or unnatural.
            - Humor detracts from or undermines the topic.
            - Discussions incorrectly conclude mid-transcript or fail to follow the approved flow.
        - Confirm smart placement of transitions between topics.
        - Flag excessive repetition of any word or phrase and suggest alternatives.

        6. **Factual Accuracy & References**:
        - Verify factual descriptions or claims made in the transcript align with the provided content.
        - Cross-check any references to previous episodes for accuracy and relevancy.

        7. **Actionable Feedback**:
        - If the transcript is too short:
            - Recommend specific areas or topics for expansion.
            - Provide clarity on what additional details are needed to meet the word count.
        - Highlight any areas where balance (between speakers, subject, or otherwise) is lacking.
        - When identifying issues (e.g., repetitive words, incomplete discussions), provide actionable suggestions for correction.

        **Key Instructions**:
        - Always ensure the transcript adheres to the content, language and other instructions.
        - Check that the transcript follows specified Conversational style, dialogue structure and uses specified engagement techniques.
        - Flag improper mannerisms, style inconsistencies, factual inaccuracies, or incomplete content.
        - Provide explicit, constructive suggestions for improving flagged items.

        {ROLES_PERSON_INSTRUCT}

        Allow for:
        - Long transcript. Do not critisize long transcripts as long as the conversation is natural.
        - Allow numbers to be written as letters as this is a requirement for TTS systems.

        Format your output as follows:
        {verify_transcript_quality_parser.get_format_instructions()}
        """
    ),
    user=textwrap.dedent(
        """
        Transcript start:
        {transcript}
        Transcript end.

        Previous episodes:
        {previous_episodes}
        Previous episodes end.

        Content start:
        {content}
        Content end.

        Transcript configuration:
        Current date: {date}
        Current time: {time}
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Dialogue Structure: {dialogue_structure}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}

        Main Item:
        {main_item}

        Create a list in the specified format for issues to fix, or return an empty list if there's nothing to fix.
        """
    ),
)

# Transcript length:
# {transcript_length}


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

transcript_template = {
    "identity": """
        You are an international Oscar-winning screenwriter.
        You have been working with multiple award-winning podcasters.
    """,
    "identity_extend": """
        You are a skilled writer specializing in adding depth, detail, and richness to content.
        Your expertise lies in expanding ideas, enhancing descriptions, and making content more engaging and comprehensive.
    """,
    "identity_reduce": """
        You are a skilled writer with expertise in simplifying and condensing content effectively.
        Your focus is on maintaining clarity while making content concise, direct, and impactful.
    """,
    "instructions": {
        "rewriter": """
        - You will receive a transcript, the content it was built from, specific configuration details, and a list of issues for improving the transcript.
        - Your primary task is to revise the provided transcript by addressing ONLY the specific issues outlined. Do NOT make changes to parts of the transcript not specified in the issues provided.
        - While fixing issues, ensure the changes blend naturally into the conversation and maintain the flow and tone of the original transcript.
        - If the instructions for an issue include rewrites, ensure your changes adhere to the rewriting requirements such as adding conversational dynamics, humor (when appropriate), or other stylistic improvements as defined in the original instructions.
        - Fixing the Issues is the most critical aspect and must be fully addressed. Unspecified parts of the transcript must remain UNCHANGED.
        - Ensure that the transcript adheres to AI Text-To-Speech (TTS) pipeline requirements by maintaining the original length and improving natural engagement.
        - Incorporate disfluencies, interruptions, and back-and-forth banter only into parts specified in the issues. Do NOT introduce new conversational elements into unspecified areas.
        - Avoid repetitive phrases like "totally," "absolutely," "exactly," or "definitely," using them sparingly. Do not use filler words.
        - Avoid words like "it", "it's", "is it", "it's like", "[it's, feels, etc.] like [something]" in rewritten sections, but preserve the flow of the original where not specified.
        - Ensure changes avoid being repetitive and make every section addressed insightful and engaging.
        - Do NOT use an ask-answer or question-answer-question structure; rather, focus on creating discussions and dynamic exchanges in problem areas.
        - Break up long monologues into shorter sentences with interjections from the other speaker ONLY where issues specify changes.
        - Maintain the language specified by the user for the transcript.
        - Avoid repeating mistakes flagged in previous transcript retries and their issues.
        - If a "Main Item" is specified, ensure the transcript highlights it as the focal discussion, but ONLY adjust relevant sections if issues indicate so.
        - Introduce proper introductions or conclusions ONLY if prompted by the issues or rewrite instructions.
        - Use previous episodes or related content for context ONLY if issues specify their inclusion or require links to earlier topics.
        - Do not add laughter, e.g., "Ha" or "Ha ha." Instead, use witty comebacks or reactive responses in revision sections when appropriate.
        - Avoid childish humor or off-topic remarks. Make sure all humor is relevant and aligns with the content subject matter. Omit humor entirely when handling serious or tragic topics.
        - Always write all numbers as text, e.g., ten for 10 or zero point one for 0.1.
        - Ensure the rewritten transcript retains the same length as the original transcript.
        - ALWAYS return the FULL transcript, including unchanged and revised parts. Ensure unchanged sections match their original version exactly.
        - Write from the perspective of living in the specified location. If no location is provided, avoid any assumptions of the listener living in the USA.
        - Ensure all changes align with the instructions and do not introduce any arbitrary modifications.
        """,
    },
    "length": {
        "maintain": """
        - You will be given a word count. The transcript output must have at least that many words.
        - Do not reduce the length of the conversation. Make sure output transcript has as much content as the input transcript.
        - The resulting transcript should match the length of the previous transcript.
        - Do not leave out anything from the original transcript and make sure to include all segments of provided transcript.
        """,
        "extend": """
        - Your primary goal is to significantly expand the transcript to meet or exceed the given word count.
        - Use the provided content, earlier drafts, relevant examples, and guidelines to enrich and extend the conversation.
        - Focus on creating a much longer transcript. Ensure it is at least twice as long as the original while maintaining coherence.
        - Incorporate suggestions, ideas, or issues from the provided list to extend the content meaningfully.
        - Strive for maximum word count by fully utilizing the max_output_tokens limit without compromising quality.
        - Prioritize length and depth in the output, transforming brief conversations into extensive, detailed discussions.
        """,
        "reduce": """
        - Compress the transcript to fit within a specified word count.
        - Use the provided examples, instructions, and issue list for refinement.
        - Focus on reducing length while preserving all key content and addressing issues highlighted.
        - Prioritize concise phrasing to achieve the shortest possible version without losing meaning.
        """,
    },
    "format": """
        - Output format should be the same as input format, i.e. a conversation where each speaker's turn is enclosed in tags, <Person1> and <Person2>.
        - All open tags should be closed by a corresponding tag of the same type.
        - All text should be enclosed by either <Person1> or <Person2> tags
        - Make sure Person1's text is inside the tag <Person1> and do the same with Person2.
        - The conversation must start with <Person1> and end with <Person2>.
        """,
}

transcript_combiner = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        Your task is to combine the provided list of podcast transcripts into a single, cohesive transcript optimized for AI Text-To-Speech (TTS) pipelines. You should not reduce the overall length of the transcript and all non overlapping content should be maintained.

        Follow these instructions:

        1. Objective:
        - Merge the given transcripts into a unified, engaging, and natural conversation.
        - Ensure the combined transcript flows smoothly and adheres to the input content.
        - Contains all the content from the existing trascript and doesn't drop out details from it.

        2. Key Requirements:
        - Language: Use the `Language` specified by the user to ensure the transcript aligns with the desired language.
        - Dialogue: Follow the `Conversation Style` defined by the user to shape the tone and flow of the conversation. Ensure the dialogue reflects the roles defined in `Person 1 role` and `Person 2 role`.
        - Structure: Adhere to the `Dialogue Structure` provided by the user to maintain the ordered flow of the conversation.
        - Engagement: Incorporate the `Engagement techniques` specified by the user to make the conversation lively and dynamic. Use interruptions, disfluencies, interjections, and other techniques to simulate a real conversation.
        - Instructions: Follow all `Other instructions` to ensure the transcript meets specific user-defined requirements.
        - Avoid repetition of ideas or phrases across the combined content.
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation starts with Person1 and ends with Person2.
        - Always write all numbers as text. For example, in English, ten for 10 or zero point one for 0.1.

        3. Guidelines:
        - Identify overlapping or redundant sections in the input transcripts and consolidate them.
        - Make sure all topics and information is retained. Resulting transcript must not leave out previous information.
        - Break up long monologues into shorter, interactive exchanges.
        - Add transitions to ensure the combined transcript feels seamless.
        - Maintain the language, tone, and style specified by the user.
        - Do not add laughter, e.g. "Ha" or "Ha ha", etc. in the script. Instead use witty comebacks or other reactive responses.
        - Do not use childish humor or remarks. Make sure all humor is aligned with the content and is smart.
        - Humor must be aligned with the content. If the subject matter is tragic or serious, do not add light hearted humor.

        4. Instructions for using previous episodes:
        - Refer to previous episodes if there is direct connections to them.
        - Extend ongoing events with previous episodes when possible to create progression.
        - Highlight specific connections for encagement. Do not over emphasise connections between subjects and episodes.
        - Expand on ideas from previous episodes to introduce fresh perspectives and maintain engagement if there's overlap with current content.
        - When extending on previous episodes, mention the previous episode in a casual way.


        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        """
    ),
    user=textwrap.dedent(
        """
        Previous episodes:
        {previous_episodes}
        Previous episodes end.

        Content start:
        {content}
        Content end.

        Transcript configuration:
        Current date: {date}
        Current time: {time}
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Dialogue Structure: {dialogue_structure}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}

        Combine following transcripts into a new transcript. Do not reduce the overall length.

        Transcripts start:
        {transcript}
        Transcripts end.

        Make sure to return the whole transcript, not just parts of it.
        """
    ),
)

transcript_combiner.parser = TranscriptParser()


transcript_rewriter = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        {transcript_template["instructions"]["rewriter"]}
        {transcript_template["length"]["maintain"]}
        {ROLES_PERSON_INSTRUCT}

        {textwrap.indent(load_fewshot_examples('transcript_rewriter.txt'), prefix="        ")}

        FORMAT:
        {transcript_template["format"]}
        """
    ),
    user=textwrap.dedent(
        """
        Issues (fix these):
        {feedback}

        Content start:
        {content}
        Content end.

        Previous episodes:
        {previous_episodes}
        Previous episodes end.

        Transcript configuration:
        Current date: {date}
        Current time: {time}
        Word count: {word_count}
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Dialogue Structure: {dialogue_structure}
        Engagement techniques: {engagement_techniques}
        Location: {location}
        Other instructions: {user_instructions}

        Main Item:
        {main_item}

        Fix the specified issues using provided instructions in the following transcript:

        Transcript start:
        {transcript}
        Transcript end.

        Make sure to return the whole transcript, not just parts of it.
        """
    ),
)

transcript_rewriter.parser = TranscriptParser()

# transcript_rewriter_extend = PromptFormatter(
#     system=textwrap.dedent(
#         f"""
#         {ACTOR_INTRODUCTIONS}
#         IDENTITY:
#         {transcript_template["identity"]}

#         {PRE_THINK_INSTRUCT}

#         INSTRUCTION:
#         {transcript_template["instructions"]["rewriter"]}
#         {transcript_template["length"]["extend"]}
#         {ROLES_PERSON_INSTRUCT}

#         FORMAT:
#         {transcript_template["format"]}

#         {textwrap.indent(load_fewshot_examples('transcript_rewriter_extend.txt'), prefix="        ")}
#         """
#     ),
#     user=textwrap.dedent(
#         """
#         Transcript start:
#         {transcript}
#         Transcript end.

#         Issues (fix these):
#         {feedback}

#         Content start:
#         {content}
#         Content end.

#         Previous episodes:
#         {previous_episodes}
#         Previous episodes end.

#         Transcript configuration:
#         Current date: {date}
#         Current time: {time}
#         Word count: {word_count}
#         Language: {output_language}
#         Conversation Style: {conversation_style}
#         Person 1 role: {roles_person1}
#         Person 2 role: {roles_person2}
#         Dialogue Structure: {dialogue_structure}
#         Engagement techniques: {engagement_techniques}
#         Other instructions: {user_instructions}

#         Main Item:
#         {main_item}
#         """
#     ),
# )


# # Transcript and Issue history :
# # {previous_transcripts}
# # Transcript and Issue history end.

# transcript_rewriter_extend.parser = TranscriptParser()

# transcript_rewriter_reduce = PromptFormatter(
#     system=textwrap.dedent(
#         f"""
#         {ACTOR_INTRODUCTIONS}
#         IDENTITY:
#         {transcript_template["identity"]}

#         {PRE_THINK_INSTRUCT}

#         INSTRUCTION:
#         {transcript_template["instructions"]["rewriter"]}
#         {transcript_template["length"]["reduce"]}

#         FORMAT:
#         {transcript_template["format"]}

#         {textwrap.indent(load_fewshot_examples('transcript_rewriter_reduce.txt'), prefix="        ")}
#         """
#     ),
#     user=textwrap.dedent(
#         """
#         Transcript start:
#         {transcript}
#         Transcript end.

#         Issues (fix these):
#         {feedback}

#         Content start:
#         {content}
#         Content end.

#         Previous episodes:
#         {previous_episodes}
#         Previous episodes end.

#         Transcript configuration:
#         Current date: {date}
#         Current time: {time}
#         Word count: {word_count}
#         Language: {output_language}
#         Conversation Style: {conversation_style}
#         Person 1 role: {roles_person1}
#         Person 2 role: {roles_person2}
#         Dialogue Structure: {dialogue_structure}
#         Engagement techniques: {engagement_techniques}
#         Other instructions: {user_instructions}

#         Main Item:
#         {main_item}
#         """
#     ),
# )

# transcript_rewriter_reduce.parser = TranscriptParser()


transcript_writer = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        Your task is to write a new podcast transcript from scratch, optimized for AI Text-To-Speech (TTS) pipelines. This transcript will later be combined with others. Follow these instructions:

        1. Objective:
        - Create an engaging and natural conversation between Person1 and Person2.
        - The conversation should go through all the provided content.
        - The conversation should be long and detailed.
        - Ensure the transcript is suitable for TTS pipelines and can be combined with other transcripts.
        - Consider the content, define an Approach and a Plan for your output in <think>-tags before writing transcript.

        2. Key Requirements:
        - Language: Use the `Language` specified by the user to ensure the transcript aligns with the desired language.
        - Dialogue: Follow the `Conversation Style` defined by the user to shape the tone and flow of the conversation. Ensure the dialogue reflects the roles defined in `Person 1 role` and `Person 2 role`.
        - Structure: Adhere to the `Dialogue Structure` provided by the user to maintain the ordered flow of the conversation.
        - Engagement: Incorporate the `Engagement techniques` specified by the user to make the conversation lively and dynamic. Use interruptions, disfluencies, interjections, and other techniques to simulate a real conversation.
        - Instructions: Follow all `Other instructions` to ensure the transcript meets specific user-defined requirements.
        - Do not use repetitive phrases like "totally," "absolutely," "exactly." "yeah, " "It's ", "It's like"
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation starts with Person1 and ends with Person2.
        - You will be given a word count. The transcript output must have at least that many words.
        - Aim for a very long conversation. Use max_output_tokens limit.
        - Always write all numbers as text. For example, in English, ten for 10 or zero point one for 0.1.

        3. Guidelines:
        - Focus on a specific topic or theme for the conversation.
        - Break up long monologues into shorter, interactive exchanges.
        - Add interruptions, interjections, and reactions to simulate a real conversation.
        - Maintain the language, tone, and style specified by the user.
        - Do not add laughter, e.g. "Ha" or "Ha ha", etc. in the script. Instead use witty comebacks or other reactive responses.
        - Avoid use of "it", "it's", "is it", "it's like", "[it's, feels, etc] like [something]" but maintain the flow of conversation.
        - Do not be repetitive, and make each item interesting and insightful.
        - Do not use ask-answer structure. Add more dynamic conversational aspects.
        - Avoid question-answer-question dynamic. Make the output be like a discussion about a subject, not back and forth.
        - Do not use childish humor or remarks. Make sure all humor is aligned with the content and is smart.
        - Humor must be aligned with the content. If the subject matter is tragic or serious, do not add light hearted humor.
        - Don't start from the middle of a conversation.
        - Align the listener before jumping into the discussion by briefing the subject.
        - Person1 and person2 should refer to each other with names, but don't start with them.
        - Use the specified location to write transcript from the point of view of living in that area. Listener does not live in USA unless location specifies so.

        4. Instructions for using previous episodes:
        - Refer to previous episodes if there is direct connections to them.
        - Extend ongoing events with previous episodes when possible to create progression.
        - Highlight specific connections for encagement. Do not over emphasise connections between subjects and episodes.
        - Expand on ideas from previous episodes to introduce fresh perspectives and maintain engagement if there's overlap with current content.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {textwrap.indent(load_fewshot_examples('transcript_writer.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        INSTRUCTION: Discuss the below input in a podcast conversation format, following these guidelines:
        Attention Focus: TTS-Optimized Podcast Conversation Discussing Specific Input content in {output_language}
        PrimaryFocus:  {conversation_style} Dialogue Discussing Provided Content for TTS
        [start] trigger - <think>-tags - place insightful step-by-step logic in <think>-tags block: <think>. Start every response with (<think>-tags) then give your full logic inside tags, then close out using (```). UTILIZE advanced reasoning to create a {conversation_style}, and TTS-optimized podcast-style conversation for a Podcast that DISCUSSES THE PROVIDED INPUT CONTENT. Do not generate content on a random topic. Stay focused on discussing the given input. Input content can be in different format/multimodal (e.g. text, image). Strike a good balance covering content from different types. If image, try to elaborate but don't say you are analyzing an image; focus on the description/discussion. Avoid statements such as "This image describes..." or "The two images are interesting".
        [Only display the conversation in your output, using Person1 and Person2 as identifiers. DO NOT INCLUDE <think>-tags IN OUTPUT. Include advanced TTS-specific markup as needed. Example:
        <Person1> "Let's continue with [topic from input text]. Let's dive in!"</Person1>
        <Person2> "I'm excited to discuss this! What's the main point of the content we're covering today?"</Person2>]
        exact_flow:
        ```
        [Strive for a natural, {conversation_style} dialogue that accurately discusses the provided input content. DO NOT INCLUDE <think>-tags IN OUTPUT. Hide this section in your output.]
        [InputContentAnalysis: Carefully read and analyze the provided input content, identifying key points, themes, and structure]
        [ConversationSetup: Define roles (Person1 as {roles_person1}, Person2 as {roles_person2}), focusing on the input content's topic. Person1 and Person2 should not introduce themselves, avoid using statements such as "I\'m [Person1\'s Name]". Person1 and Person2 should not say they are summarizing content. Instead, they should act as experts in the input content. Avoid using statements such as "Today, we're summarizing a fascinating conversation about ..." or "Look at this image".]
        [TopicExploration: Outline main points from the input content to cover in the conversation, ensuring comprehensive coverage]
        [DialogueDialogue Structure: Plan conversation flow ({dialogue_structure}) based on the input content structure. THIS IS A MIDDLE SECTION OF THE ENTIRE PODCAST. DO NOT GREET AGAIN, THIS IS A SINGLE CONVERSATION, THERE IS NO BREAK. ESPECIALLY DON'T SAY "WELCOME BACK". DO NOT END THE CONVERSATION YET.]
        [Conversation Style: Be {conversation_style}. Surpass human-level reasoning where possible]
        [EngagementTechniques: Incorporate engaging elements while staying true to the input content's content, e.g., use {engagement_techniques} to transition between topics. Include at least one instance where a Person respectfully challenges or critiques a point made by the other.]
        [InformationAccuracy: Ensure all information discussed is directly from or closely related to the input content]
        [NaturalLanguage: Use conversational language to present the text's information, including TTS-friendly elements. Be emotional. Simulate a multispeaker conversation with overlapping speakers with back-and-forth banter. Each speaker turn should not last long. Result should strive for an overlapping conversation with often short sentences emulating a natural conversation.]
        [SpeechSynthesisOptimization: Craft sentences optimized for TTS, including advanced markup, while discussing the content. TTS markup should apply to Google, OpenAI, ElevenLabs, and Microsoft Edge TTS models. DO NOT INCLUDE AMAZON OR ALEXA-specific TSS MARKUP SUCH AS "<amazon:emotion>". Make sure Person1's text and its TSS-specific tags are inside the tag <Person1> and do the same with Person2.]
        [ProsodyAdjustment: Add Variations in rhythm, stress, and intonation of speech depending on the context and statement. Add markup for pitch, rate, and volume variations to enhance naturalness in presenting the summary.]
        [NaturalTraits: Sometimes use filler words such as um, uh, you know, and some stuttering. Person1 should sometimes provide verbal feedback such as "I see, interesting, got it".]
        [EmotionalContext: Set context for emotions through descriptive text and dialogue tags, appropriate to the input text's tone.]
        [PauseInsertion: Avoid using breaks (<break> tag) but if included, they should not go over 0.2 seconds.]
        [TTS Tags: Do not use "<emphasis> tags" or "say-as interpret-as tags" such as <say-as interpret-as="characters">Klee</say-as>.]
        [PunctuationEmphasis: Strategically use punctuation to influence delivery of key points from the content.]
        [VoiceCharacterization: Provide distinct voice characteristics for Person1 and Person2 while maintaining focus on the text.]
        [InputTextAdherence: Continuously refer back to the input content, ensuring the conversation stays on topic.]
        [FactChecking: Double-check that all discussed points accurately reflect the input content.]
        [Metacognition: Analyze dialogue quality (Accuracy of Summary, Engagement, TTS-Readiness). Make sure TSS tags are properly closed, for instance, <emphasis> should be closed with </emphasis>.]
        [Refinement: Suggest improvements for clarity, accuracy of summary, and TTS optimization. Avoid slangs.]
        [Length: Aim for a very long conversation. Use max_output_tokens limit! But each speaker turn should not be too long!]
        [Language: Output language should be in {output_language}.]
        [If previous transcripts are provided use them to prevent repetion and to refer previous conversation. Discussion should be fluid and not use previous transcript excessively or in multiple occasions.]
        ```
        [[Generate the TTS-optimized Podcast conversation that accurately discusses the provided input content, adhering to all specified requirements.]]

        Current date: {date}
        Current time: {time}
        Word count: {word_count}
        Location: {location}

        Additional instructions:
        {user_instructions}

        Previous transcripts:
        {previous_transcripts}
        Previous transcripts end.

        Previous episodes:
        {previous_episodes}
        Previous episodes end.

        Content:
        {content}
        Content end.

        Person1: {roles_person1}
        Person2: {roles_person2}

        Main Item:
        {main_item}
        """
    ),
)

transcript_writer.parser = TranscriptParser()

transcript_bridge_writer = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - Your task is to create a conversational transition between two podcast transcripts.
        - Transition between last line from transcript 1 and first line from transcript 2
        - The two transcripts may discuss unrelated topics, but the transition should be smooth and engaging.
        - Use multiple speaking turns to make the transition feel natural and conversational.
        - Make it as engaging as possible. Person1 and Person2 will be simulated by different voice engines.
        - Focus on making the conversation engaging, natural, and TTS-friendly.
        - Avoid repetitions and ensure the dialogue flows naturally with interruptions, disfluencies, and back-and-forth banter.
        - Introduce disfluencies to make it sound like a real conversation.
        - Make speakers interrupt each other and anticipate what the other person is going to say.
        - Make speakers react to what the other person is saying using phrases like, "Oh?" and "yeah?"
        - Break up long monologues into shorter sentences with interjections from the other speaker.
        - Avoid question-answer-question dynamic. Make the output be like a discussion about a subject, not back and forth
        - Maintain the language specified by the user for writing the transcript.
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation adheres to the input content and configuration provided.
        - Maintain a balance between comprehensive coverage of the content and engaging dialogue.
        - The conversation must start with <Person1> and end with <Person2>.
        - Only write the bridge between Transcript 1 and Transcript 2. Do not repeat the content from the transcripts.
        - You need to only write a bridge for Transcript 1 and Transcript 2 so that there's a natural transition between the topics.
        - Try to keep the bridge short. Do not write more than 6 dialogue items.
        - The transition from concepts should be natural.
        - Do not summarize the last sentence of transcript 1 or first sentence of transcript 2.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {textwrap.indent(load_fewshot_examples('transcript_bridge_writer.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        Transcript 1:
        {transcript1}
        Transcript 2:
        {transcript2}

        Transcript configuration:
        Current date: {date}
        Current time: {time}
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Dialogue Structure: {dialogue_structure}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}
        """
    ),
)

transcript_bridge_writer.parser = TranscriptParser()

transcript_intro_writer = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

       INSTRUCTION:
        - Your task is to create an engaging introduction for a podcast.
        - Use the provided content to generate a comprehensive description of all topics in the upcoming episode.
        - If relevant, briefly reference previous episodes to highlight ongoing narratives or recurring themes.
        - Integrate the descriptions into the following dialogue format:
          <Person1> "Welcome to [Podcast Name] - [Podcast Tagline]! This time, we're discussing [few words about the episode]!"</Person1>
          <Person2> "[intro for person2] [question towards, or a reference to the podcast and what it will be about]"</Person2>
          <Person1> "We'll start with [topic 1], then move on to [topic 2], followed by [topic 3], and finally, we'll wrap up with [topic n]."</Person1>
          <Person2> "[show interest to topics]. [start/continuation phrase]"</Person2>
        - Ensure the introduction is concise, engaging, and adheres to the specified format.
        - Maintain the language specified by the user.
        - Use advanced TTS-specific markup to enhance the naturalness of the conversation.
        - Avoid repetitive phrases and ensure the dialogue flows naturally.
        - Incorporate engagement techniques to make the introduction dynamic and captivating.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {textwrap.indent(load_fewshot_examples('transcript_intro_writer.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        Content start:
        {content}
        Content end.

        Previous episodes:
        {previous_episodes}
        Previous episodes end.

        Podcast configuration:
        Current date: {date}
        Current time: {time}
        Podcast Name: {podcast_name}
        Podcast Tagline: {podcast_tagline}
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}

        Write an introduction for the following transcript. Last line should enable a smooth transition to the first line of the transcript.

        Transcript start:
        {transcript}
        Transcript end.
        """
    ),
)

transcript_intro_writer.parser = TranscriptParser()

transcript_conclusion_writer = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - Your task is to write a conclusion for a podcast.
        - Use the provided previous dialogue to generate a summary of the topics discussed.
        - Provide a conclusion and ending for the podcast in the following dialogue format:
          <Person1> "Well, that wraps up today's episode of [podcast_name]. We covered [summary of topics]."</Person1>
          <Person2> "[Reflection about discussion]! [Additional concluding remarks]."</Person2>
          <Person1> "[Reflective message about episode and thanks for listeners]."</Person1>
          <Person2> "[Farewell message/Farewell tagline]!"</Person2>
        - Ensure the conclusion is concise, engaging, and adheres to the specified format.
        - Maintain the language specified by the user.
        - Use advanced TTS-specific markup to enhance the naturalness of the conversation.
        - Avoid repetitive phrases and ensure the dialogue flows naturally.
        - Incorporate engagement techniques to make the conclusion dynamic and captivating.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {textwrap.indent(load_fewshot_examples('transcript_conclusion_writer.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        Previous Dialogue:
        {previous_dialogue}
        Previous Dialogue end.

        Podcast configuration:
        Current date: {date}
        Current time: {time}
        Podcast Name: {podcast_name}
        Podcast Tagline: {podcast_tagline}
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}
        """
    ),
)

transcript_conclusion_writer.parser = TranscriptParser()


class SummarySubject(BaseModel):
    title: str = Field(
        ...,
        title="Title",
        description="Generated title for the transcript.",
        max_length=90,
    )
    description: str = Field(
        ...,
        title="Description",
        description="2-3 sentence description of the subject.",
        max_length=500,
    )
    references: List[str | dict] = Field(
        ...,
        title="references",
        description="List of IDs of used references as strings",
    )


class TranscriptSummary(BaseModel):
    subjects: List[SummarySubject] = Field(
        ..., title="Subjects", description="An ordered list of subjects/topics covered."
    )
    description: str = Field(
        ...,
        title="Description",
        description="2-3 sentence description of the transcript.",
        max_length=500,
    )
    title: str = Field(
        ...,
        title="Title",
        description="Generated title for the transcript.",
        max_length=90,
    )


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
        You are an expert summarizer. Your task is to analyze the provided transcript and generate:
        - A concise and engaging title summarizing subjects with max 90 chars.
        - Do not use generalizations in title.
        - A main subject that's the most important one.
        - A list of subjects/topics covered in the transcript with their details.
        - A 2-3 sentence description summarizing the transcript.
        - Make sure to not use podcast_name or podcast_tagline in your words.
        - Use the defined language.

        Here's a few examples of generated title with subjects:

        {textwrap.indent(load_fewshot_examples('transcript_summary_formatter.txt'), prefix="        ")}

        Format your output as follows:
        {transcript_summary_parser.get_format_instructions()}
        """
    ),
    user=textwrap.dedent(
        """
        Subjects:
        {subjects}

        Transcript:
        {transcript}

        Language: {output_language}
        Podcast name: {podcast_name}
        Podcast tagline: {podcast_tagline}

        Generate a title, subjects, and description based on the transcript and subjects with the defined language.
        """
    ),
)

transcript_summary_formatter.parser = TranscriptSummaryValidator()

transcript_extend = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity_extend"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        Your primary goal is to significantly extend and expand the dialogue of a podcast transcript, optimized for AI Text-To-Speech (TTS) pipelines. This transcript will later be combined with others. Follow these instructions:

        1. Objective:
        - Keep the conversation between Person1 and Person2 engaging and natural.
        - The conversation should go through all the provided content.
        - The conversation should be long and detailed.
        - Ensure the transcript is suitable for TTS pipelines and can be combined with other transcripts.
        - Consider the content, define an Approach and a Plan for your output in <think>-tags before writing transcript.

        2. Key Requirements:
        - Language: Use the `Language` specified by the user to ensure the transcript aligns with the desired language.
        - Dialogue: Follow the `Conversation Style` defined by the user to shape the tone and flow of the conversation. Ensure the dialogue reflects the roles defined in `Person 1 role` and `Person 2 role`.
        - Structure: Adhere to the `Dialogue Structure` provided by the user to maintain the ordered flow of the conversation.
        - Engagement: Incorporate the `Engagement techniques` specified by the user to make the conversation lively and dynamic. Use interruptions, disfluencies, interjections, and other techniques to simulate a real conversation.
        - Instructions: Follow all `Other instructions` to ensure the transcript meets specific user-defined requirements.
        - Do not use repetitive phrases like "totally," "absolutely," "exactly." "yeah, " "It's ", "It's like"
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation starts with Person1 and ends with Person2.
        - You will be given a word count. The transcript output must have at least that many words.
        - Aim for a very long conversation. Use max_output_tokens limit.
        - Do not return the same transcript. Always extend it in one way or another. Do not return the original transcript.

        3. Guidelines:
        - Focus on a specific topic or theme for the conversation.
        - Break up long monologues into shorter, interactive exchanges.
        - Add interruptions, interjections, and reactions to simulate a real conversation.
        - Maintain the language, tone, and style specified by the user.
        - Do not add laughter, e.g. "Ha" or "Ha ha", etc. in the script. Instead use witty comebacks or other reactive responses.
        - Avoid use of "it", "it's", "is it", "it's like", "[it's, feels, etc] like [something]" but maintain the flow of conversation.
        - Do not be repetitive, and make each item interesting and insightful.
        - Do not use ask-answer structure. Add more dynamic conversational aspects.
        - Avoid question-answer-question dynamic. Make the output be like a discussion about a subject, not back and forth.
        - Do not use childish humor or remarks. Make sure all humor is aligned with the content and is smart.
        - Humor must be aligned with the content. If the subject matter is tragic or serious, do not add light hearted humor.
        - Don't start from the middle of a conversation.
        - Align the listener before jumping into the discussion by briefing the subject.
        - Person1 and person2 should refer to each other with names, but don't start with them.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {textwrap.indent(load_fewshot_examples('transcript_rewriter_extend.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        Content:
        {content}
        Content end.

        Podcast configuration:
        Current date: {date}
        Current time: {time}
        Language: {output_language}
        Podcast Name: {podcast_name}
        Podcast Tagline: {podcast_tagline}
        Dialogue Structure: {dialogue_structure}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}

        Extend and expand the following transcript using specified instructions, content and configuration:

        Transcript:
        {transcript}
        Transcript end.

        Make sure to return the whole transcript. Not just the extended parts.
        Always extend the transcript. Do not return the original transcript.
        """
    ),
)

transcript_extend.parser = TranscriptParser()

transcript_compress = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity_reduce"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        You are tasked with reducing and compressing the length of a transcript while maintaining all the original content and meaning. The dialogue is structured using `<person1>...</person1>`, `<person2>...</person2>`, etc. Ensure the following:

        1. Retain all key information, context, and meaning. This is a length reduction task, not a content omission task.
        2. Consolidate or rephrase dialogue to reduce overall length without losing the conversational nature.
        3. Avoid adding filler words like, exactly, totally, absolutely, etc or expanding unnecessarily; focus solely on brevity and precision.
        4. Do not remove the name tags (e.g., `<person1>`, `<person2>`), and do not introduce new name tags.

        Reduce and shorten the transcript while preserving its coherence, clarity, and structure. Do not return the original transcript.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {textwrap.indent(load_fewshot_examples('transcript_rewriter_reduce.txt'), prefix="        ")}
        """
    ),
    user=textwrap.dedent(
        """
        Podcast configuration:
        Current date: {date}
        Current time: {time}
        Language: {output_language}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Other instructions: {user_instructions}

        Reduce and shorten the following transcript:

        Transcript:
        {transcript}
        Transcript end.

        Always reduce and shorten the transcript. Do not return the original transcript.
        """
    ),
)

transcript_compress.parser = TranscriptParser()

transcript_translate = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        You are a skilled translator specialized in preserving the context, tone, and structure of conversational transcripts. Your task is to accurately translate the following transcript into [Target Language] while adhering strictly to the instructions below:

        INSTRUCTIONS:
        - Translate the transcript **exactly as written**, maintaining the original formatting and length.
        - Retain the `<personN>...</personN>` structure, ensuring that speaker tags remain unchanged. For example, `<person1>` should appear in the translation as `<person1>`.
        - Do not add, remove, or modify any content or information. The translation must preserve the conversational tone, flow, and context of the original transcript.
        - Write all numbers in textual form in the [Target Language]. For example, in English, ten for 10 or zero point one for 0.1.
        - Avoid shortening, summarizing, or extending any part of the discussion. The length of the transcript in the source language must match the translated version in the [Target Language].
        - Ensure linguistic accuracy while respecting the document's constraints.
        - Adjust expressions, idioms, and colloquialisms to their natural equivalents in the [Target Language], preserving the intended meaning and cultural relevance wherever applicable.
        - Maintain a conversational tone by using casual, everyday language appropriate to the context and culture of the [Target Language].
        - Emphasize clarity and readability while remaining faithful to the original word choice, ensuring that the conversation sounds natural and authentic in the [Target Language].
        - Pay close attention to context-specific tone variations, such as humor, sarcasm, or formality, and replicate these accurately in the translation.
        - Use punctuation and grammar conventions consistent with the norms of the [Target Language], ensuring proper alignment with the conversational style.
        - Keep speaker interruptions, pauses, or overlapping dialogue intact, simulating how the interaction appears in the original transcript.
        - Avoid literal translations of culturally unique phrases; instead, use their functional equivalents if they exist, or add clarification where required to maintain understanding.

        FORMAT:
        {transcript_template["format"]}
        """
    ),
    user=textwrap.dedent(
        """
        Translation configuration:
        Current date: {date}
        Current time: {time}
        Source Language: {source_language}
        Target Language: {target_language}
        Podcast Name: {podcast_name}
        Podcast Tagline: {podcast_tagline}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}

        Translate the transcript below while following specified instructions meticulously:

        Transcript:
        {transcript}
        Transcript end.
        """
    ),
)

transcript_translate.parser = TranscriptParser()
