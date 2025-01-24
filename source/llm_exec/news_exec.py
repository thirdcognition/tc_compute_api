from source.chains.init import get_chain
from source.models.structures.url_result import UrlResult
from source.prompts.web_source import NewsArticle


async def web_source_article_builder(data: UrlResult) -> NewsArticle:
    payload = {"context": data.human_readable_content, "meta": data.metadata}
    if data.image_data:
        payload["image_data"] = data.image_data

    result: NewsArticle = await get_chain("web_source_builder").ainvoke(payload)

    return result  # Pass supabase


def web_source_article_builder_sync(data: UrlResult) -> NewsArticle:
    payload = {"context": data.human_readable_content, "meta": data.metadata}
    if data.image_data:
        payload["image_data"] = data.image_data

    result: NewsArticle = get_chain("web_source_builder_sync").invoke(payload)

    print(f"Resulting article {result.title=}")

    return result  # Pass supabase
