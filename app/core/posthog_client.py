from posthog import Posthog
from source.load_env import SETTINGS
from source.models.supabase.organization import UserProfileModel


class PostHogEvents:
    NOTIFICATION_SEND = "push_notification_send"
    NOTIFICATION_FAIL = "push_notification_send_fail"
    NOTIFICATION_SUCCESS = "push_notification_send_success"


class PostHogAnalytics:
    _instance = None

    def __init__(self):
        if not SETTINGS.posthog_api_key:
            raise ValueError("PostHog API key is not set in SETTINGS.")

        print(
            f"Initialize posthog with {SETTINGS.posthog_api_key} ({SETTINGS.posthog_host})"
        )
        self.posthog = Posthog(SETTINGS.posthog_api_key, SETTINGS.posthog_host)

    def track_event(
        self, event_name, properties: dict = None, user: UserProfileModel = None
    ):
        """
        Track an event in PostHog.
        :param event_name: Name of the event.
        :param properties: Optional dictionary of event properties.
        """

        if user:
            properties = {
                **(properties or {}),
                "$set": {
                    **(
                        properties.get("$set")
                        if properties and properties.get("$set")
                        else {}
                    ),
                    "anonymous": not bool(user.email),
                    "name": user.name,
                    "email": user.email,
                },
            }

        print(f"Tracking event: {event_name}, properties: {properties}")
        self.posthog.capture(
            distinct_id=user.auth_id if user else None,
            event=event_name,
            properties=properties or {},
        )

    def get_feature_flag(self, flag_key):
        """
        Get the value of a feature flag.
        :param flag_key: Key of the feature flag.
        :return: Boolean or None.
        """
        return self.posthog.feature_enabled(flag_key)

    @staticmethod
    def get_instance(reset=False):
        """
        Get the singleton instance of PostHogAnalytics.
        :param reset: If True, create a new instance.
        :return: PostHogAnalytics instance.
        """
        if reset or PostHogAnalytics._instance is None:
            PostHogAnalytics._instance = PostHogAnalytics()
        return PostHogAnalytics._instance
