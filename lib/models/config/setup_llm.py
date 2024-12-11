import os
from lib.models.config.default_settings import Settings
from lib.models.config.llm_settings import (
    EmbeddingDefaults,
    EmbeddingModelSettings,
    EmbeddingProviderSettings,
    ModelDefaults,
    ProviderModelSettings,
    ProviderSettings,
)
from lib.models.config.mapping import EMBEDDING_MODEL_MAP, LLM_MODEL_MAP, LLM_MODELS


def setup_llm(SETTINGS: Settings):
    LLM_PROVIDERS = os.getenv("LLM_PROVIDERS", "OLLAMA").upper().split(",")
    SETTINGS.default_llms = ModelDefaults()
    for provider in LLM_PROVIDERS:
        print(f"Loading {provider} settings...")
        provider_settings = ProviderSettings(
            type=provider, class_model=LLM_MODEL_MAP[provider]
        )

        if provider == "OLLAMA":
            provider_settings.url = os.getenv(
                f"{provider}_URL", "http://127.0.0.1:11434"
            )
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
                            f"{provider}_EMBEDDING_{model_type.upper()}_CHAR_LIMIT",
                            1000,
                        )
                    ),
                    overlap=int(
                        os.getenv(
                            f"{provider}_EMBEDDING_{model_type.upper()}_OVERLAP", 100
                        )
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
    print(
        f"\tLLM: {SETTINGS.default_provider.type} {SETTINGS.default_llms.default.model}"
    )
    print(
        f"\tEMBEDDING: {SETTINGS.default_embedding_provider.type} {SETTINGS.default_embeddings.default.model}"
    )
