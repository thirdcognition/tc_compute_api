import datetime
from typing import List
from source.chains.init import get_chain
from source.models.data.web_source import WebSource
from source.models.structures.web_source_structure import WebSourceCollection
from source.prompts.web_source import WebSourceGrouping


def group_web_sources(web_sources: List[WebSource]) -> List[WebSourceCollection]:
    source_ids = {str(source.get_sorting_id()) for source in web_sources}

    grouping: WebSourceGrouping = get_chain("group_web_sources_sync").invoke(
        {
            "datetime": str(datetime.datetime.now()),
            "web_sources": "\n\n".join(
                source.to_simple_str() for source in web_sources
            ),
            "start_with": "Humor or funny topic if available",
            "end_with": "Lighthearted, or funny topic if available",
        }
    )

    source_collections: List[WebSourceCollection] = []
    main_item = int(grouping.main_group)
    i = 0
    for i, group in enumerate(grouping.ordered_groups):
        filtered_sources = [
            source for source in web_sources if str(source.get_sorting_id()) in group
        ]

        source_ids -= {str(source.get_sorting_id()) for source in filtered_sources}
        coll = WebSourceCollection(filtered_sources, grouping.ordered_group_titles[i])
        if i == main_item:
            coll.main_item = True
        source_collections.append(coll)
        i += 1

    for remaining_id in source_ids:
        remaining_source = next(
            (
                source
                for source in web_sources
                if str(source.get_sorting_id()) == remaining_id
            ),
            None,
        )
        if remaining_source:
            source_collections.append(WebSourceCollection([remaining_source]))

    return source_collections


def group_rss_items(
    web_sources: List[WebSource], guidance=""
) -> List[WebSourceCollection]:
    uniq_sources: dict[str, WebSource] = {}
    for source in web_sources:
        uniq_sources[source.get_sorting_id()] = source

    web_sources = uniq_sources.values()
    source_ids = {str(source.get_sorting_id()) for source in web_sources}

    print(f"Number of unique sources: {len(source_ids)}, sort and group start.")

    grouping: WebSourceGrouping = None
    params = {
        "datetime": str(datetime.datetime.now()),
        "all_ids": " - "
        + "\n - ".join([source.get_sorting_id() for source in web_sources]),
        "web_sources": "\n\n".join(source.to_sorting_str() for source in web_sources),
        "instructions": guidance,
    }
    grouping = get_chain("group_rss_items_sync").invoke(params)

    if not isinstance(grouping, WebSourceGrouping):
        print(f"\tFailed sorting sources, retrying. \n{repr(grouping)=}")
        grouping = get_chain("group_rss_items_sync").invoke(params)

    if not isinstance(grouping, WebSourceGrouping):
        raise ValueError("Unable to sort news sources.")

    print("Got grouping, continuing...")

    source_collections: List[WebSourceCollection] = []
    main_item = int(grouping.main_group)
    i = 0
    for i, group in enumerate(grouping.ordered_groups):
        filtered_sources = [
            source for source in web_sources if str(source.get_sorting_id()) in group
        ]

        source_ids -= {str(source.get_sorting_id()) for source in filtered_sources}
        coll = WebSourceCollection(
            filtered_sources,
            (
                grouping.ordered_group_titles[i]
                if (len(grouping.ordered_group_titles) > i)
                else f"Group {i}"
            ),
            max_amount=5,
        )
        if i == main_item:
            coll.main_item = True
        source_collections.append(coll)
        i += 1

    for remaining_id in source_ids:
        remaining_source = next(
            (
                source
                for source in web_sources
                if str(source.get_sorting_id()) == remaining_id
            ),
            None,
        )
        if remaining_source:
            source_collections.append(WebSourceCollection([remaining_source]))

    return source_collections
