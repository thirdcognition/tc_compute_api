from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class RetrySpec(BaseModel):
    max_count: int = Field(default=3, description="Maximum number of retries")
    retry_timeout: int = Field(default=10, description="Retry timeout in seconds")


class ProviderModelSettings(BaseSettings):
    type: Literal[
        "chat",
        "instruct",
        "instruct_detailed",
        "structured",
        "structured_detailed",
        "tool",
        "tester",
    ]
    class_model: Optional[Any] = None
    provider: Optional[str] = None
    url: Optional[str] = None
    model: Optional[str] = None
    context_size: Optional[int] = None
    max_tokens: Optional[int] = None
    char_limit: Optional[int] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    ratelimit_per_sec: Optional[float] = None
    ratelimit_interval: Optional[float] = None
    ratelimit_bucket: Optional[float] = None


class ModelDefaults(BaseSettings):
    default: Optional[ProviderModelSettings] = None
    chat: Optional[ProviderModelSettings] = None
    instruct: Optional[ProviderModelSettings] = None
    instruct_detailed: Optional[ProviderModelSettings] = None
    structured: Optional[ProviderModelSettings] = None
    structured_detailed: Optional[ProviderModelSettings] = None
    tool: Optional[ProviderModelSettings] = None
    tester: Optional[ProviderModelSettings] = None


class ProviderSettings(BaseSettings):
    type: Literal[
        "OLLAMA",
        "GROQ",
        "BEDROCK",
        "OPENAI",
        "ANTHROPIC",
        "AZURE",
        "AZURE_ML",
        "GEMINI",
    ]
    class_model: Optional[Any] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    api_type: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    models: List[ProviderModelSettings] = []


class EmbeddingModelSettings(BaseSettings):
    type: Literal["large", "medium", "small"]
    model: Optional[str] = None
    char_limit: Optional[int] = None
    overlap: Optional[int] = None


class EmbeddingDefaults(BaseSettings):
    default: Optional[EmbeddingModelSettings] = None
    large: Optional[EmbeddingModelSettings] = None
    medium: Optional[EmbeddingModelSettings] = None
    small: Optional[EmbeddingModelSettings] = None


class EmbeddingProviderSettings(BaseSettings):
    type: Literal["LOCAL", "HUGGINGFACE", "OPENAI", "OLLAMA", "BEDROCK", "AZURE"]
    class_model: Any = None  # Union[HuggingFaceEmbeddings, OllamaEmbeddings, HuggingFaceInferenceAPIEmbeddings, None] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    api_type: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    models: List[EmbeddingModelSettings] = []
