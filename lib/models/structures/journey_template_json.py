from typing import List
from pydantic import BaseModel, Field


class JourneyTemplateChild(BaseModel):
    key: str = Field(description="Unique key for the child item")
    title: str = Field(description="Title of the child item")


class JourneyTemplateCategory(BaseModel):
    key: str = Field(description="Unique key for the category")
    title: str = Field(description="Title of the category")
    children: List[JourneyTemplateChild] = Field(description="List of child items")


class TemplateKeyToFileMapping(BaseModel):
    key: str = Field(description="Unique key for the file")
    file_path: str = Field(description="File path for the key")


class JourneyTemplateMapping(BaseModel):
    pairs: List[TemplateKeyToFileMapping] = Field(
        description="List of file and key mappings"
    )


class JourneyTemplateIndex(BaseModel):
    categories: List[JourneyTemplateCategory] = Field(description="List of categories")
