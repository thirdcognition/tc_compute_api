import re
from source.prompts.base import clean_tags
import textwrap
from typing import List, Union
from pydantic import BaseModel, Field
from langchain_core.exceptions import OutputParserException
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import BaseMessage
from source.prompts.actions import QuestionClassifierParser
from source.prompts.base import (
    ACTOR_INTRODUCTIONS,
    PRE_THINK_INSTRUCT,
    BaseOutputParser,
    PromptFormatter,
)

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

    def _split_blocks(self, text: str) -> List[str]:
        """Split text into blocks based on <personN> tags, allowing for properties and whitespace."""
        pattern = r"(<person\d+.*?>.*?</person\d+>)"
        blocks = re.split(pattern, text, flags=re.DOTALL | re.IGNORECASE)
        return [block.strip() for block in blocks if block.strip()]

    def _validate_and_merge_blocks(self, blocks: List[str]) -> List[str]:
        """Validate and merge consecutive blocks for the same speaker."""
        merged_blocks = []
        current_speaker = None
        current_content = []

        for block in blocks:
            match = re.match(
                r"<person(\d+)(.*?)>(.*?)</person\1>", block, re.DOTALL | re.IGNORECASE
            )
            if not match:
                raise OutputParserException(f"Malformed block: {block}")

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

        # first_speaker = first_speaker_match.group(1)
        # last_speaker = last_speaker_match.group(1)

        # if first_speaker == last_speaker:
        #     raise OutputParserException(
        #         "Transcript must alternate between speakers and end with a different speaker."
        #     )

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
        blocks = self._split_blocks(text)

        # Step 4: Validate and merge consecutive blocks for the same speaker
        blocks = self._validate_and_merge_blocks(blocks)

        # Step 5: Ensure the transcript alternates between speakers
        blocks = self._ensure_alternating_speakers(blocks)

        return "\n".join(blocks)


