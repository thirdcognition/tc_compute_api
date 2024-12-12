from typing import List
from uuid import UUID
from supabase import AsyncClient
from lib.models.supabase.public_panel import (
    PublicPanelDiscussion,
    PublicPanelTranscript,
    PublicPanelAudio,
)


async def get_public_panel_discussion(
    supabase: AsyncClient, discussion_id: UUID
) -> PublicPanelDiscussion:
    discussion = PublicPanelDiscussion(id=discussion_id)
    return await discussion.read(supabase)


async def list_public_panel_discussions(
    supabase: AsyncClient,
) -> List[PublicPanelDiscussion]:
    return await PublicPanelDiscussion.fetch_existing_from_supabase(supabase)


async def get_public_panel_transcript(
    supabase: AsyncClient, transcript_id: UUID
) -> PublicPanelTranscript:
    transcript = PublicPanelTranscript(id=transcript_id)
    return await transcript.read(supabase)


async def get_public_panel_audio(
    supabase: AsyncClient, audio_id: UUID
) -> PublicPanelAudio:
    audio = PublicPanelAudio(id=audio_id)
    return await audio.read(supabase)


# New functions to list transcripts and audios
async def list_public_panel_transcripts(
    supabase: AsyncClient,
) -> List[PublicPanelTranscript]:
    return await PublicPanelTranscript.fetch_existing_from_supabase(supabase)


async def list_public_panel_audios(
    supabase: AsyncClient,
) -> List[PublicPanelAudio]:
    return await PublicPanelAudio.fetch_existing_from_supabase(supabase)
