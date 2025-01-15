import json
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from supabase import AsyncClient
from source.models.supabase.panel import (
    PanelDiscussion,
    PanelTranscript,
    PanelAudio,
    PanelTranscriptSourceReference,
)


async def get_panel(supabase: AsyncClient, panel_id: UUID) -> PanelDiscussion:
    panel = await PanelDiscussion.fetch_from_supabase(supabase, panel_id)
    if not panel:
        raise ValueError("Panel not found")
    return panel


async def list_panels(supabase: AsyncClient) -> List[PanelDiscussion]:
    panels = await PanelDiscussion.fetch_existing_from_supabase(supabase)
    return panels


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


# Functions to list transcripts and audios for a specific panel
async def list_panel_transcripts_w_id(
    supabase: AsyncClient, panel_id: UUID
) -> List[PanelTranscript]:
    return await PanelTranscript.fetch_existing_from_supabase(
        supabase, {"panel_id": panel_id}
    )


async def get_panel_transcript_sources_w_id(
    supabase: AsyncClient, transcript_id: UUID
) -> PanelTranscriptSourceReference:
    return await PanelTranscriptSourceReference.fetch_existing_from_supabase(
        supabase, {"transcript_id": transcript_id}
    )


async def list_panel_transcript_audios_w_id(
    supabase: AsyncClient, transcript_id: UUID
) -> List[PanelAudio]:
    return await PanelAudio.fetch_existing_from_supabase(
        supabase, {"transcript_id": transcript_id}
    )


async def list_panel_audios_w_id(
    supabase: AsyncClient, panel_id: UUID
) -> List[PanelAudio]:
    return await PanelAudio.fetch_existing_from_supabase(
        supabase, {"panel_id": panel_id}
    )


async def get_panel_files(supabase: AsyncClient, panel_id):
    transcript_records = await PanelTranscript.fetch_existing_from_supabase(
        supabase, {"panel_id": panel_id}
    )
    audio_records = await PanelAudio.fetch_existing_from_supabase(
        supabase, {"panel_id": panel_id}
    )

    # Generate file URLs using Supabase storage
    transcript_urls = {
        record.id: (
            await supabase.storage.from_(record.bucket_id).get_public_url(record.file)
        ).rstrip("?")
        for record in transcript_records
    }
    audio_urls = {
        record.id: (
            await supabase.storage.from_(record.bucket_id).get_public_url(record.file)
        ).rstrip("?")
        for record in audio_records
    }

    return transcript_urls, audio_urls


class PanelDetailsResponse(BaseModel):
    panel: PanelDiscussion
    transcripts: Optional[List[PanelTranscript]] = None
    transcript_urls: Optional[dict[UUID, str]] = None
    transcript_sources: Optional[
        dict[UUID, Optional[List[PanelTranscriptSourceReference]]]
    ] = None
    audios: Optional[List[PanelAudio]] = None
    audio_urls: Optional[dict[UUID, str]] = None

    def to_json(self):
        return json.dumps(self.model_dump(), default=str)


async def get_panel_details(supabase: AsyncClient, panel_id):
    panel = await get_panel(supabase, panel_id)
    transcripts = await list_panel_transcripts_w_id(supabase, panel_id)
    audios = await list_panel_audios_w_id(supabase, panel_id)
    transcript_urls, audio_urls = await get_panel_files(supabase, panel_id)

    transcript_sources = {}
    for transcript in transcripts:
        transcript_sources[transcript.id] = await get_panel_transcript_sources_w_id(
            supabase, transcript.id
        )

    return PanelDetailsResponse(
        panel=panel,
        transcripts=transcripts,
        transcript_urls=transcript_urls,
        transcript_sources=transcript_sources,
        audios=audios,
        audio_urls=audio_urls,
    )
