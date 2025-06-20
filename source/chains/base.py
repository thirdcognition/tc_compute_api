import asyncio
import re
from typing import Dict
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from openai import RateLimitError
from google.api_core.exceptions import ResourceExhausted

# , BadRequestError
from random import randint
from time import sleep

from source.helpers.shared import print_params
from source.prompts.base import PromptFormatter


def extract_delay_from_error(error_message: str) -> int:
    print(f"Retry parse {error_message=}")

    # Match case 1: "retry after X seconds"
    match = re.search(r"retry after (\d+) seconds", error_message, re.IGNORECASE)
    if match:
        return int(match.group(1)) + randint(3, 9)

    # Match case 2: "_chat_with_retry in X seconds"
    match = re.search(r"in (\d+) seconds", error_message, re.IGNORECASE)
    if match:
        return int(match.group(1)) + randint(3, 9)

    # Fallback if no match is found
    return randint(10, 60)


def keep_chain_params(params: Dict):
    print_params(params)
    if "orig_params" in params.keys() and isinstance(params["orig_params"], Dict):
        set_params = params["orig_params"]
        for key in set_params.keys():
            params[key] = set_params[key]
        # params.pop("orig_params", None)
    params["orig_params"] = params.copy()
    return params


def log_chain_params(params):
    print_params("Log params", params)
    return params


def get_error_message(params):
    error_message = {}
    if isinstance(params, dict):
        error_message = params.get("rate_limit_error", {})

    if isinstance(error_message, dict):
        if "error" in error_message.keys():
            error_message = error_message.get("error")
        return error_message.get("message", "")

    if isinstance(error_message, RateLimitError):
        return error_message.message

    if isinstance(error_message, ResourceExhausted):
        return error_message.message


# Retry logic for RateLimitError
def retry_with_delay(chain: RunnableSequence, async_mode: bool = False):
    if async_mode:

        async def retry(params):
            delay = extract_delay_from_error(get_error_message(params))
            print(f"Retrying after {delay} seconds due to RateLimitError...")
            await asyncio.sleep(delay)
            return await chain.ainvoke(params)

    else:

        def retry(params):
            delay = extract_delay_from_error(get_error_message(params))
            print(f"Retrying after {delay} seconds due to RateLimitError...")
            sleep(delay)
            return chain.invoke(params)

    return chain.with_fallbacks(
        [RunnableLambda(retry), RunnableLambda(retry)],
        exceptions_to_handle=(RateLimitError, ResourceExhausted),
        exception_key="rate_limit_error",
    )


class BaseChain:
    def __init__(
        self,
        parent_chain: RunnableSequence | None = None,
        prompt: PromptFormatter | None = None,
        llm: RunnableSequence | None = None,
        custom_prompt: tuple[str, str] | None = None,
        async_mode: bool = False,
        structured_mode: bool = False,
        max_retries: int = 3,  # New parameter for maximum retries
    ):
        if not hasattr(self, "parent_chain") or self.parent_chain is None:
            self.parent_chain = parent_chain
        if not hasattr(self, "llm") or self.llm is None:
            self.llm = llm
        if not hasattr(self, "prompt") or self.prompt is None:
            self.prompt = prompt
        if not hasattr(self, "custom_prompt") or self.custom_prompt is None:
            self.custom_prompt = custom_prompt
        if not hasattr(self, "chain"):
            self.chain = None
        if not hasattr(self, "prompt_template"):
            self.prompt_template = None

        self.async_mode = async_mode
        self.structured_mode = structured_mode
        self.max_retries = max_retries  # Store max retries

        self.id = f"{self.__class__.__name__}-{id(self)}"
        self.name = self.id

    def _setup_prompt(self, custom_prompt: tuple[str, str] | None = None):
        if self.prompt is not None and (
            self.prompt_template is None or custom_prompt is not None
        ):
            if custom_prompt is not None:
                self.custom_prompt = custom_prompt

            if self.custom_prompt is None:
                self.prompt_template = self.prompt.get_chat_prompt_template()
            else:
                self.prompt_template = self.prompt.get_chat_prompt_template(
                    custom_system=self.custom_prompt[0],
                    custom_user=self.custom_prompt[1],
                )

    def __call__(
        self, custom_prompt: tuple[str, str] | None = None
    ) -> RunnableSequence:
        if self.chain is not None and (
            custom_prompt is None or repr(self.custom_prompt) == repr(custom_prompt)
        ):
            return self.chain

        self._setup_prompt(custom_prompt)

        if self.parent_chain is not None and self.llm is not None:
            self.chain = self.parent_chain | self.prompt_template | self.llm
        elif self.llm is not None:
            self.chain = self.prompt_template | self.llm | StrOutputParser()
        elif self.parent_chain is not None:
            self.chain = self.parent_chain
        else:
            raise ValueError("Either parent_chain or prompt_template must be provided.")

        self.chain = retry_with_delay(self.chain, self.async_mode)

        self.chain.name = f"{self.name}-base"

        return self.chain
