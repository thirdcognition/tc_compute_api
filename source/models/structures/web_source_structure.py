from typing import List, Optional
from source.models.data.web_source import WebSource


class WebSourceCollection:
    main_item: bool = False

    def __init__(self, web_sources: Optional[List[WebSource]] = None):
        """
        Initialize the collection with an optional list of WebSource objects.

        :param web_sources: A list of WebSource objects to initialize the collection with.
        """
        self.web_sources: List[WebSource] = web_sources if web_sources else []

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

    def __str__(self):
        return self.to_ordered_string()
