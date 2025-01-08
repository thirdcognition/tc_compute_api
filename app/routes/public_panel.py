from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from supabase.client import AsyncClient
from app.core.supabase import SupaClientDep, AccessTokenDep, get_supabase_service_client
from source.helpers.routes import handle_exception
from source.api.public_panel.read import (
    get_public_panel,
    list_public_panels,
    get_public_panel_transcript,
    get_public_panel_audio,
    list_public_panel_transcripts,
    list_public_panel_audios,
    list_public_panel_transcripts_w_id,
    list_public_panel_audios_w_id,
)
from source.api.public_panel.update import (
    update_public_panel,
    update_public_panel_transcript,
    update_public_panel_audio,
)
from source.helpers.panel import (
    PublicPanelRequestData,
    create_public_panel_task,
    create_public_panel_transcription_task,
    create_public_panel_audio_task,
    create_public_panel,
    generate_transcripts_task,  # Import the task
)
from source.models.supabase.public_panel import (
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)
from source.models.config.logging import logger

router = APIRouter()


@router.get("/public_panel/{discussion_id}")
async def api_get_panel(
    discussion_id: str,
    supabase: SupaClientDep,
):
    try:
        discussion = await get_public_panel(supabase, discussion_id)
        return discussion
    except Exception as e:
        raise handle_exception(e, "Panel discussion not found", 404)


@router.get("/public_panel/discussions/")
async def api_list_panels(
    supabase: SupaClientDep,
):
    try:
        discussions = await list_public_panels(supabase)
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


@router.put("/public_panel/{discussion_id}")
async def api_update_panel(
    discussion_id: str,
    request_data: PublicPanelDiscussion,
    supabase: SupaClientDep,
):
    logger.debug(f"{request_data=}")
    try:
        request_data.id = discussion_id
        discussion = await update_public_panel(supabase, request_data)
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
    # TODO: Remove rights from every authenticated user
    try:
        request_data.id = transcript_id
        serviceSupabase: AsyncClient = await get_supabase_service_client()
        transcript = await update_public_panel_transcript(serviceSupabase, request_data)
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


@router.post("/public_panel/transcript")
async def api_create_public_panel_transcript(
    request_data: PublicPanelRequestData,
    access_token: AccessTokenDep,
):
    try:
        request_data_json = request_data.to_json()
        task = create_public_panel_transcription_task.delay(
            access_token, request_data_json
        )
        return {"task_id": task.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel transcript", 500)


@router.post("/public_panel/audio")
async def api_create_public_panel_audio(
    request_data: PublicPanelRequestData,
    access_token: AccessTokenDep,
):
    try:
        request_data_json = request_data.to_json()
        task = create_public_panel_audio_task.delay(access_token, request_data_json)
        return {"task_id": task.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel audio", 500)


@router.get("/public_panel/{public_panel_id}/files")
async def api_get_panel_files(
    public_panel_id: str,
    supabase: SupaClientDep,
):
    try:
        # Fetch all transcript and audio records using the models
        transcript_records = await PublicPanelTranscript.fetch_existing_from_supabase(
            supabase, {"public_panel_id": public_panel_id}
        )
        audio_records = await PublicPanelAudio.fetch_existing_from_supabase(
            supabase, {"public_panel_id": public_panel_id}
        )

        # Generate file URLs using Supabase storage with IDs as keys
        transcript_urls = {
            record.id: (
                await supabase.storage.from_(record.bucket_id).get_public_url(
                    record.file
                )
            ).rstrip("?")
            for record in transcript_records
        }
        audio_urls = {
            record.id: (
                await supabase.storage.from_(record.bucket_id).get_public_url(
                    record.file
                )
            ).rstrip("?")
            for record in audio_records
        }

        return {"transcript_urls": transcript_urls, "audio_urls": audio_urls}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_exception(e, "An error occurred while fetching files", 500)


@router.get("/public_panel/{panel_id}/transcripts")
async def api_list_public_panel_transcripts_w_id(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        transcripts = await list_public_panel_transcripts_w_id(supabase, panel_id)
        return transcripts
    except Exception as e:
        raise handle_exception(
            e, "Transcripts not found for the given discussion ID", 404
        )


@router.get("/public_panel/{panel_id}/audios")
async def api_list_public_panel_audios_w_id(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        audios = await list_public_panel_audios_w_id(supabase, panel_id)
        return audios
    except Exception as e:
        raise handle_exception(e, "Audios not found for the given discussion ID", 404)


# New endpoint for creating a public panel discussion
@router.post("/public_panel/discussion")
async def api_create_panel(
    request_data: PublicPanelRequestData,
    access_token: AccessTokenDep,
):
    try:
        panel_id = create_public_panel(access_token, request_data)
        return {"panel_id": panel_id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel discussion", 500)


@router.post("/public_panel/generate_transcripts")
async def api_generate_transcripts(
    access_token: AccessTokenDep,
):
    try:
        task = generate_transcripts_task.delay(access_token)
        return {"task_id": task.id}
    except Exception as e:
        raise handle_exception(e, "Failed to generate transcripts", 500)
