from fastapi import APIRouter, HTTPException
from app.core.celery_app import check_task_status, test_task
from app.core.supabase import excempt_from_auth_check_with_prefix

router = APIRouter()

excempt_from_auth_check_with_prefix("/system/task_status/", ["GET"])


@router.get("/system/task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Endpoint to get the status of a Celery task.

    Args:
        task_id (str): The ID of the Celery task.

    Returns:
        str: The status of the task.
    """
    status = await check_task_status(task_id)
    if status == "Error":
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": status}


@router.post("/system/start_test_task")
async def start_test_task():
    """
    Endpoint to start the test task.

    Returns:
        str: The ID of the started task.
    """
    task = test_task.delay()
    return {"task_id": task.id}
