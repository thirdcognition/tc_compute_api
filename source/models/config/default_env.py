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

    ENV_LOADED = True


# Call the function to load the environment
load_environment()

DEBUGMODE = os.getenv("LLM_DEBUG", "True").lower() == "true" or False
DEVMODE = os.getenv("LLM_DEV", "True").lower() == "true" or False
IN_PRODUCTION = os.getenv("TC_PRODUCTION", "False").lower() == "true" or False

LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "False").lower() == "true" or False
LANGSMITH_TRACING_V2 = (
    os.getenv("LANGSMITH_TRACING_V2", "False").lower() == "true" or False
)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "")

_langsmith_debug_msg = False


def langsmith_tracing_debug():
    global ENV_LOADED
    if not ENV_LOADED:
        return

    global _langsmith_debug_msg
    if _langsmith_debug_msg:
        return

    _langsmith_debug_msg = True

    global LANGSMITH_TRACING
    global LANGSMITH_TRACING_V2
    global LANGSMITH_PROJECT

    from source.models.config.logging import logger

    logger.info("Loading env: " + env_file)

    logger.info(
        f"Langsmith is tracing {'enabled' if (LANGSMITH_TRACING or LANGSMITH_TRACING_V2) else 'disabled'}"
    )
    if LANGSMITH_TRACING_V2 or LANGSMITH_TRACING:
        logger.info(f"\t{LANGSMITH_PROJECT=}")


langsmith_tracing_debug()

set_debug(DEBUGMODE)
set_verbose(DEBUGMODE)
