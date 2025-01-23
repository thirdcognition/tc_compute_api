from typing import Tuple
from uuid import UUID
from supabase import Client
from celery.worker.request import Request
from app.core.supabase import get_sync_supabase_client
from source.models.config.logging import logger
from source.models.supabase.panel import PanelDiscussion
from source.models.structures.panel import PanelRequestData


def create_panel(
    tokens: Tuple[str, str],
    request_data: PanelRequestData,
    task_request: Request = None,
    supabase_client: Client = None,
) -> UUID:
    print(f"Creating panel with tokens request data: {request_data}")
    supabase_client = (
        supabase_client
        if supabase_client is not None
        else get_sync_supabase_client(access_token=tokens[0], refresh_token=tokens[1])
    )
    logger.debug(f"create public panel {tokens=}")
    try:
        supabase_client = get_sync_supabase_client(
            access_token=tokens[0], refresh_token=tokens[1]
        )
    except Exception as e:
        logger.error(e)

    logger.debug(f"supa sesssion {supabase_client.auth.get_session()=}")

    # Initialize metadata with task_id if available
    metadata = {"task_id": task_request.id} if task_request else {}

    # Add additional fields to metadata if they are defined
    if request_data.conversation_config:
        metadata["conversation_config"] = request_data.conversation_config
    if request_data.tts_model:
        metadata["tts_model"] = request_data.tts_model
    if request_data.input_source:
        metadata["urls"] = request_data.input_source
    if request_data.longform is not None:
        metadata["longform"] = request_data.longform
    if request_data.input_text:
        metadata["input_text"] = request_data.input_text

    if request_data.google_news:
        metadata["google_news"] = request_data.google_news

    if request_data.yle_news:
        metadata["yle_news"] = request_data.yle_news

    if request_data.techcrunch_news:
        metadata["techcrunch_news"] = request_data.techcrunch_news

    if request_data.hackernews:
        metadata["hackernews"] = request_data.hackernews

    panel: PanelDiscussion = PanelDiscussion(
        title=request_data.title,
        metadata=metadata,
        is_public=True,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    print(f"Panel created with metadata: {metadata}")
    panel.create_sync(supabase=supabase_client)
    print(f"Panel ID: {panel.id}")

    return panel.id
