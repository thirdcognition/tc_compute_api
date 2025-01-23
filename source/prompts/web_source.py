from enum import Enum
import json
import textwrap
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from source.prompts.base import (
    MAINTAIN_CONTENT_AND_USER_LANGUAGE,
    PromptFormatter,
)


class NewsCategory(Enum):
    WORLD = "World"
    NATIONAL = "National"
    BUSINESS = "Business"
    TECHNOLOGY = "Technology"
    ENTERTAINMENT = "Entertainment"
    SPORTS = "Sports"
    SCIENCE = "Science"
    HEALTH = "Health"
    TRAVEL = "Travel"
    FOOD = "Food"
    # Add more categories as needed


class NewsArticle(BaseModel):
    title: str = Field(..., title="Title", description="Title for the article")

    topic: str = Field(
        ...,
        title="Topic",
        description="The topic related to the context.",
    )
    description: str = Field(
        ...,
        title="Description",
        description="Synopsis for the article.",
    )
    summary: str = Field(
        ...,
        title="Summary",
        description="Brief summary of the context.",
    )
    article: str = Field(
        ..., title="Article", description="Article based on the provided context."
    )
    lang: str = Field(
        ..., title="Language", description="An ISO code for the language."
    )
    image: str = Field(
        ...,
        title="Image",
        description="Url to an hero image which is defined in the context. If context specifies no images return as None.",
    )
    categories: Optional[List[NewsCategory]] = Field(
        default=None,
        title="Categories",
        description="List of Google News categories based on the context.",
    )

    def __str__(self) -> str:
        return (
            f"NewsArticle:\\n"
            f"Title: {self.title}\\n"
            f"Topic: {self.topic}\\n"
            f"Summary: {self.summary}"
        )

    def to_json(self) -> str:
        """
        Convert the NewsArticle instance to a compact JSON string.
        """
        return json.dumps(self.model_dump(), ensure_ascii=False)


web_source_builder_parser = PydanticOutputParser(pydantic_object=NewsArticle)


def convert_and_parse(raw_input):
    if hasattr(raw_input, "content"):  # Handle AIMessage or similar objects
        print(f"{raw_input}")
        raw_input = raw_input.content
    return web_source_builder_parser.parse(raw_input)


web_source_builder = PromptFormatter(
    system=textwrap.dedent(
        f"""
        You are a Pulitzer award winning news reporter writing an article based on the content.
        You are given a poorly written article which you're rewriting for publishing.

        Instructions:
        {MAINTAIN_CONTENT_AND_USER_LANGUAGE}
        Rewrite the text specified by the user defined in context in full detail.
        Remove any mentions about cookies, privacy policies, adverticement policies, etc.
        Use only information in the available context and metadata.
        Use metadata for classification and other relevant details.
        Incorporate any images provided in the context into the article appropriately.
        Write an article and other details based on the context using the Format instructions.
        If base64-encoded images are provided in the context, they will be referenced as placeholders like [Image 1], [Image 2], etc.
        Decode the base64-encoded images and describe their content.
        Do not use images in the output text, but use them as inspiration for the content where applicable.

        Format instructions:
        {web_source_builder_parser.get_format_instructions()}
        """
    ),
    user=textwrap.dedent(
        """
        Context start
        {context}
        Context end

        Metadata start:
        {meta}
        Metadata end

        Write an article based on the context in full detail with the specified format and details.
        Do not place images in the outputed article.
        """
    ),
)


class ConvertAndParseWrapper:
    def parse(self, raw_input):
        return convert_and_parse(raw_input)


web_source_builder.parser = ConvertAndParseWrapper()
