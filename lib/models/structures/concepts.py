from typing import List, Optional
from pydantic import BaseModel, Field
from lib.helpers.shared import get_item_str


class ConceptData(BaseModel):
    id: str = Field(
        description="An human readable id for this concept using letters and _",
        title="Id",
    )
    parent_id: Optional[str] = Field(
        description="An human readable id for the parent concept using letters and _",
        title="Parent Id",
    )
    title: str = Field(
        description="A human readable title for this concept", title="Title"
    )
    summary: str = Field(
        description="A summary of all contents related to this concept",
        title="Summary",
        default=None,
    )
    content: str = Field(
        description="Detailed and descriptive content in written format based on the context and identified concept. Should contain all relevant information in a readable format.",
        title="Contents",
    )


class ConceptStructure(BaseModel):
    id: str = Field(
        description="Concept ID",
        title="Id",
    )
    children: List["ConceptStructure"] = Field(
        description="A list of children using the defined cyclical structure of ConceptStructure(id, children: List[ConceptStructure], joined: List[str]).",
        title="Children",
    )
    joined: List[str] = Field(
        description="A list of Concept IDs that have been used to build the concept.",
        title="Combined concept IDs",
    )


class ConceptStructureList(BaseModel):
    structure: List[ConceptStructure] = Field(
        description="A list of concepts identified in the context", title="Concepts"
    )


class ConceptList(BaseModel):
    concepts: List[ConceptData] = Field(
        description="A list of concepts identified in the context", title="Concepts"
    )


def get_concept_str(
    concepts: List, one_liner=False, as_json=True, as_array=True, as_tags=False
):
    key_names = [
        "id",
        "parent_id",
        "title",
        "summary",
        "content",
        "references",
        "taxonomy",
    ]
    if one_liner:
        select_keys = [
            "id",
            "parent_id",
            "title",
            "summary",
            "references",
            "taxonomy",
        ]
    else:
        select_keys = None

    return get_item_str(
        concepts,
        as_json=as_json,
        as_array=as_array,
        as_tags=as_tags,
        key_names=key_names,
        select_keys=select_keys,
        one_liner=one_liner,
    )
