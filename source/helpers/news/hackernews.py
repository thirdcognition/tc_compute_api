import datetime
import json
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import feedparser
from supabase import Client

from source.models.data.news_item import NewsItem
from source.helpers.resolve_url import LinkResolver
from source.models.data.user import UserIDs


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


def fetch_hackernews_items(config: HackerNewsConfig) -> List[NewsItem]:
    feed_url = construct_hackernews_feed_url(config)
    print(f"HackerNews: Fetching HackerNews items from URL: {feed_url}")
    feed = feedparser.parse(feed_url)
    print(f"HackerNews: Number of items fetched: {len(feed.entries)}")

    news_items = []
    for entry in feed.entries[: config.articles]:
        news_item = NewsItem(
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


def fetch_hackernews_links(
    supabase: Client, config: HackerNewsConfig, user_ids: UserIDs = None
) -> List[NewsItem]:
    news_items = fetch_hackernews_items(config)
    resolver = LinkResolver(reformat_text=True)

    resolved_links = []
    resolved_count = 0

    print(f"HackerNews: Resolving links for {len(news_items)} news items")
    for item in news_items:
        if resolved_count >= config.articles:
            break
        if item.check_if_exists_sync(supabase):
            print(f"HackerNews: Item exists in Supabase: {item.title}")
            item.load_from_supabase_sync(supabase)
            resolved_links.append(item)
            resolved_count += 1
        else:
            try:
                print(f"HackerNews: Resolving URL for item: {item.title}")
                resolved_url, content, formatted_content = resolver.resolve_url(
                    str(item.original_source)
                )
                if len(content) > 500:
                    item.resolved_source = resolved_url
                    item.original_content = content
                    item.formatted_content = formatted_content
                    if user_ids is not None:
                        item.owner_id = user_ids.user_id
                        item.organization_id = user_ids.organization_id
                    print(f"HackerNews: Resolved URL: {resolved_url}")
                    item.create_and_save_source_sync(supabase)
                    resolved_links.append(item)
                    resolved_count += 1
                else:
                    print(
                        f"HackerNews: Resolved content length too short {len(content)}"
                    )
            except Exception as e:
                print(f"HackerNews: Failed to resolve {item.original_source}: {e}")

    resolver.close()
    return resolved_links
