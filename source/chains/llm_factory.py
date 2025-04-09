from typing import Dict, Literal, Union

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.language_models.llms import BaseLLM
from langchain_core.rate_limiters import BaseRateLimiter, InMemoryRateLimiter

# Assuming these are the correct locations after potential refactoring or existing structure
# NOTE: AzureMLEndpointApiType and CustomOpenAIChatContentFormatter were removed as they are unused
#       in the current implementation after commenting out the AZURE_ML block.
#       If AZURE_ML support is re-enabled, these imports might be needed again.
# Specific imports removed as we are reverting to model.class_model
# from langchain_community.chat_models import (
#     BedrockChat,
#     AzureChatOpenAI,
#     ChatOllama,
#     ChatGroq,
# )
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models.azureml_endpoint import (
    AzureMLEndpointApiType,  # Keep for AZURE_ML block if uncommented
    CustomOpenAIChatContentFormatter,  # Keep for AZURE_ML block if uncommented
)


from source.load_env import SETTINGS
from source.models.config.logging import logger
from source.models.config.default_env import DEBUGMODE
from source.models.config.llm_settings import (
    ProviderModelSettings,
    ProviderSettings,
)

limiters: Dict[str, BaseRateLimiter] = {}
llms: Dict[str, BaseLLM] = {}


def get_limiter(model_config: ProviderModelSettings) -> Union[BaseRateLimiter, None]:
    id = f"{model_config.provider}_{model_config.type}"
    if id in limiters.keys():
        return limiters[id]

    limiter = (
        InMemoryRateLimiter(
            requests_per_second=model_config.ratelimit_per_sec,
            check_every_n_seconds=model_config.ratelimit_interval,
            max_bucket_size=model_config.ratelimit_bucket,
        )
        if model_config and model_config.ratelimit_per_sec is not None
        else None
    )

    if limiter:
        limiters[id] = limiter

    return limiter


def init_llm(
    provider: ProviderSettings = SETTINGS.default_provider,
    model: ProviderModelSettings = SETTINGS.default_llms.default,
    temperature=0.5,
    debug_mode: bool = DEBUGMODE,
) -> BaseLLM:
    logger.info(
        f"Initializing llm: {model.model=} with {model.context_size=} and {temperature=}..."
    )

    common_kwargs = {
        "verbose": debug_mode,
        "rate_limiter": get_limiter(model),
        "callback_manager": (
            CallbackManager([StreamingStdOutCallbackHandler()]) if debug_mode else None
        ),
    }

    # Handle temperature setting based on model type
    if "o1" not in model.model:
        logger.debug(f"Setting temperature={temperature} for model={model.model}")
        common_kwargs["temperature"] = temperature
    else:
        logger.debug(f"Unsetting temperature (using default 1) for model={model.model}")
        common_kwargs["temperature"] = 1  # Explicitly set to 1 for o1 models

    llm = None  # Initialize llm to None

    # Provider-specific initialization
    if model.provider == "BEDROCK":
        llm = model.class_model(  # Reverted to model.class_model
            model_id=model.model,
            region_name=provider.region,
            model_kwargs={"temperature": temperature},
            timeout=60,  # Restored original timeout
            max_tokens=model.max_tokens,
            max_retries=2,
            **common_kwargs,
        )
        # use_structured_mode = True # Original comment

    elif model.provider == "AZURE":
        completions = {
            "max_tokens": model.max_tokens if "o1" not in model.model else None,
            "max_completion_tokens": model.max_tokens if "o1" in model.model else None,
        }
        completions = {
            key: value for key, value in completions.items() if value is not None
        }
        llm = model.class_model(  # Reverted to model.class_model
            azure_deployment=model.model,
            api_version=provider.api_version,
            model_kwargs=(
                {"response_format": {"type": "json_object"}}
                if "structured" in model.type
                else {}
            ),
            # timeout=60000, # Original comment
            request_timeout=120,
            **completions,
            max_retries=2,
            **common_kwargs,
        )

    elif model.provider == "AZURE_ML":
        # Reverted to model.class_model, kept original commented block structure
        llm = model.class_model(
            endpoint_url=model.endpoint,
            endpoint_api_type=AzureMLEndpointApiType.serverless,
            endpoint_api_key=model.api_key,
            content_formatter=CustomOpenAIChatContentFormatter(),
            model_kwargs={"temperature": temperature},
            timeout=10,
            max_tokens=model.max_tokens,
            max_retries=2,
            **common_kwargs,
        )
        # logger.warning( # Removed warning as we are now using class_model
        #     f"Azure ML provider ({model.model}) initialization skipped - requires specific class."
        # )

    elif model.provider == "OLLAMA":
        llm = model.class_model(  # Reverted to model.class_model
            base_url=model.url,
            model=model.model,
            model_kwargs=(
                {"response_format": {"type": "json_object"}}
                if "structured" in model.type
                else {}
            ),
            num_ctx=model.context_size,
            num_predict=model.context_size,  # Restored original parameter
            repeat_penalty=2,  # Restored original value
            timeout=30,  # Restored original timeout
            max_retries=2,
            max_tokens=model.max_tokens,
            **common_kwargs,
        )

    elif model.provider == "GROQ":
        llm = model.class_model(  # Reverted to model.class_model
            # streaming=debug_mode, # Original comment
            api_key=model.api_key,
            model=model.model,  # Groq uses model
            model_kwargs=(
                {"response_format": {"type": "json_object"}}
                if "structured" in model.type
                else {}
            ),
            timeout=30,  # Restored original timeout
            max_retries=2,
            max_tokens=model.max_tokens,
            **common_kwargs,
        )

    elif model.provider == "GEMINI":
        llm = model.class_model(  # Reverted to model.class_model
            # streaming=debug_mode, # Original comment
            api_key=model.api_key,  # Gemini uses api_key
            model=model.model,
            model_kwargs=(
                {"response_format": {"type": "json_object"}}
                if "structured" in model.type
                else {}
            ),
            timeout=120,  # Restored original timeout
            max_retries=2,
            max_tokens=model.max_tokens,  # Gemini uses max_tokens
            **common_kwargs,
        )

    if llm is None:
        raise ValueError(f"Unsupported LLM provider: {model.provider}")

    return llm


