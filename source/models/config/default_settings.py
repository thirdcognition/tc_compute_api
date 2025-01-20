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
