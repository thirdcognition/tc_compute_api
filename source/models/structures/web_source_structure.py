from typing import List, Optional

from supabase import Client
from source.models.data.user import UserIDs
from source.models.data.web_source import WebSource
from source.models.supabase.panel import PanelTranscript


class WebSourceCollection:
    main_item: bool = False

    def __init__(
        self, web_sources: Optional[List[WebSource]] = None, title: str = None
    ):
        """
        Initialize the collection with an optional list of WebSource objects.

        :param web_sources: A list of WebSource objects to initialize the collection with.
        """
        self.web_sources: List[WebSource] = web_sources if web_sources else []
        self.title: str = title

        self.filter_sources()

    def filter_sources(self):
        new_sources: dict[str, WebSource] = {}
        for source in self.web_sources:
            new_sources[source.get_sorting_id()] = source

        self.web_sources = new_sources.values()

    def add_web_source(self, web_source: WebSource):
        """
        Add a WebSource object to the collection.
        """
        self.web_sources.append(web_source)

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
        return "\n\n".join(str(ws) for ws in self.web_sources)

    def resolve_and_store_link(self, supabase: Client, user_ids: UserIDs = None):
        resolved = False
        resolved_sources: List[WebSource] = []
        for item in self.web_sources:
            if item.resolve_and_store_link(supabase, user_ids=user_ids):
                resolved = True
                resolved_sources.append(item)

        self.web_sources = resolved_sources

        return resolved

    def create_panel_transcript_source_reference_sync(
        self, supabase: Client, transcript: PanelTranscript
    ):
        references = []
        for item in self.web_sources:
            ref = item.create_panel_transcript_source_reference_sync(
                supabase, transcript
            )
            if ref is not None:
                references.append(ref)

        return references

    def model_dump(self, **kwargs):
        """
        Dump all WebSource objects in the collection.

        :param kwargs: Parameters to pass to each WebSource's dump method.
        :return: A list of dumped models.
        """
        return [web_source.model_dump(**kwargs) for web_source in self.web_sources]

    def __str__(self):
        return self.to_ordered_string()
