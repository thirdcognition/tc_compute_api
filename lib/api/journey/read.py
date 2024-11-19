from typing import List
from uuid import UUID
from supabase import AsyncClient

from lib.models.supabase.journey import (
    JourneyModel,
    JourneyVersionModel,
    JourneyItemModel,
    JourneyItemVersionModel,
    JourneyStructureModel,
    JourneyStructureVersionModel,
)


async def get_journey(supabase: AsyncClient, journey_id: UUID) -> JourneyModel:
    journey_model = await JourneyModel.fetch_from_supabase(supabase, journey_id)
    if not journey_model:
        raise ValueError("Journey not found")
    return journey_model


async def list_journeys(supabase: AsyncClient) -> List[JourneyModel]:
    journey_model = JourneyModel()
    response = await supabase.table(journey_model.TABLE_NAME).select("*").execute()
    journeys = [JourneyModel(**journey_data) for journey_data in response.data]
    return journeys


async def get_journey_version(
    supabase: AsyncClient, version_id: UUID
) -> JourneyVersionModel:
    journey_version_model = await JourneyVersionModel.fetch_from_supabase(
        supabase, version_id
    )
    if not journey_version_model:
        raise ValueError("Journey version not found")
    return journey_version_model


async def list_journey_versions(supabase: AsyncClient) -> List[JourneyVersionModel]:
    journey_version_model = JourneyVersionModel()
    response = (
        await supabase.table(journey_version_model.TABLE_NAME).select("*").execute()
    )
    journey_versions = [
        JourneyVersionModel(**version_data) for version_data in response.data
    ]
    return journey_versions


async def get_journey_item(supabase: AsyncClient, item_id: UUID) -> JourneyItemModel:
    journey_item_model = await JourneyItemModel.fetch_from_supabase(supabase, item_id)
    if not journey_item_model:
        raise ValueError("Journey item not found")
    return journey_item_model


async def list_journey_items(supabase: AsyncClient) -> List[JourneyItemModel]:
    journey_item_model = JourneyItemModel()
    response = await supabase.table(journey_item_model.TABLE_NAME).select("*").execute()
    journey_items = [JourneyItemModel(**item_data) for item_data in response.data]
    return journey_items


async def get_journey_item_version(
    supabase: AsyncClient, version_id: UUID
) -> JourneyItemVersionModel:
    journey_item_version_model = await JourneyItemVersionModel.fetch_from_supabase(
        supabase, version_id
    )
    if not journey_item_version_model:
        raise ValueError("Journey item version not found")
    return journey_item_version_model


async def list_journey_item_versions(
    supabase: AsyncClient,
) -> List[JourneyItemVersionModel]:
    journey_item_version_model = JourneyItemVersionModel()
    response = (
        await supabase.table(journey_item_version_model.TABLE_NAME)
        .select("*")
        .execute()
    )
    journey_item_versions = [
        JourneyItemVersionModel(**version_data) for version_data in response.data
    ]
    return journey_item_versions


async def get_journey_structure(
    supabase: AsyncClient, structure_id: UUID
) -> JourneyStructureModel:
    journey_structure_model = await JourneyStructureModel.fetch_from_supabase(
        supabase, structure_id
    )
    if not journey_structure_model:
        raise ValueError("Journey structure not found")
    return journey_structure_model


async def list_journey_structures(supabase: AsyncClient) -> List[JourneyStructureModel]:
    journey_structure_model = JourneyStructureModel()
    response = (
        await supabase.table(journey_structure_model.TABLE_NAME).select("*").execute()
    )
    journey_structures = [
        JourneyStructureModel(**structure_data) for structure_data in response.data
    ]
    return journey_structures


async def get_journey_structure_version(
    supabase: AsyncClient, version_id: UUID
) -> JourneyStructureVersionModel:
    journey_structure_version_model = (
        await JourneyStructureVersionModel.fetch_from_supabase(supabase, version_id)
    )
    if not journey_structure_version_model:
        raise ValueError("Journey structure version not found")
    return journey_structure_version_model


async def list_journey_structure_versions(
    supabase: AsyncClient,
) -> List[JourneyStructureVersionModel]:
    journey_structure_version_model = JourneyStructureVersionModel()
    response = (
        await supabase.table(journey_structure_version_model.TABLE_NAME)
        .select("*")
        .execute()
    )
    journey_structure_versions = [
        JourneyStructureVersionModel(**version_data) for version_data in response.data
    ]
    return journey_structure_versions
