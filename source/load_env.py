# Load .env file from the parent directory

from source.models.config.default_settings import Settings
from source.models.config.setup_llm import setup_llm


SETTINGS = Settings()
setup_llm(SETTINGS)
