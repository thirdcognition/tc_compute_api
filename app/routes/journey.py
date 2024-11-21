from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError
from app.core.supabase import SupaClientDep
from lib.helpers.routes import handle_exception
from lib.llm_exec.journey_exec import get_journey_template_id_with_role
from lib.models.supabase.journey import (
    JourneyModel,
    JourneyVersionModel,
    JourneyItemModel,
    JourneyItemVersionModel,
    JourneyStructureModel,
    JourneyStructureVersionModel,
)
from lib.api.journey.create import (
    create_journey,
    create_journey_version,
    create_journey_item,
    create_journey_item_version,
    create_journey_structure,
    create_journey_structure_version,
)
from lib.api.journey.read import (
    get_journey,
    list_journeys,
    get_journey_version,
    list_journey_versions,
    get_journey_item,
    list_journey_items,
    get_journey_item_version,
    list_journey_item_versions,
    get_journey_structure,
    list_journey_structures,
    get_journey_structure_version,
    list_journey_structure_versions,
)
from lib.api.journey.update import (
    update_journey,
    update_journey_version,
    update_journey_item,
    update_journey_item_version,
    update_journey_structure,
    update_journey_structure_version,
)
from lib.api.journey.delete import (
    delete_journey,
    delete_journey_version,
    delete_journey_item,
    delete_journey_item_version,
    delete_journey_structure,
    delete_journey_structure_version,
)

router = APIRouter()


class MatchJourneyRequestData(BaseModel):
    role_title: str
    role_description: str


