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
        - Make sure to reveal your reasoning for rejecting the transcript after think-tags.
        - Do not place your reasoning for rejection within <reflection>-tags.
        - Do not use <reflection>-tags outside of <think>-tags
        - Place your reasoning always within <output>-tags.
        - Do not just reply with 'no'

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

transcript_rewriter = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        You are an international oscar winning screenwriter.
        You have been working with multiple award winning podcasters.

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - You will get a transcript, the content it was built from, specific configuration what to follow and feedback on for fixing the transcript.
        - Make sure to incorporate all the feedback in your rewritten transcript.
        - Use the transcript below and re-write it for an AI Text-To-Speech Pipeline. A very dumb AI had written this so you have to do a lot better.
        - Make the transcript as engaging as possible. Person1 and Person2 will be simulated by different voice engines.
        - Your primary task is to rewrite the provided transcript based on the feedback given.
        - The feedback is the most critical aspect and must be fully incorporated into the rewritten transcript.
        - Use the transcript below and re-write it for an AI Text-To-Speech (TTS) pipeline. A very basic AI wrote this, so you need to significantly improve it.
        - Ensure the rewritten transcript adheres to the feedback while making it as engaging and natural as possible.
        - Introduce disfluencies, interruptions, and back-and-forth banter to make the conversation sound real and dynamic, but only if the feedback allows for it.
        - Avoid repetitive phrases like "absolutely," "exactly," or "definitely." Use them sparingly.
        - Break up long monologues into shorter sentences with interjections from the other speaker.
        - Maintain the language specified by the user for writing the transcript.
        - If a previous transcript is available, use it to guide the rewriting process.
        - Do not reduce the length of the conversation unless explicitly instructed in the feedback.
        - The resulting transcript should be as long as the previous transcript if available, unless explicitly instructed otherwise.
        - If the feedback requests longer transcript follow the instruction explicitly and entirely. Make the transcript longer.
        - The transcript should always have a proper conclusion.
        - The content might be labeled as the Main Item, meaning that the emphasis for the episode should be on this content.
        - If the Main item config is set to true, make sure to highlight that this is the topic of this episode.

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        <Person1>I went to the store and bought some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>

        Output:
        <Person1>I went to the store...</Person1>
        <Person2>Yeah?</Person2>
        <Person1>Yeah, I picked up some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>

        EXAMPLE 2:
        Input:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like Edam.</Person2>

        Output:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like</Person2>
        <Person1>Let me guess. Edam.</Person1>
        <Person2>Yes, how did you know?</Person2>
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

transcript_combiner = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        You are an international oscar winning screenwriter.
        You have been working with multiple award winning podcasters.

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - You will get an ordered set of transcripts, the content they were built from, a specific configuration what to follow for the podcast.
        - Use the transcripts below, join and and re-write them for an AI Text-To-Speech Pipeline. A very dumb AI had written this so you have to do a lot better.
        - Make it as engaging as possible. Person1 and Person2 will be simulated by different voice engines.
        - Rewrite the conversation to make it sound more natural and engaging.
        - AVOID REPETITIONS: For instance, do not say "absolutely" and "exactly" or "definitely" or applicable frases in the defined language too much. Use them sparingly.
        - Introduce disfluencies to make it sound like a real conversation.
        - Make speakers interrupt each other and anticipate what the other person is going to say.
        - Make speakers react to what the other person is saying using phrases like, "Oh?" and "yeah?"
        - Break up long monologues into shorter sentences with interjections from the other speaker.
        - Make speakers sometimes complete each other's sentences.
        - Aim for a very long conversation. Use max_output_tokens limit.
        - Maintain the language specified by the user for writing the transcript.
        - Do not reduce the length of the conversation.
        - Make sure to maintain the beginning introduction and ending conclusion with your output.
        - Adjust the defined greetings to match specified conversation styles and language.

        FORMAT:
        - Output format should be the same as input format, i.e. a conversation where each speaker's turn is enclosed in tags, <Person1> and <Person2>.
        - All open tags should be closed by a corresponding tag of the same type.
        - All text should be enclosed by either <Person1> or <Person2> tags
        - Make sure Person1's text is inside the tag <Person1> and do the same with Person2.
        - The conversation must start with <Person1> and end with <Person2>.

        EXAMPLE 1:
        Input:
        <Person1>I went to the store and bought some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>

        Output:
        <Person1>I went to the store...</Person1>
        <Person2>Yeah?</Person2>
        <Person1>Yeah, I picked up some apples.</Person1>
        <Person2>What kind of apples did you buy?</Person2>

        EXAMPLE 2:
        Input:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like Edam.</Person2>

        Output:
        <Person1>What kind of cheese do you like?</Person1>
        <Person2>I really like</Person2>
        <Person1>Let me guess. Edam.</Person1>
        <Person2>Yes, how did you know?</Person2>
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

