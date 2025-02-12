from typing import Generator, List, Optional
from supabase import Client
from source.tasks.web_sources import generate_resolve_tasks_for_websources
from source.models.data.user import UserIDs
from source.models.data.web_source import WebSource
from source.models.supabase.panel import PanelTranscript
from pydantic import BaseModel, Field, field_validator, ValidationError


class WebSourceCollection(BaseModel):
    web_sources: Optional[List[WebSource]] = Field(
        default=None, description="Optional list of WebSource objects."
    )
    title: Optional[str] = Field(default=None, description="Title of the collection.")
    max_amount: Optional[int] = Field(
        default=None, description="Maximum number of WebSource objects."
    )
    main_item: bool = Field(
        default=False, description="Indicates if this is the main item."
    )

    @field_validator("web_sources", mode="before")
    def validate_web_sources(cls, value):
        if value is None:
            return value

        if isinstance(value, Generator):  # Detect and convert generator
            value = list(value)

        if not isinstance(value, list):
            raise TypeError(f"web_sources must be a list, got {type(value)}")

        validated_sources = []
        for source in value:
            if isinstance(source, WebSource):
                validated_sources.append(source)
            elif isinstance(source, dict):
                try:
                    validated_sources.append(WebSource.model_validate(source))
                except ValidationError as e:
                    raise ValueError(f"Invalid WebSource data: {e}")
            else:
                raise TypeError(
                    f"web_sources must be a list of WebSource objects or dictionaries, got {type(source)}"
                )
        return validated_sources

    def __init__(self, **data):
        super().__init__(**data)
        if self.web_sources:
            self.filter_sources()

    def filter_sources(self):
        """
        Remove duplicate WebSource objects based on their sorting ID.
        """
        if self.web_sources:
            new_sources: dict[str, WebSource] = {}
            for source in self.web_sources:
                new_sources[source.get_sorting_id()] = source
            self.web_sources = list(new_sources.values())

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
        if self.max_amount is None:
            return "\n\n".join(str(ws) for ws in self.web_sources)
        else:
            return "\n\n".join(str(ws) for ws in self.web_sources[: self.max_amount])

    def resolve_and_store_link(self, supabase: Client, user_ids: UserIDs = None):
        resolved = False
        resolved_sources: List[WebSource] = []
        sources: List[WebSource] = None

        if self.max_amount is None:
            sources = self.web_sources
        else:
            sources = self.web_sources[: self.max_amount]

        for item in sources:
            if item.resolve_and_store_link(supabase, user_ids=user_ids):
                resolved = True
                resolved_sources.append(item)

        self.web_sources = resolved_sources

        return resolved

    def load_from_supabase(self, supabase: Client):
        sources: List[WebSource] = None

        if self.max_amount is None:
            sources = self.web_sources
        else:
            sources = self.web_sources[: self.max_amount]

        for item in sources:
            item.load_from_supabase_sync(supabase)

        self.web_sources = sources

        return sources

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

    # def model_dump(self, **kwargs):
    #     """
    #     Dump all WebSource objects in the collection.

    #     :param kwargs: Parameters to pass to each WebSource's dump method.
    #     :return: A list of dumped models.
    #     """
    #     return [web_source.model_dump(**kwargs) for web_source in self.web_sources]

    def generate_tasks(self, supabase: Client, user_ids: UserIDs):
        """
        Generate and execute tasks for all WebSource items in the collection.

        :param supabase: The Supabase client instance.
        :param user_ids: User IDs for task execution.
        :return: Results of the executed tasks.
        """
        return generate_resolve_tasks_for_websources(
            self.web_sources, supabase, user_ids
        )

    def __str__(self):
        return self.to_ordered_string()
