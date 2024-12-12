import aiohttp
import asyncio
from functools import wraps
from celery import Celery, Task
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar
from asgiref import sync

from lib.load_env import SETTINGS

_P = ParamSpec("_P")
_R = TypeVar("_R")

# from lib.models.config.logging import logger

# Initialize Celery with Redis settings from SETTINGS
celery_app = Celery(
    "tc_compute_api",
    broker=SETTINGS.redis_broker_url,
    backend=SETTINGS.redis_backend_url,
    # log=logger,
)

# Update Celery configuration with Celery and Flower host and port
celery_app.conf.update(
    result_expires=3600,
    broker_transport_options={
        "visibility_timeout": 3600,
        "host": SETTINGS.celery_host,
        "port": SETTINGS.celery_port,
    },
    flower_host=SETTINGS.flower_host,
    flower_port=SETTINGS.flower_port,
)

if __name__ == "__main__":
    celery_app.start()


async def check_task_status(task_id: str) -> str:
    """
    Asynchronously check the status of a Celery task using Flower.

    Args:
        task_id (str): The ID of the Celery task.

    Returns:
        str: The status of the task.
    """
    flower_url = f"http://{SETTINGS.flower_host}:{SETTINGS.flower_port}"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{flower_url}/api/task/info/{task_id}") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("state", "Unknown")
            return "Error"


def async_task(app: Celery, *args: Any, **kwargs: Any):
    def _decorator(func: Callable[_P, Coroutine[Any, Any, _R]]) -> Task:
        sync_call = sync.AsyncToSync(func)

        @app.task(*args, **kwargs)
        @wraps(func)
        def _decorated(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return sync_call(*args, **kwargs)

        return _decorated

    return _decorator


@async_task(celery_app, bind=True)
async def test_task(self: Task):
    """
    A simple asynchronous test task for Celery that takes 10 seconds to complete.

    Returns:
        str: A message indicating the task was executed.
    """
    await asyncio.sleep(10)  # Simulate a delay of 10 seconds
    return "Test task executed successfully!"