temperature_map = {"default": 0.2, "zero": 0, "warm": 0.5}


def get_llm(
    id: str = "default",
    provider: Literal[
        "OLLAMA",
        "GROQ",
        "BEDROCK",
        "OPENAI",  # Added OPENAI for completeness, though not in original init_llm
        "ANTHROPIC",  # Added ANTHROPIC for completeness
        "AZURE",
        "AZURE_ML",
        "GEMINI",
        None,
    ] = None,
    temperature: Literal["default", "zero", "warm", None] = None,
) -> BaseLLM:
    global llms
    global SETTINGS

    # Construct a unique key including temperature if specified
    temp_key_part = f"_temp-{temperature}" if temperature else ""
    provider_key_part = f"_provider-{provider}" if provider else ""
    llm_key = f"{id}{temp_key_part}{provider_key_part}"

    if llm_key in llms:
        return llms[llm_key]

    llm_type = id
    temp_setting = temperature

    # Infer temperature from id if not explicitly provided
    if temp_setting is None:
        if "_0" in id:
            temp_setting = "zero"
            llm_type = llm_type.replace("_0", "")
        elif "_warm" in id:
            temp_setting = "warm"
            llm_type = llm_type.replace("_warm", "")
        else:
            temp_setting = "default"

    temperature_value = temperature_map[temp_setting]

    # Determine provider configuration
    provider_config = SETTINGS.default_provider
    if provider is not None:
        provider_config = (
            next((p for p in SETTINGS.llms if p.type == provider), None)
            or provider_config  # Fallback to default if specific provider not found
        )

    if provider_config is None:
        raise ValueError(
            f"Could not determine provider configuration for provider type: {provider or 'default'}"
        )

    # Determine model configuration
    llm_config = None
    if provider_config.models:
        llm_config = next(
            (m for m in provider_config.models if m.type == llm_type), None
        )

    # Fallback to default LLMs if specific model not found in provider config
    if llm_config is None:
        if hasattr(SETTINGS.default_llms, llm_type):
            llm_config = getattr(SETTINGS.default_llms, llm_type)
            # If falling back, ensure the provider matches the default provider
            provider_config = SETTINGS.default_provider
        else:
            logger.warning(
                f"LLM type '{llm_type}' not found in provider '{provider_config.type}' or defaults. Using absolute default."
            )
            llm_config = SETTINGS.default_llms.default
            provider_config = (
                SETTINGS.default_provider
            )  # Ensure provider matches absolute default

    if llm_config is None:
        raise ValueError(f"Could not determine LLM configuration for type: {llm_type}")

    # Initialize and cache the LLM
    logger.debug(
        f"Initializing LLM with key: {llm_key}, config: {llm_config.model}, provider: {provider_config.type}, temp: {temperature_value}"
    )
    llms[llm_key] = init_llm(
        provider=provider_config, model=llm_config, temperature=temperature_value
    )

    return llms[llm_key]
