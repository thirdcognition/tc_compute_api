import json
import os
from bs4 import BeautifulSoup
import resend
from typing import Any, List, Union
import base64
from supabase import Client
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_service_client
from source.load_env import SETTINGS
from source.models.config.default_env import DEFAULT_PATH
from source.models.config.email_config import EmailConfig

# from source.models.config.logging import logger
from postgrest.base_request_builder import APIResponse

from source.models.supabase.panel import (
    PanelDiscussion,
    PanelTranscript,
    PanelTranscriptSourceReference,
)
from source.prompts.panel import TranscriptSummary


# Assuming a function to get the Supabase client
def get_supabase_client() -> Client:
    # Implementation to get the Supabase client
    pass


def send_email_about_new_shows(transcript_ids: List[str]):
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
    email = [
        (user["email"] if user is not None and user["email"] is not None else "")
        for user in users.data
        if user is not None and user["email"] is not None
    ]
    # email = "markus@thirdcognition.com"
    if email is not None:
        send_new_shows_email_task.delay(email, transcript_ids)


def generate_email_from_template(
    supabase: Client,
    transcripts: Union[PanelTranscript, List[PanelTranscript]],
    config: EmailConfig,
) -> tuple[str, str, str]:
    """
    Generates the HTML and plain text content for the email.

    Args:
        supabase (Client): Supabase client for fetching additional data.
        transcripts (Union[PanelTranscript, List[PanelTranscript]]): Single or multiple PanelTranscript objects.
        config (EmailConfig): Configuration for the email.

    Returns:
        tuple[str, str, str]: A tuple containing the title, HTML, and plain text content for the email.
    """
    # Determine the title for the email
    if len(transcripts) > 1:
        email_title = config.title
    else:
        try:
            email_title = (
                transcripts[0].title if transcripts[0].title else "Untitled Transcript"
            )
        except Exception as e:
            raise Exception(f"Unable to load transcript title. {e=}")

    style_block = f"""
    <style>
        body {{ height: 100%; margin: 0; padding: 0; width: 100%; }}
        .container {{ max-width: 660px; min-width: 320px; margin: 0 auto; padding: {config.block_padding}; }}
        h1, h2, h3, h4, h5, h6 {{ display: block; margin: 0; padding: 0; }}
        img, a img {{ border: 0; height: auto; outline: none; text-decoration: none; }}
        table {{ border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        td {{ mso-line-height-rule: exactly; }}
        @media (prefers-color-scheme: dark) {{
            body {{ background-color: {config.dark_background_color}; }}
        }}
        @media only screen and (max-width: 480px) {{
            .container {{ padding: 16px; }}
            h1 {{ font-size: 24px !important; }}
            p {{ font-size: 14px !important; }}
        }}
    </style>
    """

    # Ensure transcripts is a list
    if not isinstance(transcripts, list):
        transcripts = [transcripts]

    # Load the base64 image or fallback to a URL
    try:
        with open(
            os.path.join(DEFAULT_PATH, "assets/mail-header.svg"), "rb"
        ) as image_file:
            header_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            header_image_html = f"""
            <table align="center" style="margin: 0 auto; text-align: center; width: 200px;">
                <tr>
                    <td>
                        <div style="padding-top: 20px;"></div>
                        <div style="width: 200px; height: auto; background-size: cover; background-image: url('data:image/svg+xml;base64,{header_image_base64}'); text-align: center;">
                            <img src="{SETTINGS.public_host_address}/assets/mail-header.svg" alt="{SETTINGS.podcast_name}" style="width: 200px; height: auto; display: block;">
                        </div>
                        <div style="padding-top: 20px;"></div>
                    </td>
                </tr>
            </table>
            """
    except FileNotFoundError:
        print("Debug: Mail header image not found at /assets/mail-header.svg")
        header_image_html = ""

    # Prepare dynamic content for HTML and text
    body_html = ""
    body_text = f"{config.title}\n\n"
    for transcript in transcripts:
        panel = PanelDiscussion.fetch_from_supabase_sync(supabase, transcript.panel_id)
        panel_title = panel.title if panel else "Unknown Panel"
        transcript_title = transcript.title or "Unknown Transcript"
        player_url = (
            f"{SETTINGS.public_host_address}{SETTINGS.player_uri_path}panel/{panel.id}"
        )
        metadata = transcript.metadata or {}
        subjects: list[dict[str, Any]] = metadata.get("subjects", [])
        description = metadata.get("description", "No description available.")
        sources = PanelTranscriptSourceReference.fetch_existing_from_supabase_sync(
            supabase, filter={"transcript_id": transcript.id}
        )
        sources_html = "".join(
            f'<li><a href="{source.data.get("url", "#")}" style="font-family: {config.font_family}; color: {config.link_color}; text-decoration: underline;">{source.data.get("title", "Unknown Source")}</a></li>'
            for source in sources
        )
        sources_text = "\n".join(
            f"- {source.data.get('title', 'Unknown Source')} ({source.data.get('url', '#')})"
            for source in sources
        )

        # Conditionally render elements for HTML
        panel_title_html = (
            f"<h2 style='font-family: {config.font_family}; color: {config.secondary_text_color}; background-color: {config.background_color};'>Panel: {panel_title}</h2><br/><br/>"
            if config.show_panel_title
            else ""
        )
        subjects_html = "".join(
            f"<li style='font-family: {config.font_family}; color: {config.text_color}; background-color: {config.background_color};'>"
            f"<strong>{subject.get('title', '')}</strong>: {subject.get('description', '')}"
            + (
                f"<ul>{''.join(f'<li>[{i + 1}] <a href=\"{ref}\" style=\"font-family: {config.font_family}; color: {config.link_color}; text-decoration: underline;\">{ref}</a></li>' for i, ref in enumerate(subject.get('references', [])) if isinstance(ref, str))}</ul>"
                if subject.get("references")
                else ""
            )
            + "</li>"
            for subject in subjects
        )

        subjects_html_block = (
            f"<p style='font-family: {config.font_family}; color: {config.text_color}; background-color: {config.background_color};'><strong>Subjects:</strong></p><ul>{subjects_html}</ul>"
            if subjects
            else ""
        )

        body_text += (
            "Subjects:\n\n"
            + "\n".join(
                f"- {subject.get('title')}: {subject.get('description')}"
                + (
                    "\n  References:\n  "
                    + "\n  ".join(
                        f"[{i + 1}] {ref}"
                        for i, ref in enumerate(subject.get("references", []))
                    )
                    if subject.get("references", [])
                    else ""
                )
                for subject in subjects
            )
            + "\n\n\n"
        )
        sources_html_block = (
            f"<p style='font-family: {config.font_family}; color: {config.text_color}; background-color: {config.background_color};'><strong>Sources:</strong></p><ul>{sources_html}</ul>"
            if config.show_sources
            else ""
        )

        # Append to HTML content
        description_html = (
            f"<p style='font-family: {config.font_family}; color: {config.text_color}; background-color: {config.background_color};'>{description}</p>"
            if config.show_description
            else ""
        )

        body_html += f"""
        <table class="container" style="background-color: {config.background_color}; padding: {config.block_padding}; margin-bottom: {config.margin_bottom};">
            <tr>
                <td>
                    {panel_title_html}
                    <h3 style="font-family: {config.font_family}; color: {config.text_color}; background-color: {config.background_color};">{transcript_title}</h3>
                    <p style="font-family: {config.font_family}; color: {config.link_color}; background-color: {config.background_color};">
                        <a href="{player_url}" style="text-decoration: none;">{player_url}</a>
                    </p>
                    {description_html}
                    {subjects_html_block}
                    {sources_html_block}
                    <div style="padding-top: 20px;"></div>
                </td>
            </tr>
        </table>
        """

        # Append to text content based on config.show parameters
        if config.show_panel_title:
            body_text += f"Panel: {panel_title}\n\n\n"
        body_text += f"{transcript_title}\n\n\n"
        body_text += f"Player URL: {player_url}\n\n"
        if config.show_description:
            body_text += f"{description}\n\n\n"
        body_text += (
            "Subjects:\n\n"
            + "\n".join(f"- {subject}" for subject in subjects)
            + "\n\n\n"
        )
        if config.show_sources:
            body_text += "Sources:\n\n" + sources_text + "\n\n"

    footer_html = (
        f"""
            <table class="container" style="text-align: center; background-color: {config.background_color};">
            <tr>
                <td>
                    <p style="font-family: {config.font_family}; color: {config.secondary_text_color}; background-color: {config.background_color};">
                        {config.footer_text}<br>
                        <a href="{config.subscription_link}" style="font-family: {config.font_family}; color: {config.link_color}; text-decoration: underline;">Update Preferences</a> |
                        <a href="{config.preference_link}" style="font-family: {config.font_family}; color: {config.link_color}; text-decoration: underline;">Unsubscribe</a>
                    </p>
                </td>
            </tr>
        </table>
        """
        if config.show_footer
        else ""
    )

    # Combine all sections into the final HTML
    html_output = f"""
    <!DOCTYPE html>
    <html>
    <head>
        {style_block}
        <title>{config.title}</title>
    </head>
    <body style="background-color: {config.background_color};">
        {header_image_html}
        <div class="container">
            {body_html}
        </div>
        {footer_html}
    </body>
    </html>
    """

    # Append footer to text content
    body_text += f"{config.footer_text}\n"
    body_text += f"Update Preferences: {config.subscription_link}\n"
    body_text += f"Unsubscribe: {config.preference_link}\n"

    return email_title, html_output, body_text