@router.post("/journey/match_with_template")
async def api_match_with_journey_template(journey_data: MatchJourneyRequestData):
    try:
        template_id = await get_journey_template_id_with_role(
            journey_data.role_title, journey_data.role_description
        )
        return {"template_id": template_id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey/from_template/{template_id}")
async def api_create_from_journey_template(
    template_id: str,
    supabase: SupaClientDep,
):
    try:
        resp = await JourneyModel.create_from_template(supabase, template_id)
        journey: JourneyModel = resp[0]
        journey_version: JourneyVersionModel = resp[1]
        return {"journey_id": journey.id, "journey_version": journey_version.id}
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey/copy/{version_id}")
async def api_create_copy_journey(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        resp = await JourneyModel.copy_from(supabase, journey_version_id=version_id)
        journey: JourneyModel = resp[0]
        return {"journey_id": journey.id}
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.post("/journey/")
async def api_create_journey(
    request_data: JourneyModel,
    supabase: SupaClientDep,
):
    try:
        journey = await create_journey(supabase, request_data)
        return {"journey_id": journey.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey/{journey_id}")
async def api_get_journey(
    journey_id: str,
    supabase: SupaClientDep,
):
    try:
        journey = await get_journey(supabase, journey_id)
        return journey
    except Exception as e:
        raise handle_exception(e, "Journey not found", 404)


@router.get("/journeys/")
async def api_list_journeys(
    supabase: SupaClientDep,
):
    try:
        journeys = await list_journeys(supabase)
        return journeys
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/journey/{journey_id}")
async def api_update_journey(
    journey_id: str,
    request_data: JourneyModel,
    supabase: SupaClientDep,
):
    try:
        request_data.id = journey_id
        journey = await update_journey(supabase, request_data)
        return journey
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Journey not found", 404)


@router.delete("/journey/{journey_id}")
async def api_delete_journey(
    journey_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_journey(supabase, journey_id):
            return {"detail": "Journey deleted successfully"}
        return {"detail": "Failed to delete"}
    except Exception as e:
        raise handle_exception(e, "Journey not found", 404)


@router.post("/journey_version/")
async def api_create_journey_version(
    request_data: JourneyVersionModel,
    supabase: SupaClientDep,
):
    try:
        journey_version = await create_journey_version(supabase, request_data)
        return {"journey_version_id": journey_version.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey_version/{version_id}")
async def api_get_journey_version(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        journey_version = await get_journey_version(supabase, version_id)
        return journey_version
    except Exception as e:
        raise handle_exception(e, "Journey version not found", 404)


@router.get("/journey_versions/")
async def api_list_journey_versions(
    supabase: SupaClientDep,
):
    try:
        journey_versions = await list_journey_versions(supabase)
        return journey_versions
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/journey_version/{version_id}")
async def api_update_journey_version(
    version_id: str,
    request_data: JourneyVersionModel,
    supabase: SupaClientDep,
):
    try:
        request_data.id = version_id
        journey_version = await update_journey_version(supabase, request_data)
        return journey_version
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Journey version not found", 404)


@router.delete("/journey_version/{version_id}")
async def api_delete_journey_version(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_journey_version(supabase, version_id):
            return {"detail": "Journey version deleted successfully"}
        return {"detail": "Failed to delete"}
    except Exception as e:
        raise handle_exception(e, "Journey version not found", 404)


@router.post("/journey_item/")
async def api_create_journey_item(
    request_data: JourneyItemModel,
    supabase: SupaClientDep,
):
    try:
        journey_item = await create_journey_item(supabase, request_data)
        return {"journey_item_id": journey_item.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey_item/{item_id}")
async def api_get_journey_item(
    item_id: str,
    supabase: SupaClientDep,
):
    try:
        journey_item = await get_journey_item(supabase, item_id)
        return journey_item
    except Exception as e:
        raise handle_exception(e, "Journey item not found", 404)


@router.get("/journey_items/")
async def api_list_journey_items(
    supabase: SupaClientDep,
):
    try:
        journey_items = await list_journey_items(supabase)
        return journey_items
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/journey_item/{item_id}")
async def api_update_journey_item(
    item_id: str,
    request_data: JourneyItemModel,
    supabase: SupaClientDep,
):
    try:
        request_data.id = item_id
        journey_item = await update_journey_item(supabase, request_data)
        return journey_item
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Journey item not found", 404)


@router.delete("/journey_item/{item_id}")
async def api_delete_journey_item(
    item_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_journey_item(supabase, item_id):
            return {"detail": "Journey item deleted successfully"}
        return {"detail": "Failed to delete"}
    except Exception as e:
        raise handle_exception(e, "Journey item not found", 404)


@router.post("/journey_item_version/")
async def api_create_journey_item_version(
    request_data: JourneyItemVersionModel,
    supabase: SupaClientDep,
):
    try:
        journey_item_version = await create_journey_item_version(supabase, request_data)
        return {"journey_item_version_id": journey_item_version.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey_item_version/{version_id}")
async def api_get_journey_item_version(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        journey_item_version = await get_journey_item_version(supabase, version_id)
        return journey_item_version
    except Exception as e:
        raise handle_exception(e, "Journey item version not found", 404)


@router.get("/journey_item_versions/")
async def api_list_journey_item_versions(
    supabase: SupaClientDep,
):
    try:
        journey_item_versions = await list_journey_item_versions(supabase)
        return journey_item_versions
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/journey_item_version/{version_id}")
async def api_update_journey_item_version(
    version_id: str,
    request_data: JourneyItemVersionModel,
    supabase: SupaClientDep,
):
    try:
        request_data.id = version_id
        journey_item_version = await update_journey_item_version(supabase, request_data)
        return journey_item_version
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Journey item version not found", 404)


@router.delete("/journey_item_version/{version_id}")
async def api_delete_journey_item_version(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_journey_item_version(supabase, version_id):
            return {"detail": "Journey item version deleted successfully"}
        return {"detail": "Failed to delete"}
    except Exception as e:
        raise handle_exception(e, "Journey item version not found", 404)


@router.post("/journey_structure/")
async def api_create_journey_structure(
    request_data: JourneyStructureModel,
    supabase: SupaClientDep,
):
    try:
        journey_structure = await create_journey_structure(supabase, request_data)
        return {"journey_structure_id": journey_structure.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey_structure/{structure_id}")
async def api_get_journey_structure(
    structure_id: str,
    supabase: SupaClientDep,
):
    try:
        journey_structure = await get_journey_structure(supabase, structure_id)
        return journey_structure
    except Exception as e:
        raise handle_exception(e, "Journey structure not found", 404)


@router.get("/journey_structures/")
async def api_list_journey_structures(
    supabase: SupaClientDep,
):
    try:
        journey_structures = await list_journey_structures(supabase)
        return journey_structures
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/journey_structure/{structure_id}")
async def api_update_journey_structure(
    structure_id: str,
    request_data: JourneyStructureModel,
    supabase: SupaClientDep,
):
    try:
        request_data.id = structure_id
        journey_structure = await update_journey_structure(supabase, request_data)
        return journey_structure
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Journey structure not found", 404)


@router.delete("/journey_structure/{structure_id}")
async def api_delete_journey_structure(
    structure_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_journey_structure(supabase, structure_id):
            return {"detail": "Journey structure deleted successfully"}
        return {"detail": "Failed to delete"}
    except Exception as e:
        raise handle_exception(e, "Journey structure not found", 404)


@router.post("/journey_structure_version/")
async def api_create_journey_structure_version(
    request_data: JourneyStructureVersionModel,
    supabase: SupaClientDep,
):
    try:
        journey_structure_version = await create_journey_structure_version(
            supabase, request_data
        )
        return {"journey_structure_version_id": journey_structure_version.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/journey_structure_version/{version_id}")
async def api_get_journey_structure_version(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        journey_structure_version = await get_journey_structure_version(
            supabase, version_id
        )
        return journey_structure_version
    except Exception as e:
        raise handle_exception(e, "Journey structure version not found", 404)


@router.get("/journey_structure_versions/")
async def api_list_journey_structure_versions(
    supabase: SupaClientDep,
):
    try:
        journey_structure_versions = await list_journey_structure_versions(supabase)
        return journey_structure_versions
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/journey_structure_version/{version_id}")
async def api_update_journey_structure_version(
    version_id: str,
    request_data: JourneyStructureVersionModel,
    supabase: SupaClientDep,
):
    try:
        request_data.id = version_id
        journey_structure_version = await update_journey_structure_version(
            supabase, request_data
        )
        return journey_structure_version
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Journey structure version not found", 404)


@router.delete("/journey_structure_version/{version_id}")
async def api_delete_journey_structure_version(
    version_id: str,
    supabase: SupaClientDep,
):
    try:
        if await delete_journey_structure_version(supabase, version_id):
            return {"detail": "Journey structure version deleted successfully"}
        return {"detail": "Failed to delete"}
    except Exception as e:
        raise handle_exception(e, "Journey structure version not found", 404)
