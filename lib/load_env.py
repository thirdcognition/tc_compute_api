# Load .env file from the parent directory
from pathlib import Path
from typing import Any, Literal, Optional, List, Union
import warnings
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, BaseModel, Field, IPvAnyAddress
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_huggingface import (
    HuggingFaceEmbeddings,
)
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.azureml_endpoint import AzureMLChatOnlineEndpoint
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_groq import ChatGroq
from langchain_community.chat_models.ollama import ChatOllama
import logging
import os

from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose
from langchain_core.language_models.llms import BaseLLM
import toml

log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")

logging.captureWarnings(True)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), "../", ".env"))
print("Loading env: ", os.path.join(os.path.dirname(__file__), "../", ".env"))

DEBUGMODE = os.getenv("LLM_DEBUG", "True") == "True" or False
DEVMODE = os.getenv("LLM_DEV", "True") == "True" or False
IN_PRODUCTION = os.getenv("STREAMLIT_PRODUCTION", "False") == "True" or False

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "False") == "True" or False
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "")

set_debug(DEBUGMODE)
set_verbose(DEBUGMODE)


LLM_PROVIDERS = os.getenv("LLM_PROVIDERS", "OLLAMA").upper().split(",")

LLM_MODEL_MAP: dict[str, BaseLLM] = {
    "OLLAMA": ChatOllama,
    "GROQ": ChatGroq,
    "BEDROCK": ChatBedrock,
    "OPENAI": ChatOpenAI,
    "ANTHROPIC": ChatAnthropic,
    "AZURE": AzureChatOpenAI,
    "AZURE_ML": AzureMLChatOnlineEndpoint,
}

# from langchain_core.embeddings import Embeddings

EMBEDDING_MODEL_MAP: dict[str, Embeddings] = {
    "LOCAL": HuggingFaceEmbeddings,
    "OLLAMA": OllamaEmbeddings,
    "HUGGINGFACE": HuggingFaceInferenceAPIEmbeddings,
}

LLM_MODELS = [
    "chat",
    "instruct",
    "instruct_detailed",
    "structured",
    "structured_detailed",
    "tool",
    "tester",
]


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
        "OLLAMA", "GROQ", "BEDROCK", "OPENAI", "ANTHROPIC", "AZURE", "AZURE_ML"
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


with open(os.path.join(os.path.dirname(__file__), "../", "pyproject.toml"), "r") as f:
    pyproject = toml.load(f)

# Get the project name
project_name = pyproject["tool"]["poetry"]["name"]


class RetrySpec(BaseModel):
    max_count: int = Field(default=3, description="Maximum number of retries")
    retry_timeout: int = Field(default=10, description="Retry timeout in seconds")


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
    backend_cors_origins: list[AnyHttpUrl] = [""]
    backend_cors_origins: list[Union[AnyHttpUrl, str]] = ["*"]

    file_repository_path: str = Field(
        default_factory=lambda: str(
            Path(os.path.abspath(__file__)).parent.parent / "file_repository"
        )
    )
    langchain_retries: RetrySpec = RetrySpec()


SETTINGS = Settings()

SETTINGS.default_llms = ModelDefaults()
for provider in LLM_PROVIDERS:
    print(f"Loading {provider} settings...")
    provider_settings = ProviderSettings(
        type=provider, class_model=LLM_MODEL_MAP[provider]
    )

    if provider == "OLLAMA":
        provider_settings.url = os.getenv(f"{provider}_URL", "http://127.0.0.1:11434")
    elif provider == "GROQ":
        provider_settings.api_key = os.getenv(f"{provider}_API_KEY", None)
    elif provider == "BEDROCK":
        provider_settings.region = os.getenv("AWS_BEDROCK_REGION", "us-west-2")
        provider_settings.access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        provider_settings.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    elif provider == "OPENAI":
        provider_settings.api_key = os.getenv(f"{provider}_API_KEY", "")
    elif provider == "ANTHROPIC":
        provider_settings.api_key = os.getenv(f"{provider}_API_KEY", "")
    elif provider == "AZURE":
        provider_settings.api_type = os.getenv("AZURE_API_TYPE", "")
        provider_settings.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        provider_settings.api_base = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        provider_settings.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")
    elif provider == "AZURE_ML":
        provider_settings.api_key = os.getenv("AZUREML_APIKEY", "")

    for type in LLM_MODELS:
        type_model = os.getenv(f"{provider}_{type.upper()}_MODEL", "")
        endpoint = os.getenv(f"{provider}_{type.upper()}_ENDPOINT", None)
        if type_model != "" or endpoint is not None:
            type_settings = ProviderModelSettings(
                type=type,
                provider=provider,
                url=os.getenv(f"{provider}_{type}_URL", provider_settings.url),
                model=type_model,
                class_model=LLM_MODEL_MAP.get(
                    f"{provider}_{type}", provider_settings.class_model
                ),
                context_size=int(
                    os.getenv(f"{provider}_{type.upper()}_CTX_SIZE", 8192)
                ),
                max_tokens=int(
                    os.getenv(f"{provider}_{type.upper()}_OUT_CTX_SIZE", 2048)
                ),
                char_limit=int(
                    os.getenv(f"{provider}_{type.upper()}_CHAR_LIMIT", 12000)
                ),
                api_key=os.getenv(
                    f"{provider}_{type.upper()}_API_KEY", provider_settings.api_key
                ),
                endpoint=endpoint,
                ratelimit_per_sec=float(
                    os.getenv(f"{provider}_{type.upper()}_PER_SEC", 2)
                ),
                ratelimit_interval=float(
                    os.getenv(f"{provider}_{type.upper()}_INTERVAL", 0.5)
                ),
                ratelimit_bucket=float(
                    os.getenv(f"{provider}_{type.upper()}_BUCKET", 1)
                ),
            )
            if SETTINGS.default_llms.__getattribute__("default") is None:
                SETTINGS.default_llms.default = type_settings
            if SETTINGS.default_llms.__getattribute__(type) is None:
                SETTINGS.default_llms.__setattr__(type, type_settings)
            provider_settings.models.append(type_settings)

    SETTINGS.llms.append(provider_settings)
    # Set default provider if not already set
    if SETTINGS.default_provider is None:
        SETTINGS.default_provider = provider_settings

