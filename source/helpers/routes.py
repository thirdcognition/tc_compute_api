from fastapi import HTTPException
from postgrest import APIError
from pydantic import ValidationError
from supabase import AuthApiError

from source.models.config.default_env import IN_PRODUCTION
from source.models.config.logging import logger


def handle_exception(e: Exception, default_message: str, status_code: int = None):
    logger.error("error %s", e)
    if (
        isinstance(e, ValidationError)
        or isinstance(e, AuthApiError)
        or isinstance(e, ValueError)
        or isinstance(e, APIError)
    ):
        if not isinstance(e, APIError):
            status_code = status_code or 400
        else:
            status_code = status_code or 403

        if not IN_PRODUCTION:
            return HTTPException(status_code=status_code, detail=str(e))
        else:
            return HTTPException(status_code=status_code, detail=default_message)
    if isinstance(e, HTTPException):
        return e
    if not IN_PRODUCTION:
        raise e
    else:
        status_code = status_code or 500
        return HTTPException(status_code=status_code, detail=default_message)
