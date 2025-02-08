import collections
from enum import Enum
import json
import textwrap
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from source.prompts.actions import QuestionClassifierParser
from source.prompts.base import (
    ACTOR_INTRODUCTIONS,
    KEEP_PRE_THINK_TOGETHER,
    MAINTAIN_CONTENT_AND_USER_LANGUAGE,
    PRE_THINK_INSTRUCT,
    PromptFormatter,
    TagsParser,
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


# class WebSourceGroupingItem(BaseModel):
#     id: str = Field(
#         ...,
#         description="ID of the original item derived from ID([ID]) at the beginning of the item.",
#     )
#     categories: List[str] = Field(
#         ..., description="A list of specified or assigned categories"
#     )


# Define the Pydantic model for the output structure
class WebSourceGrouping(BaseModel):
    ordered_groups: List[List[str]] = Field(
        ..., description="An ordered list of lists of grouped IDs.", min_length=5
    )
    ordered_group_titles: List[str] = Field(
        ...,
        description="An ordered list of titles for ordered_groups based on the titles of the items within the group.",
        min_length=5,
    )
    main_group: int = Field(
        ...,
        description="The index of the group which is considered to be the most important group in the groups",
    )
    all_ids: List[str] = Field(
        ...,
        description="A list of all IDs derived from ID([ID]) at the beginning of each item.",
    )


# Create the PydanticOutputParser for the WebSourceGrouping model
web_source_grouping_parser = PydanticOutputParser(pydantic_object=WebSourceGrouping)


class WebSourceGroupingValidator:
    def __init__(self):
        self.cleaner = TagsParser(tags=["think", "reflection"], return_tag=False)

    def parse(self, raw_input: str) -> WebSourceGrouping:
        # Clean the <think> and <reflection> tags
        cleaned_input = self.cleaner.parse(raw_input)
        # print(f"{cleaned_input=}")

        # Parse the cleaned input into a WebSourceGrouping object
        parsed_response = web_source_grouping_parser.parse(cleaned_input)

        # Flatten the grouped IDs from the parsed response
        grouped_ids = {
            item for group in parsed_response.ordered_groups for item in group
        }

        original_ids = parsed_response.all_ids

        tolerance = max(len(grouped_ids), len(original_ids)) // 5

        # Check for duplicate IDs
        if len(grouped_ids) != len(original_ids):
            duplicates = set(
                id
                for id, count in collections.Counter(original_ids).items()
                if count > 1 and len(str(id).strip()) > 0
            )
            if len(duplicates) > 0:
                raise OutputParserException(
                    f"The following IDs are duplicated in the LLM response: {', '.join(duplicates)}"
                )

        # Find missing IDs
        missing_ids = set(original_ids) - grouped_ids

        if len(missing_ids) > tolerance:
            raise OutputParserException(
                f"The following IDs are missing from the LLM response: {', '.join(missing_ids)}"
            )

        return parsed_response


# Create the PromptFormatter for the LLM
group_web_sources = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        {PRE_THINK_INSTRUCT}
        {KEEP_PRE_THINK_TOGETHER}

        You are tasked with analyzing a list of articles and then grouping and sorting them based on their topical or categorical connections.
        Instructions:
        - Group articles into lists of IDs based on their categories, topic, title and summary.
        - Each group must be directly connected by categories, topic and title or summary.
        - Do not group items just by topic or category.
        - Sorting of the groups should be based on categories and topics.
        - Make sure to sort groups through similarity of topics/categories.
        - Use the `start_with` and `end_with` parameters to determine which items to place at the beginning and end of the ordered groups.
        - Ensure all provided IDs are included in the output.
        - Return the result as a JSON object using the specified format.
        - Do not use one ID more than once in the groups.

        Format instructions:
        <think>Place your think here</think>
        <output>
        {web_source_grouping_parser.get_format_instructions()}
        </output>
        """
    ),
    user=textwrap.dedent(
        """
        Current date and time:
        {datetime}

        Articles:
        {web_sources}

        Parameters:
        Start with: {start_with}
        End with: {end_with}

        Group the articles and return the result.
        """
    ),
)

group_web_sources.parser = WebSourceGroupingValidator()

group_rss_items = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        {PRE_THINK_INSTRUCT}
        {KEEP_PRE_THINK_TOGETHER}

        You are tasked with analyzing a list of rss items and then grouping and sorting them based on their title, alternative sources and/or categorical connections.
        Instructions:
        - Group rss items into lists of IDs based on their categories, title and description.
        - Each group must be directly connected by categories, alternative sources or description.
        - If the a list of alternative sources are specified use that to connect matching items where possible.
        - Do not group items just by title or category. Grouped item must share the same description, be of the same news item or be linked directly.
        - Make sure to sort groups through similarity of titles/categories.
        - Sorting of the groups should be based on importance or significance of the news.
        - If defined use Instructions determine which items to place at the beginning and end of the ordered groups.
        - Ensure all IDs are included in the output.
        - Every id from the All IDs list must be included in the ordered_groups.
        - Return the result as a JSON object using the specified format.
        - If you are given instructions follow them as closely as possible.
        - ordered_groups and ordered_groups_titles cannot be empty. They must have the groups defined in them.

        Format instructions:
        <think>Place your thinking here.</think>
        <output>
        {web_source_grouping_parser.get_format_instructions()}
        </output>
        """
    ),
    user=textwrap.dedent(
        """
        Current date and time:
        {datetime}

        All IDs:
        {all_ids}

        RSS Items:
        {web_sources}

        Instructions:
        {instructions}

        Group and sort the RSS Items and return the result.

        Make sure to include every id from the All IDs in the ordered_groups.
        ordered_groups and ordered_groups_titles cannot be empty. They must have the groups defined in them.
        """
    ),
)

group_rss_items.parser = WebSourceGroupingValidator()

# New Prompt: Validate News Article
validate_news_article = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        Act as a news article validator.

        {PRE_THINK_INSTRUCT}

        Instructions:
        - Validate the provided content/HTML for:
          - Presence of the original article information.
          - Alignment with the provided title and description.
          - Allowance of mentions of content policies, privacy policies, or automated system responses, as long as the original article is present.
        - Return "yes" if the content is valid and meets all criteria, otherwise return "no" with a list of issues.
        - If the content does not contain the original article information, fail the validation.

        Format your response as follows:
        - "yes" or "no".
        - If "no", include a list of issues and suggestions for improvement.
        """
    ),
    user=textwrap.dedent(
        """
        Content start:
        {content}
        Content end.

        Title: {title}
        Description: {description}

        Validate the content against the title and description and return the result.
        """
    ),
)

validate_news_article.parser = QuestionClassifierParser()