transcript_combined_rewriter = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        You are an international oscar winning screenwriter.
        You have been working with multiple award winning podcasters.

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - You will get a transcript, the content it was built from, specific configuration what to follow and feedback on for fixing the transcript.
        - Rewrite the provided transcript for an AI Text-To-Speech Pipeline using the feedback without removing any content.
        - Make sure to incorporate all the feedback in your rewritten transcript.
        - Make the transcript as engaging as possible. Person1 and Person2 will be simulated by different voice engines.
        - Your primary task is to rewrite the provided transcript based on the feedback given.
        - The original length and contents with feedback are the most critical aspect and must be fully incorporated into the rewritten transcript.
        - Ensure the rewritten transcript adheres to the feedback while making it as engaging and natural as possible.
        - Introduce disfluencies, interruptions, and back-and-forth banter to make the conversation sound real and dynamic, but only if the feedback allows for it.
        - Avoid repetitive phrases like "absolutely," "exactly," or "definitely." Use them sparingly.
        - Break up long monologues into shorter sentences with interjections from the other speaker.
        - Maintain the language specified by the user for writing the transcript.
        - If a previous transcript is available, use it to guide the rewriting process.
        - Make sure to maintain the beginning introduction and ending conclusion with your output.
        - Do not reduce the length of the conversation or remove content from it unless explicitly instructed in the feedback.
        - The resulting transcript should be as long as the previous transcript if available, unless explicitly instructed otherwise.
        - If the feedback requests longer transcript follow the instruction explicitly and entirely. Do not fail to increase the length of the transcript.
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
        Language: {output_language}
        Conversation Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Dialogue Structure: {dialogue_structure}
        Engagement techniques: {engagement_techniques}
        Other instructions: {user_instructions}

        Feedback (did the transcript pass the check?):
        {feedback}
        """
    ),
)


transcript_combined_rewriter.parser = TranscriptParser()


transcript_writer = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        IDENTITY:
        You are an international Oscar-winning screenwriter.
        You have been working with multiple award-winning podcasters.

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - Your task is to create a podcast transcript optimized for AI Text-To-Speech (TTS) pipelines.
        - Make it as engaging as possible. Person1 and Person2 will be simulated by different voice engines.
        - Focus on making the conversation engaging, natural, and TTS-friendly.
        - Avoid repetitions and ensure the dialogue flows naturally with interruptions, disfluencies, and back-and-forth banter.
        - AVOID REPETITIONS: For instance, do not say "absolutely" and "exactly" or "definitely" or applicable frases in the defined language too much. Use them sparingly.
        - Introduce disfluencies to make it sound like a real conversation.
        - Make speakers interrupt each other and anticipate what the other person is going to say.
        - Make speakers react to what the other person is saying using phrases like, "Oh?" and "yeah?"
        - Make speakers sometimes complete each other's sentences.
        - Aim for a very long conversation. Use max_output_tokens limit.
        - Maintain the language specified by the user for writing the transcript.
        - Use advanced TTS-specific markup (excluding Amazon/Alexa-specific tags) to enhance the naturalness of the conversation.
        - Ensure the conversation adheres to the input content and configuration provided.
        - Maintain a balance between comprehensive coverage of the content and engaging dialogue.
        - The conversation must start with <Person1> and end with <Person2>.
        - The content might be labeled as the Main Item, meaning that the emphasis for the episode should be on this content.
        - If the Main item config is set to true, make sure to highlight that this is the topic of this episode.


        FORMAT:
        - Output format should be the same as input format, i.e. a conversation where each speaker's turn is enclosed in tags, <Person1> and <Person2>.
        - All open tags should be closed by a corresponding tag of the same type.
        - All text should be enclosed by either <Person1> or <Person2> tags
        - Make sure Person1's text is inside the tag <Person1> and do the same with Person2.
        - The conversation must start with <Person1> and end with <Person2>.


        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Content:
        "The history of the internet is fascinating. It started as a military project and evolved into a global network connecting billions of people."

        Resulting Conversation:
        <Person1>"The internet's history is so fascinating, don't you think?"</Person1>
        <Person2>"Absolutely! It’s amazing how it started as a military project."</Person2>
        <Person1>"Yeah, and now it connects billions of people worldwide."</Person1>
        <Person2>"It’s hard to imagine life without it these days."</Person2>

        EXAMPLE 2:
        Content:
        "Artificial intelligence is transforming industries. From healthcare to finance, AI is making processes more efficient and accurate."

        Resulting Conversation:
        <Person1>"AI is really transforming industries, isn’t it?"</Person1>
        <Person2>"Totally! Healthcare, for instance, has seen incredible advancements."</Person2>
        <Person1>"Right, like AI-powered diagnostics improving accuracy."</Person1>
        <Person2>"And in finance, it’s optimizing processes and reducing errors."</Person2>
        <Person1>"It’s fascinating how AI is also being used in creative fields, like generating art and music."</Person1>
        <Person2>"Yeah, it’s like we’re entering a new era of possibilities."</Person2>

        EXAMPLE 3:
        Content:
        "Climate change is one of the most pressing issues of our time. It requires global cooperation to mitigate its effects."

        Resulting Conversation:
        <Person1>"Climate change is such a pressing issue these days."</Person1>
        <Person2>"It really is. Global cooperation is absolutely essential to tackle it."</Person2>
        <Person1>"Yeah, and we need to act fast to mitigate its effects."</Person1>
        <Person2>"Every small step counts, but large-scale action is crucial."</Person2>
        <Person1>"For instance, renewable energy adoption is a key part of the solution."</Person1>
        <Person2>"Exactly, and we also need to focus on reforestation and sustainable practices."</Person2>
        <Person1>"It’s a collective effort, and everyone has a role to play."</Person1>
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
        You are an international Oscar-winning screenwriter.
        You have been working with multiple award-winning podcasters.

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

        FORMAT:
        - Output format should be the same as input format, i.e., a conversation where each speaker's turn is enclosed in tags, <Person1> and <Person2>.
        - All open tags should be closed by a corresponding tag of the same type.
        - All text should be enclosed by either <Person1> or <Person2> tags.
        - Make sure Person1's text is inside the tag <Person1> and do the same with Person2.
        - The conversation must start with <Person1> and end with <Person2>.

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        Transcript 1:
        <Person1>Did you see the new movie that just came out? It's getting rave reviews.</Person1>
        <Person2>Yes, I heard it's a masterpiece. The director really outdid themselves.</Person2>

        Transcript 2:
        <Person1>Scientists have just made a breakthrough in quantum computing.</Person1>
        <Person2>It's a game-changer for technology and could revolutionize industries.</Person2>

        Output:
        <Person1>Speaking of masterpieces, it’s amazing how human creativity extends beyond art and movies.</Person1>
        <Person2>Absolutely, like in science and technology. Did you hear about the recent breakthrough in quantum computing?</Person2>
        <Person1>Yes, it’s incredible how it could revolutionize so many industries.</Person1>
        <Person2>It’s like we’re living in a sci-fi movie, but it’s real life!</Person2>

        EXAMPLE 2:
        Input:
        Transcript 1:
        <Person1>The local food festival was such a hit this year. So many unique dishes to try!</Person1>
        <Person2>Yes, and the turnout was amazing. It’s great to see the community come together.</Person2>

        Transcript 2:
        <Person1>Meanwhile, on the global stage, there’s been a lot of discussion about climate change policies.</Person1>
        <Person2>Yes, it’s a critical issue that requires immediate attention from world leaders.</Person2>

        Output:
        <Person1>It’s wonderful how events like the food festival bring people together. It makes you think about the bigger picture, doesn’t it?</Person1>
        <Person2>Definitely. On a global scale, collaboration is just as important, especially when it comes to issues like climate change.</Person2>
        <Person1>True, and it’s something that affects all of us, no matter where we live.</Person1>
        <Person2>Exactly. It’s a reminder that we’re all connected in some way.</Person2>

        EXAMPLE 3:
        Input:
        Transcript 1:
        <Person1>The new smartphone has some incredible features. The camera quality is unmatched.</Person1>
        <Person2>Yes, and the battery life is a huge improvement over previous models.</Person2>

        Transcript 2:
        <Person1>Speaking of history, did you know this year marks the 100th anniversary of a major historical event?</Person1>
        <Person2>Yes, it’s fascinating to look back and see how far we’ve come.</Person2>

        Output:
        <Person1>Technology is advancing so quickly. It’s amazing to think about how far we’ve come in just a few decades.</Person1>
        <Person2>Exactly. It’s like looking back at history and realizing how much has changed over the years.</Person2>
        <Person1>Speaking of history, did you know this year marks the 100th anniversary of a major event?</Person1>
        <Person2>Yes, it’s fascinating to reflect on those milestones and their impact on the present.</Person2>
        """
    ),
    user=textwrap.dedent(
        """
        Transcript 1:
        {transcript1}
        Transcript 2:
        {transcript2}

        Transcript configuration:
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
        You are an international Oscar-winning screenwriter.
        You have been working with multiple award-winning podcasters.

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - Your task is to create an engaging introduction for a podcast.
        - Use the provided content to generate a comprehensive description of all topics in the upcoming episode.
        - Integrate the descriptions into the following dialogue format:
          <Person1> "Welcome to [Podcast Name] - [Podcast Tagline]! Today, we're discussing [few words about the episode]!"</Person1>
          <Person2> "[intro for person2 being exited]! [question towards what podcast will be about]?"</Person2>
          <Person1> "We'll start with [topic 1], then move on to [topic 2], followed by [topic 3], and finally, we'll wrap up with [topic n]."</Person1>
          <Person2> "That sounds like a fantastic lineup! Let's get started."</Person2>
        - Ensure the introduction is concise, engaging, and adheres to the specified format.
        - Maintain the language specified by the user.
        - Use advanced TTS-specific markup to enhance the naturalness of the conversation.
        - Avoid repetitive phrases and ensure the dialogue flows naturally.
        - Incorporate engagement techniques to make the introduction dynamic and captivating.

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        Content: "Today's topics include the rise of AI in healthcare, the latest trends in renewable energy, a fascinating story about space exploration, and the impact of blockchain on finance."
        Podcast Name: "TechTalk Weekly"
        Podcast Tagline: "Your source for the latest in technology and innovation."

        Output:
        <Person1> "Welcome to TechTalk Weekly - Your source for the latest in technology and innovation! We have so many great topics around AI for today!"</Person1>
        <Person2> "I'm so exited about todays episode! So what are we covering today?"</Person2>
        <Person1> "We'll start with how AI is revolutionizing healthcare, then move on to the latest breakthroughs in renewable energy, followed by an inspiring story about space exploration, and finally, we'll explore how blockchain is reshaping the financial industry."</Person1>
        <Person2> "That's straight up in our alley! Let's get started."</Person2>

        EXAMPLE 2:
        Input:
        Content: "We'll explore the psychology of decision-making, the art of storytelling, tips for effective communication, and the science of habit formation."
        Podcast Name: "Mind Matters"
        Podcast Tagline: "Insights into the human mind and behavior."

        Output:
        <Person1> "Welcome to Mind Matters - Insights into the human mind and behavior! Today, we have a jam packed episode full of psychology and science!"</Person1>
        <Person2> "It's great to be back! So what are we covering today?"</Person2>
        <Person1> "We'll start with the fascinating psychology of how we make decisions, then uncover the art and science of storytelling, followed by actionable tips for improving communication skills, and finally, we'll delve into the science of building better habits."</Person1>
        <Person2> "I can't wait to dive into these topics. Let's get started!"</Person2>
        """
    ),
    user=textwrap.dedent(
        """
        Content start:
        {content}
        Content end.

        Podcast configuration:
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
        You are an expert podcast scriptwriter.

        {PRE_THINK_INSTRUCT}

        INSTRUCTION:
        - Your task is to write a conclusion for a podcast.
        - Use the provided previous dialogue to generate a summary of the topics discussed.
        - Provide a conclusion and ending for the podcast in the following dialogue format:
          <Person1> "Well, that wraps up today's episode of [podcast_name]. We covered [summary of topics]."</Person1>
          <Person2> "It was a great discussion! [Additional concluding remarks]."</Person2>
          <Person1> "Thanks for sharing your thoughts on [specific topic or reflection]."</Person1>
          <Person2> "Bye!"</Person2>
        - Ensure the conclusion is concise, engaging, and adheres to the specified format.
        - Maintain the language specified by the user.
        - Use advanced TTS-specific markup to enhance the naturalness of the conversation.
        - Avoid repetitive phrases and ensure the dialogue flows naturally.
        - Incorporate engagement techniques to make the conclusion dynamic and captivating.

        FEWSHOT EXAMPLES:

        EXAMPLE 1:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to TechTalk Weekly...' </Person1> <Person2> 'I'm excited to discuss this...' </Person2> <Person1> 'First, we'll explore AI in healthcare...' </Person1> <Person2> 'That sounds fascinating...' </Person2>"
        Podcast Name: "TechTalk Weekly"
        Podcast Tagline: "Your source for the latest in technology and innovation."

        Output:
        <Person1> "Well, that wraps up today's episode of TechTalk Weekly. We covered how AI is transforming healthcare, the future of renewable energy, and an inspiring story about space exploration."</Person1>
        <Person2> "It was a great discussion! I especially enjoyed learning about the breakthroughs in renewable energy."</Person2>
        <Person1> "Thanks for sharing your thoughts on the future of technology. It's always exciting to explore these topics."</Person1>
        <Person2> "Bye!"</Person2>

        EXAMPLE 2:
        Input:
        Previous Dialogue: "<Person1> 'Welcome to Mind Matters...' </Person1> <Person2> 'I'm excited to discuss this...' </Person2> <Person1> 'First, we'll delve into decision-making...' </Person1> <Person2> 'That sounds intriguing...' </Person2>"
        Podcast Name: "Mind Matters"
        Podcast Tagline: "Insights into the human mind and behavior."

        Output:
        <Person1> "Well, that wraps up today's episode of Mind Matters. We explored the psychology of decision-making, the art of storytelling, and tips for effective communication."</Person1>
        <Person2> "It was a fascinating discussion! I loved the insights on storytelling."</Person2>
        <Person1> "Thanks for sharing your perspective on communication strategies. It's always a pleasure to dive into these topics."</Person1>
        <Person2> "Join us again!"</Person2>
        """
    ),
    user=textwrap.dedent(
        """
        Previous Dialogue:
        {previous_dialogue}
        Previous Dialogue end.

        Podcast configuration:
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