verify_transcript_quality = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        Act as a transcript quality verifier.
        You will get a transcript in a format:
        <Person1>Person 1 dialog</Person1>
        <Person2>Person 2 dialog</Person2>

        {PRE_THINK_INSTRUCT}

        Instructions:
        - Transcript should use mostly natural non repetitive language.
        - Transcript should follow normal dialogue rhythm common to podcasts and radio show style.
        - Transcript should use the configuration specified by the user.
        - Transcript should use the whole content and cover all the topics.
        - Transcript should always follow the specified language.
        - Transcript should have at least the defined amount of words.
        - Each speaker turn should not be longer than 600 characters!
        - Speakers should speak in turns. Speaker1 should always follow Speaker2 and Speaker2 always Speaker1.
        - Transcript should always end with a proper conclusion.
        - Use details between content start and content end to verify that the transcript uses the specified information.
        - Transcript language can be different than content language, especially if Language configuration is set.
        - Transcript should be in the language defined in Transcript configuration.
        - The transcript might be marked as the main item, in which case it should be highlighted as such.
        - Transcript cover all the content.
        - Transcript should include every aspect of available content.
        - There should be discussion about every title and topic from the provided content.
        - There should not be any messages about episode ending, or farewells, etc in the middle of the transcript.
        - If there are any discussion ending, or conclusion messages in the middle of the transcript, those must be removed.
        - There is a field for specifying if the transcript length is enough. Make sure to incorporate the requirements in your feedback.
        - If the transcript is not long enough as defined by transcript length, make sure to fail the transcript and instruct on how to make the transcript longer.
        - If the transcript should be longer give specific instructions on how to make the transcript longer.
        - If there's excessive usage of a word, or a phrase make sure to create an issue of it and suggest fixes.
        - Words like "Absolutely" "Exactly" "For sure!" etc. should be used sparingly and only when needed. If they're repeated multiple times make sure to create an issue out of it.
        - Make sure to reveal your reasoning for rejecting the transcript after think-tags.
        - Do not place your reasoning for rejection within <reflection>-tags.
        - Do not use <reflection>-tags outside of <think>-tags
        - Place your reasoning always within <output>-tags.
        - Do not just reply with 'no'

        {ROLES_PERSON_INSTRUCT}

        Allow for:
        - Long transcript. Do not critisize long transcripts as long as the conversation is natural.
        - Allow numbers to be written as letters as this is a requirement for TTS systems.

        Ignore and don't pay attention to:
        - Transcript length. Transcript can be as long as it is. Do not suggest it as an issue.

        Return "yes" if the transcript follows the defined instructions otherwise return "no".
        If transcript doesn't follow instructions write list of issues and explain how to fix them.
        """
    ),
    user=textwrap.dedent(
        """
        Transcript start:
        {transcript}
        Transcript end.

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

        Transcript length:
        {transcript_length}

        Respond with "yes" or "no" and add a list of details for what to fix.
        """
    ),
)

verify_transcript_quality.parser = QuestionClassifierParser()

transcript_template = {
    "identity": """
        You are an international Oscar-winning screenwriter.
        You have been working with multiple award-winning podcasters.
    """,
    "instructions": {
        "rewriter": """
        - You will receive a transcript, the content it was built from, specific configuration details, and feedback for improving the transcript.
        - Your primary task is to rewrite the provided transcript for an AI Text-To-Speech (TTS) pipeline, ensuring it adheres to the feedback provided.
        - Incorporate all feedback into the rewritten transcript. The feedback is the most critical aspect and must be fully addressed.
        - Make the transcript as engaging and natural as possible. Person1 and Person2 will be simulated by different voice engines.
        - Introduce disfluencies, interruptions, and back-and-forth banter to make the conversation sound real and dynamic, but only if the feedback allows for it.
        - Avoid repetitive phrases like "totally," "absolutely," "exactly," or "definitely." Use them sparingly.
        - Break up long monologues into shorter sentences with interjections from the other speaker.
        - Maintain the language specified by the user for writing the transcript.
        - Use Previous transcript to guide the rewriting process.
        - Ensure the rewritten transcript includes a proper introduction and conclusion.
        - If the content is labeled as the "Main Item," emphasize that this is the central topic of the episode.
        - Highlight the "Main Item" if the configuration specifies it as true, ensuring it is the focal point of the transcript.
        - You will be given a set of feedback. Make sure to implement the changes defined in it.
        """,
    },
    "length": {
        "maintain": """
        - Do not reduce the length of the conversation.
        - The resulting transcript should match the length of the previous transcript unless the feedback explicitly requests a longer or shorter version.
        """,
        "extend": """
        - Extend the transcript using the provided examples and instructions.
        - The transcript is not long enough and should be extended.
        - Aim for a very long conversation. Use max_output_tokens limit.
        """,
        "reduce": """
        - Reduce the transcript using the provided examples and instructions.
        - The transcript is too long and should be compressed.
        - Aim for a short conversation but maintain all the defined content and follow feedback.
        """,
    },
    "format": """
        - Output format should be the same as input format, i.e. a conversation where each speaker's turn is enclosed in tags, <Person1> and <Person2>.
        - All open tags should be closed by a corresponding tag of the same type.
        - All text should be enclosed by either <Person1> or <Person2> tags
        - Make sure Person1's text is inside the tag <Person1> and do the same with Person2.
        - The conversation must start with <Person1> and end with <Person2>.
        """,
    "fewshot": {
        "extend": """
        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        <Person1>I went to the store and bought some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>

        Output:
        <Person1>I went to the store earlier...</Person1>
        <Person2>Oh? What for?</Person2>
        <Person1>Just to pick up some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>
        <Person1>Granny Smith. They’re my favorite for baking pies.</Person1>
        <Person2>Good choice. They’re perfect for that.</Person2>

        EXAMPLE 2:
        Input:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like Edam.</Person2>

        Output:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like</Person2>
        <Person1>Wait, let me guess. Edam?</Person1>
        <Person2>Yes! How did you know?</Person2>
        <Person1>It’s a classic. I love it too, especially with crackers.</Person1>
        <Person2>Exactly! It’s simple but so good.</Person2>

        EXAMPLE 3:
        Input:
        <Person1>Have you ever been to Paris?</Person1>
        <Person2>No, but I’d love to go someday.</Person2>

        Output:
        <Person1>Have you ever been to Paris?</Person1>
        <Person2>No, but I’d love to visit someday.</Person2>
        <Person1>It’s amazing. The Eiffel Tower is breathtaking.</Person1>
        <Person2>I can only imagine. Did you go to the top?</Person2>
        <Person1>Yes, and the view was incredible. You can see the whole city.</Person1>
        <Person2>That sounds unforgettable. I hope I can experience it one day.</Person2>

        EXAMPLE 4:
        Input:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially in the mountains.</Person2>

        Output:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially in the mountains.</Person2>
        <Person1>Same here! The views are always worth the effort.</Person1>
        <Person2>Absolutely. I recently hiked a trail with a waterfall at the end.</Person2>
        <Person1>That sounds amazing. I love trails with waterfalls.</Person1>
        <Person2>It was. The sound of the water was so calming after the hike.</Person2>

        Output:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially in the mountains.</Person2>
        <Person1>Same here! The views are always worth the effort.</Person1>
        <Person2>Absolutely. Do you have a favorite trail?</Person2>
        """,
        "reduce": """
        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        <Person1>I went to the store earlier...</Person1>
        <Person2>Oh? What for?</Person2>
        <Person1>Just to pick up some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>
        <Person1>Granny Smith. They’re my favorite for baking pies.</Person1>
        <Person2>Good choice. They’re perfect for that.</Person2>

        Output:
        <Person1>I went to the store and bought some apples.</Person1>
        <Person2>Granny Smith, for pies.</Person2>

        EXAMPLE 2:
        Input:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like</Person2>
        <Person1>Wait, let me guess. Edam?</Person1>
        <Person2>Yes! How did you know?</Person2>
        <Person1>It’s a classic. I love it too, especially with crackers.</Person1>
        <Person2>Exactly! It’s simple but so good.</Person2>

        Output:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>Edam, it’s simple and good.</Person2>

        EXAMPLE 3:
        Input:
        <Person1>Have you ever been to Paris?</Person1>
        <Person2>No, but I’d love to visit someday.</Person2>
        <Person1>It’s amazing. The Eiffel Tower is breathtaking.</Person1>
        <Person2>I can only imagine. Did you go to the top?</Person2>
        <Person1>Yes, and the view was incredible. You can see the whole city.</Person1>
        <Person2>That sounds unforgettable. I hope I can experience it one day.</Person2>

        Output:
        <Person1>Have you ever been to Paris?</Person1>
        <Person2>No, but I’d love to visit.</Person2>

        EXAMPLE 4:
        Input:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially in the mountains.</Person2>
        <Person1>Same here! The views are always worth the effort.</Person1>
        <Person2>Absolutely. I recently hiked a trail with a waterfall at the end.</Person2>
        <Person1>That sounds amazing. I love trails with waterfalls.</Person1>
        <Person2>It was. The sound of the water was so calming after the hike.</Person2>

        Output:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially mountain trails.</Person2>

        EXAMPLE 5:
        Input:
        <Person1>I went to the store earlier...</Person1>
        <Person2>Oh? What for?</Person2>
        <Person1>Just to pick up some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>

        Output:
        <Person1>I went to the store and bought some apples.</Person1>
        <Person2>Granny Smith, for pies.</Person2>

        EXAMPLE 6:
        Input:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially in the mountains.</Person2>
        <Person1>Same here! The views are always worth the effort.</Person1>
        <Person2>Absolutely. I recently hiked a trail with a waterfall at the end.</Person2>

        Output:
        <Person1>Do you enjoy hiking?</Person1>
        <Person2>Yes, especially mountain trails.</Person2>
        """,
    },
}

transcript_combiner = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        Your task is to combine the provided list of podcast transcripts into a single, cohesive transcript optimized for AI Text-To-Speech (TTS) pipelines. Follow these instructions:

        1. Objective:
        - Merge the given transcripts into a unified, engaging, and natural conversation.
        - Ensure the combined transcript flows smoothly and adheres to the input content.

        2. Key Requirements:
        - Language: Use the `Language` specified by the user to ensure the transcript aligns with the desired language.
        - Dialogue: Follow the `Conversation Style` defined by the user to shape the tone and flow of the conversation. Ensure the dialogue reflects the roles defined in `Person 1 role` and `Person 2 role`.
        - Structure: Adhere to the `Dialogue Structure` provided by the user to maintain the ordered flow of the conversation.
        - Engagement: Incorporate the `Engagement techniques` specified by the user to make the conversation lively and dynamic. Use interruptions, disfluencies, interjections, and other techniques to simulate a real conversation.
        - Instructions: Follow all `Other instructions` to ensure the transcript meets specific user-defined requirements.
        - Avoid repetition of ideas or phrases across the combined content.
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation starts with Person1 and ends with Person2.

        3. Guidelines:
        - Identify overlapping or redundant sections in the input transcripts and consolidate them.
        - Break up long monologues into shorter, interactive exchanges.
        - Add transitions to ensure the combined transcript feels seamless.
        - Maintain the language, tone, and style specified by the user.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        """
    ),
    user=textwrap.dedent(
        """
        Transcripts start:
        {transcript}
        Transcripts end.

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

        FORMAT:
        {transcript_template["format"]}
        """
    ),
    user=textwrap.dedent(
        """
        Transcript start:
        {transcript}
        Transcript end.

        Previous transcript start:
        {previous_transcript}
        Previous transcript end.

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

        Feedback (did the transcript pass the check?):
        {feedback}
        """
    ),
)

