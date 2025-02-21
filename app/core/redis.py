import json
from pydantic import BaseModel
from functools import wraps
from pydoc import locate
from typing import Callable
from cachetools import TTLCache

import redis

from source.load_env import SETTINGS
from source.models.config.logging import logger

async_redis_client: redis.asyncio.Redis = None
sync_redis_client: redis.Redis = None


async def get_async_redis_client() -> redis.asyncio.Redis:
    global async_redis_client
    if async_redis_client is None:
        try:
            async_redis_client = redis.asyncio.from_url(
                SETTINGS.redis_broker_url, decode_responses=True
            )
            logger.info("Async Redis client initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing async Redis client: {e}")
            raise e
    return async_redis_client


def get_sync_redis_client() -> redis.Redis:
    global sync_redis_client
    if sync_redis_client is None:
        try:
            sync_redis_client = redis.Redis.from_url(
                SETTINGS.redis_broker_url, decode_responses=True
            )
            logger.info("Sync Redis client initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing sync Redis client: {e}")
            raise e
    return sync_redis_client


def serialize_object(obj):
    """Recursively serialize objects, including nested Pydantic models."""
    try:
        if isinstance(obj, BaseModel):
            return json.dumps(
                {
                    "__pydantic_model__": obj.__class__.__name__,
                    "data": obj.model_dump_json(),
                }
            )  # Pydantic v2 serialization with marker
        else:
            return obj
        # elif isinstance(obj, (list, tuple)):
        #     return json.dumps([serialize_object(item) for item in obj])
        # elif isinstance(obj, dict):
        #     return json.dumps(
        #         {key: serialize_object(value) for key, value in obj.items()}
        #     )
        # return json.dumps(obj)  # Fallback for non-Pydantic objects
    except (TypeError, ValueError) as e:
        logger.error(f"Serialization error: {e} for object: {obj}")
        raise


def deserialize_object(data):
    """Recursively deserialize JSON strings into Python objects."""
    if data is None or data == "":
        return None
    try:
        # If data is already a dictionary, process it directly
        if isinstance(data, dict):
            if "__pydantic_model__" in data:
                model_name = data["__pydantic_model__"]
                model_class = locate(model_name)
                if model_class and issubclass(model_class, BaseModel):
                    return model_class.model_validate_json(data["data"])
            # Process nested dictionaries
            return {key: deserialize_object(value) for key, value in data.items()}
        # If data is a list, process each item
        if isinstance(data, list):
            return [deserialize_object(item) for item in data]
        # If data is a JSON string, parse it

        return data
    except AttributeError as e:
        logger.error(f"Attribute error during deserialization: {e} for data: {data}")
        return data
    except Exception as e:
        logger.error(f"Unexpected deserialization error: {e} for data: {data}")
        return data


def async_memoize(ttl: int = 60):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = (
                f"{func.__name__}:{serialize_object(args)}:{serialize_object(kwargs)}"
            )
            redis_client = await get_async_redis_client()
            cached_value = await redis_client.get(cache_key)
            if cached_value:
                logger.info(f"Cache hit for key: {cache_key}")
                return deserialize_object(cached_value)
            logger.info(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            await redis_client.set(cache_key, serialize_object(result), ex=ttl)
            return result

        return wrapper

    return decorator


# Sync memoization decorator
def sync_memoize(ttl: int = 60):
    def decorator(func: Callable):
        cache = TTLCache(maxsize=100, ttl=ttl)

        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = (
                f"{func.__name__}:{serialize_object(args)}:{serialize_object(kwargs)}"
            )
            redis_client = get_sync_redis_client()
            if cache_key in cache:
                print(f"Cache hit (in-memory) for key: {cache_key}")
                return cache[cache_key]
            cached_value = redis_client.get(cache_key)
            if cached_value:
                print(f"Cache hit (Redis) for key: {cache_key}")
                result = deserialize_object(cached_value)
                cache[cache_key] = result
                return result
            print(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)
            redis_client.set(cache_key, serialize_object(result), ex=ttl)
            cache[cache_key] = result
            return result

        return wrapper

    return decorator