EMBEDDING_PROVIDERS = os.getenv("EMBEDDING_PROVIDERS", "LOCAL").upper().split(",")
EMBEDDING_MODEL_TYPES = ["large", "medium", "small"]

SETTINGS.default_embeddings = EmbeddingDefaults()
for provider in EMBEDDING_PROVIDERS:
    provider_settings = EmbeddingProviderSettings(
        type=provider, class_model=EMBEDDING_MODEL_MAP.get(provider)
    )

    if provider == "OLLAMA":
        provider_settings.url = os.getenv(f"{provider}_EMBEDDING_URL", "")
    if provider == "HUGGINGFACE":
        provider_settings.api_key = os.getenv(f"{provider}_EMBEDDING_API_KEY", "")
    # if provider == "OPENAI":
    #     provider_settings.api_key = os.getenv(f"{provider}_API_KEY", "")
    # elif provider == "BEDROCK":
    #     provider_settings.region = os.getenv("AWS_BEDROCK_REGION", "us-west-2")
    #     provider_settings.access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
    #     provider_settings.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    # elif provider == "AZURE":
    #     provider_settings.api_type = os.getenv("AZURE_API_TYPE", "")
    #     provider_settings.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    #     provider_settings.api_base = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    #     provider_settings.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")
    for model_type in EMBEDDING_MODEL_TYPES:
        model = os.getenv(f"{provider}_EMBEDDING_{model_type.upper()}_MODEL", "")
        if model != "":
            model_settings = EmbeddingModelSettings(
                type=model_type,
                model=model,
                char_limit=int(
                    os.getenv(
                        f"{provider}_EMBEDDING_{model_type.upper()}_CHAR_LIMIT", 1000
                    )
                ),
                overlap=int(
                    os.getenv(f"{provider}_EMBEDDING_{model_type.upper()}_OVERLAP", 100)
                ),
            )
            if SETTINGS.default_embeddings.__getattribute__("default") is None:
                SETTINGS.default_embeddings.default = model_settings
            if SETTINGS.default_embeddings.__getattribute__(model_type) is None:
                SETTINGS.default_embeddings.__setattr__(model_type, model_settings)
            provider_settings.models.append(model_settings)

    SETTINGS.embeddings.append(provider_settings)
    if SETTINGS.default_embedding_provider is None:
        SETTINGS.default_embedding_provider = provider_settings


for provider_settings in SETTINGS.llms:
    print(f"+++ {provider_settings.type} +++")
    for model_settings in provider_settings.models:
        print(
            f"\t{model_settings.type.capitalize()}: {model_settings.model=} {model_settings.context_size=} {model_settings.char_limit=}"
        )

for embedding_provider_settings in SETTINGS.embeddings:
    print(f"+++ {embedding_provider_settings.type} EMBEDDINGS +++")
    for model_settings in embedding_provider_settings.models:
        print(
            f"\t{model_settings.type.capitalize()}: {model_settings.model=} {model_settings.char_limit=} {model_settings.overlap=}"
        )

print("+++ DEFAULTS +++")
print(f"\tLLM: {SETTINGS.default_provider.type} {SETTINGS.default_llms.default.model}")
print(
    f"\tEMBEDDING: {SETTINGS.default_embedding_provider.type} {SETTINGS.default_embeddings.default.model}"
)
