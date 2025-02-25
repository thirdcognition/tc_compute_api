import hashlib
import re
from typing import Any, List, Optional, Union
from bs4 import BeautifulSoup
from supabase.client import AsyncClient, Client

# from source.helpers.shared import pretty_print
from source.helpers.json_exportable_enum import JSONExportableEnum
from source.llm_exec.news_exec import web_source_article_builder_sync
from source.models.structures.url_result import UrlResult
from source.models.supabase.sources import SourceModel, SourceRelationshipModel
from pydantic import BaseModel, Field
from datetime import datetime
from source.models.supabase.panel import PanelTranscript, PanelTranscriptSourceReference
from source.helpers.resolve_url import LinkResolver
from source.models.structures.user import UserIDs

# from source.models.config.logging import logger
from source.prompts.web_source import NewsArticle


class ResolveState(str, JSONExportableEnum):
    FAILED = "failed"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


class WebSource(BaseModel):
    title: str
    topic: Optional[str] = None
    original_source: str
    resolved_source: Optional[str] = None
    source: str
    rss_source: Optional[str] = None
    source_id: Optional[str] = None
    source_model: Optional[SourceModel] = None
    description: Optional[str] = None
    original_content: Optional[str] = None
    url_result: Optional[UrlResult] = None
    article: Optional[NewsArticle] = None
    resolve_state: Optional[ResolveState] = ResolveState.UNRESOLVED
    image: Optional[str] = None
    publish_date: Optional[datetime] = None
    categories: Optional[List[str]] = Field(default_factory=list)
    linked_items: Optional[List[str]] = Field(default_factory=list)
    lang: Optional[str] = None
    metadata: Optional[dict] = None
    owner_id: Optional[str] = None
    organization_id: Optional[str] = None
    main_item: bool = False

    rss_item: Any = None

    _sorting_id: str = None

    def _verify_image(self, article_image) -> bool:
        """
        Check if the image from the article exists in any of the specified fields
        of self.url_result.
        """
        if not self.url_result:
            return False

        image_to_check = article_image
        if not image_to_check:
            return False

        # Check in various fields of UrlResult
        return any(
            [
                image_to_check in (self.url_result.image or ""),
                image_to_check in (self.url_result.metadata or ""),
                image_to_check in (self.url_result.original_content or ""),
                image_to_check in (self.url_result.human_readable_content or ""),
            ]
        )

    def _update_from_(self, obj: Union[UrlResult, NewsArticle, SourceModel]):
        """
        Update the fields of the WebSource instance based on the provided object.
        """
        if isinstance(obj, UrlResult):
            self.title = obj.title or self.title
            self.image = obj.image or self.image
            self.description = obj.description or self.description
            self.lang = obj.lang or self.lang
            self.categories = obj.categories or self.categories
            self.original_content = obj.human_readable_content or self.original_content
            self.resolved_source = obj.resolved_url or self.resolved_source
            self.source = obj.source or self.source
            self.publish_date = obj.publish_date or self.publish_date
            self.metadata = obj.metadata or self.metadata
            self.resolve_state = ResolveState.RESOLVED
        elif isinstance(obj, NewsArticle):
            self.title = obj.title or self.title
            if self._verify_image(obj.image):
                self.image = obj.image or self.image
            self.description = obj.description or self.description
            self.lang = obj.lang or self.lang
            self.categories = (
                [category for category in obj.categories]
                if obj.categories and isinstance(obj.categories, list)
                else (
                    [self.categories]
                    if isinstance(obj.categories, str)
                    else self.categories
                )
            )
            self.resolve_state = ResolveState.RESOLVED
        elif isinstance(obj, SourceModel):
            self.resolved_source = obj.resolved_source or self.resolved_source
            self.source = obj.data.get("source")
            self.rss_source = obj.data.get("rss_source")
            self.linked_items = obj.data.get("linked_items")
            self.title = obj.title or self.title
            self.image = obj.metadata.get("image") or self.image
            self.description = obj.data.get("description") or self.description
            self.lang = obj.lang or self.lang
            self.categories = obj.data.get("categories") or self.categories
            self.original_content = (
                obj.data.get("original_content") or self.original_content
            )
            self.resolve_state = ResolveState.resolve(
                obj.data.get("resolve_state") or self.resolve_state
            )
            self.publish_date = (
                datetime.fromisoformat(obj.metadata.get("publish_date"))
                if obj.metadata.get("publish_date")
                else self.publish_date
            )
            self.source_id = obj.id or self.source_id
            self.source_model = obj
            self.owner_id = obj.owner_id or self.owner_id
            self.organization_id = obj.organization_id or self.organization_id
            if obj.data.get("url_result"):
                self.url_result = UrlResult.model_validate(obj.data.get("url_result"))
            if obj.data.get("article"):
                self.article = NewsArticle.model_validate(obj.data.get("article"))
            if self.resolve_state is None:
                if self.article is not None:
                    self.resolve_state = ResolveState.RESOLVED
                else:
                    self.resolve_state = ResolveState.UNRESOLVED

        else:
            raise ValueError(f"Unsupported object type: {type(obj)}")

    def _populate_source_model(self):
        print(f"Populating source model for: {self.title} ({self.original_source})")
        content_to_hash = (
            str(self.article) if self.article else (self.original_content or self.title)
        )
        content_hash = (
            hashlib.sha256(content_to_hash.encode("utf-8")).hexdigest()
            if content_to_hash
            else None
        )

        common_data = {
            "rss_source": self.rss_source,
            "source": self.source,
            "description": self.description,
            "url_result": self.url_result.model_dump() if self.url_result else None,
            "article": self.article.model_dump() if self.article else None,
            "categories": self.categories,
            "linked_items": self.linked_items,
            "resolve_state": str(self.resolve_state) if self.resolve_state else None,
        }

        common_metadata = {
            "image": str(self.image) if self.image else None,
            "publish_date": (
                self.publish_date.isoformat() if self.publish_date else None
            ),
        }

        if self.source_model:
            # Update existing source_model fields
            self.source_model.original_source = str(self.original_source)
            self.source_model.resolved_source = (
                str(self.resolved_source) if self.resolved_source else None
            )
            self.source_model.title = self.title
            self.source_model.type = "webpage"
            self.source_model.lang = self.lang
            self.source_model.content_hash = content_hash
            self.source_model.is_public = True
            self.source_model.data = common_data
            self.source_model.metadata = common_metadata
            self.source_model.owner_id = self.owner_id
            self.source_model.organization_id = self.organization_id
        else:
            # Create a new SourceModel instance
            self.source_model = SourceModel(
                original_source=str(self.original_source),
                resolved_source=(
                    str(self.resolved_source) if self.resolved_source else None
                ),
                title=self.title,
                type="webpage",
                lang=self.lang,
                content_hash=content_hash,
                is_public=True,
                data=common_data,
                metadata=common_metadata,
                owner_id=self.owner_id,
                organization_id=self.organization_id,
            )

        return self.source_model

    async def create_and_save_source(self, supabase: AsyncClient):
        print(f"Creating and saving source for: {self.title} ({self.original_source})")
        self._populate_source_model()
        result = await self.source_model.create(supabase)
        self._update_from_(result)

    def create_and_save_source_sync(self, supabase: Client):
        print(
            f"Synchronously creating and saving source for: {self.title} ({self.original_source})"
        )
        self._populate_source_model()
        result = self.source_model.create_sync(supabase)
        self._update_from_(result)

    def check_if_exists_sync(self, supabase: Client) -> bool:
        print(f"Checking if source exists for: {self.original_source}")
        return SourceModel.exists_in_supabase_sync(
            supabase, value=str(self.original_source), id_column="original_source"
        )

    def load_from_supabase_sync(self, supabase: Client):
        print(f"Loading source from Supabase for: {self.original_source}")
        result = SourceModel.fetch_from_supabase_sync(
            supabase, value=str(self.original_source), id_column="original_source"
        )
        if result:
            print(f"Loaded result: {result.id}, {result.original_source}")
            self._update_from_(result)
        else:
            print(f"No result found for: {self.original_source}")

    async def check_if_exists(self, supabase: AsyncClient) -> bool:
        print(f"Asynchronously checking if source exists for: {self.original_source}")
        return await SourceModel.exists_in_supabase(
            supabase, value=str(self.original_source), id_column="original_source"
        )

    async def process_linked_items(self, supabase: AsyncClient):
        print(f"Processing linked items for: {self.title} ({self.original_source})")
        link_upsert = []
        for linked_item in self.linked_items:
            # Check if the original source exists in the sources table
            exists = await SourceModel.exists_in_supabase(
                supabase, value=linked_item, id_column="original_source"
            )
            if exists:
                # Fetch the source model
                source_model: SourceModel = await SourceModel.fetch_from_supabase(
                    supabase, value=linked_item, id_column="original_source"
                )
                if source_model and (
                    source_model.data.get("resolved_state") == "resolved"
                    or source_model.data.get("article")
                ):
                    # Check if the SourceRelationshipModel already exists
                    exists_relationship = (
                        await SourceRelationshipModel.exists_in_supabase(
                            supabase,
                            value={
                                "source_id": self.source_id,
                                "related_source_id": source_model.id,
                            },
                        )
                        or await SourceRelationshipModel.exists_in_supabase(
                            supabase,
                            value={
                                "source_id": source_model.id,
                                "related_source_id": self.source_id,
                            },
                        )
                    )

                    if not exists_relationship:
                        # Create or update the SourceRelationshipModel
                        relationship = SourceRelationshipModel(
                            source_id=self.source_id,
                            related_source_id=source_model.id,
                            relationship_type="linked_news_items",
                            is_public=source_model.is_public,
                            owner_id=source_model.owner_id,
                            organization_id=source_model.organization_id,
                        )
                        link_upsert.append(relationship)

        await SourceRelationshipModel.upsert_to_supabase(supabase, link_upsert)

    def _get_field(self, article_attr, url_result_attr, self_attr):
        """
        Helper function to return the first non-None value in priority order:
        NewsArticle -> UrlResult -> WebSource.
        Handles attribute availability checks.
        """
        article_value = (
            getattr(self.article, article_attr, None) if self.article else None
        )
        url_result_value = (
            getattr(self.url_result, url_result_attr, None) if self.url_result else None
        )
        self_value = getattr(self, self_attr, None)
        return article_value or url_result_value or self_value

    def to_simple_str(self):
        title = self._get_field("title", "title", "title")
        topic = self.article.topic if self.article else ""
        summary = self._get_field("summary", "description", "description")
        categories = self._get_field("categories", "categories", "categories")
        id = self.get_sorting_id()

        return (
            f"ID({id}), Categories({str(categories)})"
            + (f" Topic({topic})" if topic else "")
            + f"\n Title: {title}"
            + f"\n Summary: {summary}"
        )

    def get_sorting_id(self):
        if self._sorting_id is None:
            self._sorting_id = hashlib.md5(
                str(self.original_source).encode("utf-8")
            ).hexdigest()
        return self._sorting_id

    @classmethod
    def get_links(cls, rss_item):
        links = []
        if "<ol><li>" in rss_item["summary"] or 'href="http' in rss_item["summary"]:
            soup = BeautifulSoup(rss_item["summary"], "html.parser")
            for li in soup.find_all("li"):
                link_tag = li.find("a", href=True)
                source_tag = li.find("font")
                if link_tag:
                    link = link_tag["href"]
                    title = link_tag.get_text(strip=True)
                    source = source_tag.get_text(strip=True) if source_tag else None
                    if link != rss_item["link"]:
                        links.append((link, title, source))
        return links

    @classmethod
    def get_link_ids(cls, rss_item, filter_id=None):
        links = []
        if "<ol><li>" in rss_item["summary"] or 'href="http' in rss_item["summary"]:
            links = re.findall(r'href="(.*?)"', rss_item["summary"])
            links = [
                hashlib.md5(str(link).encode("utf-8")).hexdigest()
                for link in links
                if link != rss_item["link"]
            ]
            if filter_id:
                links = [link for link in links if link != filter_id]
        return links

    def to_sorting_str(self, additional_details=True):
        if self.rss_item is None:
            return self.to_simple_str()

        id = self.get_sorting_id()

        str_rep = f"ID({id}) - Published({str(self.publish_date)}):\n"
        if "tags" in self.rss_item and len(self.rss_item["tags"]) > 0:
            str_rep += f"Categories: {', '.join([tag['term'] for tag in self.rss_item['tags']])}\n"

        str_rep += f"Title: {self.rss_item['title']}\n"
        if additional_details:
            if (
                "<ol><li>" in self.rss_item["summary"]
                or 'href="http' in self.rss_item["summary"]
            ):
                links = self.get_link_ids(self.rss_item, self.get_sorting_id())
                if len(links) > 0:
                    str_rep += f"Alternative source: \n - {'\n - '.join(links)}\n\n"
            else:
                str_rep += f"Description: {self.rss_item['summary']}\n\n"

        return str_rep

    def short_id(cls, title: Optional[str] = None) -> str:
        """
        Generate a short form of source_model.id (UUID) or create an ID from title.

        :param title: The title to generate an ID from if source_model.id is not available.
        :return: A short id (first 8 characters of UUID) or hashed id from title.
        """
        if cls.source_model and cls.source_model.id:
            return str(cls.source_model.id).split("-")[0]
        elif title:
            return hashlib.sha256(title.encode("utf-8")).hexdigest()[:8]
        return "unknown_id"

    def find_match(self, search_id: str) -> Optional["WebSource"]:
        """
        Recursively search for a matching source within the collection or its children
        by `search_id` against `short_id` or `source_model.id`.

        :param search_id: The string to search for in `short_id` or `source_model.id`.
        :return: The matching WebSourceCollection or WebSource instance if found, else None.
        """

        search_id_cleaned = str(search_id).strip()
        if search_id_cleaned.startswith("ID(") and search_id_cleaned.endswith(")"):
            search_id_cleaned = search_id_cleaned[3:-1].strip()

        if self.short_id(self.title) == str(search_id) or (
            self.source_model and str(self.source_model.id) == str(search_id)
        ):
            return self
        return None

    def short_string(self):
        # Construct the string representation
        title = self._get_field("title", "title", "title")
        description = self._get_field("description", "description", "description")

        # Combine all parts into a list
        parts = [
            f"ID({self.short_id()}) {title}:" if title else None,
            f"{description}" if description else None,
        ]

        # Filter out None values and join parts with newlines
        return "\n".join(filter(None, parts))

    def __str__(self):
        """
        Generate a string representation of the WebSource instance.
        Fields are included in the order: Title, Description, Content, Image, and Categories.
        Data is prioritized from NewsArticle, then UrlResult, and finally WebSource itself.
        """

        # Construct the string representation
        title = self._get_field("title", "title", "title")
        description = self._get_field("description", "description", "description")
        content = self._get_field(
            "article", "human_readable_content", "original_content"
        )
        categories = self._get_field("categories", "categories", "categories")

        # Format categories if they exist
        if categories and isinstance(categories, list):
            if self.article and categories == self.article.categories:
                categories = ", ".join([cat for cat in categories])
            else:
                categories = ", ".join(categories)

        # Combine all parts into a list
        parts = [
            f"Title: {title}" if title else None,
            f"Description: {description}" if description else None,
            f"Content: {content}" if content else None,
            f"Categories: {categories}" if categories else None,
        ]

        # Filter out None values and join parts with newlines
        return "\n".join(filter(None, parts))

    async def process_linked_items_sync(self, supabase: Client):
        link_upsert = []
        for linked_item in self.linked_items:
            # Check if the original source exists in the sources table
            exists = await SourceModel.exists_in_supabase_sync(
                supabase, value=linked_item, id_column="original_source"
            )
            if exists:
                # Fetch the source model
                source_model: SourceModel = await SourceModel.fetch_from_supabase_sync(
                    supabase, value=linked_item, id_column="original_source"
                )
                if source_model and (
                    source_model.data.get("resolved_state") == "resolved"
                    or source_model.data.get("article")
                ):
                    # Check if the SourceRelationshipModel already exists
                    exists_relationship = (
                        await SourceRelationshipModel.exists_in_supabase_sync(
                            supabase,
                            value={
                                "source_id": self.source_id,
                                "related_source_id": source_model.id,
                            },
                        )
                        or await SourceRelationshipModel.exists_in_supabase_sync(
                            supabase,
                            value={
                                "source_id": source_model.id,
                                "related_source_id": self.source_id,
                            },
                        )
                    )

                    if not exists_relationship:
                        # Create or update the SourceRelationshipModel
                        relationship = SourceRelationshipModel(
                            source_id=self.source_id,
                            related_source_id=source_model.id,
                            relationship_type="linked",
                            is_public=source_model.is_public,
                            owner_id=source_model.owner_id,
                            organization_id=source_model.organization_id,
                        )
                        link_upsert.append(relationship)

        await SourceRelationshipModel.upsert_to_supabase_sync(supabase, link_upsert)

    async def load_from_supabase(self, supabase: AsyncClient):
        result = await SourceModel.fetch_from_supabase(
            supabase, value=str(self.original_source), id_column="original_source"
        )
        if result:
            self._update_from_(result)

    def get_url(self):
        return self.resolved_source or (
            self.original_source
            if self.resolve_state == ResolveState.UNRESOLVED
            else None
        )

    def _create_panel_transcript_source_reference(
        self, transcript: PanelTranscript, user_ids: UserIDs = None
    ):
        print(f"Connect source to {self.source_id=} {transcript.id=}")
        # pretty_print(self, "news_item", True, print)
        return PanelTranscriptSourceReference(
            transcript_id=transcript.id,
            source_id=self.source_id,
            type="web_source",
            data={
                "title": self.title,
                "image": str(self.image) if self.image else None,
                "publish_date": (
                    self.publish_date.isoformat() if self.publish_date else None
                ),
                "url": self.resolved_source,
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

    async def create_panel_transcript_source_reference(
        self,
        supabase: AsyncClient,
        transcript: PanelTranscript,
        user_ids: UserIDs = None,
    ) -> PanelTranscriptSourceReference:
        if self.source_id is not None:
            reference = self._create_panel_transcript_source_reference(
                transcript, user_ids
            )
            return await reference.create(supabase)
        else:
            print(
                f"No source id set for {self.original_source}, skipping reference creation"
            )

    def create_panel_transcript_source_reference_sync(
        self, supabase: Client, transcript: PanelTranscript, user_ids: UserIDs = None
    ) -> PanelTranscriptSourceReference:
        if self.source_id is not None:
            reference = self._create_panel_transcript_source_reference(
                transcript, user_ids
            )
            return reference.create_sync(supabase)
        else:
            print(
                f"No source id set for {self.original_source}, skipping reference creation"
            )

    def resolve_and_store_link(
        self, supabase: Client, user_ids: UserIDs = None
    ) -> bool:
        # print(f"Resolving and storing link for: {self.original_source}")
        if self.check_if_exists_sync(supabase):
            # print(f"Source exists, loading from Supabase for: {self.original_source}")
            self.load_from_supabase_sync(supabase)
            return (
                self.resolve_state == ResolveState.RESOLVED or self.article is not None
            )
        else:
            resolver = LinkResolver(reformat_text=True)
            try:
                # print(f"Resolving URL: {self.original_source}")
                url_result = resolver.resolve_url(
                    str(self.original_source),
                    title=self.title,
                    description=self.description,
                )
                self.url_result = url_result
                if len(url_result.human_readable_content) > 500:
                    self._update_from_(url_result)  # Replaced manual updates
                    self.build_article()  # Update article

                    # print(
                    #     f"Resolved URL successfully, saving source for: {self.title} ({self.original_source})"
                    # )
                    self.resolve_state = ResolveState.RESOLVED
                    return True
            except Exception as e:
                self.resolve_state = ResolveState.FAILED
                print(f"Failed to resolve {self.original_source}: {repr(e)}")
            finally:
                if user_ids is not None:
                    self.owner_id = user_ids.user_id
                    self.organization_id = user_ids.organization_id
                # print(f"Closing resolver for: {self.original_source}")
                self.create_and_save_source_sync(supabase)
                resolver.close()
        return False

    def build_article(self):
        print(f"Formatting content for: {self.original_source}")
        # try:
        if self.original_content:
            self.article = None
            # try:
            self.article = web_source_article_builder_sync(self.url_result)
            # Extract details to the instance after generation
            if self.article:
                self._update_from_(self.article)  # Replaced manual updates

            # except Exception as e:
            #     logger.error(f"Failed to format text: {e}")
        # except Exception as e:
        #     print(f"Failed to format content for: {self.original_source}: {e}")
