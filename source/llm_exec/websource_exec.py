import datetime
from typing import List, Tuple

from langsmith import traceable
from source.chains import get_chain  # Updated import
from source.models.structures.panel import SummaryReference, TranscriptMetadata
from source.models.structures.user import UserIDs
from source.models.structures.web_source import WebSource
from source.models.structures.web_source_collection import WebSourceCollection
from source.models.supabase.panel import PanelTranscript
from source.prompts.web_source import WebSourceGrouping


@traceable(
    run_type="llm",
    name="Group web sources",
)
def group_web_sources(
    web_sources: List[WebSource], min_amount=5, max_ids=5
) -> List[WebSourceCollection]:
    source_ids = {str(source.get_sorting_id()) for source in web_sources}

    grouping: WebSourceGrouping = get_chain("group_web_sources_sync").invoke(
        {
            "datetime": str(datetime.datetime.now()),
            "web_sources": "\n\n".join(
                source.to_simple_str() for source in web_sources
            ),
            "start_with": "Humor or funny topic if available",
            "end_with": "Lighthearted, or funny topic if available",
            "min_groups": min_amount,
            "max_ids": max_ids,
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
        coll = WebSourceCollection(
            web_sources=filtered_sources,
            title=group.title if group.title else f"Group {i}",
            categories=group.categories if group.categories else [],
            topic=group.topic if group.topic else None,
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
            source_collections.append(
                WebSourceCollection(web_sources=[remaining_source])
            )

    return source_collections


@traceable(
    run_type="llm",
    name="Group RSS sources",
)
def group_rss_items(
    web_sources: List[WebSource],
    guidance="",
    min_amount=5,
    max_ids=5,
    user_ids: UserIDs = None,
    previous_episodes: List[Tuple[PanelTranscript, str]] = None,
) -> List[WebSourceCollection]:
    uniq_sources: dict[str, WebSource] = {}
    for source in web_sources:
        uniq_sources[source.get_sorting_id()] = source

    web_sources = uniq_sources.values()
    web_sources = sorted(web_sources, key=lambda x: x.publish_date)
    source_ids = {str(source.get_sorting_id()) for source in web_sources}
    used_ids = []

    groups: list[list[WebSource]] = []
    for source in web_sources:
        sorting_id = source.get_sorting_id()
        if sorting_id in used_ids:
            continue
        links = source.get_link_ids(source.rss_item, sorting_id)
        used_ids.append(sorting_id)
        group = [source]
        if len(links) > 0:
            for link in links:
                if link in source_ids and link not in used_ids:
                    item = next(
                        (source for source in web_sources if sorting_id == link),
                        None,
                    )
                    if item:
                        used_ids.append(link)
                        group.append(item)
        groups.append(group)

    print(f"Number of unique sources: {len(source_ids)}, sort and group start.")

    previous_episodes_str = ""
    if previous_episodes:
        for prev_item in previous_episodes:
            metadata: TranscriptMetadata = TranscriptMetadata(**prev_item[0].metadata)
            try:
                previous_episodes_str += (
                    "\n".join(
                        [
                            (
                                f"{subject.title}:\nDescription: {subject.description}\nReferences:\n"
                                + "\n - ".join(
                                    [
                                        (
                                            f"{ref.title}"
                                            if isinstance(ref, SummaryReference)
                                            else ref
                                        )
                                        for ref in subject.references
                                    ]
                                )
                            )
                            for subject in metadata.subjects
                        ]
                    )
                    + "\n\n"
                )
            except Exception as e:
                print(f"Failed to use previous items: {e}")

    grouping: WebSourceGrouping = None
    params = {
        "datetime": str(datetime.datetime.now()),
        "all_ids": " - "
        + "\n - ".join([source.get_sorting_id() for source in web_sources]),
        "web_sources": "\n\n".join(
            [
                f"{('Group ' + str(i + 1) + ':\n') if len(group) > 1 else ''}{'\n'.join([source.to_sorting_str(additional_details=False) for source in group])}"
                for i, group in enumerate(groups)
            ]
        ),
        "instructions": guidance,
        "min_groups": min_amount,
        "max_ids": max_ids,
        "previous_episodes": previous_episodes_str,
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
        group_ids = [item for item in group.ids]
        filtered_sources: list[WebSource] = sorted(
            [
                source
                for source in web_sources
                if str(source.get_sorting_id()) in group_ids
            ],
            key=lambda source: source.publish_date,
            reverse=True,  # Ensures sorting in descending order
        )

        source_ids -= {str(source.get_sorting_id()) for source in filtered_sources}
        image = next(
            (
                source.image
                for source in filtered_sources
                if getattr(source, "image", None)
            ),
            None,
        )

        coll = WebSourceCollection(
            web_sources=filtered_sources,
            title=group.title if group.title else f"Group {i}",
            categories=group.categories if group.categories else [],
            topic=group.topic if group.topic else None,
            image=image,
            publish_date=(
                filtered_sources[0].publish_date if len(filtered_sources) > 0 else None
            ),
            # title=(
            #     grouping.ordered_group_titles[i]
            #     if (len(grouping.ordered_group_titles) > i)
            #     else f"Group {i}"
            # ),
            max_amount=grouping.min_groups,
        )

        if user_ids is not None:
            coll.owner_id = user_ids.user_id
            coll.organization_id = user_ids.organization_id

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
            source = WebSourceCollection(
                web_sources=[remaining_source], title="Remaining sources", categories=[]
            )
            if user_ids is not None:
                source.owner_id = user_ids.user_id
                source.organization_id = user_ids.organization_id

            source_collections.append(source)

    return source_collections
