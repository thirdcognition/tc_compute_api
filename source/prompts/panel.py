import textwrap
from source.prompts.actions import QuestionClassifierParser
from source.prompts.base import (
    # KEEP_PRE_THINK_TOGETHER,
    # MAINTAIN_CONTENT_AND_USER_LANGUAGE,
    # PRE_THINK_INSTRUCT,
    PromptFormatter,
    # TagsParser,
)

# Get prompts from:
# https://smith.langchain.com/hub/heurekalabs/podcastfy_multimodal_cleanmarkup_beginning?organizationId=de27563a-abea-51c1-93ae-bc32bd8606e9
# https://smith.langchain.com/hub/heurekalabs/podcastfy_multimodal_cleanmarkup_middle?organizationId=de27563a-abea-51c1-93ae-bc32bd8606e9
# https://smith.langchain.com/hub/heurekalabs/podcastfy_multimodal_cleanmarkup_ending?organizationId=de27563a-abea-51c1-93ae-bc32bd8606e9

verify_transcript_quality = PromptFormatter(
    system=textwrap.dedent(
        """
        Act as a transcript quality verifier.
        You will get a transcript in a format:
        <Person1>Person 1 dialog</Person1>
        <Person2>Person 2 dialog</Person2>

        Make sure that the conversation uses natural non repetitive language, follows normal dialogue
        rythm and uses the defined configuration specified by the user.
        Return "yes" if the transcript follows the defined specification otherwise return "no".
        Do not add anything else in the response. Just return "yes" or "no".
        """
    ),
    user=textwrap.dedent(
        """
        Content start:
        {content}
        Content end.

        Transcript start:
        {transcript}
        Transcript end.

        Transcript configuration:
        Language: {output_language}
        Style: {conversation_style}
        Person 1 role: {roles_person1}
        Person 2 role: {roles_person2}
        Structure: {dialogue_structure}
        Engagement techniques: {engagement_techniques}
        Word count: {word_count}

        Respond with "yes" or "no"
        """
    ),
)

verify_transcript_quality.parser = QuestionClassifierParser()
