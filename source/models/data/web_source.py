import hashlib
from typing import List, Optional
from supabase.client import AsyncClient, Client

# from source.helpers.shared import pretty_print
from source.models.supabase.sources import SourceModel, SourceRelationshipModel
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from source.models.supabase.panel import PanelTranscript, PanelTranscriptSourceReference
from source.helpers.resolve_url import LinkResolver
from source.models.data.user import UserIDs


class WebSource(BaseModel):
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
    lang: Optional[str] = None
    owner_id: Optional[str] = None
    organization_id: Optional[str] = None

    def _populate_source_model(self):
        # pretty_print(self, "News_item save", True, print)
        print(f"Populating source model for: {self.title} ({self.original_source})")
        content_to_hash = (self.original_content or "") + (self.formatted_content or "")
        content_hash = (
            hashlib.sha256(content_to_hash.encode("utf-8")).hexdigest()
            if content_to_hash
            else None
        )

        return SourceModel(
            original_source=str(self.original_source),
            resolved_source=str(self.resolved_source) if self.resolved_source else None,
            title=self.title,
            type=None,  # Assuming type is not directly available in WebSource
            lang=self.lang,  # Assuming lang is not directly available in WebSource
            content_hash=content_hash,
            is_public=True,
            data={
                "source": self.source,
                "description": self.description,
                "original_content": self.original_content,
                "formatted_content": self.formatted_content,
                "categories": self.categories,
                "linked_items": self.linked_items,
            },
            metadata={
                "image": str(self.image) if self.image else None,
                "publish_date": (
                    self.publish_date.isoformat() if self.publish_date else None
                ),
            },
            owner_id=self.owner_id,
            organization_id=self.organization_id,
        )

    def _populate_news_item(self, result: SourceModel):
        print(f"Populating news item from result: {result.id}")
        self.resolved_source = result.resolved_source
        self.title = result.title
        self.source = result.data.get("source")
        self.source_id = result.id
        self.description = result.data.get("description")
        self.original_content = result.data.get("original_content")
        self.formatted_content = result.data.get("formatted_content")
        self.categories = result.data.get("categories")
        self.linked_items = result.data.get("linked_items")
        self.image = result.metadata.get("image")
        self.lang = result.lang
        self.publish_date = (
            datetime.fromisoformat(result.metadata.get("publish_date"))
            if result.metadata.get("publish_date")
            else None
        )
        self.owner_id = result.owner_id
        self.organization_id = result.organization_id

    async def create_and_save_source(self, supabase: AsyncClient):
        print(f"Creating and saving source for: {self.title} ({self.original_source})")
        source_model = self._populate_source_model()
        result = await source_model.create(supabase)
        self._populate_news_item(result)

    def create_and_save_source_sync(self, supabase: Client):
        print(
            f"Synchronously creating and saving source for: {self.title} ({self.original_source})"
        )
        source_model = self._populate_source_model()
        result = source_model.create_sync(supabase)
        self._populate_news_item(result)

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
            self._populate_news_item(result)
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
                if source_model:
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
                            relationship_type="linked",
                            is_public=True,
                        )
                        link_upsert.append(relationship)

        await SourceRelationshipModel.upsert_to_supabase(
            supabase,
            link_upsert,
            on_conflict=["source_id", "related_source_id"],
        )

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
                if source_model:
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
                            is_public=True,
                        )
                        link_upsert.append(relationship)

        await SourceRelationshipModel.upsert_to_supabase_sync(
            supabase,
            link_upsert,
            on_conflict=["source_id", "related_source_id"],
        )

    async def load_from_supabase(self, supabase: AsyncClient):
        result = await SourceModel.fetch_from_supabase(
            supabase, value=str(self.original_source), id_column="original_source"
        )
        if result:
            self._populate_news_item(result)

    def _create_panel_transcript_source_reference(self, transcript: PanelTranscript):
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
            owner_id=self.owner_id,
            organization_id=self.organization_id,
        )

    async def create_panel_transcript_source_reference(
        self, supabase: AsyncClient, transcript: PanelTranscript
    ) -> PanelTranscriptSourceReference:
        if self.source_id is not None:
            reference = self._create_panel_transcript_source_reference(transcript)
            return await reference.create(supabase)
        else:
            print(
                f"No source id set for {self.original_source}, skipping reference creation"
            )

    def create_panel_transcript_source_reference_sync(
        self, supabase: Client, transcript: PanelTranscript
    ) -> PanelTranscriptSourceReference:
        if self.source_id is not None:
            reference = self._create_panel_transcript_source_reference(transcript)
            return reference.create_sync(supabase)
        else:
            print(
                f"No source id set for {self.original_source}, skipping reference creation"
            )

    def resolve_and_store_link(
        self, supabase: Client, user_ids: UserIDs = None
    ) -> bool:
        print(f"Resolving and storing link for: {self.original_source}")
        resolver = LinkResolver(reformat_text=True)
        if self.check_if_exists_sync(supabase):
            print(f"Source exists, loading from Supabase for: {self.original_source}")
            self.load_from_supabase_sync(supabase)
            return True
        else:
            try:
                print(f"Resolving URL: {self.original_source}")
                url_results = resolver.resolve_url(str(self.original_source))
                if len(url_results.human_readable_content) > 500:
                    self.source = url_results.source
                    self.description = (
                        url_results.description
                        if url_results.description is not None
                        else self.description
                    )
                    self.image = (
                        url_results.image
                        if url_results.image is not None
                        else self.image
                    )
                    self.title = (
                        url_results.title
                        if url_results.title is not None
                        else self.title
                    )
                    self.publish_date = (
                        url_results.publish_date
                        if url_results.publish_date is not None
                        else self.publish_date
                    )
                    self.lang = (
                        url_results.lang if url_results.lang is not None else self.lang
                    )
                    self.resolved_source = url_results.resolved_url
                    self.original_content = url_results.human_readable_content
                    self.formatted_content = url_results.formatted_content
                    if user_ids is not None:
                        self.owner_id = user_ids.user_id
                        self.organization_id = user_ids.organization_id
                    print(
                        f"Resolved URL successfully, saving source for: {self.title} ({self.original_source})"
                    )
                    self.create_and_save_source_sync(supabase)
                    return True
            except Exception as e:
                print(f"Failed to resolve {self.original_source}: {e}")
            finally:
                print(f"Closing resolver for: {self.original_source}")
                resolver.close()
        return False
