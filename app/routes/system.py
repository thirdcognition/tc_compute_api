from fastapi import APIRouter, HTTPException
from app.core.celery_app import check_task_status

router = APIRouter()


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
