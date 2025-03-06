# import collections

# from enum import Enum
import os
import re
import textwrap
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage
from source.helpers.json_exportable_enum import JSONExportableEnum
from source.helpers.shared import read_and_load_yaml
from source.load_env import SETTINGS
from source.models.structures.news_article import NewsArticle
from source.prompts.actions import QuestionClassifierParser
from source.prompts.base import (
    ACTOR_INTRODUCTIONS,
    KEEP_PRE_THINK_TOGETHER,
    MAINTAIN_CONTENT_AND_USER_LANGUAGE,
    PRE_THINK_INSTRUCT,
    PromptFormatter,
    TagsParser,
)

news_taxonomy_dir = os.path.join(SETTINGS.file_repository_path, "taxonomy")

_news_taxonomy_dict: dict = read_and_load_yaml(
    os.path.join(news_taxonomy_dir, "news.yaml")
)


class NewsTaxonomy(BaseModel):
    id: str
    parent: Optional[str] = None
    title: Optional[str]
    definition: Optional[str] = None
    children: Optional[list["NewsTaxonomy"]] = None

    def describe(self, skip_children: bool = False, depth=0, detailed=False) -> str:
        result = str(self)
        if detailed:
            result = (
                f"ID: {self.id}, Title: {self.title}, Definition: {self.definition}"
            )
        if not skip_children and self.children:
            for child in self.children:
                result += f" ({child.describe(depth=depth + 1, detailed=detailed)})"
        return result

    def __str__(self):
        return f"{self.id}"


news_taxonomy_hierarchy: dict[str, NewsTaxonomy] = {}
news_taxonomy_all: dict[str, NewsTaxonomy] = {}
_tmp = []
_enum_data: dict = {}
_enum_data_extended: dict = {}
for taxonomy_id, taxonomy_data in _news_taxonomy_dict.items():
    # Create a NewsTaxonomy instance
    news_taxonomy_item = NewsTaxonomy(
        id=taxonomy_id,
        parent=taxonomy_data.get("parent"),
        title=taxonomy_data.get("title"),
        definition=taxonomy_data.get("definition"),
    )
    news_taxonomy_all[taxonomy_id] = news_taxonomy_item
    parent = news_taxonomy_item.parent
    if parent:
        if parent in news_taxonomy_all.keys():
            if news_taxonomy_all[parent].children is None:
                news_taxonomy_all[parent].children = []
            news_taxonomy_all[parent].children.append(news_taxonomy_item)
        else:
            _tmp.append(news_taxonomy_item)
    else:
        news_taxonomy_hierarchy[taxonomy_id] = news_taxonomy_item
        _enum_data[taxonomy_id] = news_taxonomy_item.title or ""

    _enum_data_extended[taxonomy_id] = news_taxonomy_item.title or ""
    # Add the created item to the news_taxonomy list

for item in _tmp:
    if parent in news_taxonomy_all.keys():
        if news_taxonomy_all[parent].children is None:
            news_taxonomy_all[parent].children = []
        news_taxonomy_all[parent].children.append(news_taxonomy_item)
    else:
        _tmp.append(news_taxonomy_item)

news_taxonomy_str = ", ".join(
    [item.describe(skip_children=True) for item in news_taxonomy_hierarchy.values()]
)
news_taxonomy_extended_str = ", ".join(
    [item.describe() for item in news_taxonomy_hierarchy.values()]
)

NewsCategory = JSONExportableEnum("NewsCategory", _enum_data)
NewsCategoryExtended = JSONExportableEnum("NewsCategoryExtended", _enum_data_extended)

# class NewsCategory(str, JSONExportableEnum):
#     WORLD = "World"
#     NATIONAL = "National"
#     BUSINESS = "Business"
#     TECHNOLOGY = "Technology"
#     ENTERTAINMENT = "Entertainment"
#     SPORTS = "Sports"
#     SCIENCE = "Science"
#     HEALTH = "Health"
#     TRAVEL = "Travel"
#     FOOD = "Food"

# def __str__(self):
#     return self.value

# def __json__(self):
#     """
#     Custom method to make NewsCategory JSON serializable.
#     """
#     return self.value

# def to_json(self):
#     return self.value

# @staticmethod
# def from_json(value: str):
#     return NewsCategory(value)


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

        Available category IDs:
        {news_taxonomy_extended_str}

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


class WebSourceGroupingItem(BaseModel):
    ids: List[str] = Field(
        ...,
        description="List of IDs of the original item derived from ID([ID]) at the beginning of the item.",
        max_length=5,
    )
    categories: Optional[List[str]] = Field(
        ...,
        description="A list of specified or assigned categories aligned with items of the group. Must use the defined available category ids.",
    )
    topic: Optional[str] = Field(..., description="Generalized topic of the group.")
    title: str = Field(
        ..., description="Descriptive title for the group based on selected items."
    )


