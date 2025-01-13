from supabase import AsyncClient
from source.models.supabase.public_panel import (
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)


async def update_public_panel(
    supabase: AsyncClient, request_data: PublicPanelDiscussion
) -> PublicPanelDiscussion:
    return await request_data.update(supabase)


async def update_public_panel_transcript(
    supabase: AsyncClient, request_data: PublicPanelTranscript
) -> PublicPanelTranscript:
    return await request_data.update(supabase)


async def update_public_panel_audio(
    supabase: AsyncClient, request_data: PublicPanelAudio
) -> PublicPanelAudio:
    return await request_data.update(supabase)
