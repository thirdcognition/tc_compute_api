import datetime
import json
import re
from typing import List, Optional, Tuple, Union
from pydantic import BaseModel
from pygooglenews import GoogleNews

# from source.helpers.shared import pretty_print
from source.models.config.logging import logger
from source.helpers.resolve_url import LinkResolver
from source.models.data.user import UserIDs


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


def fetch_google_news_links(
    config: GoogleNewsConfig, user_ids: UserIDs = None
) -> List[Tuple[str, str]]:
    gn = GoogleNews(lang=config.lang, country=config.country)
    time_span = parse_since_value(config.since)

    if config.query:
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

    # Initialize the LinkResolver
    resolver = LinkResolver()

    # Resolve each URL and fetch content
    resolved_links = []
    entries_iter = iter(news["entries"])
    resolved_count = 0

    while resolved_count < config.articles:
        try:
            entry = next(entries_iter)
            resolved_url, content = resolver.resolve_url(entry.link)
            resolved_links.append((resolved_url, content))
            resolved_count += 1
        except StopIteration:
            logger.info("No more entries to process.")
            break
        except Exception as e:
            logger.info(f"Failed to resolve {entry.link}: {e}")

    # Close the resolver
    resolver.close()

    return resolved_links