# Define the Pydantic model for the output structure
class WebSourceGrouping(BaseModel):
    min_groups: int = Field(..., description="Minimum amount of ordered groups.")
    max_group_ids: int = Field(..., description="Maximum amount of IDs per group.")
    ordered_groups: List[WebSourceGroupingItem] = Field(
        ..., description="An ordered list of lists of grouped IDs."
    )
    # ordered_group_titles: List[str] = Field(
    #     ...,
    #     description="An ordered list of titles for ordered_groups based on the titles of the items within the group.",
    # )
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
        if isinstance(raw_input, BaseMessage):
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

        # Parse the cleaned input into a WebSourceGrouping object
        parsed_response = web_source_grouping_parser.parse(cleaned_input)

        # Flatten the grouped IDs from the parsed response
        grouped_ids = {
            item for group in parsed_response.ordered_groups for item in group.ids
        }

        original_ids = list(set(parsed_response.all_ids))

        exception_str = ""

        # tolerance = max(len(grouped_ids), len(original_ids)) // 5

        if len(grouped_ids) < parsed_response.min_groups:
            exception_str += f"The response does not have enough groups defined. Minimum amount is: {parsed_response.min_groups}\n\n"

        too_many_ids = [
            group
            for group in parsed_response.ordered_groups
            if len(group.ids) > parsed_response.max_group_ids
        ]

        if len(too_many_ids) > 0:
            exception_str += f"Following groups have too many IDs: {', '.join([(group.title if group.title else group.topic) for group in too_many_ids])}\n\n"

        unknown_ids = [id for id in grouped_ids if id not in original_ids]

        if len(unknown_ids) > 0:
            exception_str += (
                f"Unknown IDs are used in groups: {', '.join(unknown_ids)}\n\n"
            )

        for group in parsed_response.ordered_groups:
            if group.categories:
                for category in group.categories:
                    if (
                        category not in NewsCategoryExtended.__members__
                        and category not in NewsCategoryExtended.__members__.values()
                    ):
                        exception_str += f"Unknown category '{category}' found in group '{group.title or group.topic}'.\n\n"

        # Check for duplicate IDs
        # if len(grouped_ids) != len(original_ids):
        #     duplicates = set(
        #         id
        #         for id, count in collections.Counter(original_ids).items()
        #         if count > 1 and len(str(id).strip()) > 0
        #     )
        #     if len(duplicates) > 0:
        #         exception_str += f"The following IDs are duplicated in the LLM response: {', '.join(duplicates)}"

        # # Find missing IDs
        # missing_ids = set(original_ids) - grouped_ids

        # if (
        #     len(missing_ids) > tolerance
        #     and len(parsed_response.ordered_groups) < parsed_response.min_groups
        # ):
        #     exception_str += f"The following IDs are missing from the LLM response: {', '.join(missing_ids)}"
        # else:
        # print("Adding missing ids to the list")
        # parsed_response.ordered_groups.append(
        #     WebSourceGroupingItem(
        #         ids=[id for id in missing_ids],
        #         categories=[],
        #         topic="Various",
        #         title="Missing ids",
        #     )
        # )

        if exception_str:
            raise OutputParserException(exception_str)

        return parsed_response


# Create the PromptFormatter for the LLM
group_web_sources = PromptFormatter(
    system=textwrap.dedent(
        f"""
        {ACTOR_INTRODUCTIONS}
        {PRE_THINK_INSTRUCT}
        {KEEP_PRE_THINK_TOGETHER}

        You are tasked with analyzing a list of articles and then grouping them by their subject and sorting them based on their topical and categorical connections.
        Instructions:
        - Group articles into lists of IDs by their subject based on title and summary.
        - Each group must be directly connected by subject.
        - Do not group items by topic or category.
        - Sorting of the groups should be based on categories and topics.
        - Make sure to sort groups through similarity of topics/categories.
        - Use the `start_with` and `end_with` parameters to determine which topics and themes to place at the beginning and end of the ordered groups.
        - Ensure all provided IDs are included in the output.
        - Return the result as a JSON object using the specified format.
        - Do not use one ID more than once in the groups.

        Available category IDs:
        {news_taxonomy_str}

        Format instructions:
        <think>Place your thinking here.</think>
        <output>
        {web_source_grouping_parser.get_format_instructions()}
        </output>
        """
        # Format instructions:
        # {web_source_grouping_parser.get_format_instructions()}
        # """
    ),
    user=textwrap.dedent(
        """
        Current date and time:
        {datetime}

        Minimum amount of groups: {min_groups}
        Maximum amount of ids per group: {max_ids}

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

        Available category IDs:
        {news_taxonomy_str}

        Format instructions:
        <think>Place your thinking here.</think>
        <output>
        {web_source_grouping_parser.get_format_instructions()}
        </output>
        """
        # Format instructions:
        # {web_source_grouping_parser.get_format_instructions()}
        # """
    ),
    user=textwrap.dedent(
        """
        Current date and time:
        {datetime}

        Minimum amount of groups: {min_groups}
        Maximum amount of ids per group: {max_ids}

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
          - Content policies, privacy policies, or automated system responses, are allowed to an extent as long as the original article is present
          - If 403, access denied, or any other http error is mentioned in the content, the article is not valid.
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
