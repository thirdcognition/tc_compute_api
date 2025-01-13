from typing import List, Tuple
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import feedparser
from supabase import Client

# from source.helpers.shared import pretty_print
from source.models.data.news_item import NewsItem
from source.helpers.resolve_url import LinkResolver
from source.models.config.logging import logger
from source.models.data.user import UserIDs


# Enum for feed types
class YleFeedType(str, Enum):
    MAJOR_HEADLINES = "majorHeadlines"
    MOST_READ = "mostRead"


class YleNewsConfig(BaseModel):
    type: YleFeedType
    articles: int


def fetch_yle_news_items(config: YleNewsConfig) -> List[NewsItem]:
    # Construct the feed URL based on the feed type
    feed_url = f"https://feeds.yle.fi/uutiset/v1/{config.type.value}/YLE_UUTISET.rss"

    # Parse the RSS feed
    feed = feedparser.parse(feed_url)

    # Extract the required number of news items
    news_items = []
    for entry in feed.entries:
        news_item = NewsItem(
            title=entry.title,
            source="Yle",
            original_source=entry.link,
            description=entry.description,
            image=(entry.enclosures[0].href if entry.enclosures else None),
            publish_date=(
                datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                if hasattr(entry, "published") and entry.published
                else None
            ),
            categories=[category.term for category in entry.tags],
            lang="FI",
        )
        news_items.append(news_item)

    return news_items


def fetch_yle_news_links(
    supabase: Client, config: YleNewsConfig, user_ids: UserIDs = None
) -> List[Tuple[str, str]]:
    # Fetch news items using the existing function
    news_items = fetch_yle_news_items(config)

    # Initialize the LinkResolver
    resolver = LinkResolver()

    # Check if each news item exists in the database
    resolved_links = []
    resolved_count = 0

    for item in news_items:
        if resolved_count >= config.articles:
            break
        if item.check_if_exists_sync(supabase):
            print(f"Use existing item for {str(item.original_source)=}")
            item.load_from_supabase_sync(supabase)
            resolved_links.append(item)
            resolved_count += 1
        else:
            try:
                print(f"Create new item for {str(item.original_source)=}")
                # pretty_print(item, "News_item", True, print)
                resolved_url, content = resolver.resolve_url(str(item.original_source))
                item.resolved_source = resolved_url
                item.original_content = content
                if user_ids is not None:
                    item.owner_id = user_ids.user_id
                    item.organization_id = user_ids.organization_id
                item.create_and_save_source_sync(supabase)
                resolved_links.append(item)
                resolved_count += 1
            except Exception as e:
                logger.info(f"Failed to resolve {item.original_source}: {e}")
                raise e

    # Close the resolver
    resolver.close()

    return resolved_links
