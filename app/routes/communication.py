from fastapi import APIRouter, HTTPException
from source.api.mailchimp.read import get_lists, get_templates

router = APIRouter()


@router.get("/communication/mailchimp/lists")
async def fetch_mailchimp_lists():
    """
    Endpoint to fetch available lists from Mailchimp.
    """
    try:
        return await get_lists()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/communication/mailchimp/templates")
async def fetch_mailchimp_templates():
    """
    Endpoint to fetch available templates from Mailchimp.
    """
    try:
        return await get_templates()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
