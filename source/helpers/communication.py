import requests
from typing import List
from supabase import Client

from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_service_client
from source.load_env import SETTINGS

# from source.models.config.logging import logger
from postgrest.base_request_builder import APIResponse


# Assuming a function to get the Supabase client
def get_supabase_client() -> Client:
    # Implementation to get the Supabase client
    pass


def send_email_about_new_shows(panels: List[str]):
    supabase = get_sync_supabase_service_client()
    # Fetch all users
    users: APIResponse = (
        supabase.from_("user_profile")
        .select("id, name, email, organization_users(user_id, organization_id)")
        .eq("organization_users.organization_id", SETTINGS.tc_org_id)
        .execute()
    )
    for user in users.data:
        email = user["email"]
        # Logic to send email
        # email = "markus@thirdcognition.com"
        # if email == "markus@thirdcognition.com":
        send_new_shows_email_task.delay(email, panels)


@celery_app.task
def send_new_shows_email_task(email: str, panels: List[str]):
    # print(f"Send email to {email=}")
    # return

    api_key = SETTINGS.resend_api_key
    url = "https://api.resend.com/emails"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    formatted_panels = [
        f'<a href="https://show.thirdcognition.app/morning_show/panel/{panel.split(": ")[0]}">{panel.split(": ")[1]}</a>'
        for panel in panels
    ]
    data = {
        "to": email,
        "from": "show@thirdcognition.app",
        "subject": "New Morning Shows Available",
        "html": f"<p>These shows were generated today:</p><ul>{''.join(f'<li>{panel}</li>' for panel in formatted_panels)}</ul>",
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Email sent to {email}")
    else:
        print(f"Failed to send email to {email}: {response.text}")


# Celery task
@celery_app.task
def send_email_about_new_shows_task(panels: list[str]):
    send_email_about_new_shows(panels)
