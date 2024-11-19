from supabase import AsyncClient

from lib.models.supabase.journey import (
    JourneyModel,
    JourneyVersionModel,
    JourneyItemModel,
    JourneyItemVersionModel,
    JourneyStructureModel,
    JourneyStructureVersionModel,
)


async def update_journey(
    supabase: AsyncClient, request_data: JourneyModel
) -> JourneyModel:
    existing_journey = await JourneyModel.fetch_from_supabase(supabase, request_data.id)
    if not existing_journey:
        raise ValueError("Journey not found")

    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(existing_journey, key, value)

    await existing_journey.update(supabase)
    return existing_journey


async def update_journey_version(
    supabase: AsyncClient, request_data: JourneyVersionModel
) -> JourneyVersionModel:
    existing_version = await JourneyVersionModel.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_version:
        raise ValueError("Journey version not found")

    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(existing_version, key, value)

    await existing_version.update(supabase)
    return existing_version


async def update_journey_item(
    supabase: AsyncClient, request_data: JourneyItemModel
) -> JourneyItemModel:
    existing_item = await JourneyItemModel.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_item:
        raise ValueError("Journey item not found")

    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(existing_item, key, value)

    await existing_item.update(supabase)
    return existing_item


async def update_journey_item_version(
    supabase: AsyncClient, request_data: JourneyItemVersionModel
) -> JourneyItemVersionModel:
    existing_item_version = await JourneyItemVersionModel.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_item_version:
        raise ValueError("Journey item version not found")

    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(existing_item_version, key, value)

    await existing_item_version.update(supabase)
    return existing_item_version


async def update_journey_structure(
    supabase: AsyncClient, request_data: JourneyStructureModel
) -> JourneyStructureModel:
    existing_structure = await JourneyStructureModel.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_structure:
        raise ValueError("Journey structure not found")

    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(existing_structure, key, value)

    await existing_structure.update(supabase)
    return existing_structure


async def update_journey_structure_version(
    supabase: AsyncClient, request_data: JourneyStructureVersionModel
) -> JourneyStructureVersionModel:
    existing_structure_version = await JourneyStructureVersionModel.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_structure_version:
        raise ValueError("Journey structure version not found")

    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(existing_structure_version, key, value)

    await existing_structure_version.update(supabase)
    return existing_structure_version
