from typing import List, Union
from pydantic import BaseModel, Field


class ActionModel(BaseModel):
    id: str = Field(
        default=None,
        description="Unique identifier for the action. If available use the existing ID.",
        title="ID",
    )
    after_id: str = Field(
        default=None,
        description="Identifier of the item preseeds this subject.",
        title="After ID",
    )
    parent_id: str = Field(
        default=None,
        description="Identifier of the parent subject for this action.",
        title="Parent ID",
    )
    title: str = Field(description="Title for the content", title="Title")
    description: str = Field(
        description="Objective, or target for the content", title="Description"
    )
    use_guide: str = Field(
        description="Detailed instructions on how to use the content with the user",
        title="Usage guidance",
    )
    test: str = Field(
        description="Description on how to do a test to verify that the student has succeeded in learning the contents.",
        title="Test",
    )
    end_of_day: int = Field(
        description="Number of days after the start of the journey that the action should be completed.",
        title="Done by end of day #",
    )


class ModuleStructure(BaseModel):
    id: str = Field(
        default=None,
        description="Unique identifier for the module. If available use the existing ID.",
        title="ID",
    )
    after_id: str = Field(
        default=None,
        description="Identifier of the item preseeds this subject.",
        title="After ID",
    )
    parent_id: str = Field(
        default=None,
        description="Identifier of the parent subject for this subject.",
        title="Parent ID",
    )
    title: str = Field(description="The title or name of this subject.", title="Title")
    icon: str = Field(
        description="Icon to represent this subject. Use an icon from the provided options.",
        title="Icon",
    )
    subject: str = Field(description="Section of this subject", title="Section")
    intro: str = Field(description="Introduction to this subject", title="Intro")
    content: str = Field(
        description="Detailed content of this subject", title="Content"
    )
    children: List[Union[ActionModel, "ModuleStructure"]] = Field(
        description="List of child subjects and actions for this subject.",
        title="children",
    )
    end_of_day: int = Field(
        description="Number of days after the start of the journey that the module should be completed.",
        title="Done by end of day #",
    )
