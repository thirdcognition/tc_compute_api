from collections import defaultdict
from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    DeviceNotRegisteredError,
    PushTicketError,
    PushTicket,
)
from pydantic import BaseModel, Field
from requests.exceptions import ConnectionError, HTTPError
from supabase import Client
from app.core.celery_app import celery_app
from app.core.supabase import get_sync_supabase_service_client
from source.load_env import SETTINGS
import json
import time
from datetime import datetime, timedelta

from source.models.supabase.organization import UserDataModel, UserProfileModel
from source.models.supabase.panel import PanelDiscussion, PanelTranscript
from app.core.posthog_client import PostHogAnalytics, PostHogEvents


class UserPushNotification(BaseModel):
    user: UserProfileModel = Field(default=None)
    transcripts: list[PanelTranscript] = Field(default=[])


@celery_app.task
def task_send_push_notifications_for_new_tasks():
    if not SETTINGS.enable_push_notifications:
        print("[Notifications] Push notifications are disabled.")
        return

    supabase = get_sync_supabase_service_client()

    ts = (datetime.now() - timedelta(days=1)).isoformat()

    print(f"[Notifications] Fetching new transcripts since: {ts}")
    transcripts: list[
        PanelTranscript
    ] = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase,
        filter={"created_at": {"gt": ts}},
    )
    # Sort transcripts by 'updated_at' in descending order
    transcripts = sorted(transcripts, key=lambda t: t.updated_at, reverse=True)
    print(
        f"[Notifications] Send notification for Transcripts: {['\n\n'.join(f'{transcript.title} ({transcript.id}) - {transcript.created_at}' for transcript in transcripts)]}"
    )

    send_push_notifications_for_tasks(supabase, transcripts)


@celery_app.task
def task_send_push_notifications_for_tasks(transcript_ids: list[str]):
    """
    Celery task to send push notifications about new transcripts.
    """
    # print(
    #     f"[Notifications] Push notifications enabled: {SETTINGS.enable_push_notifications}"
    # )
    if not SETTINGS.enable_push_notifications:
        print("[Notifications] Push notifications are disabled.")
        return

    print(f"[Notifications] Raw transcript IDs: {transcript_ids}")
    if isinstance(transcript_ids, str):
        try:
            transcript_ids = json.loads(transcript_ids)
            # print(f"[Notifications] Decoded transcript IDs: {transcript_ids}")
        except json.JSONDecodeError as e:
            print(f"[Notifications] Unable to decode transcript IDs: {e}")
            return

    supabase = get_sync_supabase_service_client()

    print(f"[Notifications] Fetching transcripts for IDs: {transcript_ids}")
    transcripts = PanelTranscript.fetch_existing_from_supabase_sync(
        supabase,
        values=transcript_ids if isinstance(transcript_ids, list) else [transcript_ids],
    )

    send_push_notifications_for_tasks(supabase, transcripts)


