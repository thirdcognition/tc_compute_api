from supabase import AsyncClient

from source.models.supabase.journey import (
    JourneyModel,
    JourneyVersionModel,
    JourneyItemModel,
    JourneyItemVersionModel,
    JourneyStructureModel,
    JourneyStructureVersionModel,
)


async def create_journey(
    supabase: AsyncClient, request_data: JourneyModel
) -> JourneyModel:
    await request_data.create(supabase)
    return request_data


async def create_journey_version(
    supabase: AsyncClient, request_data: JourneyVersionModel
) -> JourneyVersionModel:
    await request_data.create(supabase)
    return request_data


async def create_journey_item(
    supabase: AsyncClient, request_data: JourneyItemModel
) -> JourneyItemModel:
    await request_data.create(supabase)
    return request_data


async def create_journey_item_version(
    supabase: AsyncClient, request_data: JourneyItemVersionModel
) -> JourneyItemVersionModel:
    await request_data.create(supabase)
    return request_data


async def create_journey_structure(
    supabase: AsyncClient, request_data: JourneyStructureModel
) -> JourneyStructureModel:
    await request_data.create(supabase)
    return request_data


async def create_journey_structure_version(
    supabase: AsyncClient, request_data: JourneyStructureVersionModel
) -> JourneyStructureVersionModel:
    await request_data.create(supabase)
    return request_data
