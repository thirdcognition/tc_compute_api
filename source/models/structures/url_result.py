from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class UrlResult(BaseModel):
    orig_url: Optional[str] = None
    resolved_url: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    image_data: Optional[list[dict]] = None
    publish_date: Optional[datetime] = None
    categories: Optional[List[str]] = None
    lang: Optional[str] = None
    # original_content: Optional[str] = None
    metadata: Optional[str] = None
    human_readable_content: Optional[str] = None

    def __str__(self):
        return f"Original URL: {self.orig_url}, Resolved URL: {self.resolved_url}, Title: {self.title}, Source: {self.source}, Description: {self.description}, Image: {self.image}, Publish Date: {self.publish_date}, Categories: {self.categories}, Language: {self.lang}"
