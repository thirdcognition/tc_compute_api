from supabase import AsyncClient
from source.models.supabase.panel import PanelDiscussion, PanelTranscript, PanelAudio


async def update_panel(
    supabase: AsyncClient, request_data: PanelDiscussion
) -> PanelDiscussion:
    existing_discussion = await PanelDiscussion.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_discussion:
        raise ValueError("Panel discussion not found")

    for key, value in request_data.model_dump(exclude_unset=False).items():
        setattr(existing_discussion, key, value)

    await existing_discussion.update(supabase)
    return existing_discussion


async def update_panel_transcript(
    supabase: AsyncClient, request_data: PanelTranscript
) -> PanelTranscript:
    existing_transcript = await PanelTranscript.fetch_from_supabase(
        supabase, request_data.id
    )
    if not existing_transcript:
        raise ValueError("Panel transcript not found")

    for key, value in request_data.model_dump(exclude_unset=False).items():
        setattr(existing_transcript, key, value)

    await existing_transcript.update(supabase)
    return existing_transcript


async def update_panel_audio(
    supabase: AsyncClient, request_data: PanelAudio
) -> PanelAudio:
    existing_audio = await PanelAudio.fetch_from_supabase(supabase, request_data.id)
    if not existing_audio:
        raise ValueError("Panel audio not found")

    for key, value in request_data.model_dump(exclude_unset=False).items():
        setattr(existing_audio, key, value)

    await existing_audio.update(supabase)
    return existing_audio