@celery_app.task
def send_new_shows_email_task(email: str, transcript_ids: List[str]):
    print(f"Email: {email}")
    if not SETTINGS.send_emails:
        print("Email sending is disabled.")
        return

    if isinstance(transcript_ids, str):
        try:
            transcript_ids = json.loads(transcript_ids)
            if isinstance(transcript_ids, str):
                transcript_ids = [transcript_ids]
        except json.JSONDecodeError:
            transcript_ids = [transcript_ids]

    if email is None or len(transcript_ids) == 0:
        print(
            "No email defined or length of transcript_ids is 0, skipping email sending"
        )
        return

    print(f"Send email to Email: {email} for Transcript IDs: {transcript_ids}")

    supabase = get_sync_supabase_service_client()

    # Fetch transcript details
    transcripts = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase,
        values=transcript_ids if isinstance(transcript_ids, list) else [transcript_ids],
    )

    # Initialize EmailConfig
    email_config = EmailConfig()

    # Generate email content using the new template function
    email_title, email_html, email_text = generate_email_from_template(
        supabase, transcripts, email_config
    )

    # Minify HTML using BeautifulSoup
    soup = BeautifulSoup(email_html, "html.parser")
    email_html = soup.prettify(formatter="minimal")

    # Send email using Resend SDK

    resend.api_key = SETTINGS.resend_api_key

    params: resend.Emails.SendParams = {
        "from": "show@thirdcognition.app",
        "to": email if isinstance(email, list) else [email],
        "subject": email_title,
        "html": email_html,
        "text": email_text,  # Include the text alternative
    }

    try:
        email_response = resend.Emails.send(params)
        print(f"Email sent successfully: {email_response}")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Celery task
@celery_app.task
def send_email_about_new_shows_task(transcript_ids: list[str]):
    if isinstance(transcript_ids, str):
        try:
            transcript_ids = json.loads(transcript_ids)
        except json.JSONDecodeError:
            transcript_ids = transcript_ids

    send_email_about_new_shows(transcript_ids)


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
