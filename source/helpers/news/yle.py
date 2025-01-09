from typing import List, Tuple
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import feedparser
from source.helpers.news.news_item import NewsItem
from source.helpers.resolve_url import LinkResolver
from source.models.config.logging import logger


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
            link=entry.link,
            description=entry.description,
            image=(entry.enclosures[0].href if entry.enclosures else None),
            publish_date=(
                datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                if hasattr(entry, "published") and entry.published
                else None
            ),
            categories=[category.term for category in entry.tags],
        )
        news_items.append(news_item)

    return news_items


def fetch_yle_news_links(config: YleNewsConfig) -> List[Tuple[str, str]]:
    # Fetch news items using the existing function
    news_items = fetch_yle_news_items(config)

    # Initialize the LinkResolver
    resolver = LinkResolver()

    # Resolve each URL and fetch content
    resolved_links = []
    resolved_count = 0

    for item in news_items:
        if resolved_count >= config.articles:
            break
        try:
            resolved_url, content = resolver.resolve_url(str(item.link))
            resolved_links.append((resolved_url, content))
            resolved_count += 1
        except Exception as e:
            logger.info(f"Failed to resolve {item.link}: {e}")

    # Close the resolver
    resolver.close()

    return resolved_links
