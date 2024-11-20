from fastapi import HTTPException

from lib.load_env import IN_PRODUCTION


def handle_exception(e: Exception, default_message: str, status_code: int = 500):
    if isinstance(e, HTTPException):
        return e
    if not IN_PRODUCTION:
        raise e
    else:
        return HTTPException(status_code=status_code, detail=default_message)
