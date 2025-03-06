import json
from typing import List, Optional
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    title: str = Field(..., title="Title", description="Title for the article")
    topic: str = Field(..., title="Topic", description="Generic topic of the article.")
    subject: Optional[str] = Field(
        None, title="Subject", description="Detailed subject of the article."
    )
    description: str = Field(
        ..., title="Description", description="Synopsis for the article."
    )
    summary: str = Field(
        ..., title="Summary", description="Brief summary of the context."
    )
    article: str = Field(
        ..., title="Article", description="Article based on the provided context."
    )
    lang: str = Field(
        ..., title="Language", description="An ISO code for the language."
    )
    image: Optional[str] = Field(
        None,
        title="Image",
        description="URL to a hero image which is defined in the context. If context specifies no images, return as None.",
    )
    categories: Optional[List[str]] = Field(
        title="Categories",
        description="List of categories based on the context. Must use the defined available category IDs.",
        min_length=1,
        default_factory=list,
    )

    def __str__(self) -> str:
        return (
            f"NewsArticle:\\n"
            f"Title: {self.title}\\n"
            f"Topic: {self.topic}\\n"
            f"Summary: {self.summary}"
        )

    def to_json(self) -> str:
        """
        Convert the NewsArticle instance to a compact JSON string using Pydantic v2 serialization.
        """
        data = self.model_dump(mode="json", exclude_none=True)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def from_json(json_str: str) -> "NewsArticle":
        """
        Deserialize a JSON string into a NewsArticle instance using Pydantic v2 deserialization.
        """
        data = json.loads(json_str)
        return NewsArticle.model_validate(data)
