from datetime import datetime
import hashlib
import json
from typing import Any, Generator, List, Optional, Type, TypeVar, Union
from supabase import AsyncClient, Client
from source.llm_exec.news_exec import web_source_article_builder_sync
from source.models.structures.news_article import NewsArticle
from source.tasks.web_sources import generate_resolve_tasks_for_websources
from source.models.structures.user import UserIDs
from source.models.structures.web_source import WebSource
from source.models.supabase.panel import PanelTranscript, PanelTranscriptSourceReference
from source.models.supabase.sources import SourceModel, SourceRelationshipModel
from pydantic import BaseModel, Field, field_validator, ValidationError

T = TypeVar("T")  # Generic type for model validation


def list_validator(
    value: Any, expected_type: Type[T], model_validate_func: callable, field_name: str
) -> List[T]:
    if value is None:
        return value

    if isinstance(value, str):  # Detect and convert JSON string
        try:
            print(f"Deserializing: {field_name}={value}")
            value = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON for {field_name}: {repr(e)}")

    if isinstance(value, Generator):  # Detect and convert generator
        value = list(value)

    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list, got {type(value)}")

    validated_items = []
    for item in value:
        if isinstance(item, expected_type):
            validated_items.append(item)
        elif isinstance(item, dict):
            try:
                validated_items.append(model_validate_func(item))
            except ValidationError as e:
                raise ValueError(
                    f"Invalid {expected_type.__name__} data in {field_name}: {e}"
                )
        else:
            raise TypeError(
                f"{field_name} must be a list of {expected_type.__name__} objects or dictionaries, got {type(item)}"
            )
    return validated_items


