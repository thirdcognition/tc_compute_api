import logging
import os
from typing import ClassVar, Union
import toml

from app.core.enums import LanguageModel, LanguageModelService

# Load the pyproject.toml file
with open("pyproject.toml", "r") as f:
    pyproject = toml.load(f)

# Get the project name
project_name = pyproject["tool"]["poetry"]["name"]


from dotenv import load_dotenv
from pydantic import AnyHttpUrl, ConfigDict, Field, IPvAnyAddress
from pydantic_settings import BaseSettings

log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")

# root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)
load_dotenv()


class Settings(BaseSettings):
    # API_V1_STR: str = "/api/v1"
    SUPABASE_URL: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL"))
    SUPABASE_KEY: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY"))
    SUPABASE_SERVICE_KEY: str = Field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_KEY"))
    # SUPERUSER_EMAIL: str = Field(default_factory=lambda: os.getenv("SUPERUSER_EMAIL"))
    # SUPERUSER_PASSWORD: str = Field(default=lambda: os.getenv("SUPERUSER_PASSWORD"))
    # SERVER_NAME: str
    SERVER_HOST: IPvAnyAddress = Field(default_factory=lambda: os.getenv("SERVER_HOST", "0.0.0.0"))
    SERVER_PORT: int = Field(default_factory=lambda: os.getenv("SERVER_PORT", 8000))
    # # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [""]
    BACKEND_CORS_ORIGINS: list[Union[AnyHttpUrl, str]] = ["*"]
    #
    # @validator("BACKEND_CORS_ORIGINS", pre=True)
    # def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
    #     if isinstance(v, str) and not v.startswith("["):
    #         return [i.strip() for i in v.split(",")]
    #     elif isinstance(v, (list, str)):
    #         return v
    #     raise ValueError(v)
    #
    PROJECT_NAME: str = Field(default=project_name)

    LLM_TIMEOUT: int = Field(default_factory=lambda: int(os.getenv("LLM_TIMEOUT", 20 * 1000)))
    LLM_REPEAT_PENALTY: float = Field(default_factory=lambda: float(os.getenv("LLM_REPEAT_PENALTY", 1.5)))
    LLM_CTX_SIZE: int = Field(default_factory=lambda: int(os.getenv("LLM_CTX_SIZE", 8192)))
    LLM_TEMPERATURE: float = Field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", 0.0)))
    LLM_SERVICE: LanguageModelService = Field(default_factory=lambda: LanguageModelService(os.getenv("LLM_SERVICE", LanguageModelService.OLLAMA.value)))
    LLM_MODEL: LanguageModel = Field(default_factory=lambda: LanguageModel(os.getenv("LLM_MODEL", LanguageModel.DOLPHIN.value)))
    OLLAMA_HOST: str = Field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))
    SUPABASE_CACHE_TTL: int = Field(default_factory=lambda: int(os.getenv("SUPABASE_CACHE_TTL", 30)))
    SUPABASE_CACHE_SIZE: int = Field(default_factory=lambda: int(os.getenv("SUPABASE_CACHE_SIZE", 100)))

    # class Config(ConfigDict):
    #     """sensitive to lowercase"""
    #
    #     case_sensitive = True
    Config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)


settings = Settings()
