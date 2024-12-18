from uuid import UUID
from supabase import AsyncClient
from source.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio


async def delete_panel(supabase: AsyncClient, discussion_id: UUID) -> bool:
    if not await PanelDiscussion.exists_in_supabase(supabase, discussion_id):
        raise ValueError("Panel discussion not found")
    return await PanelDiscussion.delete_from_supabase(supabase, discussion_id)


async def delete_panel_transcript(supabase: AsyncClient, transcript_id: UUID) -> bool:
    if not await PanelTranscript.exists_in_supabase(supabase, transcript_id):
        raise ValueError("Panel transcript not found")
    return await PanelTranscript.delete_from_supabase(supabase, transcript_id)


async def delete_panel_audio(supabase: AsyncClient, audio_id: UUID) -> bool:
    if not await PanelAudio.exists_in_supabase(supabase, audio_id):
        raise ValueError("Panel audio not found")
    return await PanelAudio.delete_from_supabase(supabase, audio_id)
