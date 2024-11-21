from fastapi import HTTPException
from postgrest import APIError
from pydantic import ValidationError
from supabase import AuthApiError

from lib.load_env import IN_PRODUCTION


def handle_exception(e: Exception, default_message: str, status_code: int = None):
    print("error", e)
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
