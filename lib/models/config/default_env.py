import os
from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose

load_dotenv(os.path.join(os.path.dirname(__file__), "../", ".env"))
print("Loading env: ", os.path.join(os.path.dirname(__file__), "../", ".env"))

DEBUGMODE = os.getenv("LLM_DEBUG", "True") == "True" or False
DEVMODE = os.getenv("LLM_DEV", "True") == "True" or False
IN_PRODUCTION = os.getenv("TC_PRODUCTION", "False") == "True" or False

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "False") == "True" or False
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "")

set_debug(DEBUGMODE)
set_verbose(DEBUGMODE)
