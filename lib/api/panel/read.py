from typing import List
from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio


async def get_panel(supabase: AsyncClient, discussion_id: UUID) -> PanelDiscussion:
    discussion = await PanelDiscussion.fetch_from_supabase(supabase, discussion_id)
    if not discussion:
        raise ValueError("Panel discussion not found")
    return discussion


async def list_panels(supabase: AsyncClient) -> List[PanelDiscussion]:
    discussions = await PanelDiscussion.fetch_existing_from_supabase(supabase)
    return discussions


async def get_panel_transcript(
    supabase: AsyncClient, transcript_id: UUID
) -> PanelTranscript:
    transcript = await PanelTranscript.fetch_from_supabase(supabase, transcript_id)
    if not transcript:
        raise ValueError("Panel transcript not found")
    return transcript


async def get_panel_audio(supabase: AsyncClient, audio_id: UUID) -> PanelAudio:
    audio = await PanelAudio.fetch_from_supabase(supabase, audio_id)
    if not audio:
        raise ValueError("Panel audio not found")
    return audio


# New functions to list transcripts and audios
async def list_panel_transcripts(
    supabase: AsyncClient,
) -> List[PanelTranscript]:
    return await PanelTranscript.fetch_existing_from_supabase(supabase)


async def list_panel_audios(
    supabase: AsyncClient,
) -> List[PanelAudio]:
    return await PanelAudio.fetch_existing_from_supabase(supabase)
