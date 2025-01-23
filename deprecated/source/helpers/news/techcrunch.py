from typing import List
from pydantic import BaseModel
from datetime import datetime
import feedparser

from source.models.data.web_source import WebSource


class TechCrunchNewsConfig(BaseModel):
    articles: int


def fetch_techcrunch_news_items(config: TechCrunchNewsConfig) -> List[WebSource]:
    # TechCrunch RSS feed URL
    feed_url = "https://techcrunch.com/feed/"

    print(f"TechCrunch: Fetching TechCrunch news items from URL: {feed_url}")
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    print(f"TechCrunch: Number of items fetched: {len(feed.entries)}")

    # Extract the required number of news items
    news_items = []
    for entry in feed.entries[: config.articles]:
        news_item = WebSource(
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