class WebSourceCollection(BaseModel):
    source_model: Optional[SourceModel] = Field(
        default=None, description="Optional SourceModel."
    )
    relationships: Optional[List[SourceRelationshipModel]] = Field(
        default=None, description="Optional list of SourceRelationshipModel objects."
    )

    @field_validator("relationships", mode="before")
    def validate_relationships(cls, value):
        return list_validator(
            value,
            expected_type=SourceRelationshipModel,
            model_validate_func=SourceRelationshipModel.model_validate,
            field_name="relationships",
        )

    web_sources: Optional[List[WebSource]] = Field(
        default=None, description="Optional list of WebSource objects."
    )

    @field_validator("web_sources", mode="before")
    def validate_web_sources(cls, value):
        return list_validator(
            value,
            expected_type=WebSource,
            model_validate_func=WebSource.model_validate,
            field_name="web_sources",
        )

    source_id: Optional[str] = None
    title: Optional[str] = Field(default=None, description="Title of the collection.")
    topic: Optional[str] = None
    description: Optional[str] = Field(
        default=None, description="Description for collection."
    )
    categories: Optional[List[str]] = Field(default_factory=list)
    max_amount: Optional[int] = Field(
        default=None, description="Maximum number of WebSource objects."
    )
    main_item: bool = Field(
        default=False, description="Indicates if this is the main item."
    )
    image: Optional[str] = Field(
        default=None, description="Image from the web sources."
    )
    article: Optional[NewsArticle] = Field(
        default=None, description="Article generated from the websources"
    )
    publish_date: Optional[datetime] = None
    organization_id: Optional[str] = Field(
        default=None, description="Organization ID associated with the collection."
    )
    lang: Optional[str] = None
    metadata: Optional[dict] = None
    owner_id: Optional[str] = Field(
        default=None, description="Owner ID associated with the collection."
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.web_sources:
            self.filter_sources()

    def short_id(self) -> str:
        """
        Generate a short form of source_model.id (UUID) or create an ID from title.

        :param title: The title to generate an ID from if source_model.id is not available.
        :return: A short id (first 8 characters of UUID) or hashed id from title.
        """
        if self.source_model and self.source_model.id:
            return str(self.source_model.id).split("-")[0]
        elif self.title:
            return hashlib.sha256(self.title.encode("utf-8")).hexdigest()[:8]
        return "unknown_id"

    def filter_sources(self):
        """
        Remove duplicate WebSource objects based on their sorting ID.
        """
        if self.web_sources:
            new_sources: dict[str, WebSource] = {}
            for source in self.web_sources:
                new_sources[source.get_sorting_id()] = source
            self.web_sources = list(new_sources.values())
            self.update_image()

    def add_web_source(self, web_source: WebSource):
        """
        Add a WebSource object to the collection.
        """
        self.web_sources.append(web_source)
        self.update_image()

    def update_image(self):
        """
        Update the image attribute with the first available image from the web_sources.
        """
        for web_source in self.web_sources:
            if web_source.image:
                self.image = web_source.image
                return
        self.image = None

    def short_string(self, key: Optional[str] = None, reverse: bool = False) -> str:
        """
        Return all WebSource objects as a single string in the specified order.

        :param key: The attribute of WebSource to sort by (e.g., 'title', 'publish_date').
        :param reverse: Whether to sort in descending order.
        :return: A single string representation of all WebSource objects.
        """
        if key:
            # Sort the web sources based on the specified key
            self.web_sources.sort(
                key=lambda ws: getattr(ws, key, None), reverse=reverse
            )

        ret_str = f"ID({self.short_id()}) - {self.title}:\n\n"

        # Concatenate the string representations of all WebSource objects
        if self.max_amount is None:
            ret_str += "\n\n".join(
                [ws.short_string() for ws in self.web_sources if ws.short_string()]
            )
        else:
            ret_str += "\n\n".join(
                [
                    ws.short_string()
                    for ws in self.web_sources[: self.max_amount]
                    if ws.short_string()
                ]
            )
        return ret_str

    def find_match(
        self, search_id: str
    ) -> Optional[Union["WebSourceCollection", WebSource]]:
        """
        Recursively search for a matching source within the collection or its children
        by `search_id` against `short_id` or `source_model.id`.

        :param search_id: The string to search for in `short_id` or `source_model.id`.
        :return: The matching WebSourceCollection or WebSource instance if found, else None.
        """

        search_id_cleaned = str(search_id).strip()
        if search_id_cleaned.lower().startswith("id(") and search_id_cleaned.endswith(
            ")"
        ):
            search_id_cleaned = search_id_cleaned[3:-1].strip()

        if self.short_id() == str(search_id_cleaned) or (
            self.source_model and str(self.source_model.id) == str(search_id_cleaned)
        ):
            return self

        if self.web_sources:
            for web_source in self.web_sources:
                if hasattr(web_source, "find_match"):
                    result = web_source.find_match(search_id_cleaned)
                    if result:
                        return result

        return None

    def to_ordered_string(
        self, key: Optional[str] = None, reverse: bool = False
    ) -> str:
        """
        Return all WebSource objects as a single string in the specified order.

        :param key: The attribute of WebSource to sort by (e.g., 'title', 'publish_date').
        :param reverse: Whether to sort in descending order.
        :return: A single string representation of all WebSource objects.
        """
        if key:
            # Sort the web sources based on the specified key
            self.web_sources.sort(
                key=lambda ws: getattr(ws, key, None), reverse=reverse
            )

        # Concatenate the string representations of all WebSource objects
        if self.max_amount is None:
            return "\n\n".join([str(ws) for ws in self.web_sources if str(ws)])
        else:
            return "\n\n".join(
                [str(ws) for ws in self.web_sources[: self.max_amount] if str(ws)]
            )

    def resolve_and_store_link(self, supabase: Client, user_ids: UserIDs = None):
        resolved = False
        resolved_sources: List[WebSource] = []
        sources: List[WebSource] = None

        if user_ids and self.owner_id is None:
            self.organization_id = user_ids.organization_id
            self.owner_id = user_ids.user_id

        if self.max_amount is None:
            sources = self.web_sources
        else:
            sources = self.web_sources[: self.max_amount]

        for item in sources:
            if item.resolve_and_store_link(supabase, user_ids=user_ids):
                resolved = True
                resolved_sources.append(item)

        self.web_sources = resolved_sources

        if resolved:
            self.save_to_database_sync(supabase)

        return resolved

    async def load_from_supabase(self, supabase: AsyncClient):
        sources: List[WebSource] = None

        if self.max_amount is None:
            sources = self.web_sources
        else:
            sources = self.web_sources[: self.max_amount]

        for item in sources:
            item.load_from_supabase(supabase)

        self.web_sources = sources

        return sources

    def load_from_supabase_sync(self, supabase: Client):
        sources: List[WebSource] = None

        if self.max_amount is None:
            sources = self.web_sources
        else:
            sources = self.web_sources[: self.max_amount]

        for item in sources:
            item.load_from_supabase_sync(supabase)

        self.web_sources = sources

        return sources

    def get_url(self):
        urls = []
        for source in self.web_sources:
            url = (
                source.get_url()
                if isinstance(source, (WebSource, "WebSourceCollection"))
                else None
            )
            if isinstance(url, list):
                urls.extend(url)
            elif url:
                urls.append(url)

        return url

    def create_panel_transcript_source_reference_sync(
        self, supabase: Client, transcript: PanelTranscript, user_ids: UserIDs = None
    ):
        references = []
        # Ensure the source_model is set

        if self.owner_id is None and user_ids:
            self.owner_id = user_ids.user_id
            self.organization_id = user_ids.organization_id

        if not self.source_model:
            self.save_to_database_sync(supabase)

        # Create a source reference for the WebSourceCollection
        collection_reference = PanelTranscriptSourceReference(
            transcript_id=transcript.id,
            source_id=self.source_model.id,
            type="web_source_collection",
            data={
                "title": self.title,
                "image": str(self.image) if self.image else None,
                "publish_date": (
                    self.publish_date.isoformat() if self.publish_date else None
                ),
                "url": self.get_url(),
                "lang": self.lang,
            },
            is_public=True,
            owner_id=(
                self.owner_id
                if self.owner_id is not None
                else (user_ids.user_id if user_ids is not None else None)
            ),
            organization_id=(
                self.organization_id
                if self.organization_id is not None
                else (user_ids.organization_id if user_ids is not None else None)
            ),
        )
        collection_reference.create_sync(supabase)
        references.append(collection_reference)

        return references

    def generate_tasks(self, tokens, user_ids: UserIDs):
        """
        Generate and execute tasks for all WebSource items in the collection.

        :param supabase: The Supabase client instance.
        :param user_ids: User IDs for task execution.
        :return: Results of the executed tasks.
        """
        return generate_resolve_tasks_for_websources(self.web_sources, tokens, user_ids)

    def save_to_database_sync(self, supabase: Client):
        """
        Save the WebSourceCollection as a SourceModel in the database and
        establish relationships with its web sources in the source_relationship table.
        """
        # Save relationships between the collection and its web sources
        content_to_hash = "\n".join(
            (
                web_source.source_model.content_hash or str(self.article)
                if self.article
                else (
                    web_source.url_result.human_readable_content
                    if web_source.url_result
                    else web_source.title
                )
            )
            for web_source in self.web_sources
        )

        content_hash = (
            hashlib.sha256(content_to_hash.encode("utf-8")).hexdigest()
            if content_to_hash
            else None
        )

        if not self.image:
            self.update_image()

        common_data = {
            "max_amount": self.max_amount,
            "main_item": self.main_item,
            "image": self.image,
            "description": self.description,
            "article": self.article.model_dump() if self.article else None,
            "categories": self.categories,
        }
        common_metadata = {
            "image": str(self.image) if self.image else None,
            "publish_date": (
                self.publish_date.isoformat() if self.publish_date else None
            ),
            "children": [
                {
                    "image": source.image,
                    "title": source.title,
                    "publish_date": source.publish_date,
                    "url": source.resolved_source or source.original_source,
                    "source": source.source,
                }
                for source in self.web_sources
                if isinstance(source, WebSource)
            ],
        }

        # Save the collection as a source
        if self.source_model:
            # Update existing source_model fields
            self.source_model.title = self.title
            self.source_model.type = "collection"
            self.source_model.lang = self.lang
            self.source_model.content_hash = content_hash
            self.source_model.is_public = True
            self.source_model.data = common_data
            self.source_model.metadata = common_metadata
            self.source_model.owner_id = self.owner_id
            self.source_model.organization_id = self.organization_id
        else:
            self.source_model = SourceModel(
                title=self.title,
                is_public=True,
                type="collection",
                data=common_data,
                metadata=common_metadata,
                owner_id=self.owner_id,
                organization_id=self.organization_id,
            )

        self.source_model.content_hash = (
            hashlib.sha256(content_to_hash.encode("utf-8")).hexdigest()
            if content_to_hash
            else None
        )

        self.source_model.create_sync(supabase)

        self.save_relationships_to_database_sync(supabase)

    def save_relationships_to_database_sync(self, supabase: Client):
        relationships = []
        for web_source in self.web_sources:
            if web_source.source_model:
                relationships.append(
                    SourceRelationshipModel(
                        source_id=self.source_model.id,
                        related_source_id=web_source.source_model.id,
                        relationship_type="parent_child_link",
                        is_public=web_source.source_model.is_public,
                        owner_id=web_source.source_model.owner_id,
                        organization_id=web_source.source_model.organization_id,
                    )
                )
        self.relationships = relationships
        if len(relationships) > 0:
            # print(relationships)

            self.relationships = SourceRelationshipModel.upsert_to_supabase_sync(
                supabase, relationships
            )

    def load_from_database_sync(self, supabase: Client, collection_id: str):
        """
        Load a WebSourceCollection from the database using its source ID.
        """
        # Fetch the collection source
        if not self.source_model:
            self.source_model = SourceModel.fetch_from_supabase_sync(
                supabase, value=collection_id, id_column="id"
            )

        if not self.source_model:
            raise ValueError(f"No collection found with ID: {collection_id}")

        # Populate the collection fields
        if self.source_model.title:
            self.title = self.title or self.source_model.title
            self.source_id = self.source_id or str(self.source_model.id)
            self.max_amount = (
                self.source_model.data.get("max_amount") or self.max_amount
            )
            self.main_item = self.source_model.data.get("main_item") or self.main_item
            self.image = self.source_model.data.get("image") or self.image

        self.organization_id = self.organization_id or self.source_model.organization_id
        self.owner_id = self.organization_id or self.source_model.owner_id

        # Fetch relationships and populate web sources
        relationships: list[
            SourceRelationshipModel
        ] = SourceRelationshipModel.fetch_from_supabase_sync(
            supabase, value=collection_id, id_column="source_id"
        )
        self.relationships = relationships
        self.web_sources = []
        for relationship in relationships:
            related_source = SourceModel.fetch_from_supabase_sync(
                supabase, value=relationship.related_source_id, id_column="id"
            )
            if related_source:
                web_source = WebSource()
                web_source._update_from_(related_source)
                self.web_sources.append(web_source)

    def build_article(self):
        """
        Build an article for the collection by aggregating the url_results
        of all connected web_sources.
        """
        print("Building article for the collection using web_sources' url_results.")
        aggregated_content = ""
        for web_source in self.web_sources:
            if web_source.url_result and web_source.url_result.human_readable_content:
                aggregated_content += (
                    web_source.url_result.human_readable_content + "\n\n"
                )

        if aggregated_content:
            self.article = web_source_article_builder_sync(aggregated_content)

    def __str__(self):
        return self.to_ordered_string()

    @classmethod
    async def load_linked_sources_as_collection(
        cls, supabase: AsyncClient, source: str | WebSource
    ) -> "WebSourceCollection":
        """
        Load all linked instances of source and return them as a WebSourceCollection.

        :param supabase: The Supabase AsyncClient instance.
        :param source_id: The ID of the source to load linked items for.
        :return: A WebSourceCollection containing all linked WebSource instances.
        """
        # Fetch relationships where the source_id matches
        relationships: List[
            SourceRelationshipModel
        ] = await SourceRelationshipModel.fetch_from_supabase(
            supabase,
            value=source.source_id if isinstance(source, WebSource) else source,
            id_column="source_id",
        )

        if not relationships:
            return None

        # Fetch linked sources
        linked_sources = []
        for relationship in relationships:
            related_source_id = relationship.related_source_id
            source_model = await SourceModel.fetch_from_supabase(
                supabase, value=related_source_id, id_column="id"
            )
            if source_model:
                # Convert SourceModel to WebSource
                web_source = WebSource()
                web_source._update_from_(source_model)
                linked_sources.append(web_source)

        # Return as WebSourceCollection
        return WebSourceCollection(web_sources=linked_sources)
