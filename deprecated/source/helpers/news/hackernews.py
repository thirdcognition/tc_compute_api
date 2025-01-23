import datetime
import json
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import feedparser
from source.models.data.web_source import WebSource


class HackerNewsFeedType(str, Enum):
    NEWEST = "newest"
    NEWCOMMENTS = "newcomments"
    FRONT_PAGE = "frontpage"
    BEST_COMMENTS = "bestcomments"
    ASK = "ask"
    SHOW = "show"
    POLLS = "polls"
    JOBS = "jobs"
    WHOISHIRING = "whoishiring"


class HackerNewsConfig(BaseModel):
    feed_type: HackerNewsFeedType
    query: Optional[str] = None
    points: Optional[int] = None
    comments: Optional[int] = None
    articles: Optional[int] = 5

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


def construct_hackernews_feed_url(config: HackerNewsConfig) -> str:
    base_url = f"https://hnrss.org/{config.feed_type.value}"

    print(f"HackerNews: Constructing feed URL for feed type: {config.feed_type}")
    if (
        config.feed_type
        in {HackerNewsFeedType.NEWCOMMENTS, HackerNewsFeedType.BEST_COMMENTS}
        and config.points
    ):
        raise ValueError(
            "The 'points' parameter is not supported for the selected feed type."
        )

    params = []

    if config.query:
        params.append(f"q={config.query}")
    if config.points:
        params.append(f"points={config.points}")
    if config.comments:
        params.append(f"comments={config.comments}")

    if params:
        return f"{base_url}?" + "&".join(params)
    return base_url


def fetch_hackernews_items(config: HackerNewsConfig) -> List[WebSource]:
    feed_url = construct_hackernews_feed_url(config)
    print(f"HackerNews: Fetching HackerNews items from URL: {feed_url}")
    feed = feedparser.parse(feed_url)
    print(f"HackerNews: Number of items fetched: {len(feed.entries)}")

    news_items = []
    for entry in feed.entries[: config.articles]:
        news_item = WebSource(
            title=entry.title,
            source="Hacker News",
            original_source=entry.link,
            description=entry.summary,
            image=None,
            publish_date=(
                datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                if hasattr(entry, "published") and entry.published
                else None
            ),
            categories=[],
            lang="EN",
        )
        news_items.append(news_item)

    return news_items
