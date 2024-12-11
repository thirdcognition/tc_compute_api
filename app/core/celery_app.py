from celery import Celery
import aiohttp
from lib.load_env import SETTINGS

# from lib.models.config.logging import logger

# Initialize Celery with Redis settings from SETTINGS
app = Celery(
    "tc_compute_api",
    broker=SETTINGS.redis_broker_url,
    backend=SETTINGS.redis_backend_url,
    # log=logger,
)

# Update Celery configuration with Celery and Flower host and port
app.conf.update(
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
    app.start()


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
