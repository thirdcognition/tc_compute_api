from fastapi import APIRouter, HTTPException
from source.api.mailchimp.read import get_lists, get_templates
from source.helpers.communication import send_email_about_new_shows_task

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


@router.post("/communication/send-transcript-email")
async def send_email_about_new_shows(transcript_ids: list[str]):
    """
    Endpoint to send an email about specified transcript IDs.
    """
    try:
        send_email_about_new_shows_task.delay(transcript_ids)
        return {"message": "Email task initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
