import datetime
import json
import re
from typing import List, Optional, Union
from pydantic import BaseModel
from enum import Enum
import feedparser
from pygooglenews import GoogleNews
from supabase import Client
from source.helpers.resolve_url import LinkResolver, parse_publish_date
from source.models.data.user import UserIDs
from source.models.data.web_source import WebSource


# Google News
class GoogleNewsConfig(BaseModel):
    lang: Optional[str] = "en"
    country: Optional[str] = "US"
    topic: Optional[Union[str, List[str]]] = None
    query: Optional[str] = None
    location: Optional[Union[str, List[str]]] = None
    since: Optional[str] = "1d"
    articles: Optional[int] = 5

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


def parse_since_value(since_value):
    print(f"GoogleNews: Parsing since value: {since_value}")
    pattern = r"(\d+)([hdm])"
    matches = re.findall(pattern, since_value)

    total_timedelta = datetime.timedelta()

    for amount, unit in matches:
        time_amount = int(amount)

        if unit == "h":
            total_timedelta += datetime.timedelta(hours=time_amount)
        elif unit == "d":
            total_timedelta += datetime.timedelta(days=time_amount)
        elif unit == "m":
            total_timedelta += datetime.timedelta(days=(time_amount * 30.44))

    return total_timedelta


def create_web_source(
    entry, source: str, lang: str, original_source: Optional[str] = None
) -> WebSource | None:
    """
    Helper function to create a WebSource object from an entry.
    """
    try:
        result = WebSource(
            title=entry.title,
            source=source,
            original_source=original_source or entry.link,
            description=getattr(entry, "summary", None),
            image=(
                entry.enclosures[0].href
                if hasattr(entry, "enclosures") and entry.enclosures
                else None
            ),
            publish_date=(
                parse_publish_date(entry.published.replace("GMT", "+0000"))
                if hasattr(entry, "published") and entry.published
                else None
            ),
            categories=(
                [category.term for category in entry.tags]
                if hasattr(entry, "tags")
                else []
            ),
            lang=lang,
        )
        return result
    except Exception as e:
        print(f"{source}: Issue with {original_source or entry.link} - {e}")


def fetch_google_news_items(config: GoogleNewsConfig) -> List[WebSource]:
    print(f"GoogleNews: Fetching news items with config: {config!r}")
    gn = GoogleNews(lang=config.lang, country=config.country)
    time_span = parse_since_value(config.since)

    print(f"GoogleNews: Time span for news items: {time_span}")
    if config.query:
        print(f"GoogleNews: Searching news with query: {config.query}")
        news = gn.search(config.query, when=config.since)
    elif config.location:
        if isinstance(config.location, list):
            news = gn.geo_multiple_headlines(config.location)
        else:
            news = gn.geo_headlines(config.location)
    elif config.topic:
        if isinstance(config.topic, list):
            news = gn.topic_multiple_headlines(config.topic, time_span=time_span)
        else:
            news = gn.topic_headlines(config.topic)
    else:
        news = gn.top_news()

    print(f"GoogleNews: Number of news entries fetched: {len(news['entries'])}")
    news_items = []
    for entry in news["entries"]:
        print(f"GoogleNews: Processing news entry: {entry.title}")
        news_item = create_web_source(entry, source="Google News", lang=config.lang)
        if news_item is not None:
            news_items.append(news_item)

    return news_items


# Hacker News
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
        news_item = create_web_source(entry, source="Hacker News", lang="EN")
        if news_item is not None:
            news_items.append(news_item)

    return news_items


# TechCrunch
class TechCrunchNewsConfig(BaseModel):
    articles: int


def fetch_techcrunch_news_items(config: TechCrunchNewsConfig) -> List[WebSource]:
    feed_url = "https://techcrunch.com/feed/"

    print(f"TechCrunch: Fetching TechCrunch news items from URL: {feed_url}")
    feed = feedparser.parse(feed_url)
    print(f"TechCrunch: Number of items fetched: {len(feed.entries)}")

    news_items = []
    for entry in feed.entries[: config.articles]:
        news_item = create_web_source(entry, source="TechCrunch", lang="EN")
        if news_item is not None:
            news_items.append(news_item)

    return news_items


# Yle
class YleFeedType(str, Enum):
    MAJOR_HEADLINES = "majorHeadlines"
    MOST_READ = "mostRead"


class YleNewsConfig(BaseModel):
    type: YleFeedType
    articles: int


def fetch_yle_news_items(config: YleNewsConfig) -> List[WebSource]:
    feed_url = f"https://feeds.yle.fi/uutiset/v1/{config.type.value}/YLE_UUTISET.rss"

    print(f"Yle: Fetching Yle news items from URL: {feed_url}")
    feed = feedparser.parse(feed_url)
    print(f"Yle: Number of items fetched: {len(feed.entries)}")

    news_items = []
    for entry in feed.entries:
        news_item = create_web_source(entry, source="Yle", lang="FI")
        if news_item is not None:
            news_items.append(news_item)

    return news_items


def fetch_urls_items(urls: List[str]) -> List[WebSource]:
    # Initialize the LinkResolver
    resolver = LinkResolver(reformat_text=True)
    news_items = []

    for url in urls:
        try:
            url_results = resolver.resolve_url(url)
            news_item = WebSource(
                title=url_results.title,
                source="url",
                original_source=url,
                description=url_results.description,
                image=url_results.image,
                publish_date=url_results.publish_date,
                categories=url_results.categories,
                lang=url_results.lang,
            )
            news_items.append(news_item)
        except Exception as e:
            print(f"Failed to resolve {url}: {e}")

    resolver.close()
    return news_items


def fetch_links(
    supabase: Client,
    sources: List[
        Union[
            str,
            List[str],
            GoogleNewsConfig,
            HackerNewsConfig,
            TechCrunchNewsConfig,
            YleNewsConfig,
        ]
    ],
    user_ids: UserIDs = None,
) -> List["WebSource"]:
    print(f"Fetching links for sources: {sources}")
    all_resolved_links = []
    for source in sources:
        urls = None
        if isinstance(source, str):
            # Handle single URL directly
            print(f"Handling single URL: {source}")
            urls = [source]
        elif isinstance(source, list) and all(isinstance(url, str) for url in source):
            # Handle list of URLs
            print(f"Handling list of URLs: {source}")
            urls = source

        if urls is not None:
            # Use fetch_urls_items and fetch_url_links to resolve URLs
            print(f"Fetching URL items for: {urls}")
            items = fetch_urls_items(urls)
        elif isinstance(source, GoogleNewsConfig):
            print(f"Fetching Google News items for config: {source}")
            items = fetch_google_news_items(source)
        elif isinstance(source, HackerNewsConfig):
            print(f"Fetching HackerNews items for config: {source}")
            items = fetch_hackernews_items(source)
        elif isinstance(source, TechCrunchNewsConfig):
            print(f"Fetching TechCrunch news items for config: {source}")
            items = fetch_techcrunch_news_items(source)
        elif isinstance(source, YleNewsConfig):
            print(f"Fetching Yle news items for config: {source}")
            items = fetch_yle_news_items(source)
        else:
            continue

        resolved_count = 0
        for item in items:
            print(f"news count {resolved_count=} {source.articles=}")
            if urls is None and resolved_count >= source.articles:
                break
            print(f"Resolving and storing link for item: {item.title}")
            if item.resolve_and_store_link(supabase, user_ids):
                all_resolved_links.append(item)
                resolved_count += 1

    print(f"Total resolved links: {len(all_resolved_links)}")
    return all_resolved_links
