from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.core.supabase import SupaClientDep
from lib.helpers.routes import handle_exception
from lib.api.panel.read import (
    get_panel_discussion,
    list_panel_discussions,
    get_panel_transcript,
    get_panel_audio,
)
from lib.api.panel.update import (
    update_panel_discussion,
    update_panel_transcript,
    update_panel_audio,
)
from lib.helpers.panel import create_public_panel, PublicPanelRequestData
from lib.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio

router = APIRouter()


@router.get("/public_panel/discussion/{discussion_id}")
async def api_get_panel_discussion(
    discussion_id: str,
    supabase: SupaClientDep,
):
    try:
        discussion = await get_panel_discussion(supabase, discussion_id)
        return discussion
    except Exception as e:
        raise handle_exception(e, "Panel discussion not found", 404)


@router.get("/public_panel/discussions/")
async def api_list_panel_discussions(
    supabase: SupaClientDep,
):
    try:
        discussions = await list_panel_discussions(supabase)
        return discussions
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/public_panel/discussion/{discussion_id}")
async def api_update_panel_discussion(
    discussion_id: str,
    request_data: PanelDiscussion,
    supabase: SupaClientDep,
):
    try:
        request_data.id = discussion_id
        discussion = await update_panel_discussion(supabase, request_data)
        return discussion
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Panel discussion not found", 404)


@router.get("/public_panel/transcript/{transcript_id}")
async def api_get_panel_transcript(
    transcript_id: str,
    supabase: SupaClientDep,
):
    try:
        transcript = await get_panel_transcript(supabase, transcript_id)
        return transcript
    except Exception as e:
        raise handle_exception(e, "Panel transcript not found", 404)


@router.put("/public_panel/transcript/{transcript_id}")
async def api_update_panel_transcript(
    transcript_id: str,
    request_data: PanelTranscript,
    supabase: SupaClientDep,
):
    try:
        request_data.id = transcript_id
        transcript = await update_panel_transcript(supabase, request_data)
        return transcript
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Panel transcript not found", 404)


@router.get("/public_panel/audio/{audio_id}")
async def api_get_panel_audio(
    audio_id: str,
    supabase: SupaClientDep,
):
    try:
        audio = await get_panel_audio(supabase, audio_id)
        return audio
    except Exception as e:
        raise handle_exception(e, "Panel audio not found", 404)


@router.put("/public_panel/audio/{audio_id}")
async def api_update_panel_audio(
    audio_id: str,
    request_data: PanelAudio,
    supabase: SupaClientDep,
):
    try:
        request_data.id = audio_id
        audio = await update_panel_audio(supabase, request_data)
        return audio
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Panel audio not found", 404)


@router.post("/public_panel/")
async def api_create_public_panel(
    request_data: PublicPanelRequestData,
    supabase: SupaClientDep,
):
    try:
        panel_id, task_id = await create_public_panel(
            {"request": {"id": "test"}}, supabase, request_data
        )
        return {"panel_id": panel_id, "task_id": task_id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")
