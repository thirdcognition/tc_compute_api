import datetime
import json
import re
from typing import List, Optional, Type, Union

import feedparser
from langsmith import traceable
from pygooglenews import GoogleNews
from supabase import Client
from source.helpers.resolve_url import LinkResolver, parse_publish_date
from source.llm_exec.websource_exec import group_rss_items
from source.models.data.user import UserIDs
from source.models.data.web_source import WebSource
from source.models.structures.panel import PanelRequestData
from source.models.structures.sources import (
    GoogleNewsConfig,
    GooglenewsFeedType,
    HackerNewsConfig,
    HackerNewsFeedType,
    TechCrunchNewsConfig,
    YleFeedType,
    YleLanguage,
    YleNewsConfig,
)
from source.models.structures.web_source_structure import WebSourceCollection


# Google News


def parse_since_value(since_value):
    if since_value is None:
        return None
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
    entry, source: str, lang: str, original_source: Optional[str] = None, category=None
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
                if category is None
                else [category]
            ),
            lang=lang,
            rss_item=entry,
        )
        return result
    except Exception as e:
        print(f"{source}: Issue with {original_source or entry.link} - {e}")


def fetch_google_news_items(config: GoogleNewsConfig) -> List[WebSource]:
    print(f"GoogleNews: Fetching news items with config: {config!r}")
    gn = GoogleNews(lang=config.lang, country=config.country)
    time_span = parse_since_value(config.since)

    print(f"GoogleNews: Time span for news items: {time_span}")
    if config.feed_type == GooglenewsFeedType.SEARCH or config.query:
        config.feed_type = GooglenewsFeedType.SEARCH
        print(f"GoogleNews: Searching news with query: {config.query}")
        news = gn.search(config.query, when=config.since)
    elif config.feed_type == GooglenewsFeedType.LOCATION or config.location:
        config.feed_type = GooglenewsFeedType.LOCATION
        if isinstance(config.location, list):
            news = gn.geo_multiple_headlines(config.location)
        else:
            news = gn.geo_headlines(config.location)
    elif config.feed_type == GooglenewsFeedType.TOPIC or config.topic:
        config.feed_type = GooglenewsFeedType.TOPIC
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


def fetch_yle_news_items(config: YleNewsConfig) -> List[WebSource]:
    source = "YLE_UUTISET" if config.lang == YleLanguage.FI else "YLE_NEWS"
    feed_url = f"https://feeds.yle.fi/uutiset/v1/{(config.feed_type or config.type).value}/YLE_UUTISET.rss"

    if config.feed_type == YleFeedType.TOPICS:
        feed_url = f"https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds={source}"
        concepts = (config.topics or []) + (config.locations or [])
        if len(concepts) > 0:
            feed_url += "&concepts=" + ",".join(concepts)

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


@traceable(
    run_type="llm",
    name="Fetch transcript sources",
)
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
    dry_run: bool = False,
    guidance: str = None,
    max_items=5,
) -> List[WebSourceCollection | WebSource]:
    max_items = int(max_items)
    print(f"Fetching links for sources ({max_items}): {sources}")
    all_resolved_links: List[WebSourceCollection | WebSource] = []
    all_items: List[WebSource] = []
    for source in sources:
        urls = None
        try:
            if isinstance(source, str):
                # Handle single URL directly
                print(f"Handling single URL: {source}")
                urls = [source]
            elif isinstance(source, list) and all(
                isinstance(url, str) for url in source
            ):
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

            all_items += items
        except Exception as e:
            print(f"Unable to fetch source {e=} \n\n {source=}")

    resolved_count = 0
    resolve_items: List[WebSourceCollection] = None
    if len(all_items) > max_items:
        resolve_items = group_rss_items(all_items, guidance, min_amount=max_items)
    else:
        resolve_items = [
            WebSourceCollection(web_sources=[item], title=item.title)
            for item in all_items
        ]

    if not dry_run:
        for item in resolve_items:
            print(f"Resolving and storing link for item: {item.title}")
            if item.resolve_and_store_link(supabase, user_ids):
                all_resolved_links.append(item)
                resolved_count += 1
            if resolved_count >= max_items:
                break

    else:
        all_resolved_links.extend(resolve_items[:max_items])

    print(f"Total resolved links: {len(all_resolved_links)}")
    return all_resolved_links


def deduplicate_and_validate_configs(
    configs_json: List[dict],
    config_class: Union[
        Type[GoogleNewsConfig],
        Type[YleNewsConfig],
        Type[TechCrunchNewsConfig],
        Type[HackerNewsConfig],
    ],
) -> List:
    unique_configs = list(
        {
            json.dumps(
                (
                    config.model_dump(mode="json")
                    if isinstance(config, config_class)
                    else config
                ),
                sort_keys=True,
            )
            for config in configs_json
        }
    )
    return [
        config_class.model_validate(json.loads(config)) for config in unique_configs
    ]


def manage_news_sources(
    request_data: PanelRequestData = PanelRequestData(), metadata: dict = {}
):
    sources = []

    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("google_news", []) + (request_data.google_news or []),
            GoogleNewsConfig,
        )
    )
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("yle_news", []) + (request_data.yle_news or []), YleNewsConfig
        )
    )
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("techcrunch_news", []) + (request_data.techcrunch_news or []),
            TechCrunchNewsConfig,
        )
    )
    sources.extend(
        deduplicate_and_validate_configs(
            metadata.get("hackernews", []) + (request_data.hackernews or []),
            HackerNewsConfig,
        )
    )

    return sources
