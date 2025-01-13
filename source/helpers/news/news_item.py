from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class NewsItem(BaseModel):
    title: str
    original_source: HttpUrl
    resolved_source: Optional[HttpUrl] = None
    source: str
    source_id: Optional[str] = None
    description: Optional[str] = None
    original_content: Optional[str] = None
    formatted_content: Optional[str] = None
    image: Optional[HttpUrl] = None
    publish_date: Optional[datetime] = None
    categories: Optional[List[str]] = Field(default_factory=list)
    linked_items: Optional[List[str]] = Field(default_factory=list)
