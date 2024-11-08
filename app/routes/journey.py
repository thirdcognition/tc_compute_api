from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.supabase import SupaClientDep
from lib.llm_exec.journey_exec import get_journey_template_with_role

router = APIRouter()


class JourneyRequestData(BaseModel):
    role_title: str
    role_description: str


@router.post("/journey/template")
async def api_get_journey_template(
    journey_data: JourneyRequestData,
    supabase: SupaClientDep,
):
    try:
        template = await get_journey_template_with_role(
            supabase, journey_data.role_title, journey_data.role_description
        )
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
