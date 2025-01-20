import datetime
import json
import re
from typing import List, Optional, Union
from pydantic import BaseModel
from pygooglenews import GoogleNews

# from source.helpers.shared import pretty_print
from source.helpers.resolve_url import LinkResolver
from source.models.data.user import UserIDs
from source.models.data.news_item import NewsItem
from supabase import Client


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
    # Regular expression to match time units (e.g., 10h, 5d, 2m)
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
            # approx 30.44 days per month for timedelta from months
            total_timedelta += datetime.timedelta(days=(time_amount * 30.44))

    return total_timedelta


def fetch_google_news_items(config: GoogleNewsConfig) -> List[NewsItem]:
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
    # Extract news items
    news_items = []
    for entry in news["entries"]:
        print(f"GoogleNews: Processing news entry: {entry.title}")
        news_item = NewsItem(
            title=entry.title,
            source="Google News",
            original_source=entry.link,
            description=entry.summary,
            image=None,  # Google News entries may not have images
            publish_date=(
                datetime.datetime.strptime(
                    entry.published.replace("GMT", "+0000"), "%a, %d %b %Y %H:%M:%S %z"
                )
                if hasattr(entry, "published") and entry.published
                else None
            ),
            categories=(
                [category.term for category in entry.tags]
                if hasattr(entry, "tags")
                else []
            ),
            lang=config.lang,
        )
        news_items.append(news_item)

    return news_items


def fetch_google_news_links(
    supabase: Client, config: GoogleNewsConfig, user_ids: UserIDs = None
) -> List[NewsItem]:
    print("GoogleNews: Fetching Google News links")
    # Fetch news items using the existing function
    news_items = fetch_google_news_items(config)

    print("GoogleNews: Initializing LinkResolver")
    # Initialize the LinkResolver
    resolver = LinkResolver(reformat_text=True)

    # Check if each news item exists in the database
    resolved_links = []
    resolved_count = 0

    for item in news_items:
        print(f"GoogleNews: Checking if item exists in Supabase: {item.title}")
        if resolved_count >= config.articles:
            break
        if item.check_if_exists_sync(supabase):
            print(f"GoogleNews: Item exists in Supabase: {item.title}")
            item.load_from_supabase_sync(supabase)
            resolved_links.append(item)
            resolved_count += 1
        else:
            try:
                print(f"GoogleNews: Resolving URL for item: {item.title}")
                resolved_url, content, formatted_content = resolver.resolve_url(
                    str(item.original_source)
                )

                print(f"GoogleNews: Resolved URL: {resolved_url}")
                if len(content) > 500:
                    item.resolved_source = resolved_url
                    item.original_content = content
                    item.formatted_content = formatted_content
                    if user_ids is not None:
                        item.owner_id = user_ids.user_id
                        item.organization_id = user_ids.organization_id
                    item.create_and_save_source_sync(supabase)
                    resolved_links.append(item)
                    resolved_count += 1
                else:
                    print(
                        f"GoogleNews: Resolved content length too short {len(content)}"
                    )
            except Exception as e:
                print(f"GoogleNews: Failed to resolve {item.original_source}: {e}")

    print("GoogleNews: Closing LinkResolver")
    # Close the resolver
    resolver.close()

    return resolved_links
