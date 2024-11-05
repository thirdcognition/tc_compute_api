import importlib
import logging
import os
from enum import Enum
from types import MappingProxyType, ModuleType
from typing import Union
from app.core.enums import LanguageModel, LanguageModelService, ollama_models_llm, ollama_models_chat
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.callbacks.base import BaseCallbackHandler
from app.prompts.base import DEFAULT_PROMPT_FORMATTER, PromptFormatter
from app.core.config import settings

# Define the default prompt
DEFAULT_PROMPT = PromptTemplate.from_template("This is the default prompt.")

def load_prompt_formatter(
    prompt_id: str,
    llm: LanguageModel = settings.LLM_MODEL,
    llm_service: LanguageModelService = settings.LLM_SERVICE,
) -> PromptFormatter:
    """
    Load a prompt formatter based on the provided prompt_id, llm, and llm_service.
    Args:
        prompt_id (str): The ID of the prompt to load.
        llm (LanguageModel): The language model for which to load the prompt.
        llm_service (LanguageModelService): The language model service for which to load the prompt.

    Returns:
        PromptFormatter] The loaded prompt formatter, or DefaultPromptFormatter if an error occurs.
    """
    try:
        # Dynamically import the prompt module with the llm and llm_service
        print(f"Load prompt app.prompts.{llm_service.value}.{llm.value}")
        prompt_module: ModuleType = importlib.import_module(
            f"app.prompts.{llm_service.value}.{llm.value}"
        )

        # Check if the prompt exists for the given llm and llm_service in the module
        if not hasattr(prompt_module, prompt_id):
            logging.warning(
                f"The {prompt_id} does not exist for {llm.name} with {llm_service.name}. Using default prompt."
            )
            return DEFAULT_PROMPT_FORMATTER

        # Get the prompt template for the given llm and llm_service from the module
        prompt_formatter: PromptFormatter = getattr(prompt_module, prompt_id)
        return prompt_formatter
    except Exception as e:
        logging.error(
            f"An error occurred while importing the module: {str(e)}. Using default prompt."
        )
        return DEFAULT_PROMPT_FORMATTER


initialized_llms: dict[str : Union[BaseLanguageModel, Embeddings]] = {}

# Define the enum for the language model types
class LanguageModelType(Enum):
    LLM = "llm"
    CHAT = "chat"
    EMBEDDING = "embedding"


def get_llm_model(
    service: LanguageModelService = settings.LLM_SERVICE,
    model_type: LanguageModelType = LanguageModelType.LLM,
) -> Union[BaseLanguageModel, Embeddings]:

    if service == LanguageModelService.OLLAMA:
        if model_type == LanguageModelType.CHAT:
            from langchain_community.chat_models import ChatOllama

            return ChatOllama
        elif model_type == LanguageModelType.EMBEDDING:
            from langchain_community.embeddings import OllamaEmbeddings

            return OllamaEmbeddings
        else:
            from langchain_community.llms.ollama import Ollama

            return Ollama
    elif service == LanguageModelService.OPENAI:
        if model_type == LanguageModelType.CHAT:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI
        elif model_type == LanguageModelType.EMBEDDING:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings
        else:
            from langchain_openai import OpenAI

            return OpenAI
    elif service == LanguageModelService.AMAZON_BEDROCK:
        if model_type == LanguageModelType.CHAT:
            from langchain_aws import ChatBedrock

            return ChatBedrock
        elif model_type == LanguageModelType.EMBEDDING:
            from langchain_aws import BedrockEmbeddings

            return BedrockEmbeddings
        else:
            from langchain_aws import BedrockLLM

            return BedrockLLM
    elif service == LanguageModelService.MICROSOFT_AZURE:
        if model_type == LanguageModelType.LLM or model_type == LanguageModelType.CHAT:
            from langchain_community.llms.azureml_endpoint import AzureMLOnlineEndpoint

            return AzureMLOnlineEndpoint
        elif model_type == LanguageModelType.EMBEDDING:
            from langchain_openai import AzureOpenAIEmbeddings

            return AzureOpenAIEmbeddings
    elif service == LanguageModelService.HUGGINGFACE:
        if model_type == LanguageModelType.CHAT:
            from langchain_huggingface import ChatHuggingFace

            return ChatHuggingFace
        elif model_type == LanguageModelType.EMBEDDING:
            from langchain_huggingface import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings
        else:
            from langchain_huggingface import HuggingFacePipeline

            return HuggingFacePipeline
    else:
        raise ValueError(
            f"No LLMModel found for service: {service} and model type: {model_type}"
        )


## TODO implement rest of the custom model args for different providers.
def map_custom_args_to_model_args(
    custom_args,
    service: LanguageModelService = LanguageModelService.OLLAMA,
    model_type: LanguageModelType = LanguageModelType.LLM,
):
    model_args = {}

    if model_type is not LanguageModelType.EMBEDDING:
        model_args = {}
        if "verbose" in custom_args:
            model_args["verbose"] = custom_args["verbose"]
        if "callbacks" in custom_args:
            model_args["callbacks"] = custom_args["callbacks"]
        if "temperature" in custom_args:
            model_args["temperature"] = custom_args["temperature"]
        if "repeat_penalty" in custom_args:
            model_args["repeat_penalty"] = custom_args["repeat_penalty"]
        if "timeout" in custom_args:
            model_args["timeout"] = custom_args["timeout"]

    if service == LanguageModelService.OLLAMA:
        model_args = {
            **model_args,
            "model": custom_args["model"],
            "base_url": custom_args["base_url"] if  "base_url" in custom_args else settings.OLLAMA_HOST,
        }
        if model_type is not LanguageModelType.EMBEDDING:
            ctx_size = custom_args["ctx_size"] if custom_args else settings.LLM_CTX_SIZE

            model_args = {
                **model_args,
                "num_ctx": ctx_size,
                "num_predict": ctx_size,
            }

    return model_args


def init_llm(
    model: str = ollama_models_llm[settings.LLM_MODEL],
    service: LanguageModelService = settings.LLM_SERVICE,
    model_type: LanguageModelType = LanguageModelType.LLM,
    temperature: float = settings.LLM_TEMPERATURE,
    ctx_size: int = settings.LLM_CTX_SIZE,
    callbacks: list[BaseCallbackHandler] = None,
    verbose: bool = False,
    **kwargs,
) -> Union[BaseLanguageModel, Embeddings]:
    if model == ollama_models_llm[settings.LLM_MODEL] and model_type == LanguageModelType.CHAT:
        model = ollama_models_chat[settings.LLM_MODEL]

    global initialized_llms
    id = (
        f"{model}_{service.value}_{model_type.value}_{str(temperature)}_{str(ctx_size)}"
    )

    if id in initialized_llms:
        return initialized_llms[id]

    LLMModel = get_llm_model(service, model_type)

    if LLMModel is None:
        raise ValueError(
            "LLMModel must be provided if the LLM is not already initialized."
        )

    custom_args = {
        "model": model,
        "verbose": verbose,
        "callbacks": callbacks,
        "ctx_size": ctx_size,
        "temperature": temperature,
    }

    model_args = map_custom_args_to_model_args(custom_args, service, model_type)

    llm_kwargs = {
        **model_args,
        **kwargs,
    }

    print(f"Initializing LLM with args: {llm_kwargs =}")

    llm = LLMModel(**llm_kwargs)

    initialized_llms[id] = llm
    return llm
