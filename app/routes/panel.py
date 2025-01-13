from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.core.supabase import SupaClientDep, get_supabase_tokens
from source.helpers.routes import handle_exception
from source.api.panel.read import (
    get_panel,
    list_panel_audios_w_id,
    list_panel_transcripts_w_id,
    list_panels,
    get_panel_transcript,
    get_panel_audio,
    list_panel_transcripts,
    list_panel_audios,
)
from source.api.panel.update import (
    update_panel,
    update_panel_transcript,
    update_panel_audio,
)
from source.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio
from source.helpers.panel import (
    PanelRequestData,
    create_panel,
    create_panel_audio_task,
    create_panel_task,
    create_panel_transcription_task,
    fetch_google_news_links,
    GoogleNewsConfig,
    generate_transcripts_task,
)

router = APIRouter()


@router.post("/panel/news_links")
async def api_fetch_news_links(
    config: GoogleNewsConfig,
):
    try:
        news_links = fetch_google_news_links(config)
        return {"news_links": news_links}
    except Exception as e:
        raise handle_exception(e, "Failed to fetch news links")


@router.get("/panel/{discussion_id}")
async def api_get_panel(
    discussion_id: str,
    supabase: SupaClientDep,
):
    try:
        discussion = await get_panel(supabase, discussion_id)
        return discussion
    except Exception as e:
        raise handle_exception(e, "Panel discussion not found", 404)


@router.get("/panel/discussions/")
async def api_list_panels(
    supabase: SupaClientDep,
):
    try:
        discussions = await list_panels(supabase)
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


@router.put("/panel/{discussion_id}")
async def api_update_panel(
    discussion_id: str,
    request_data: PanelDiscussion,
    supabase: SupaClientDep,
):
    try:
        request_data.id = discussion_id
        discussion = await update_panel(supabase, request_data)
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


@router.post("/panel/")
async def api_create_panel(
    request_data: PanelRequestData,
    supabase: SupaClientDep,
):
    try:
        # Convert request_data to a JSON-serializable format
        request_data_json = request_data.to_json()

        task = create_panel_task.delay(
            await get_supabase_tokens(supabase), request_data_json
        )
        return {"task_id": task.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Internal Server Error")


@router.post("/panel/transcript")
async def api_create_panel_transcript(
    request_data: PanelRequestData,
    supabase: SupaClientDep,
):
    try:
        request_data_json = request_data.to_json()
        task = create_panel_transcription_task.delay(
            await get_supabase_tokens(supabase), request_data_json
        )
        return {"task_id": task.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel transcript", 500)


@router.post("/panel/audio")
async def api_create_panel_audio(
    request_data: PanelRequestData,
    supabase: SupaClientDep,
):
    try:
        request_data_json = request_data.to_json()
        task = create_panel_audio_task.delay(
            await get_supabase_tokens(supabase), request_data_json
        )
        return {"task_id": task.id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel audio", 500)


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
    except Exception as e:
        raise handle_exception(e, "An error occurred while fetching files", 500)


@router.get("/panel/{panel_id}/transcripts")
async def api_list_panel_transcripts_w_id(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        transcripts = await list_panel_transcripts_w_id(supabase, panel_id)
        return transcripts
    except Exception as e:
        raise handle_exception(
            e, "Transcripts not found for the given discussion ID", 404
        )


@router.get("/panel/{panel_id}/audios")
async def api_list_panel_audios_w_id(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        audios = await list_panel_audios_w_id(supabase, panel_id)
        return audios
    except Exception as e:
        raise handle_exception(e, "Audios not found for the given discussion ID", 404)


# New endpoint for creating a public panel discussion
@router.post("/panel/discussion")
async def api_create_panel_discussion(
    request_data: PanelRequestData,
    supabase: SupaClientDep,
):
    try:
        panel_id = create_panel(await get_supabase_tokens(supabase), request_data)
        return {"panel_id": panel_id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel discussion", 500)


@router.post("/panel/generate_transcripts")
async def api_generate_transcripts(
    supabase: SupaClientDep,
):
    try:
        task = generate_transcripts_task.delay(await get_supabase_tokens(supabase))
        return {"task_id": task.id}
    except Exception as e:
        raise handle_exception(e, "Failed to generate transcripts", 500)
