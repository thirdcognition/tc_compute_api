from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.core.celery_app import create_public_panel_task
from app.core.supabase import SupaClientDep, AccessTokenDep
from lib.helpers.routes import handle_exception
from lib.api.public_panel.read import (
    get_public_panel_discussion,
    list_public_panel_discussions,
    get_public_panel_transcript,
    get_public_panel_audio,
    list_public_panel_transcripts,
    list_public_panel_audios,
)
from lib.api.public_panel.update import (
    update_public_panel_discussion,
    update_public_panel_transcript,
    update_public_panel_audio,
)
from lib.helpers.panel import PublicPanelRequestData
from lib.models.supabase.public_panel import (
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)

router = APIRouter()


@router.get("/public_panel/discussion/{discussion_id}")
async def api_get_panel_discussion(
    discussion_id: str,
    supabase: SupaClientDep,
):
    try:
        discussion = await get_public_panel_discussion(supabase, discussion_id)
        return discussion
    except Exception as e:
        raise handle_exception(e, "Panel discussion not found", 404)


@router.get("/public_panel/discussions/")
async def api_list_panel_discussions(
    supabase: SupaClientDep,
):
    try:
        discussions = await list_public_panel_discussions(supabase)
        return discussions
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/public_panel/transcripts/")
async def api_list_public_panel_transcripts(
    supabase: SupaClientDep,
):
    try:
        transcripts = await list_public_panel_transcripts(supabase)
        return transcripts
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/public_panel/audios/")
async def api_list_public_panel_audios(
    supabase: SupaClientDep,
):
    try:
        audios = await list_public_panel_audios(supabase)
        return audios
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.put("/public_panel/discussion/{discussion_id}")
async def api_update_panel_discussion(
    discussion_id: str,
    request_data: PublicPanelDiscussion,
    supabase: SupaClientDep,
):
    try:
        request_data.id = discussion_id
        discussion = await update_public_panel_discussion(supabase, request_data)
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
        transcript = await get_public_panel_transcript(supabase, transcript_id)
        return transcript
    except Exception as e:
        raise handle_exception(e, "Panel transcript not found", 404)


@router.put("/public_panel/transcript/{transcript_id}")
async def api_update_panel_transcript(
    transcript_id: str,
    request_data: PublicPanelTranscript,
    supabase: SupaClientDep,
):
    try:
        request_data.id = transcript_id
        transcript = await update_public_panel_transcript(supabase, request_data)
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
        audio = await get_public_panel_audio(supabase, audio_id)
        return audio
    except Exception as e:
        raise handle_exception(e, "Panel audio not found", 404)


@router.put("/public_panel/audio/{audio_id}")
async def api_update_panel_audio(
    audio_id: str,
    request_data: PublicPanelAudio,
    supabase: SupaClientDep,
):
    try:
        request_data.id = audio_id
        audio = await update_public_panel_audio(supabase, request_data)
        return audio
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Panel audio not found", 404)


@router.post("/public_panel/")
async def api_create_public_panel(
    request_data: PublicPanelRequestData,
    access_token: AccessTokenDep,
):
    try:
        # Convert request_data to a JSON-serializable format
        request_data_json = request_data.to_json()
        task = create_public_panel_task.delay(access_token, request_data_json)
        return {"task_id": task.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.get("/public_panel/{public_panel_id}/files")
async def api_get_panel_files(
    public_panel_id: str,
    supabase: SupaClientDep,
):
    try:
        # Fetch transcript and audio records using the models
        transcript_record = await PublicPanelTranscript.fetch_from_supabase(
            supabase, {"public_panel_id": public_panel_id}
        )
        audio_record = await PublicPanelAudio.fetch_from_supabase(
            supabase, {"public_panel_id": public_panel_id}
        )

        # Check if transcript_record and audio_record are not None
        if transcript_record is None:
            raise HTTPException(
                status_code=404,
                detail="Transcript not found for the given public panel ID",
            )

        if audio_record is None:
            raise HTTPException(
                status_code=404, detail="Audio not found for the given public panel ID"
            )

        # Generate file URLs using Supabase storage
        transcript_url = (
            await supabase.storage.from_(transcript_record.bucket_id).get_public_url(
                transcript_record.file
            )
        ).rstrip("?")
        audio_url = (
            await supabase.storage.from_(audio_record.bucket_id).get_public_url(
                audio_record.file
            )
        ).rstrip("?")

        return {"transcript_url": transcript_url, "audio_url": audio_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_exception(e, "An error occurred while fetching files", 500)
