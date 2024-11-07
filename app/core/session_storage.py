from cachetools import TTLCache
from fastapi import HTTPException
from supabase.client import AsyncClient, create_async_client
from supabase import ClientOptions

# from gotrue.types import CodeExchangeParams

from typing import Dict, Any, Optional

from lib.load_env import SETTINGS, logger


async def get_supabase_client(access_token: str | None = None) -> AsyncClient:
    options = ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=10,
        flow_type="pkce",
        persist_session=True,
    )
    if access_token:
        options.headers = {"Authorization": f"Bearer {access_token}"}

    return await create_async_client(
        SETTINGS.supabase_url,
        SETTINGS.supabase_key,
        options=options,
    )


class SessionStorage:
    """
    A class used to store session data for a user.

    Attributes
    ----------
    access_token : str
        The access token for the session.
    refresh_token : str
        The refresh token for the session.
    supabase_client : AsyncClient | None
        The Supabase client for the session.
    storage : dict
        A dictionary to store additional session data.
    code : str | None
        The code for the session.
    redirect : str | None
        The redirect URL for the session.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        code: Optional[str] = None,
        redirect: Optional[str] = None,
        supabase_client: Optional[AsyncClient] = None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.code = code
        self.redirect = redirect
        self.supabase_client: Optional[AsyncClient] = supabase_client
        self.storage: Dict[str, Any] = {}

    async def get_supabase_client(self) -> AsyncClient:
        """
        Get the Supabase client for the session.

        If the client does not exist, it will be created using the access token,
        refresh token, and code (if provided).

        Returns
        -------
        AsyncClient
            The Supabase client for the session.
        """
        if self.supabase_client is None:
            self.supabase_client = await get_supabase_client(self.access_token)
            # Code just doesn't work as expected
            # if self.code is not None:
            #     await self.supabase_client.auth.exchange_code_for_session
            # (CodeExchangeParams(code_verifier=self.access_token, auth_code=self.code,
            # redirect_to=self.redirect))
            # else:
            await self.supabase_client.auth.set_session(
                access_token=self.access_token, refresh_token=self.refresh_token
            )
        return self.supabase_client

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the storage dictionary.

        Parameters
        ----------
        key : str
            The key to retrieve the value for.
        default : Any, optional
            The default value to return if the key is not found, by default None.

        Returns
        -------
        Any
            The value associated with the key, or the default value if
            the key is not found.
        """
        return self.storage.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the storage dictionary.

        Parameters
        ----------
        key : str
            The key to set the value for.
        value : Any
            The value to set.
        """
        self.storage[key] = value


# Create a cache with a TTL of 1 hour
storage_cache: TTLCache[str, SessionStorage] = TTLCache(maxsize=1000, ttl=3600)
# there should be a way to clean old auths, but maybe it's not required.
# Anyhow clean_storage is the function to use for it if implemented.

# Assuming SessionStorage and storage_cache are defined elsewhere


def get_storage(
    access_token: str,
    refresh_token: Optional[str] = None,
    code: Optional[str] = None,
    redirect: Optional[str] = None,
    supabase_client: Optional[AsyncClient] = None,
) -> SessionStorage:
    """
    Get the SessionStorage for the given access token.

    If the access token is not in the storage cache, a new SessionStorage
    object will be created and added to the cache. If the refresh token and
    code are not provided, an exception will be raised.

    Parameters
    ----------
    access_token : str
        The access token for the session.
    refresh_token : str, optional
        The refresh token for the session, by default None.
    code : str, optional
        The code for the session, by default None.
    redirect : str, optional
        The redirect URL for the session, by default None.
    supabase_client : AsyncClient, optional
        The supabase client for handling database connections.

    Returns
    -------
    SessionStorage
        The SessionStorage object for the given access token.

    Raises
    ------
    HTTPException
        If the refresh token, code, or supabase_client are not provided when the
        session hasn't been initialized.
    """
    global storage_cache

    if access_token not in storage_cache:
        if refresh_token is None and code is None and supabase_client is None:
            raise HTTPException(
                status_code=401,  # Unauthorized
                detail="Unauthorized access: a refresh token, code, or client is required to initialize the session.",
            )

        storage_cache[access_token] = SessionStorage(
            access_token=access_token,
            refresh_token=refresh_token,
            code=code,
            redirect=redirect,
            supabase_client=supabase_client,
        )
    return storage_cache[access_token]


async def clean_storage(access_token: str) -> None:
    """
    Clean the storage for the given access token.

    If the access token is in the storage cache and the Supabase client is not None,
    the client will be signed out and the corresponding SessionStorage object will be removed from the cache.

    Parameters
    ----------
    access_token : str
        The access token for the session.
    """
    global storage_cache
    if access_token in storage_cache:
        session_storage: Optional[SessionStorage] = storage_cache[access_token]
        if session_storage.supabase_client is not None:
            try:
                await session_storage.supabase_client.auth.sign_out()
                del storage_cache[access_token]
            except Exception as e:
                logger.error(f"Error while signing out and cleaning storage: {e}")


# async def get_storage(supabase_client: AsyncClient) -> SessionStorage:
#     """
#     Get the SessionStorage for the given Supabase client.

#     This function retrieves the session from the Supabase client, extracts the access token,
#     and checks if a corresponding SessionStorage object exists in the storage cache.
#     If it does, the function returns the SessionStorage object.
#     If it doesn't, the function raises an exception.

#     Parameters
#     ----------
#     supabase_client : AsyncClient
#         The Supabase client for the session.

#     Returns
#     -------
#     SessionStorage
#         The SessionStorage object for the given Supabase client.

#     Raises
#     ------
#     Exception
#         If no storage is found for the given access token.
#     """
#     global storage_cache
#     session = await supabase_client.auth.get_session()
#     access_token = session.access_token
#     if access_token in storage_cache:
#         return storage_cache[access_token]
#     else:
#         raise Exception("No storage found for the given access token")
