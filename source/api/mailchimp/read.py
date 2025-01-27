from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from source.models.config.default_settings import Settings
from fastapi import HTTPException

settings = Settings()


def get_mailchimp_client():
    """
    Initialize and return a Mailchimp client.
    """
    if not settings.enable_mailchimp:
        raise HTTPException(
            status_code=400, detail="Mailchimp integration is disabled."
        )
    if not settings.mailchimp_api_key or not settings.mailchimp_server_prefix:
        raise HTTPException(
            status_code=400,
            detail="Mailchimp API key or server prefix is not configured.",
        )

    client = Client()
    client.set_config(
        {
            "api_key": settings.mailchimp_api_key,
            "server": settings.mailchimp_server_prefix,
        }
    )
    return client


async def get_lists():
    """
    Asynchronously fetch available lists from Mailchimp.
    """
    client = get_mailchimp_client()
    try:
        response = client.lists.get_all_lists()
        return response
    except ApiClientError as error:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch lists: {error.text}"
        )


async def get_templates():
    """
    Asynchronously fetch available templates from Mailchimp.
    """
    client = get_mailchimp_client()
    try:
        response = client.templates.list()
        return response
    except ApiClientError as error:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch templates: {error.text}"
        )
