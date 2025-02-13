import datetime
import json
import re
import time
from typing import List, Optional, Type, Union

from celery import group
from celery.result import AsyncResult
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
from source.tasks.web_sources import generate_resolve_tasks_for_websources


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
    tokens: tuple = None,
) -> List[WebSourceCollection | WebSource]:
    max_items = int(max_items)
    print(f"Fetch links: Fetching links for sources ({max_items}): {sources}")
    all_resolved_links: List[WebSourceCollection | WebSource] = []
    all_items: List[WebSource] = []
    for source in sources:
        urls = None
        try:
            if isinstance(source, str):
                # Handle single URL directly
                print(f"Fetch links: Handling single URL: {source}")
                urls = [source]
            elif isinstance(source, list) and all(
                isinstance(url, str) for url in source
            ):
                # Handle list of URLs
                print(f"Fetch links: Handling list of URLs: {source}")
                urls = source

            if urls is not None:
                # Use fetch_urls_items and fetch_url_links to resolve URLs
                print(f"Fetch links: Fetching URL items for: {urls}")
                items = fetch_urls_items(urls)
            elif isinstance(source, GoogleNewsConfig):
                print(f"Fetch links: Fetching Google News items for config: {source}")
                items = fetch_google_news_items(source)
            elif isinstance(source, HackerNewsConfig):
                print(f"Fetch links: Fetching HackerNews items for config: {source}")
                items = fetch_hackernews_items(source)
            elif isinstance(source, TechCrunchNewsConfig):
                print(
                    f"Fetch links: Fetching TechCrunch news items for config: {source}"
                )
                items = fetch_techcrunch_news_items(source)
            elif isinstance(source, YleNewsConfig):
                print(f"Fetch links: Fetching Yle news items for config: {source}")
                items = fetch_yle_news_items(source)
            else:
                continue

            all_items += items
        except Exception as e:
            print(f"Fetch links: Unable to fetch source {e=} \n\n {source=}")

    resolve_items: List[WebSourceCollection | WebSource] = None
    if len(all_items) > max_items:
        resolve_items = group_rss_items(all_items, guidance, min_amount=max_items)
    else:
        resolve_items = [
            WebSourceCollection(web_sources=[item], title=item.title)
            for item in all_items
        ]

    if not dry_run:
        # Initialize variables
        successful_results = []
        start_index = 0  # Start index for batching

        while len(successful_results) < max_items and start_index < len(resolve_items):
            print(
                f"Fetch links: Starting batch processing with {max_items=}, starting from {start_index=}"
            )
            batch_tasks = []
            task_mapping = []  # To track which item each task corresponds to
            collection_task_counts = (
                {}
            )  # To track the number of tasks for each WebSourceCollection
            collection_item_map = {}  # Map to track items by their keys

            end_index = min(start_index + max_items, len(resolve_items))
            print(
                f"Fetch links: Collecting tasks for items: start_index={start_index}, end_index={end_index}"
            )
            for idx, item in enumerate(
                resolve_items[start_index:end_index], start=start_index
            ):
                print(f"Fetch links: Processing item at index {idx}: {item}")
                if isinstance(item, WebSourceCollection):
                    collection_key = (item.title, item.max_amount)
                    tasks = item.generate_tasks(tokens, user_ids)
                    batch_tasks.extend(tasks)
                    collection_task_counts[collection_key] = len(
                        tasks
                    )  # Track the number of tasks
                    collection_item_map[
                        collection_key
                    ] = item  # Map the key to the item
                    task_mapping.extend(
                        [collection_key] * len(tasks)
                    )  # Map each task to the collection
                else:
                    standalone_task = generate_resolve_tasks_for_websources(
                        [item], tokens, user_ids
                    )[0]
                    batch_tasks.append(standalone_task)
                    task_mapping.append(item)  # Map the task to the standalone item

            # Group and execute the batch of tasks
            if batch_tasks:
                print(f"Fetch links: Generated {len(batch_tasks)} tasks for the batch")
                task_group = group(batch_tasks)
                print("Fetch links: Executing task group asynchronously")
                async_result: AsyncResult = task_group.apply_async()

                start_time = time.time()
                timeout = 15 * 60
                elapsed_time = 0

                # Poll for task completion without blocking
                while not async_result.ready() and elapsed_time < timeout:
                    elapsed_time = time.time() - start_time
                    print(
                        f"Fetch links: Waiting for tasks to complete ({elapsed_time:.2f}s)..."
                    )
                    time.sleep(30)  # Sleep for 5 seconds to avoid busy-waiting

                # Process results asynchronously
                if async_result.successful():
                    print("Fetch links: Tasks completed. Retrieving results...")
                    task_results = async_result.get(disable_sync_subtasks=False)
                    print(
                        f"Fetch links: Retrieved {len(task_results)} results from the batch"
                    )

                    # Process results
                    result_index = 0
                    for item in resolve_items[start_index:end_index]:
                        if len(successful_results) >= max_items:
                            break  # Stop if max_items successful results are achieved
                        if isinstance(item, WebSourceCollection):
                            collection_key = (item.title, item.max_amount)
                            task_count = collection_task_counts[collection_key]
                            collection_results = task_results[
                                result_index : result_index + task_count
                            ]
                            result_index += task_count
                            if any(
                                collection_results
                            ):  # Check if all tasks in the group were successful
                                item.load_from_supabase(supabase=supabase)
                                successful_results.append(item)
                        else:
                            if task_results[
                                result_index
                            ]:  # Check if the standalone task was successful
                                item.load_from_supabase(supabase=supabase)
                                successful_results.append(item)
                            result_index += 1
                else:
                    print("Fetch links: Some tasks failed. Handling errors...")

            start_index = end_index

        # Add successful results to all_resolved_links
        all_resolved_links.extend(successful_results)
    else:
        all_resolved_links.extend(resolve_items[:max_items])

    print(f"Fetch links: Total resolved links: {len(all_resolved_links)}")
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
