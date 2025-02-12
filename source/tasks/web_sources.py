from app.core.celery_app import celery_app
from app.core.supabase import get_supabase_tokens_sync
from source.models.data.web_source import WebSource
from app.core.supabase import get_sync_supabase_client


@celery_app.task
def resolve_and_store_link_task(serialized_web_source, tokens, user_ids):
    """
    Resolve and store a link for a serialized WebSource.

    :param serialized_web_source: Serialized WebSource instance.
    :param tokens: Supabase tokens for authentication.
    :param user_ids: User IDs for task execution.
    :return: Result of the operation.
    """
    # Deserialize the WebSource instance
    web_source = WebSource.model_validate(serialized_web_source)

    # Recreate the Supabase client using tokens
    supabase_client = get_sync_supabase_client(
        access_token=tokens[0], refresh_token=tokens[1]
    )

    # Call resolve_and_store_link and return the result
    return web_source.resolve_and_store_link(supabase_client, user_ids)


def generate_resolve_tasks_for_websources(web_sources, supabase, user_ids):
    """
    Generate and execute Celery tasks for WebSource items.

    :param web_sources: List of WebSource items to process.
    :param supabase: The Supabase client instance.
    :param user_ids: User IDs for task execution.
    :return: Results of the executed tasks.
    """
    # Serialize WebSource items
    serialized_items = [item.model_dump() for item in web_sources]

    # Extract tokens from the Supabase sync client
    tokens = get_supabase_tokens_sync(supabase)

    # Return a list of tasks for parallel execution
    return [
        resolve_and_store_link_task.s(item, tokens, user_ids)
        for item in serialized_items
    ]
