from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.core.supabase import SupaClientDep
from lib.helpers.routes import handle_exception
from lib.api.panel.read import (
    get_panel_discussion,
    list_panel_discussions,
    get_panel_transcript,
    get_panel_audio,
    list_panel_transcripts,
    list_panel_audios,
)
from lib.api.panel.update import (
    update_panel_discussion,
    update_panel_transcript,
    update_panel_audio,
)
from lib.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio

router = APIRouter()


@router.get("/panel/discussion/{discussion_id}")
async def api_get_panel_discussion(
    discussion_id: str,
    supabase: SupaClientDep,
):
    try:
        discussion = await get_panel_discussion(supabase, discussion_id)
        return discussion
    except Exception as e:
        raise handle_exception(e, "Panel discussion not found", 404)


@router.get("/panel/discussions/")
async def api_list_panel_discussions(
    supabase: SupaClientDep,
):
    try:
        discussions = await list_panel_discussions(supabase)
        return discussions
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/panel/transcripts/")
async def api_list_panel_transcripts(
    supabase: SupaClientDep,
):
    try:
        transcripts = await list_panel_transcripts(supabase)
        return transcripts
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/panel/audios/")
async def api_list_panel_audios(
    supabase: SupaClientDep,
):
    try:
        audios = await list_panel_audios(supabase)
        return audios
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/panel/discussion/{discussion_id}")
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


@router.get("/panel/transcript/{transcript_id}")
async def api_get_panel_transcript(
    transcript_id: str,
    supabase: SupaClientDep,
):
    try:
        transcript = await get_panel_transcript(supabase, transcript_id)
        return transcript
    except Exception as e:
        raise handle_exception(e, "Panel transcript not found", 404)


@router.put("/panel/transcript/{transcript_id}")
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


@router.get("/panel/audio/{audio_id}")
async def api_get_panel_audio(
    audio_id: str,
    supabase: SupaClientDep,
):
    try:
        audio = await get_panel_audio(supabase, audio_id)
        return audio
    except Exception as e:
        raise handle_exception(e, "Panel audio not found", 404)


@router.put("/panel/audio/{audio_id}")
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


@router.get("/panel/{panel_id}/files")
async def api_get_panel_files(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        # Fetch all transcript and audio records associated with the panel_id
        transcript_records = await PanelTranscript.fetch_existing_from_supabase(
            supabase, {"panel_id": panel_id}
        )
        audio_records = await PanelAudio.fetch_existing_from_supabase(
            supabase, {"panel_id": panel_id}
        )

        # Generate file URLs using Supabase storage
        transcript_urls = [
            supabase.storage.from_(record.bucket_id).get_public_url(record.file)
            for record in transcript_records
        ]
        audio_urls = [
            supabase.storage.from_(record.bucket_id).get_public_url(record.file)
            for record in audio_records
        ]

        return {"transcript_urls": transcript_urls, "audio_urls": audio_urls}
    except Exception as e:
        raise handle_exception(e, "Files not found for the given panel ID", 404)
