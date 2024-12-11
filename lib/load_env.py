# Load .env file from the parent directory

from lib.models.config.default_settings import Settings
from lib.models.config.setup_llm import setup_llm


SETTINGS = Settings()
setup_llm(SETTINGS)
