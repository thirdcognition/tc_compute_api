from supabase import AsyncClient
from source.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio


async def create_panel(
    supabase: AsyncClient, request_data: PanelDiscussion
) -> PanelDiscussion:
    await request_data.create(supabase)
    return request_data


async def create_panel_transcript(
    supabase: AsyncClient, request_data: PanelTranscript
) -> PanelTranscript:
    await request_data.create(supabase)
    return request_data


async def create_panel_audio(
    supabase: AsyncClient, request_data: PanelAudio
) -> PanelAudio:
    await request_data.create(supabase)
    return request_data
