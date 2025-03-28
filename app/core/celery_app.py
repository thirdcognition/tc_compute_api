# import json
import aiohttp
import asyncio
import logging
import logging.config
from functools import wraps
from celery import Celery, Task
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar
from celery.schedules import crontab
from asgiref import sync

# from source.models.config.default_env import IN_PRODUCTION
from source.load_env import SETTINGS
from source.models.config.logging import log_format, ColoredFormatter
from celery.signals import after_setup_logger

_P = ParamSpec("_P")

_R = TypeVar("_R")

celery_app = Celery(
    "tc_compute_api",
    broker=SETTINGS.redis_broker_url,
    backend=SETTINGS.redis_backend_url,
    include=[
        "source.panel.tasks",
        "source.helpers.communication",
        "source.helpers.push_notifications",
        "source.tasks.utils",
        "source.tasks.web_sources",
        "source.tasks.transcript",
    ],
    log="source.models.config.logging.CeleryLogger",
)

# Ensure all handlers use the ColoredFormatter


@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            ColoredFormatter(
                "%(processName)s - %(levelname)-8s: %(asctime)s| %(message)s"
            )
        )


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": ColoredFormatter,
                "format": "%(processName)s - %(levelname)-8s: %(asctime)s| %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
        },
        "loggers": {
            "celery": {
                "handlers": ["console"],
                "level": SETTINGS.log_level,
            },
            "celery.task": {
                "handlers": ["console"],
                "level": SETTINGS.log_level,
            },
        },
    }
)

for logger_name in ["celery", "celery.task"]:
    logger = logging.getLogger(logger_name)
    for handler in logger.handlers:
        handler.setFormatter(
            ColoredFormatter(
                "%(processName)s - %(levelname)-8s: %(asctime)s| %(message)s"
            )
        )

celery_app.conf.update(
    result_expires=3600,
    broker_transport_options={
        "visibility_timeout": 3600,
        "host": SETTINGS.celery_host,
        "port": SETTINGS.celery_port,
        "retry_on_startup": True,
    },
    broker_connection_retry_on_startup=True,
    worker_log_format=log_format._fmt,
    worker_task_log_format=log_format._fmt,
    flower_host=SETTINGS.flower_host,
    flower_port=SETTINGS.flower_port,
)

# Schedule the generate_transcripts_task to run daily at 9am
celery_app.conf.beat_schedule = {
    "generate-transcripts-every-1h": {
        "task": "source.panel.tasks.generate_transcripts_task",
        "schedule": crontab(hour="*/1", minute="0"),
        # "schedule": crontab(hour=4, minute=30),
        # "schedule": crontab(minute="*/30"),
        # "schedule": crontab(minute="*/2"),
        # if IN_PRODUCTION else crontab(minute="*/2"),
        "args": (
            None,
            True,
        ),
    },
    "send-push-notifications-1d": {
        "task": "source.helpers.push_notifications.task_send_push_notifications_for_new_tasks",
        "schedule": crontab(hour="8", minute="0"),
        # "schedule": crontab(hour=8, minute=0, day_of_week="1-5"), # Weekdays only
        "args": (
            None,
            True,
        ),
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
            logger.debug(response)
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
