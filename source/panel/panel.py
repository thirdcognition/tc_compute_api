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

    EXCLUDED_KEYS = [
        "title",
        "bucket_name",
        "panel_id",
        "transcript_parent_id",
        "transcript_id",
        "cronjob",
        "owner_id",
        "organization_id",
    ]

    # Dump all fields from the Pydantic model and filter while looping
    for key, value in request_data.model_dump().items():
        if key not in EXCLUDED_KEYS and value is not None:
            # If the field has a `model_dump` method, serialize it; otherwise, use the raw value
            metadata[key] = (
                value.model_dump() if hasattr(value, "model_dump") else value
            )

    panel: PanelDiscussion = PanelDiscussion(
        title=request_data.title,
        metadata=metadata,
        is_public=request_data.is_public,
        owner_id=request_data.owner_id,
        organization_id=request_data.organization_id,
    )
    print(f"Panel created with metadata: {metadata}")
    panel.create_sync(supabase=supabase_client)
    print(f"Panel ID: {panel.id}")

    return panel.id
