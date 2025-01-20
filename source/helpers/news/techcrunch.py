from typing import List, Tuple
from pydantic import BaseModel
from datetime import datetime
import feedparser
from supabase import Client

from source.models.data.news_item import NewsItem
from source.helpers.resolve_url import LinkResolver
from source.models.data.user import UserIDs


class TechCrunchNewsConfig(BaseModel):
    articles: int


def fetch_techcrunch_news_items(config: TechCrunchNewsConfig) -> List[NewsItem]:
    # TechCrunch RSS feed URL
    feed_url = "https://techcrunch.com/feed/"

    print(f"TechCrunch: Fetching TechCrunch news items from URL: {feed_url}")
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    print(f"TechCrunch: Number of items fetched: {len(feed.entries)}")

    # Extract the required number of news items
    news_items = []
    for entry in feed.entries[: config.articles]:
        news_item = NewsItem(
            title=entry.title,
            source="TechCrunch",
            original_source=entry.link,
            description=entry.description,
            image=(entry.enclosures[0].href if entry.enclosures else None),
            publish_date=(
                datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                if hasattr(entry, "published") and entry.published
                else None
            ),
            categories=(
                [category.term for category in entry.tags]
                if hasattr(entry, "tags")
                else []
            ),
            lang="EN",
        )
        news_items.append(news_item)

    return news_items


def fetch_techcrunch_news_links(
    supabase: Client, config: TechCrunchNewsConfig, user_ids: UserIDs = None
) -> List[Tuple[str, str]]:
    # Fetch news items using the existing function
    news_items = fetch_techcrunch_news_items(config)

    print(f"TechCrunch: Resolving links for {len(news_items)} news items")
    # Initialize the LinkResolver
    resolver = LinkResolver(reformat_text=True)

    # Check if each news item exists in the database
    resolved_links = []
    resolved_count = 0

    for item in news_items:
        if resolved_count >= config.articles:
            break
        if item.check_if_exists_sync(supabase):
            print(f"TechCrunch: Use existing item for {str(item.original_source)=}")
            item.load_from_supabase_sync(supabase)
            resolved_links.append(item)
            resolved_count += 1
        else:
            try:
                print(f"TechCrunch: Create new item for {str(item.original_source)=}")
                resolved_url, content, formatted_content = resolver.resolve_url(
                    str(item.original_source)
                )
                item.resolved_source = resolved_url
                item.original_content = content
                item.formatted_content = formatted_content
                if user_ids is not None:
                    item.owner_id = user_ids.user_id
                    item.organization_id = user_ids.organization_id
                item.create_and_save_source_sync(supabase)
                resolved_links.append(item)
                resolved_count += 1
            except Exception as e:
                print(f"TechCrunch: Failed to resolve {item.original_source}: {e}")

    # Close the resolver
    resolver.close()

    return resolved_links
