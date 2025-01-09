from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime

# Define a Pydantic model for the news item


class NewsItem(BaseModel):
    title: str
    original_source: HttpUrl
    resolved_source: HttpUrl
    source: str
    description: Optional[str]
    original_content: Optional[str]
    formatted_content: Optional[str]
    image: Optional[HttpUrl]
    publish_date: Optional[datetime]
    categories: Optional[List[str]]
    linked_items: Optional[List[str]]
