import uuid
from app.core.celery_app import celery_app
from source.models.data.user import UserIDs
from source.models.data.web_source import WebSource
from app.core.supabase import get_sync_supabase_client, get_sync_supabase_service_client


@celery_app.task
def resolve_and_store_link_task(serialized_web_source, tokens, serialized_user_ids):
    """
    Resolve and store a link for a serialized WebSource.

    :param serialized_web_source: Serialized WebSource instance.
    :param tokens: Supabase tokens for authentication.
    :param user_ids: User IDs for task execution.
    :return: Result of the operation.
    """
    # Deserialize the WebSource instance
    web_source = WebSource.model_validate(serialized_web_source)
    user_ids = None
    if serialized_user_ids is not None:
        user_ids = UserIDs.model_validate(serialized_user_ids)

    # Recreate the Supabase client using tokens
    if tokens:
        supabase_client = get_sync_supabase_client(
            access_token=tokens[0], refresh_token=tokens[1]
        )
    else:
        supabase_client = get_sync_supabase_service_client()

    # Call resolve_and_store_link and return the result
    return web_source.resolve_and_store_link(supabase_client, user_ids)


def generate_resolve_tasks_for_websources(web_sources, tokens, user_ids):
    """
    Generate and execute Celery tasks for WebSource items.

    :param web_sources: List of WebSource items to process.
    :param supabase: The Supabase client instance.
    :param user_ids: User IDs for task execution.
    :return: Results of the executed tasks.
    """
    # Serialize WebSource items
    serialized_items = [item.model_dump() for item in web_sources]
    serialized_user_ids = user_ids.model_dump() if user_ids else None

    # Return a list of tasks for parallel execution
    tasks = []
    for item in serialized_items:
        try:
            # Generate a unique ID for the task using item's unique identifier
            item_id = str(uuid.uuid4())
            task_id = f"resolve_store_{item_id}"

            # Create the task and set a unique ID
            task = resolve_and_store_link_task.s(item, tokens, serialized_user_ids).set(
                task_id=task_id
            )
            tasks.append(task)
        except Exception as e:
            print(f"Failed to create task for item {item}: {e}")
    return tasks
