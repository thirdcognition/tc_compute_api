import requests
from typing import List
from supabase import Client
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_service_client
from source.load_env import SETTINGS

# from source.models.config.logging import logger
from postgrest.base_request_builder import APIResponse

from source.prompts.panel import TranscriptSummary


# Assuming a function to get the Supabase client
def get_supabase_client() -> Client:
    # Implementation to get the Supabase client
    pass


def send_email_about_new_shows(panels: List[str]):
    if not SETTINGS.send_emails:
        print("Email sending is disabled.")
        return

    supabase = get_sync_supabase_service_client()
    # Fetch all users
    users: APIResponse = (
        supabase.from_("user_profile")
        .select("id, name, email, organization_users(user_id, organization_id)")
        .eq("organization_users.organization_id", SETTINGS.tc_org_id)
        .execute()
    )
    # for user in users.data:
    #     email = user["email"]
    #     # Logic to send email
    #     # email = "markus@thirdcognition.com"
    #     # if email == "markus@thirdcognition.com":
    email = ", ".join(
        (user["email"] if user is not None and user["email"] is not None else "")
        for user in users.data
        if user is not None and user["email"] is not None
    )
    if email is not None:
        send_new_shows_email_task.delay(email, panels)


@celery_app.task
def send_new_shows_email_task(email: str, panels: List[str]):
    print(f"{email=}")
    if not SETTINGS.send_emails:
        print("Email sending is disabled.")
        return

    if email is None or len(panels) == 0:
        print("No email defined or length of panels is 0, skipping email sending")
        return

    print(f"Send email to {email=} for {panels=}")

    api_key = SETTINGS.resend_api_key
    url = "https://api.resend.com/emails"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    formatted_panels = [
        f'<a href="https://show.thirdcognition.app/admin/panel/{panel.split(": ")[0]}">{panel.split(": ")[1]}</a>'
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


def send_email_to_mailchimp_group(
    transcript_summary: TranscriptSummary, list_id: str, template_id: str
):
    if not SETTINGS.enable_mailchimp:
        print("Mailchimp integration is disabled.")
        return

    client = MailchimpMarketing.Client()
    client.set_config(
        {
            "api_key": SETTINGS.mailchimp_api_key,
            "server": SETTINGS.mailchimp_server_prefix,
        }
    )

    # Extract fields from TranscriptSummary
    episode_title = transcript_summary.title
    episode_summary = transcript_summary.description

    try:
        # Create campaign using a predefined template
        response = client.campaigns.create(
            {
                "type": "regular",
                "recipients": {"list_id": list_id},
                "settings": {
                    "subject_line": episode_title,
                    "title": episode_title,
                    "from_name": "Your Name",
                    "reply_to": "your-email@example.com",
                    "template_id": template_id,  # Use the provided template ID
                },
            }
        )

        # Populate specific fields in the template
        client.campaigns.set_content(
            response["id"],
            {
                "template": {
                    "id": template_id,
                    "sections": {
                        "episode_title": episode_title,  # Field for the episode title
                        "episode_summary": episode_summary,  # Field for the episode summary
                    },
                }
            },
        )

        print("Campaign created successfully: {}".format(response))
    except ApiClientError as error:
        print("An error occurred: {}".format(error.text))


@celery_app.task
def send_email_to_mailchimp_group_task(
    transcript_details: str, sources: List[str], list_id: str
):
    send_email_to_mailchimp_group(transcript_details, sources, list_id)
