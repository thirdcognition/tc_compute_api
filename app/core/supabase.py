import json
import time
from typing import Annotated, AsyncGenerator, Any, Awaitable, Callable, Optional, Tuple

from app.core.session_storage import SessionStorage, get_storage
from supabase.client import AsyncClient, create_async_client
from supabase import ClientOptions
from supabase_auth.types import Session
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from supabase_auth.errors import AuthApiError
from supabase.client import AsyncClient

from lib.load_env import SETTINGS, logger

get_oauth2: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="please login by supabase-js to get token"
)
AccessTokenDep = Annotated[str, Depends(get_oauth2)]

_service_client: AsyncClient | None = None

async def get_supabase_service_client() -> AsyncGenerator[AsyncClient, None]:
    opt=ClientOptions(
        auto_refresh_token=False,
        persist_session=False,
    )
    global _service_client
    try:
        resetClient = False
        session:Session = None
        if (_service_client):
            try:
                session = await _service_client.auth.get_session()
            except Exception as e:
                logger.error(e)
                resetClient = True

        if (not _service_client or resetClient or (session and session.expires_at < int(time.time()))):
            _service_client = await create_async_client(SETTINGS.supabase_url, SETTINGS.supabase_service_key, opt)

        yield _service_client
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Failed to get supabase service client"
        )


async def _get_supabase_client(
    access_token: AccessTokenDep,
) -> AsyncGenerator[AsyncClient, None]:
    try:
        supabase_client:AsyncClient = await get_storage(access_token).get_supabase_client()

        yield supabase_client

    except AuthApiError as e:
        logger.error(e)
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    # don't signout user automatically, it's up to the user to signout
    # finally:
    #     if supabase_client:
    #         await supabase_client.auth.sign_out()

async def get_supabase_client_by_request(request: Request) -> Tuple[Optional[AsyncClient], Optional[SessionStorage]]:
    """
    This function extracts access token, refresh token, and code from the request headers or query parameters.
    It then uses these tokens to get a session storage and a supabase client.

    :param request: The incoming request object.
    :return: A tuple containing the supabase client and the session storage, if they are successfully retrieved.
    """
    authorization_header: Optional[str] = request.headers.get("Authorization")
    refresh_header: Optional[str] = request.headers.get("Refresh-Authorization")
    code_header: Optional[str] = request.headers.get("Auth-Code")

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    code: Optional[str] = None
    redirect: Optional[str] = None

    # Extract access token, refresh token, and code from headers or query parameters
    if authorization_header:
        _, __, access_token = authorization_header.partition(" ")

    if refresh_header:
        _, __, refresh_token = refresh_header.partition(" ")



    if 'code' in request.query_params:
        redirect = f"{request.url.scheme}://{request.url.netloc}{request.url.path.split('?')[0]}"

        if code_header:
            _, __, code = code_header.partition(" ")
        elif request.query_params.get("code"):
            code = request.query_params.get("code")

        logger.debug(f"Extracted tokens: {access_token =} {refresh_token =} {code =}")

    # Get session storage and supabase client
    store: SessionStorage = get_storage(access_token, refresh_token, code, redirect)
    supabase_client: AsyncClient = await store.get_supabase_client()

    return supabase_client, store


async def supabase_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Middleware function to handle Supabase authentication.

    :param request: The incoming request object.
    :param call_next: The next middleware or route handler in the chain.
    :return: The response object.
    """
    # Skip auth check for CORS preflight requests and /auth/login.
    if request.method == "OPTIONS" and request.headers.get("access-control-request-method") or request.url.path == "/auth/login":
        return await call_next(request)

    supabase_client: AsyncClient | None = None
    try:
        supabase_client, _ = await get_supabase_client_by_request(request)
    except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        raise e

    try:
        session = None
        if supabase_client:
            session = await supabase_client.auth.get_session()

        if session is None or session.user is None:
            return JSONResponse(
                status_code=401, content={"error": "Invalid authentication credentials"}
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    print(f"Properly authenticated user {session.user.id}")

    if request.headers.get('content-type') == 'application/json':
        request_data = await request.json()
        if "input" in request_data:
            request_data["input"]["tokens"] = {
                "access": session.access_token,
                "refresh": session.refresh_token,
            }
            request._body = json.dumps(request_data).encode("utf-8")

    response = await call_next(request)
    # response.headers["Authorization"] = f"Bearer {session.access_token}"
    return response


SupaClientDep = Annotated[AsyncClient, Depends(_get_supabase_client)]
