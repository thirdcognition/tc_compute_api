from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from typing import List
from app.core.supabase import (
    SupaClientDep,
    allow_anonymous_login,
    get_supabase_tokens,
    get_sync_supabase_client,
)
from source.helpers.routes import handle_exception
from source.api.panel.read import (
    PanelDetailsResponse,
    get_panel,
    get_panel_details,
    get_panel_files,
    get_panel_transcript_sources_w_id,
    list_panel_audios_w_id,
    list_panel_transcript_audios_w_id,
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
from source.api.panel.delete import (
    delete_panel,
    delete_panel_transcript,
    delete_panel_audio,
)
from source.models.structures.panel import PanelRequestData
from source.models.structures.web_source_structure import WebSourceCollection
from source.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio
from source.panel.panel import create_panel
from source.panel.tasks import (
    create_panel_audio_task,
    create_panel_task,
    create_panel_transcription_task,
    generate_transcripts_task,
)

from source.helpers.sources import (
    fetch_links,
    manage_news_sources,
)
from source.models.data.web_source import WebSource

router = APIRouter()

allow_anonymous_login("/panel", ["GET"])


@router.post("/panel/news_links")
async def api_fetch_news_links(
    configs: dict,
    supabase: SupaClientDep,
):
    try:
        print(f"{configs=}")
        tokens = await get_supabase_tokens(supabase)
        supabase_sync = get_sync_supabase_client(
            access_token=tokens[0], refresh_token=tokens[1]
        )

        sources = manage_news_sources(metadata=configs)

        news_links: List[WebSourceCollection | WebSource] = fetch_links(
            supabase_sync,
            sources,
            dry_run=True,
            guidance=configs.get("news_guidance", ""),
            max_items=configs.get("news_items", 5),
        )
        return {
            "news_links": [
                {"title": link.title, "data": link.model_dump()} for link in news_links
            ]
        }
    except Exception as e:
        raise handle_exception(e, "Failed to fetch news links")


@router.get("/panel/{panel_id}")
async def api_get_panel(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        panel = await get_panel(supabase, panel_id)
        return panel
    except Exception as e:
        raise handle_exception(e, "Panel not found", 404)


@router.get("/panel/discussions/")
async def api_list_panels(
    supabase: SupaClientDep,
):
    try:
        panels = await list_panels(supabase)
        return panels
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


@router.put("/panel/{panel_id}")
async def api_update_panel(
    panel_id: str,
    request_data: PanelDiscussion,
    supabase: SupaClientDep,
):
    try:
        request_data.id = panel_id
        panel = await update_panel(supabase, request_data)
        return panel
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Panel not found", 404)


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


@router.get("/panel/transcript/{transcript_id}/audios")
async def api_get_panel_transcript_audios(
    transcript_id: str,
    supabase: SupaClientDep,
):
    try:
        audios = await list_panel_transcript_audios_w_id(supabase, transcript_id)
        return audios
    except Exception as e:
        raise handle_exception(e, "Panel transcript not found", 404)


@router.get("/panel/transcript/{transcript_id}/sources")
async def api_get_panel_transcript_sources(
    transcript_id: str,
    supabase: SupaClientDep,
):
    try:
        sources = await get_panel_transcript_sources_w_id(supabase, transcript_id)
        return sources
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
        transcript_urls, audio_urls = await get_panel_files(supabase, panel_id)

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
        raise handle_exception(e, "Transcripts not found for the given panel ID", 404)


@router.get("/panel/{panel_id}/audios")
async def api_list_panel_audios_w_id(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        audios = await list_panel_audios_w_id(supabase, panel_id)
        return audios
    except Exception as e:
        raise handle_exception(e, "Audios not found for the given panel ID", 404)


@router.get("/panel/{panel_id}/details")
async def api_get_panel_details(
    panel_id: str,
    supabase: SupaClientDep,
) -> PanelDetailsResponse:
    try:
        panel = await get_panel_details(supabase, panel_id)
        return panel
    except Exception as e:
        raise handle_exception(e, "Panel not found", 404)


# New endpoint for creating a public panelpanel
@router.post("/panel/discussion")
async def api_create_panel_panel(
    request_data: PanelRequestData,
    supabase: SupaClientDep,
):
    try:
        panel_id = create_panel(await get_supabase_tokens(supabase), request_data)
        return {"panel_id": panel_id}
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to create panel panel", 500)


@router.post("/panel/generate_transcripts")
async def api_generate_transcripts(
    supabase: SupaClientDep,
):
    try:
        task = generate_transcripts_task.delay(await get_supabase_tokens(supabase))
        return {"task_id": task.id}
    except Exception as e:
        raise handle_exception(e, "Failed to generate transcripts", 500)


@router.delete("/panel/{panel_id}")
async def api_delete_panel(
    panel_id: str,
    supabase: SupaClientDep,
):
    try:
        await delete_panel(supabase, panel_id)
        return {"message": "Panel deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to delete panel", 500)


@router.delete("/panel/transcript/{transcript_id}")
async def api_delete_panel_transcript(
    transcript_id: str,
    supabase: SupaClientDep,
):
    try:
        await delete_panel_transcript(supabase, transcript_id)
        return {"message": "Panel transcript deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to delete panel transcript", 500)


@router.delete("/panel/audio/{audio_id}")
async def api_delete_panel_audio(
    audio_id: str,
    supabase: SupaClientDep,
):
    try:
        await delete_panel_audio(supabase, audio_id)
        return {"message": "Panel audio deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise handle_exception(e, "Failed to delete panel audio", 500)
