from typing import Dict
from langchain.chains.hyde.base import HypotheticalDocumentEmbedder
from langchain_core.embeddings import Embeddings

# Assuming these are the correct locations after potential refactoring or existing structure
from langchain_community.embeddings import (
    HuggingFaceEmbeddings,  # Assuming local uses HF
    OllamaEmbeddings,
    HuggingFaceInferenceAPIEmbeddings,  # For HUGGINGFACE provider type
)

from source.load_env import SETTINGS
from source.models.config.llm_settings import (
    EmbeddingModelSettings,
    EmbeddingProviderSettings,
)
from source.prompts.hyde import hyde, hyde_document
from .llm_factory import get_llm  # Relative import

embeddings: Dict[str, Embeddings] = {}


def init_embeddings(
    embedding_provider: EmbeddingProviderSettings = SETTINGS.default_embedding_provider,
    embedding_model: EmbeddingModelSettings = SETTINGS.default_embeddings.default,
) -> Embeddings:
    """Initializes an embedding model based on provider configuration."""
    if embedding_provider.type == "LOCAL":
        # Assuming LOCAL provider uses HuggingFaceEmbeddings
        model_kwargs = {"device": "cpu"}  # Make device configurable?
        encode_kwargs = {
            "normalize_embeddings": True
        }  # Make normalization configurable?
        return HuggingFaceEmbeddings(
            model_name=embedding_model.model,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
    elif embedding_provider.type == "OLLAMA":
        return OllamaEmbeddings(
            model=embedding_model.model, base_url=embedding_provider.url
        )
    elif embedding_provider.type == "HUGGINGFACE":
        # Using HuggingFaceInferenceAPIEmbeddings for API access
        return HuggingFaceInferenceAPIEmbeddings(
            api_key=embedding_provider.api_key, model_name=embedding_model.model
        )
    # Add other providers like AZURE, BEDROCK if needed
    # elif embedding_provider.type == "AZURE":
    #     return AzureOpenAIEmbeddings(...)
    else:
        raise ValueError(
            f"Unsupported embedding provider type: {embedding_provider.type}"
        )


def get_embeddings(embedding_id: str) -> Embeddings:
    """
    Retrieves or initializes and caches an embedding model instance.

    Args:
        embedding_id: The identifier for the embedding model ('base', 'hyde', 'hyde_document').

    Returns:
        An initialized Embeddings instance.

    Raises:
        ValueError: If the embedding_id is unknown.
    """
    global embeddings
    if embedding_id in embeddings:
        return embeddings[embedding_id]

    if embedding_id == "base":
        embeddings[embedding_id] = init_embeddings()
    elif embedding_id == "hyde":
        # Ensure 'base' is initialized first
        if "base" not in embeddings:
            embeddings["base"] = init_embeddings()
        embeddings[embedding_id] = HypotheticalDocumentEmbedder.from_llm(
            llm=get_llm("tester"),  # Assuming 'tester' LLM is defined/available
            base_embeddings=embeddings["base"],
            prompt_template=hyde.get_chat_prompt_template(),  # Use prompt_template arg
        )
    elif embedding_id == "hyde_document":
        # Ensure 'base' is initialized first
        if "base" not in embeddings:
            embeddings["base"] = init_embeddings()
        embeddings[embedding_id] = HypotheticalDocumentEmbedder.from_llm(
            llm=get_llm("tester"),  # Assuming 'tester' LLM is defined/available
            base_embeddings=embeddings["base"],
            prompt_template=hyde_document.get_chat_prompt_template(),  # Use prompt_template arg
        )
    else:
        raise ValueError(f"Unknown embedding ID: {embedding_id}")

    return embeddings[embedding_id]
