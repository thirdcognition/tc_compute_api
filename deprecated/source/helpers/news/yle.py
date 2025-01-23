from typing import List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import feedparser

from source.models.data.web_source import WebSource


# Enum for feed types
class YleFeedType(str, Enum):
    MAJOR_HEADLINES = "majorHeadlines"
    MOST_READ = "mostRead"


class YleNewsConfig(BaseModel):
    type: YleFeedType
    articles: int


def fetch_yle_news_items(config: YleNewsConfig) -> List[WebSource]:
    # Construct the feed URL based on the feed type
    feed_url = f"https://feeds.yle.fi/uutiset/v1/{config.type.value}/YLE_UUTISET.rss"

    print(f"Yle: Fetching Yle news items from URL: {feed_url}")
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    print(f"Yle: Number of items fetched: {len(feed.entries)}")

    # Extract the required number of news items
    news_items = []
    for entry in feed.entries:
        news_item = WebSource(
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
