import aiohttp
import asyncio
from functools import wraps
from celery import Celery, Task
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar
from celery.schedules import crontab
from asgiref import sync
from source.load_env import SETTINGS

_P = ParamSpec("_P")

_R = TypeVar("_R")

# from source.models.config.logging import logger

# Initialize Celery with Redis settings from SETTINGS
celery_app = Celery(
    "tc_compute_api",
    broker=SETTINGS.redis_broker_url,
    backend=SETTINGS.redis_backend_url,
    include=["source.helpers.panel", "source.helpers.communication"],
    # log=logger,
)

# Update Celery configuration with Celery and Flower host and port
celery_app.conf.update(
    result_expires=3600,
    broker_transport_options={
        "visibility_timeout": 3600,
        "host": SETTINGS.celery_host,
        "port": SETTINGS.celery_port,
        "retry_on_startup": True,
    },
    broker_connection_retry_on_startup=True,
    worker_log_format="%(processName)s - %(levelname)s: %(asctime)s| %(message)s",
    worker_task_log_format="%(processName)s - %(levelname)s: %(asctime)s| %(message)s",
    flower_host=SETTINGS.flower_host,
    flower_port=SETTINGS.flower_port,
)

# Schedule the generate_transcripts_task to run daily at 9am
celery_app.conf.beat_schedule = {
    "generate-transcripts-every-day-at-9am": {
        "task": "source.helpers.panel.generate_transcripts_task",
        "schedule": crontab(hour=8, minute=15),
        "args": ("",),  # Replace with actual access token if needed
    },
}

celery_app.conf.timezone = "UTC"

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
            print(response)
            if response.status == 200:
                data = await response.json()
                return data.get("state", "Unknown")
            return "Error"


# def ensure_event_loop(func):
#     def wrapper(*args, **kwargs):
#         try:
#             try:
#                 loop = asyncio.get_event_loop()
#             except RuntimeError:
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)

#             return loop.run_until_complete(asyncio.ensure_future(func(*args, **kwargs)))

#         finally:
#             # Properly close the loop
#             loop.close()

#     # This ensures the resulting function after decorating retains important properties
#     wrapper.__name__ = func.__name__
#     wrapper.__doc__ = func.__doc__

#     return wrapper


# def async_task(app: Celery, *args: Any, **kwargs: Any):
#     def _decorator(func: Callable[_P, Coroutine[Any, Any, _R]]) -> Task:
#         sync_call = sync.AsyncToSync(func)

#         @app.task(*args, **kwargs)
#         @wraps(func)
#         def _decorated(*args: _P.args, **kwargs: _P.kwargs) -> _R:
#             return sync_call(*args, **kwargs)

#         return _decorated

#     return _decorator


def async_task(app: Celery, *args: Any, **kwargs: Any):
    def _decorator(func: Callable[_P, Coroutine[Any, Any, _R]]) -> Task:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            if loop.is_running():
                return await func(*args, **kwargs)
            else:
                return await loop.run_until_complete(
                    asyncio.ensure_future(func(*args, **kwargs))
                )

        sync_call = sync.AsyncToSync(wrapper)

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
