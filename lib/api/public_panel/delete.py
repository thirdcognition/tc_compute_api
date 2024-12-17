from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.public_panel import (
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)


async def delete_public_panel(supabase: AsyncClient, discussion_id: UUID) -> bool:
    discussion = PublicPanelDiscussion(id=discussion_id)
    return await discussion.delete(supabase)


async def delete_public_panel_transcript(
    supabase: AsyncClient, transcript_id: UUID
) -> bool:
    transcript = PublicPanelTranscript(id=transcript_id)
    return await transcript.delete(supabase)


async def delete_public_panel_audio(supabase: AsyncClient, audio_id: UUID) -> bool:
    audio = PublicPanelAudio(id=audio_id)
    return await audio.delete(supabase)
