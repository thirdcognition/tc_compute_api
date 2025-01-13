from supabase import AsyncClient
from source.models.supabase.public_panel import (
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)
from source.api.panel.create import (
    create_panel,
    create_panel_transcript,
    create_panel_audio,
)


async def create_public_panel(
    supabase: AsyncClient, request_data: PublicPanelDiscussion
) -> PublicPanelDiscussion:
    return await create_panel(supabase, request_data)


async def create_public_panel_transcript(
    supabase: AsyncClient, request_data: PublicPanelTranscript
) -> PublicPanelTranscript:
    return await create_panel_transcript(supabase, request_data)


async def create_public_panel_audio(
    supabase: AsyncClient, request_data: PublicPanelAudio
) -> PublicPanelAudio:
    return await create_panel_audio(supabase, request_data)
