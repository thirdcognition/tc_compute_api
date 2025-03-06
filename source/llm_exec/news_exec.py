from langsmith import traceable
from langchain_core.messages import BaseMessage
from source.chains.init import get_chain
from source.models.structures.news_article import NewsArticle
from source.models.structures.url_result import UrlResult
from typing import Tuple


@traceable(
    run_type="llm",
    name="Build web source article",
)
async def web_source_article_builder(data: UrlResult) -> NewsArticle:
    payload = {"context": data.human_readable_content, "meta": data.metadata}
    if data.image_data:
        payload["image_data"] = data.image_data

    result: NewsArticle = await get_chain("web_source_builder").ainvoke(payload)

    return result  # Pass supabase


@traceable(
    run_type="llm",
    name="Build web source article (sync)",
)
def web_source_article_builder_sync(data: UrlResult) -> NewsArticle:
    payload = {"context": data.human_readable_content, "meta": data.metadata}
    if data.image_data:
        payload["image_data"] = data.image_data

    result: NewsArticle = get_chain("web_source_builder_sync").invoke(payload)

    if isinstance(result, BaseMessage):
        raise ValueError("Generation failed: Received a BaseMessage.")

    print(f"Resulting article {result.title=}")

    return result  # Pass supabase


@traceable(
    run_type="llm",
    name="Format text",
)
# New Functions for Validating News Articles
async def text_format(content: str) -> str:
    """
    Asynchronous function to validate if the content is a valid news article.
    Returns a tuple: (is_valid: bool, explanation: str).
    """
    payload = {"context": content}
    return await get_chain("text_formatter_simple").ainvoke(payload)


@traceable(
    run_type="llm",
    name="Format text (sync)",
)
def text_format_sync(content: str) -> str:
    """
    Synchronous function to validate if the content is a valid news article.
    Returns a tuple: (is_valid: bool, explanation: str).
    """
    payload = {"context": content}
    return get_chain("text_formatter_simple_sync").invoke(payload)


@traceable(
    run_type="llm",
    name="Validate news item",
)
# New Functions for Validating News Articles
async def validate_news_article(
    content: str, title: str, description: str
) -> Tuple[bool, str]:
    """
    Asynchronous function to validate if the content is a valid news article.
    Returns a tuple: (is_valid: bool, explanation: str).
    """
    payload = {"content": content, "title": title, "description": description}
    result: Tuple[bool, str] = await get_chain("validate_news_article").ainvoke(payload)
    return result


@traceable(
    run_type="llm",
    name="Validate news item (sync)",
)
def validate_news_article_sync(
    content: str, title: str, description: str
) -> Tuple[bool, str]:
    """
    Synchronous function to validate if the content is a valid news article.
    Returns a tuple: (is_valid: bool, explanation: str).
    """
    payload = {"content": content, "title": title, "description": description}
    result: Tuple[bool, str] = get_chain("validate_news_article_sync").invoke(payload)
    return result
