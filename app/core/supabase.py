import json
import time
from typing import Annotated, AsyncGenerator, Awaitable, Callable, Optional, Tuple

from app.core.session_storage import SessionStorage, get_storage, get_supabase_client
from supabase.client import AsyncClient, create_async_client, Client, create_client
from supabase import ClientOptions
from supabase_auth.types import Session
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from supabase_auth.errors import AuthApiError

from source.load_env import SETTINGS
from source.models.config.logging import logger

anon_paths = []
exception_paths = []
exception_path_starts = []


def allow_anonymous_login(path: str, methods: list):
    global anon_paths
    logger.info(f"Allow anonymous login for {path}, using {methods=}")
    anon_paths.append((path, methods))


def excempt_from_auth_check(path: str, methods: list):
    global exception_paths
    logger.info(f"Excemption of auth for {path}, using {methods=}")
    exception_paths.append((path, methods))


def excempt_from_auth_check_with_prefix(prefix: str, methods: list):
    global exception_path_starts
    logger.info(
        f"Excemption of auth for paths starting with {prefix}, using {methods=}"
    )
    exception_path_starts.append((prefix, methods))


# Define existing paths using the utility methods


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        global anon_paths

        authorization: str = request.headers.get("Authorization")
        scheme, _, param = authorization.partition(" ")
        has_auth = scheme.lower() == "bearer" and bool(param)

        if not has_auth and any(
            request.url.path.startswith(path) and request.method in methods
            for path, methods in anon_paths
        ):
            return None
        return await super().__call__(request)


get_oauth2: CustomOAuth2PasswordBearer = CustomOAuth2PasswordBearer(
    tokenUrl="please login by supabase-js to get token"
)
AccessTokenDep = Annotated[str, Depends(get_oauth2)]

_service_client: AsyncClient | None = None
_sync_service_client: Client | None = None


async def get_supabase_service_client() -> AsyncClient:
    global _service_client
    opt = ClientOptions(
        auto_refresh_token=False,
        persist_session=False,
    )

    try:
        reset_client = False
        session = None

        if _service_client:
            try:
                session = await _service_client.auth.get_session()
            except Exception as e:
                logger.error(e)
                reset_client = True

        if (
            not _service_client
            or reset_client
            or (session and session.expires_at < int(time.time()))
        ):
            _service_client = await create_async_client(
                SETTINGS.supabase_url, SETTINGS.supabase_service_key, opt
            )

        return _service_client

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Failed to get supabase service client"
        )


def get_sync_supabase_service_client() -> Client:
    global _sync_service_client
    opt = ClientOptions(
        auto_refresh_token=False,
        persist_session=False,
    )

    try:
        reset_client = False
        session = None

        if _sync_service_client:
            try:
                session = _sync_service_client.auth.get_session()
            except Exception as e:
                logger.error(e)
                reset_client = True

        if (
            not _sync_service_client
            or reset_client
            or (session and session.expires_at < int(time.time()))
        ):
            _sync_service_client = create_client(
                SETTINGS.supabase_url, SETTINGS.supabase_service_key, opt
            )

        return _sync_service_client

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Failed to get supabase service client"
        )


async def get_supabase_service_client_dep() -> AsyncGenerator[AsyncClient, None]:
    opt = ClientOptions(
        auto_refresh_token=False,
        persist_session=False,
    )
    global _service_client
    try:
        resetClient = False
        session: Session = None
        if _service_client:
            try:
                session = await _service_client.auth.get_session()
            except Exception as e:
                logger.error(e)
                resetClient = True

        if (
            not _service_client
            or resetClient
            or (session and session.expires_at < int(time.time()))
        ):
            _service_client = await create_async_client(
                SETTINGS.supabase_url, SETTINGS.supabase_service_key, opt
            )

        yield _service_client
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500, detail="Failed to get supabase service client"
        )


anon_async_client: AsyncClient = None
anon_sync_client: Client = None


async def _get_supabase_client(
    access_token: AccessTokenDep,
) -> AsyncGenerator[AsyncClient, None]:
    try:
        if access_token is not None:
            supabase_client: AsyncClient = await get_storage(
                access_token
            ).get_supabase_client()

            yield supabase_client
        else:
            global anon_async_client
            yield anon_async_client

    except AuthApiError as e:
        logger.error(e)
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


