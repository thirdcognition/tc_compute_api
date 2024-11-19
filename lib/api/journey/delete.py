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


async def delete_journey(supabase: AsyncClient, journey_id: UUID) -> None:
    if not await JourneyModel.exists_in_supabase(supabase, journey_id):
        raise ValueError("Journey not found")
    await JourneyModel.delete_from_supabase(supabase, journey_id)


async def delete_journey_version(supabase: AsyncClient, version_id: UUID) -> None:
    if not await JourneyVersionModel.exists_in_supabase(supabase, version_id):
        raise ValueError("Journey version not found")
    await JourneyVersionModel.delete_from_supabase(supabase, version_id)


async def delete_journey_item(supabase: AsyncClient, item_id: UUID) -> None:
    if not await JourneyItemModel.exists_in_supabase(supabase, item_id):
        raise ValueError("Journey item not found")
    await JourneyItemModel.delete_from_supabase(supabase, item_id)


async def delete_journey_item_version(supabase: AsyncClient, version_id: UUID) -> None:
    if not await JourneyItemVersionModel.exists_in_supabase(supabase, version_id):
        raise ValueError("Journey item version not found")
    await JourneyItemVersionModel.delete_from_supabase(supabase, version_id)


async def delete_journey_structure(supabase: AsyncClient, structure_id: UUID) -> None:
    if not await JourneyStructureModel.exists_in_supabase(supabase, structure_id):
        raise ValueError("Journey structure not found")
    await JourneyStructureModel.delete_from_supabase(supabase, structure_id)


async def delete_journey_structure_version(
    supabase: AsyncClient, version_id: UUID
) -> None:
    if not await JourneyStructureVersionModel.exists_in_supabase(supabase, version_id):
        raise ValueError("Journey structure version not found")
    await JourneyStructureVersionModel.delete_from_supabase(supabase, version_id)
