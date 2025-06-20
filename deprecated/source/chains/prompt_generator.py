import json
import os
import textwrap
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from source.helpers.shared import read_and_load_yaml
from source.prompts.base import PromptFormatter
from source.load_env import SETTINGS


prompt_template_dir = os.path.join(
    SETTINGS.file_repository_path, "llm/prompt_generator_templates"
)


class CustomPrompt(BaseModel):
    system: str = Field(
        default=None, description="System message to set the behavior of the assistant."
    )
    user: str = Field(default=None, description="User message for the LLM generation")


class CustomPromptContainer(BaseModel):
    plan: CustomPrompt = Field(description="Description for the plan of the scenario.")
    module_content: CustomPrompt = Field(
        description="Detailed explanation of each module in the scenario."
    )
    module_intro: CustomPrompt = Field(
        description="Introduction to the scenario, setting the context."
    )
    module_actions: CustomPrompt = Field(
        description="Tasks that should be taken in each module of the scenario."
    )
    action_details: CustomPrompt = Field(
        description="Specific details about the actions to be taken in each module."
    )


template_files: dict = read_and_load_yaml(
    os.path.join(prompt_template_dir, "desc.yaml")
)

for key in template_files.keys():
    template_files[key]["output"] = read_and_load_yaml(
        os.path.join(prompt_template_dir, key)
    )

journey_prompts = PromptFormatter(
    system=(
        textwrap.dedent(
            """
            You are an expert Prompt Writer for Large Language Models.

            Use following examples as a guide on how to write prompts for different actors and targets.

            Export prompts in the define format using JSON.
            """
        )
        + "\n\n".join(
            [
                textwrap.dedent(
                    f"""
        Example {i + 1}:
        Actor:
        {template_files[key]['actor']}
        Target:
        {template_files[key]['target']}
        Output:
        {textwrap.indent(json.dumps(template_files[key]['output'], indent=2), "         ")}
        """
                )
                for i, key in enumerate(template_files.keys())
            ]
        )
    ),
    user=textwrap.dedent(
        """
        Actor:
        {actor}
        Target:
        {target}
        Output:
        """
    ),
)
journey_prompts.parser = PydanticOutputParser(pydantic_object=CustomPromptContainer)