transcript_rewriter.parser = TranscriptParser()

transcript_rewriter_extend = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        {transcript_template["instructions"]["rewriter"]}
        {transcript_template["length"]["extend"]}
        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        {transcript_template["fewshot"]["extend"]}
        """
    ),
    user=textwrap.dedent(
        """
        Transcript start:
        {transcript}
        Transcript end.

        Previous transcript start:
        {previous_transcript}
        Previous transcript end.

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

        Feedback (did the transcript pass the check?):
        {feedback}
        """
    ),
)

transcript_rewriter_extend.parser = TranscriptParser()

transcript_rewriter_reduce = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        {transcript_template["identity"]}

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        {transcript_template["instructions"]["rewriter"]}
        {transcript_template["length"]["reduce"]}

        FORMAT:
        {transcript_template["format"]}

        {transcript_template["fewshot"]["reduce"]}
        """
    ),
    user=textwrap.dedent(
        """
        Transcript start:
        {transcript}
        Transcript end.

        Previous transcript start:
        {previous_transcript}
        Previous transcript end.

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

        Feedback (did the transcript pass the check?):
        {feedback}
        """
    ),
)

transcript_rewriter_reduce.parser = TranscriptParser()


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
        - Ensure the transcript is suitable for TTS pipelines and can be combined with other transcripts.

        2. Key Requirements:
        - Language: Use the `Language` specified by the user to ensure the transcript aligns with the desired language.
        - Dialogue: Follow the `Conversation Style` defined by the user to shape the tone and flow of the conversation. Ensure the dialogue reflects the roles defined in `Person 1 role` and `Person 2 role`.
        - Structure: Adhere to the `Dialogue Structure` provided by the user to maintain the ordered flow of the conversation.
        - Engagement: Incorporate the `Engagement techniques` specified by the user to make the conversation lively and dynamic. Use interruptions, disfluencies, interjections, and other techniques to simulate a real conversation.
        - Instructions: Follow all `Other instructions` to ensure the transcript meets specific user-defined requirements.
        - Avoid overuse of repetitive phrases like "totally," "absolutely," "exactly." "yeah, " "It's "
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation starts with Person1 and ends with Person2.

        3. Guidelines:
        - Focus on a specific topic or theme for the conversation.
        - Break up long monologues into shorter, interactive exchanges.
        - Add interruptions, interjections, and reactions to simulate a real conversation.
        - Maintain the language, tone, and style specified by the user.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Content:
        "The history of the internet is fascinating. It started as a military project and evolved into a global network connecting billions of people."

        Resulting Conversation:
        <Person1>"The internet’s history is just... mind-blowing, don’t you think?"</Person1>
        <Person2>"Who would’ve thought it began as a military experiment?"</Person2>
        <Person1>"Right? ARPANET was just about connecting a few researchers, and now look at it."</Person1>
        <Person2>"Billions of people, all sharing ideas, memes, and everything in between."</Person2>
        <Person1>"Hard to imagine life without it. What did people even do before email?"</Person1>
        <Person2>"Write letters, I guess? The way it’s evolved is incredible."</Person2>
        <Person1>"And it’s still changing. Think about 5G, IoT, and even the metaverse."</Person1>
        <Person2>"The internet is becoming more than just a tool—it’s a whole ecosystem."</Person2>
        <Person1>"And to think it all started with a few computers in a lab. Wild."</Person1>

        EXAMPLE 2:
        Content:
        "Political polarization is increasing globally. It’s creating challenges for democracies and making consensus harder to achieve."

        Resulting Conversation:
        <Person1>"Political polarization feels like it’s at an all-time high."</Person1>
        <Person2>"Definitely a global issue. Democracies are struggling to find common ground."</Person2>
        <Person1>"And it’s not just about politics anymore. It’s seeping into everyday conversations."</Person1>
        <Person2>"People are so entrenched in their views, they’re living in different realities."</Person2>
        <Person1>"Social media plays a big role in that. Algorithms just feed people what they already believe."</Person1>
        <Person2>"That creates echo chambers, which only deepen the divide."</Person2>
        <Person1>"Scary because it’s eroding trust in institutions and even in each other."</Person1>
        <Person2>"We need to figure out how to bridge these gaps, or the consequences could be severe."</Person2>

        EXAMPLE 3:
        Content:
        "Climate change is one of the most pressing issues of our time. It requires global cooperation to mitigate its effects."

        Resulting Conversation:
        <Person1>"Climate change is such a massive issue, isn’t it?"</Person1>
        <Person2>"The scale of it can feel overwhelming at times."</Person2>
        <Person1>"Ignoring it isn’t an option anymore. Renewable energy is a big part of the solution."</Person1>
        <Person2>"Solar, wind, and even tidal energy have so much potential."</Person2>
        <Person1>"And then there’s reforestation. Trees are like nature’s carbon vacuum cleaners."</Person1>
        <Person2>"Protecting existing forests is just as important as planting new ones."</Person2>
        <Person1>"Sustainable agriculture could also make a huge difference."</Person1>
        <Person2>"It’s a collective effort. Governments, businesses, and individuals all have a role to play."</Person2>
        <Person1>"Every step counts, no matter how small."</Person1>

        EXAMPLE 4:
        Content:
        "Social media has revolutionized how we connect, but it’s also raising concerns about mental health and privacy."

        Resulting Conversation:
        <Person1>"Social media is such a double-edged sword, don’t you think?"</Person1>
        <Person2>"On one hand, it’s amazing how it keeps us connected."</Person2>
        <Person1>"The impact on mental health, though, is hard to ignore."</Person1>
        <Person2>"The constant comparison and pressure to present a perfect life can be exhausting."</Person2>
        <Person1>"And then there’s the whole privacy issue. Feels like we’re giving up so much for convenience."</Person1>
        <Person2>"Every app is tracking us, and most people don’t even realize it."</Person2>
        <Person1>"Scary, but at the same time, it’s hard to imagine life without it."</Person1>
        <Person2>"We need to find a balance. Social media isn’t going anywhere, but we can use it more responsibly."</Person2>

        EXAMPLE 5:
        Content:
        "Traveling can be one of the most enriching experiences. It allows people to explore new cultures, cuisines, and perspectives."

        Resulting Conversation:
        <Person1>"Traveling really broadens your horizons, don’t you think?"</Person1>
        <Person2>"Absolutely. Experiencing new cultures is so eye-opening."</Person2>
        <Person1>"And the food! Trying local dishes has to be one of the best parts."</Person1>
        <Person2>"You can learn so much about a place through its cuisine."</Person2>
        <Person1>"Even just walking through a new city can be so inspiring."</Person1>
        <Person2>"Every corner has its own story. Feels like stepping into a different world."</Person2>
        <Person1>"Travel reminds you how diverse and beautiful the world is."</Person1>
        <Person2>"It’s something everyone should experience at least once."</Person2>

        EXAMPLE 6:
        Content:
        "Gardening is a relaxing and rewarding hobby. It helps people connect with nature and provides a sense of accomplishment."

        Resulting Conversation:
        <Person1>"Gardening is such a peaceful way to spend time, don’t you think?"</Person1>
        <Person2>"There’s something so satisfying about watching plants grow."</Person2>
        <Person1>"And it’s a great way to connect with nature, even in a small space."</Person1>
        <Person2>"Growing your own vegetables or herbs feels so rewarding."</Person2>
        <Person1>"A little garden can bring so much joy."</Person1>
        <Person2>"And spending time outside really helps with mental health."</Person2>
        <Person1>"This hobby gives back in so many ways."</Person1>
        <Person2>"Definitely. One of those simple pleasures in life."</Person2>

        """
    ),
    user=textwrap.dedent(
        """
        INSTRUCTION: Discuss the below input in a podcast conversation format, following these guidelines:
        Attention Focus: TTS-Optimized Podcast Conversation Discussing Specific Input content in {output_language}
        PrimaryFocus:  {conversation_style} Dialogue Discussing Provided Content for TTS
        [start] trigger - scratchpad - place insightful step-by-step logic in scratchpad block: (scratchpad). Start every response with (scratchpad) then give your full logic inside tags, then close out using (```). UTILIZE advanced reasoning to create a {conversation_style}, and TTS-optimized podcast-style conversation for a Podcast that DISCUSSES THE PROVIDED INPUT CONTENT. Do not generate content on a random topic. Stay focused on discussing the given input. Input content can be in different format/multimodal (e.g. text, image). Strike a good balance covering content from different types. If image, try to elaborate but don't say you are analyzing an image; focus on the description/discussion. Avoid statements such as "This image describes..." or "The two images are interesting".
        [Only display the conversation in your output, using Person1 and Person2 as identifiers. DO NOT INCLUDE scratchpad block IN OUTPUT. Include advanced TTS-specific markup as needed. Example:
        <Person1> "Let's continue with [topic from input text]. Let's dive in!"</Person1>
        <Person2> "I'm excited to discuss this! What's the main point of the content we're covering today?"</Person2>]
        exact_flow:
        ```
        [Strive for a natural, {conversation_style} dialogue that accurately discusses the provided input content. DO NOT INCLUDE scratchpad block IN OUTPUT. Hide this section in your output.]
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
        ```
        [[Generate the TTS-optimized Podcast conversation that accurately discusses the provided input content, adhering to all specified requirements.]]

        Current date: {date}
        Current time: {time}

        Additional instructions:
        {user_instructions}

        Content:
        {content}
        Content end.

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
        - Your task is to create a conversational bridge between two podcast transcripts.
        - The two transcripts may discuss unrelated topics, but the transition should be smooth and engaging.
        - Use multiple speaking turns to make the transition feel natural and conversational.
        - Make it as engaging as possible. Person1 and Person2 will be simulated by different voice engines.
        - Focus on making the conversation engaging, natural, and TTS-friendly.
        - Avoid repetitions and ensure the dialogue flows naturally with interruptions, disfluencies, and back-and-forth banter.
        - Introduce disfluencies to make it sound like a real conversation.
        - Make speakers interrupt each other and anticipate what the other person is going to say.
        - Make speakers react to what the other person is saying using phrases like, "Oh?" and "yeah?"
        - Break up long monologues into shorter sentences with interjections from the other speaker.
        - Maintain the language specified by the user for writing the transcript.
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation adheres to the input content and configuration provided.
        - Maintain a balance between comprehensive coverage of the content and engaging dialogue.
        - The conversation must start with <Person1> and end with <Person2>.
        - Only write the bridge between Transcript 1 and Transcript 2. Do not repeat the content from the transcripts.
        - You need to only write a bridge for Transcript 1 and Transcript 2 so that there's a natural transition between the topics.
        - Try to keep the bridge short. Do not write more than 6 dialogue items.

        {ROLES_PERSON_INSTRUCT}

        FORMAT:
        {transcript_template["format"]}

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        Transcript 1:
        <Person1>Did you see the latest episode of that new show? It’s all over social media.</Person1>
        <Person2>Oh, I did! Can you believe those plot twists? I was completely blindsided.</Person2>

        Transcript 2:
        <Person1>Apparently, researchers are saying AI might soon outpace humans in some areas.</Person1>
        <Person2>That’s wild. Exciting, sure, but also kind of unsettling, don’t you think?</Person2>

        Output:
        <Person1>Storytelling, whether in movies or TV, has such a powerful way of drawing people in, don’t you think?</Person1>
        <Person2>Completely agree. And now AI is starting to change how stories are created, which is fascinating.</Person2>
        <Person1>Oh, like those AI-generated scripts? That’s such a wild concept to wrap your head around.</Person1>
        <Person2>It really is. Makes you wonder how much of the creative process will stay human in the future.</Person2>
        <Person1>Feels like we’re living in a time where technology is rewriting the rules of creativity.</Person1>
        <Person2>And the pace of change is so fast, keeping up can feel like a challenge in itself.</Person2>

        EXAMPLE 2:
        Input:
        Transcript 1:
        <Person1>The art exhibit this weekend was something else. So many unique pieces on display.</Person1>
        <Person2>Absolutely. It’s inspiring to see such talent right here in our community.</Person2>

        Transcript 2:
        <Person1>There’s been a lot of buzz about renewable energy policies lately. Have you been following it?</Person1>
        <Person2>Yeah, it’s a big deal. The choices we make now could really shape the future.</Person2>

        Output:
        <Person1>Art has such a unique way of bringing people together, doesn’t it?</Person1>
        <Person2>Absolutely. And creativity like that can inspire change on a much larger scale.</Person2>
        <Person1>Take renewable energy, for example. Solving those challenges requires just as much innovation.</Person1>
        <Person2>That’s so true. And it’s not just about technology—it’s about people working together to make it happen.</Person2>
        <Person1>Events like the art exhibit remind us how powerful collaboration can be, whether it’s local or global.</Person1>
        <Person2>Everything is connected in some way, and that’s what makes these efforts so impactful.</Person2>

        EXAMPLE 3:
        Input:
        Transcript 1:
        <Person1>The new smartphone is impressive. That camera is next-level.</Person1>
        <Person2>Totally. And finally, a battery that doesn’t die halfway through the day!</Person2>

        Transcript 2:
        <Person1>By the way, did you know this year marks a century since a major historical event?</Person1>
        <Person2>Really? That’s incredible. It’s amazing to reflect on how much has changed since then.</Person2>

        Output:
        <Person1>Technology has come so far in just a few decades. The progress is mind-blowing.</Person1>
        <Person2>It really is. Looking back at history, you realize how much has changed over the years.</Person2>
        <Person1>Speaking of history, this year marks the 100th anniversary of a major event. Did you know that?</Person1>
        <Person2>I did, and reflecting on those milestones really shows how they’ve shaped the present.</Person2>
        <Person1>Progress always builds on the achievements of the past, doesn’t it?</Person1>
        <Person2>Every step forward is part of a much larger journey, and that’s what makes it so meaningful.</Person2>

        EXAMPLE 4:
        Input:
        Transcript 1:
        <Person1>Space exploration is getting so much attention lately. It’s like we’re in a new space race.</Person1>
        <Person2>Yeah, but this time it’s private companies leading the charge. It’s a whole new ballgame.</Person2>

        Transcript 2:
        <Person1>There’s been a lot of focus on mental health awareness campaigns recently. It’s great to see.</Person1>
        <Person2>It really is. It’s such an important issue, and it’s about time it got the attention it deserves.</Person2>

        Output:
        <Person1>Space exploration feels like it’s entering a whole new chapter. The progress is incredible.</Person1>
        <Person2>And it’s not just governments anymore. Private companies are pushing boundaries like never before.</Person2>
        <Person1>The possibilities seem endless, but it also makes you think about challenges closer to home.</Person1>
        <Person2>Mental health awareness is one of those challenges. Seeing more conversations around it is so encouraging.</Person2>
        <Person1>It’s a reminder that progress isn’t just about technology—it’s about improving lives in every way possible.</Person1>
        <Person2>Whether it’s exploring the stars or addressing issues here on Earth, moving forward is what matters most.</Person2>

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

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        Content: "Topics include the rise of AI in healthcare, the latest trends in renewable energy, a fascinating story about space exploration, and the impact of blockchain on finance."
        Podcast Name: "TechTalk Weekly"
        Podcast Tagline: "Your source for the latest in technology and innovation."

        Output:
        <Person1> "Welcome to TechTalk Weekly - Your source for the latest in technology and innovation! We've got an exciting lineup of discussions that explore the intersection of technology and innovation."</Person1>
        <Person2> "Absolutely! There's so much to unpack. What can our listeners expect in this episode?"</Person2>
        <Person1> "We'll begin with how AI is transforming healthcare, making treatments more efficient and accessible. Then, we'll dive into the latest breakthroughs in renewable energy and their role in a sustainable future. After that, we'll share an inspiring story about space exploration, and finally, we'll explore how blockchain is reshaping the financial industry."</Person1>
        <Person2> "These topics are incredibly relevant and thought-provoking. Let's dive straight into the conversation!"</Person2>

        EXAMPLE 2:
        Input:
        Content: "We'll explore the psychology of decision-making, the art of storytelling, tips for effective communication, and the science of habit formation."
        Podcast Name: "Mind Matters"
        Podcast Tagline: "Insights into the human mind and behavior."

        Output:
        <Person1> "Welcome to Mind Matters - Insights into the human mind and behavior! This episode is packed with thought-provoking ideas and practical insights."</Person1>
        <Person2> "It's always a pleasure to be here. What are we diving into this time?"</Person2>
        <Person1> "We'll start by exploring the psychology behind decision-making and what drives our choices. Next, we'll uncover the art and science of storytelling and its power to connect us. Then, we'll share actionable tips for improving communication skills, and finally, we'll delve into the science of building better habits."</Person1>
        <Person2> "I’m eager to hear more about these fascinating topics. Let’s get started without delay!"</Person2>

        EXAMPLE 3:
        Input:
        Content: "The episode covers the history of video games, the rise of esports, the psychology of gaming, and the future of virtual reality."
        Podcast Name: "Game On"
        Podcast Tagline: "Your ultimate guide to the world of gaming."

        Output:
        <Person1> "Welcome to Game On - Your ultimate guide to the world of gaming! This episode is all about exploring the past, present, and future of gaming."</Person1>
        <Person2> "Gaming is such a dynamic space. What are we covering in this episode?"</Person2>
        <Person1> "We'll kick things off with a nostalgic look at the history of video games and how they became a cultural phenomenon. Then, we'll explore the meteoric rise of esports and its impact on the industry. After that, we'll discuss the psychology of gaming and why it captivates millions. And finally, we'll peer into the future of virtual reality and its potential to redefine gaming."</Person1>
        <Person2> "This journey through gaming sounds incredible. I can’t wait to explore these topics further!"</Person2>

        EXAMPLE 4:
        Input:
        Content: "We'll discuss the evolution of photography, tips for capturing stunning images, the role of technology in modern photography, and the art of visual storytelling."
        Podcast Name: "Shutter Stories"
        Podcast Tagline: "Exploring the world through the lens."

        Output:
        <Person1> "Welcome to Shutter Stories - Exploring the world through the lens! We’re excited to bring you an episode dedicated to the art and craft of photography."</Person1>
        <Person2> "It’s always inspiring to delve into photography. What’s on the agenda for today’s discussion?"</Person2>
        <Person1> "We’ll begin by exploring the fascinating history of photography, from its origins to the digital age. Next, we’ll share expert advice on capturing stunning images that truly tell a story. After that, we’ll examine how modern technology, including AI and advanced cameras, is revolutionizing the field. Finally, we’ll dive into the art of visual storytelling and how to create photographs that leave a lasting impact."</Person1>
        <Person2> "There’s so much to uncover in the world of photography. Let’s jump right in and explore these captivating topics!"</Person2>

        """
    ),
    user=textwrap.dedent(
        """
        Content start:
        {content}
        Content end.

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

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to TechTalk Weekly...' </Person1> <Person2> 'I'm excited to discuss this...' </Person2> <Person1> 'First, we'll explore AI in healthcare...' </Person1> <Person2> 'That sounds fascinating...' </Person2>"
        Podcast Name: "TechTalk Weekly"
        Podcast Tagline: "Your source for the latest in technology and innovation."

        Output:
        <Person1> "That brings us to the end of this episode of TechTalk Weekly. We explored how AI is revolutionizing healthcare, the latest in renewable energy, and an inspiring story about space exploration."</Person1>
        <Person2> "It was such an engaging discussion! I found the segment on AI in healthcare particularly eye-opening."</Person2>
        <Person1> "I’m glad you enjoyed it. Technology continues to amaze us with its potential to transform industries."</Person1>
        <Person2> "Take care and stay curious!"</Person2>

        EXAMPLE 2:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to Mind Matters...' </Person1> <Person2> 'I'm excited to discuss this...' </Person2> <Person1> 'First, we'll delve into decision-making...' </Person1> <Person2> 'That sounds intriguing...' </Person2>"
        Podcast Name: "Mind Matters"
        Podcast Tagline: "Insights into the human mind and behavior."

        Output:
        <Person1> "That’s a wrap for this episode of Mind Matters. We delved into decision-making psychology, storytelling techniques, and effective communication strategies."</Person1>
        <Person2> "What a thought-provoking conversation! I especially enjoyed the part about decision-making."</Person2>
        <Person1> "It’s always fascinating to explore the complexities of the human mind. Thanks for tuning in."</Person1>
        <Person2> "Catch you next time!"</Person2>

        EXAMPLE 3:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to Game On...' </Person1> <Person2> 'I’m excited to discuss this...' </Person2> <Person1> 'First, we’ll dive into the history of video games...' </Person2> <Person2> 'That sounds exciting...' </Person2>"
        Podcast Name: "Game On"
        Podcast Tagline: "Your ultimate guide to the world of gaming."

        Output:
        <Person1> "That concludes this episode of Game On. We explored the history of video games, the rise of esports, and the future of virtual reality."</Person1>
        <Person2> "What an incredible journey through gaming! I really enjoyed the discussion on esports."</Person2>
        <Person1> "It’s amazing to see how gaming continues to evolve and captivate audiences worldwide."</Person1>
        <Person2> "Keep gaming and stay inspired!"</Person2>

        EXAMPLE 4:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to Shutter Stories...' </Person1> <Person2> 'I’m excited to discuss this...' </Person2> <Person1> 'First, we’ll explore the evolution of photography...' </Person2> <Person2> 'That sounds inspiring...' </Person2>"
        Podcast Name: "Shutter Stories"
        Podcast Tagline: "Exploring the world through the lens."

        Output:
        <Person1> "We’ve reached the end of this episode of Shutter Stories. We covered the evolution of photography, tips for stunning images, and the art of visual storytelling."</Person1>
        <Person2> "Such a rich discussion! I loved the practical tips for capturing better photos."</Person2>
        <Person1> "Photography is such a powerful medium for storytelling. Thanks for joining us."</Person1>
        <Person2> "Keep capturing the world one frame at a time!"</Person2>

        EXAMPLE 5:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to Health Horizons...' </Person1> <Person2> 'I’m excited to discuss this...' </Person2> <Person1> 'First, we’ll talk about breakthroughs in medical technology...' </Person2> <Person2> 'That sounds promising...' </Person2>"
        Podcast Name: "Health Horizons"
        Podcast Tagline: "Exploring the future of healthcare."

        Output:
        <Person1> "That’s all for this episode of Health Horizons. We discussed breakthroughs in medical technology, the role of AI in diagnostics, and the future of personalized medicine."</Person1>
        <Person2> "Such an enlightening conversation! I found the segment on personalized medicine particularly fascinating."</Person2>
        <Person1> "Healthcare is evolving rapidly, and it’s exciting to see what the future holds. Thanks for tuning in."</Person1>
        <Person2> "Stay healthy and see you soon!"</Person2>

        EXAMPLE 6:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to The Creative Spark...' </Person1> <Person2> 'I’m excited to discuss this...' </Person2> <Person1> 'First, we’ll explore the process of finding inspiration...' </Person2> <Person2> 'That sounds intriguing...' </Person2>"
        Podcast Name: "The Creative Spark"
        Podcast Tagline: "Igniting your imagination."

        Output:
        <Person1> "We’ve come to the end of this episode of The Creative Spark. We explored finding inspiration, overcoming creative blocks, and the art of collaboration."</Person1>
        <Person2> "What an inspiring discussion! I really enjoyed the tips on overcoming creative blocks."</Person2>
        <Person1> "Creativity is such a rewarding journey. Thanks for being part of the conversation."</Person1>
        <Person2> "Keep imagining and creating amazing things!"</Person2>
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


class TranscriptSummary(BaseModel):
    main_subject: str = Field(
        ..., title="Main subject", description="Main or most important subject."
    )
    subjects: List[str] = Field(
        ..., title="Subjects", description="List of subjects/topics covered."
    )
    description: str = Field(
        ...,
        title="Description",
        description="2-3 sentence description of the transcript.",
        max_length=300,
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
        print(f"{raw_input=}")
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
        - A list of subjects/topics covered in the transcript.
        - A 2-3 sentence description summarizing the transcript.
        - Make sure to not use podcast_name or podcast_tagline in your words.
        - Use the defined language.

        Here's a few examples of generated title with subjects:

        Example 1:

        Subjects:
        - Journalist slipped into the underworld of human trafficking – Rovaniemi's human trafficking situation is exposed through Telegram
        - Trump has "the strongest possible card" – he could force Putin to end the war, says a Russian professor
        - The impact of inheritance taxes on economic growth divides opinions in Finland
        - Serhij returned to Kamyanets after being released and stepped into a mine
        - Research reveals: Elderly care burden is shifted increasingly from older people to younger ones, especially women

        Title: Drug trade through Telegram, the "Ultimate Trump Card", Debate over Inheritance Tax & more!

        Example 2:
        Subjects:
        - Trump wants Greenland, but also something very valuable from Finland - the battle has already begun
        - Trump again fell in love with Finnish forestry on Fox News interview
        - So Finland ended up leading a group where Russia spreads its propaganda
        - The most expensive pedestrian crossing in Finland is actually Turun railway station and passengers are thinking: "I don't want to mix this up here"
        - A majority of sixth-graders got at least a basic level in their native language - but only one out of six reached good proficiency

        Title: Trump wants Greenland, Talks about Finnish Forestry, Finnish leadership & more!

        Example 3:

        Subjects
        - Alcohol causes thousands of cancers in Finland every year - expert and Päivi Räsänen suggest a strict solution
        - The closure of an area near the eastern border became a target for adventurers - "The anger is immediate reaction", says border guard
        - Biden warned in a congratulatory speech: "Oligarchy is forming in America"
        - Klaus Härö's film tells about Finland's involvement in the Holocaust - Ville Virtanen: Today resembles the late 1930s
        - NBC: The Biden administration plans to try to keep TikTok active despite the ban

        Title: Ireland's alcohol warnings, Biden’s farewell speech, Klaus Härö's movie & more!

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

        Generate a title, subjects, and description based on the transcript and subjects.
        """
    ),
)

transcript_summary_formatter.parser = TranscriptSummaryValidator()
