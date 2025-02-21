from cachetools import TTLCache

from fastapi import HTTPException
from supabase.client import AsyncClient, create_async_client, Client
from supabase import ClientOptions, create_client
from typing import Dict, Any, Optional

from source.load_env import SETTINGS
from source.models.config.logging import logger


async def get_supabase_client(
    access_token: str | None = None, custom_options: dict = None
) -> AsyncClient:
    options = ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=10,
        flow_type="pkce",
        persist_session=True,
    )
    if access_token:
        options.headers = {"Authorization": f"Bearer {access_token}"}

    # Update options with custom_options if provided
    if custom_options:
        options_dict = vars(options)  # Convert options to a dictionary
        options_dict.update(custom_options)
        options = ClientOptions(**options_dict)  # Recreate options with updated dict

    return await create_async_client(
        SETTINGS.supabase_url,
        SETTINGS.supabase_key,
        options=options,
    )


def get_sync_supabase_client(
    access_token: str | None = None, custom_options: dict = None
) -> Client:
    options = ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=10,
        flow_type="pkce",
        persist_session=True,
    )
    if access_token:
        options.headers = {"Authorization": f"Bearer {access_token}"}

    # Update options with custom_options if provided
    if custom_options:
        options_dict = vars(options)  # Convert options to a dictionary
        options_dict.update(custom_options)
        options = ClientOptions(**options_dict)  # Recreate options with updated dict

    try:
        return create_client(
            SETTINGS.supabase_url,
            SETTINGS.supabase_key,
            options=options,
        )
    except Exception as e:
        logger.debug(f"{options=}")
        logger.error(f"error while creating sync client {e=}")
        raise e


class SessionStorage:
    sync_supabase_client: Optional[Client] = None
    storage: Dict[str, Any] = {}

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    code: Optional[str] = None
    redirect: Optional[str] = None

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        code: Optional[str] = None,
        redirect: Optional[str] = None,
        supabase_client: Optional[AsyncClient] = None,
        sync_supabase_client: Optional[Client] = None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.code = code
        self.redirect = redirect
        self.supabase_client = supabase_client
        self.sync_supabase_client = sync_supabase_client
        self.storage = {}

    async def get_supabase_client(self) -> AsyncClient:
        if self.supabase_client is None:
            try:
                self.supabase_client = await get_supabase_client(self.access_token)
            except Exception as e:
                logger.error(e)
                raise e
            auth_resp = await self.supabase_client.auth.set_session(
                access_token=self.access_token, refresh_token=self.refresh_token
            )
            self.access_token = (
                auth_resp.session.access_token
                if auth_resp.session.access_token is not None
                else self.access_token
            )
            self.refresh_token = (
                auth_resp.session.refresh_token
                if auth_resp.session.refresh_token is not None
                else self.refresh_token
            )

        return self.supabase_client

    def get_sync_supabase_client(self) -> Client:
        if self.sync_supabase_client is None:
            self.sync_supabase_client = get_sync_supabase_client(self.access_token)
            try:
                logger.debug(f"tokens {self.access_token=} {self.refresh_token=}")
                logger.debug(f"client {self.sync_supabase_client=}")
                auth_resp = self.sync_supabase_client.auth.set_session(
                    access_token=self.access_token, refresh_token=self.refresh_token
                )
                logger.debug(f"{auth_resp=}")
                self.access_token = (
                    auth_resp.session.access_token
                    if auth_resp.session.access_token is not None
                    else self.access_token
                )
                self.refresh_token = (
                    auth_resp.session.refresh_token
                    if auth_resp.session.refresh_token is not None
                    else self.refresh_token
                )
            except Exception as e:
                logger.error(f"error while initializing storage client {e=}")
                raise e
        return self.sync_supabase_client

    def get(self, key: str, default: Any = None) -> Any:
        return self.storage.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.storage[key] = value


storage_cache: TTLCache[str, SessionStorage] = TTLCache(maxsize=1000, ttl=3600)


def get_storage(
    access_token: str,
    refresh_token: Optional[str] = None,
    code: Optional[str] = None,
    redirect: Optional[str] = None,
    supabase_client: Optional[AsyncClient] = None,
    sync_supabase_client: Optional[Client] = None,
) -> SessionStorage:
    global storage_cache

    if access_token not in storage_cache:
        logger.info(
            f"Initializing new storage for {access_token=} {refresh_token=} {code=}"
        )
        if (
            refresh_token is None
            and code is None
            and supabase_client is None
            and sync_supabase_client is None
        ):
            raise HTTPException(
                status_code=401,
                detail="Unauthorized access: a refresh token, code, or client is required to initialize the session.",
            )

        storage_cache[access_token] = SessionStorage(
            access_token=access_token,
            refresh_token=refresh_token,
            code=code,
            redirect=redirect,
            supabase_client=supabase_client,
            sync_supabase_client=sync_supabase_client,
        )
    else:
        logger.info(
            f"Loading existing storage for {access_token=} {refresh_token=} {code=}"
        )
        storage_cache[access_token].access_token = (
            access_token
            if access_token is not None
            else storage_cache[access_token].access_token
        )
        storage_cache[access_token].refresh_token = (
            refresh_token
            if refresh_token is not None
            else storage_cache[access_token].refresh_token
        )
    return storage_cache[access_token]


async def clean_storage(access_token: str) -> None:
    global storage_cache
    if access_token in storage_cache:
        session_storage: Optional[SessionStorage] = storage_cache[access_token]
        if session_storage.supabase_client is not None:
            try:
                await session_storage.supabase_client.auth.sign_out()
                del storage_cache[access_token]
            except Exception as e:
                logger.error(f"Error while signing out and cleaning storage: {e}")
