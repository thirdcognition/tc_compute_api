from langchain_core.language_models.llms import BaseLLM
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
from langchain_google_genai import ChatGoogleGenerativeAI

LLM_MODEL_MAP: dict[str, BaseLLM] = {
    "OLLAMA": ChatOllama,
    "GROQ": ChatGroq,
    "BEDROCK": ChatBedrock,
    "OPENAI": ChatOpenAI,
    "ANTHROPIC": ChatAnthropic,
    "AZURE": AzureChatOpenAI,
    "AZURE_ML": AzureMLChatOnlineEndpoint,
    "GEMINI": ChatGoogleGenerativeAI,  # Added Google Gemini
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