def send_push_notifications_for_tasks(
    supabase: Client, transcripts: list[PanelTranscript]
):
    # print(f"[Notifications] Fetched transcripts: {transcripts}")

    if len(transcripts) == 0:
        print("[Notifications] Unable to find transcripts")
        return

    transcript_ids = [transcript.id for transcript in transcripts]
    panel_ids = list({transcript.panel_id for transcript in transcripts})

    panel_list = PanelDiscussion.fetch_existing_from_supabase_sync(
        supabase,
        values=panel_ids,
    )

    panels = {panel.id: panel for panel in panel_list}

    if len(transcripts) == 0:
        print(
            f"[Notifications] No transcripts found for the given IDs. {type(transcript_ids)=} {transcript_ids=}"
        )
        return

    user_notifications: dict[str, UserPushNotification] = {}

    print("[Notifications] Fetch Panel User Data")
    all_user_data_panels = UserDataModel.fetch_existing_from_supabase_sync(
        supabase,
        filter={"item": "panel_subscription"},
        id_column="target_id",
        values=panel_ids,
    )
    print("[Notifications] Fetch Transcript User Data")
    all_user_data_transcripts = UserDataModel.fetch_existing_from_supabase_sync(
        supabase,
        id_column="target_id",
        values=transcript_ids,
        # values = {"target_id": transcript.id},
    )
    all_user_ids = list(
        {user_data_instance.auth_id for user_data_instance in all_user_data_transcripts}
    )
    print(f"[Notifications] Fetch Connected User Profile Data {all_user_ids=}")
    all_users = UserProfileModel.fetch_existing_from_supabase_sync(
        supabase,
        filter={
            "notification_data": {"neq": None},
            "last_sign_in_at": {
                "gt": (datetime.now() - timedelta(weeks=1)).isoformat()
            },
        },
        values=all_user_ids,
        id_column="auth_id",
    )

    for transcript in transcripts:
        user_data_panels = [
            user_data
            for user_data in all_user_data_panels
            if user_data.target_id == transcript.panel_id
        ]
        user_data_transcripts = [
            user_data
            for user_data in all_user_data_transcripts
            if user_data.target_id == transcript.id
        ]

        user_ids = [user_data.auth_id for user_data in user_data_panels]
        users = [user for user in all_users if user.auth_id in user_ids]

        for user in users:
            if user_notifications.get(user.auth_id) is None:
                user_notifications[user.auth_id] = UserPushNotification(user=user)
            if transcript.lang.lower() == user.lang.lower():
                transcript_user_data = [
                    user_data_instance
                    for user_data_instance in user_data_transcripts
                    if user_data_instance.auth_id == user.auth_id
                ]
                if len(transcript_user_data) == 0:
                    print(
                        f"[Notifications] Add transcript {transcript.title} ({transcript.id=}) for {user.name} ({user.auth_id=})"
                    )
                    user_notifications[user.auth_id].transcripts.append(transcript)

    push_client = PushClient()
    messages = []

    # Initialize PostHogAnalytics
    analytics = PostHogAnalytics.get_instance()

    for notification in user_notifications.values():
        push_tokens = notification.user.notification_data

        if not push_tokens or len(notification.transcripts) == 0:
            continue

        panel = panels[notification.transcripts[0].panel_id]

        # title = notification.transcripts[0].title

        # body = notification.transcripts[0].metadata["description"]
        title = f"{notification.user.name.split(' ')[0] + ', t' if notification.user.name else 'T'}oday on {panel.metadata['display_tag'] or panel.title}"
        body = notification.transcripts[0].title
        data = {"transcript_ids": [str(notification.transcripts[0].id)]}

        if len(notification.transcripts) > 1:
            # title = "New episodes!"
            # body = "\n".join(
            #     [transcript.title for transcript in notification.transcripts]
            # )
            data = {
                "transcript_ids": [
                    str(transcript.id) for transcript in notification.transcripts
                ]
            }

        track_id = f"notification_{notification.user.auth_id}_{int((time.time() % 307584000) * 10000)}"

        data["track_id"] = track_id

        try:
            analytics.track_event(
                PostHogEvents.NOTIFICATION_SEND,
                {
                    "notification_id": track_id,
                    "transcript_ids": [
                        transcript.id for transcript in notification.transcripts
                    ],
                    "notification_title": title,
                    "notification_body": body,
                },
                user=notification.user,
            )
        except Exception as e:
            print(f"[Notifications] Unable to track analytics event. {e=}")

        print(
            f"[Notifications] Preparing notification(s) for user: {notification.user.auth_id}"
        )
        used_tokens = defaultdict(list)
        for device_id, push_token in push_tokens.items():
            used_tokens[push_token].append(device_id)

        for push_token, device_ids in used_tokens.items():
            messages.append(
                {
                    "id": track_id,
                    "message": PushMessage(
                        to=push_token,
                        title=title,
                        body=body,
                        data=data,
                        badge=len(notification.transcripts),
                    ),
                    "user": notification.user,
                    "token": push_token,
                    "device": device_ids if len(device_ids) > 1 else device_ids[0],
                }
            )

    if len(messages) == 0:
        print("[Notifications] No notifications sent.")
        return

    # print(f"[Notifications]  {messages=}")

    responses = []

    CHUNK_SIZE = 100  # Messages per batch
    RATE_LIMIT = 500  # Maximum messages per second

    start_time = time.time()  # Start timing

    for i in range(0, len(messages), CHUNK_SIZE):
        # Check elapsed time and enforce rate limit
        elapsed_time = time.time() - start_time
        completed_messages = i
        if completed_messages / elapsed_time > RATE_LIMIT:
            print(
                f"[Notifications] Rate limit reached, sleeping: {max(0, completed_messages / RATE_LIMIT - elapsed_time)}"
            )
            time.sleep(max(0, completed_messages / RATE_LIMIT - elapsed_time))

        print(
            f"[Notifications] Sending batch of messages: {messages[i : i + CHUNK_SIZE]}"
        )
        # Process the current batch
        new_responses = push_client.publish_multiple(
            [item["message"] for item in messages[i : i + CHUNK_SIZE]]
        )
        responses.extend(
            {
                "response": response,
                "user": item["user"],
                "id": item["id"],
                "token": item["token"],
                "device": item["device"],
            }
            for response, item in zip(new_responses, messages[i : i + CHUNK_SIZE])
        )
    successfull = []
    for response in responses:
        print(f"[Notifications] Validating response: {response['id']}")
        try:
            response["response"].validate_response()
            successfull.append(response)
        except DeviceNotRegisteredError:
            print(
                f"[Notifications] Device not registered for token: {response['token']}"
            )
            user: UserProfileModel = response["user"]
            notification_data = user.notification_data

            del notification_data[response["device"]]

            user.notification_data = notification_data
            user.update_sync(supabase=supabase)
        except PushTicketError as e:
            try:
                analytics.track_event(
                    PostHogEvents.NOTIFICATION_FAIL,
                    {
                        "notification_id": response["id"],
                        "notification_token": response["token"],
                        "error": e.push_response,
                    },
                    user=response["user"],
                )
            except Exception as e:
                print(f"[Notifications] Unable to track analytics event. {e=}")
        except (PushServerError, ConnectionError, HTTPError) as exc:
            print(
                f"[Notifications] Error sending push notification: {exc}. Retrying..."
            )
            time.sleep(2)  # Simple retry logic
        except Exception as e:
            print(f"[Notifications] Uncaught exception: {e}")

    print("[Notifications] Sleep for 5 seconds before validating receipts.")
    time.sleep(5)

    final_responses = []
    for i in range(0, len(successfull), 1000):
        print(
            f"[Notifications] Checking receipts for responses: {[item['response'] for item in successfull[i : i + 1000]]}"
        )
        new_receipts = push_client.check_receipts_multiple(
            [item["response"] for item in successfull[i : i + 1000]]
        )
        final_responses.extend(
            {
                "receipt": receipt,
                "response": item["response"],
                "user": item["user"],
                "id": item["id"],
                "token": item["token"],
                "device": item["device"],
            }
            for receipt, item in zip(new_receipts, successfull[i : i + 1000])
        )

    track_success: dict[str, list[dict]] = {}
    track_fail: dict[str, list[dict]] = {}
    for item in final_responses:
        print(f"[Notifications] Final receipt: {item['id']}")

        receipt: PushTicket = item["receipt"]
        if receipt.status == PushTicket.SUCCESS_STATUS:
            if not track_success.get(item["id"]):
                track_success[item["id"]] = []
            track_success[item["id"]].append(item)
        else:
            if not track_fail.get(item["id"]):
                track_fail[item["id"]] = []
            track_fail[item["id"]].append(item)

    for track_id in track_success:
        response = track_success[track_id][0]
        try:
            analytics.track_event(
                PostHogEvents.NOTIFICATION_SUCCESS,
                {
                    "notification_id": response["id"],
                    "notification_token": response["token"],
                },
                user=response["user"],
            )
        except Exception as e:
            print(f"[Notifications] Unable to track analytics event. {e=}")
    for track_id in track_fail:
        fail_items = track_fail[track_id]
        for response in fail_items:
            ticket: PushTicket = response["receipt"]
            error = ticket.details.get("error", None)
            try:
                analytics.track_event(
                    PostHogEvents.NOTIFICATION_FAIL,
                    {
                        "notification_id": response["id"],
                        "notification_token": response["token"],
                        "error": error,
                    },
                    user=response["user"],
                )
            except Exception as e:
                print(f"[Notifications] Unable to track analytics event. {e=}")
