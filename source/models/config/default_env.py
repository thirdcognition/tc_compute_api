import os
from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose

# Flag to check if the environment is already loaded
ENV_LOADED = False
env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../", ".env"))
DEFAULT_PATH = os.path.dirname(env_file)


def load_environment():
    global ENV_LOADED
    if ENV_LOADED:
        return

    load_dotenv(env_file)
    from source.models.config.logging import logger

    logger.info("Loading env: " + env_file)

    ENV_LOADED = True


# Call the function to load the environment
load_environment()

DEBUGMODE = os.getenv("LLM_DEBUG", "True") == "True" or False
DEVMODE = os.getenv("LLM_DEV", "True") == "True" or False
IN_PRODUCTION = os.getenv("TC_PRODUCTION", "False") == "True" or False

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "False") == "True" or False
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "")

set_debug(DEBUGMODE)
set_verbose(DEBUGMODE)
