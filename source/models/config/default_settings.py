import os
from pathlib import Path
from typing import List, Literal, Optional, Union
from pydantic import Field, AnyHttpUrl, IPvAnyAddress
from pydantic_settings import BaseSettings
import toml

from source.models.config.default_env import DEFAULT_PATH
from source.models.config.llm_settings import (
    EmbeddingDefaults,
    EmbeddingProviderSettings,
    ModelDefaults,
    ProviderSettings,
    RetrySpec,
)


with open(os.path.join(DEFAULT_PATH, "pyproject.toml"), "r") as f:
    pyproject = toml.load(f)

# Get the project name
project_name = pyproject["tool"]["poetry"]["name"]


class Settings(BaseSettings):
    project_name: str = Field(default=project_name)
    llms: List[ProviderSettings] = []
    default_provider: Optional[ProviderSettings] = None
    default_llms: Optional[ModelDefaults] = None
    embeddings: List[EmbeddingProviderSettings] = []
    default_embedding_provider: Optional[EmbeddingProviderSettings] = None
    default_embeddings: Optional[EmbeddingDefaults] = None
    podcastfy_llm_api_key_label: str = Field(
        default_factory=lambda: os.getenv("PODCASTFY_API_KEY", "AZURE_API_KEY")
    )
    google_translate_api_key: str = Field(
        default_factory=lambda: os.getenv(
            "GOOGLE_TRANSLATE_API_KEY", "your-default-api-key"
        )
    )
    podcastfy_llm_model: str = Field(
        default_factory=lambda: os.getenv("PODCASTFY_MODEL", "azure/gpt-4o")
    )
    server_port: int = Field(default_factory=lambda: os.getenv("SERVER_PORT", 8000))
    server_host: Union[IPvAnyAddress, Literal["localhost"]] = Field(
        default_factory=lambda: os.getenv("SERVER_HOST", "0.0.0.0")
    )
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "DEBUG"))
    supabase_url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL"))
    supabase_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY"))
    supabase_service_key: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_SERVICE_KEY")
    )
    supabase_cache_ttl: int = Field(
        default_factory=lambda: int(os.getenv("SUPABASE_CACHE_TTL", 30))
    )
    supabase_cache_size: int = Field(
        default_factory=lambda: int(os.getenv("SUPABASE_CACHE_SIZE", 100))
    )
    resend_api_key: str = Field(default_factory=lambda: os.getenv("RESEND_API_KEY"))
    backend_cors_origins: list[AnyHttpUrl] = [""]
    backend_cors_origins: list[Union[AnyHttpUrl, str]] = ["*"]

    posthog_api_key: str = Field(default_factory=lambda: os.getenv("POSTHOG_API_KEY"))
    posthog_host: str = Field(default_factory=lambda: os.getenv("POSTHOG_HOST"))

    file_repository_path: str = Field(
        default_factory=lambda: str(
            Path(os.path.abspath(__file__)).parent.parent.parent.parent
            / "file_repository"
        )
    )
    langchain_retries: RetrySpec = RetrySpec()

    # Redis configuration
    redis_broker_url: str = Field(
        default_factory=lambda: os.getenv("REDIS_BROKER", "redis://localhost:6379/0")
    )
    redis_backend_url: str = Field(
        default_factory=lambda: os.getenv("REDIS_BACKEND", "redis://localhost:6379/0")
    )

    # Celery and Flower configuration
    celery_host: str = Field(
        default_factory=lambda: os.getenv("CELERY_HOST", "localhost")
    )
    celery_port: int = Field(
        default_factory=lambda: int(os.getenv("CELERY_PORT", 5556))
    )
    flower_host: str = Field(
        default_factory=lambda: os.getenv("FLOWER_HOST", "localhost")
    )
    flower_port: int = Field(
        default_factory=lambda: int(os.getenv("FLOWER_PORT", 5555))
    )
    tc_org_id: str = Field(
        default_factory=lambda: str(
            os.getenv("tc_org_id", "34303437-3164-6431-6439-393230626365")
        )
    )
    send_emails: bool = Field(
        default_factory=lambda: os.getenv("SEND_EMAILS", "false").lower() == "true"
    )
    mailchimp_api_key: str = Field(
        default_factory=lambda: os.getenv("MAILCHIMP_API_KEY", "")
    )
    mailchimp_server_prefix: str = Field(
        default_factory=lambda: os.getenv("MAILCHIMP_SERVER_PREFIX", "")
    )
    enable_mailchimp: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_MAILCHIMP", "false").lower() == "true"
    )

    enable_push_notifications: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_PUSH_NOTIFICATIONS", "false").lower()
        == "true"
    )
    expo_token: str = Field(
        default_factory=lambda: os.getenv("EXPO_ACCESS_TOKEN", "").lower()
    )

    podcast_name: str = Field(
        default_factory=lambda: os.getenv("panel_defaults_podcast_name", "Morning Show")
    )
    podcast_tagline: str = Field(
        default_factory=lambda: os.getenv(
            "panel_defaults_podcast_tagline", "Your Personal Morning Podcast"
        )
    )
    public_host_address: str = Field(
        default_factory=lambda: os.getenv(
            "PUBLIC_HOST_ADDRESS", "https://show.thirdcognition.app"
        )
    )
    admin_uri_path: str = Field(
        default_factory=lambda: os.getenv("ADMIN_URI_PATH", "/admin/")
    )
    player_uri_path: str = Field(
        default_factory=lambda: os.getenv("PLAYER_URI_PATH", "/player/")
    )