async def get_supabase_tokens(supabase: AsyncClient) -> Tuple[str, str]:
    session = await supabase.auth.get_session()
    return session.access_token, session.refresh_token


def get_sync_supabase_client(access_token: str, refresh_token: str) -> Client:
    try:
        logger.info(f"Get sync session with {access_token=} {refresh_token=}")
        supabase_client: Client = get_storage(
            access_token, refresh_token
        ).get_sync_supabase_client()

        return supabase_client

    except AuthApiError as e:
        logger.error(e)
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


def get_supabase_tokens_sync(supabase: Client) -> Tuple[str, str]:
    session = supabase.auth.get_session()
    return session.access_token, session.refresh_token


async def get_supabase_client_by_request(
    request: Request, anon_paths=[]
) -> Tuple[Optional[AsyncClient], Optional[SessionStorage]]:
    # Check if the request is for the /panel path
    if any(
        request.url.path.startswith(path) and request.method in methods
        for path, methods in anon_paths
    ):
        # Initialize anonymous Supabase client for /panel path
        supabase_client = await get_supabase_client(
            None,
            {
                "auto_refresh_token": False,
                "persist_session": False,
            },
        )
        global anon_async_client
        await supabase_client.auth.sign_in_anonymously()
        anon_async_client = supabase_client

        return supabase_client, None

    authorization_header: Optional[str] = request.headers.get("Authorization")
    refresh_header: Optional[str] = request.headers.get("Refresh-Authorization")
    code_header: Optional[str] = request.headers.get("Auth-Code")

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    code: Optional[str] = None
    redirect: Optional[str] = None

    if authorization_header:
        _, __, access_token = authorization_header.partition(" ")

    if refresh_header:
        _, __, refresh_token = refresh_header.partition(" ")

    if "code" in request.query_params:
        redirect = f"{request.url.scheme}://{request.url.netloc}{request.url.path.split('?')[0]}"

        if code_header:
            _, __, code = code_header.partition(" ")
        elif request.query_params.get("code"):
            code = request.query_params.get("code")

        logger.debug(f"Extracted tokens: {access_token=} {refresh_token=} {code=}")

    store: SessionStorage = get_storage(access_token, refresh_token, code, redirect)
    supabase_client: AsyncClient = await store.get_supabase_client()

    return supabase_client, store


async def supabase_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Define lists for exceptional paths and methods
    global exception_paths
    global exception_path_starts
    global anon_paths

    # Check if the request is an exception
    if (
        request.method == "OPTIONS"
        and request.headers.get("access-control-request-method")
        or any(
            request.url.path == path and request.method in methods
            for path, methods in exception_paths
        )
        or any(
            request.url.path.startswith(prefix) and request.method in methods
            for prefix, methods in exception_path_starts
        )
    ):
        return await call_next(request)

    supabase_client: AsyncClient | None = None
    try:
        supabase_client, _ = await get_supabase_client_by_request(request, anon_paths)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        logger.error(f"Error occurred while getting supabase client: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
    try:
        session = None
        if supabase_client:
            session = await supabase_client.auth.get_session()

        if session is None or session.user is None:
            return JSONResponse(
                status_code=401, content={"error": "Invalid authentication credentials"}
            )
    except AuthApiError as e:
        logger.error(f"Error occurred while getting session: {str(e)}")
        return JSONResponse(
            status_code=401, content={"error": "Invalid authentication credentials"}
        )
    except Exception as e:
        logger.error(f"Error occurred while getting session: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

    logger.info(f"Properly authenticated user {session.user.id}")

    try:
        if request.headers.get("content-type") == "application/json":
            request_data = await request.json()
            if "input" in request_data:
                request_data["input"]["tokens"] = {
                    "access": session.access_token,
                    "refresh": session.refresh_token,
                }
                request._body = json.dumps(request_data).encode("utf-8")
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    response = await call_next(request)

    return response


SupaClientDep = Annotated[AsyncClient, Depends(_get_supabase_client)]
