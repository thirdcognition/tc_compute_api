import json
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Union


class GooglenewsFeedType(str, Enum):
    SEARCH = "search"
    TOPIC = "topic"
    TOP_TOPICS = "top_topics"
    LOCATION = "location"


class GoogleNewsConfig(BaseModel):
    feed_type: Optional[GooglenewsFeedType] = None
    lang: Optional[str] = "en"
    country: Optional[str] = "US"
    topic: Optional[Union[str, List[str]]] = None
    query: Optional[str] = None
    location: Optional[Union[str, List[str]]] = None
    since: Optional[str] = "1d"
    articles: Optional[int] = None

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


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
    articles: Optional[int] = None

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


class TechCrunchNewsConfig(BaseModel):
    articles: Optional[int] = None


class YleFeedType(str, Enum):
    MAJOR_HEADLINES = "majorHeadlines"
    MOST_READ = "mostRead"
    TOPICS = "topics"


class YleLanguage(str, Enum):
    EN = "en"
    FI = "fi"


class YleNewsConfig(BaseModel):
    feed_type: Optional[YleFeedType] = None
    type: Optional[YleFeedType] = None
    articles: Optional[int] = None
    topics: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    lang: Optional[YleLanguage] = YleLanguage.FI
