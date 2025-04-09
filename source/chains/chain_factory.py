from typing import Dict, Union
from langchain_core.runnables import RunnableSequence
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain

# from source.load_env import SETTINGS # Removed unused import
from source.models.config.default_env import DEVMODE
from source.prompts.base import PromptFormatter

# Import base chain types
from .base import BaseChain
from .chain import Chain

# Import LLM factory function
from .llm_factory import get_llm

# --- Import ALL necessary prompt formatters ---
# Actions
from source.prompts.actions import (
    action,
    summary,
    summary_guided,
    summary_with_title,
    question_classifier,
    check,
    grader,
    combine_description,
)

# Formatters
from source.prompts.formatters import (
    text_formatter,
    text_formatter_simple,
    text_formatter_compress,
    text_formatter_guided,
    text_formatter_compress_guided,
    md_formatter,
    md_formatter_guided,
)

# Topics
from source.prompts.topics import (
    page_formatter,
    page_formatter_guided,
    topic_formatter,
    topic_formatter_guided,
    topic_hierarchy,
    topic_combiner,
)

# Concepts
from source.prompts.concepts import (
    concept_structured,
    concept_more,
    concept_hierarchy,
    concept_combiner,
)

# Chat
from source.prompts.chat import chat, question, helper

# Panel - Quality
from source.prompts.panel.quality import verify_transcript_quality

# Panel - Modify
from source.prompts.panel.modify import (
    transcript_rewriter,
    transcript_rewriter_extend,
    transcript_rewriter_reduce,
    transcript_compress,
    transcript_extend,
    transcript_translate,
)

# Panel - Structure
from source.prompts.panel.structure import (
    transcript_combiner,
    transcript_writer,
    transcript_bridge_writer,
    transcript_intro_writer,
    transcript_conclusion_writer,
    transcript_short_intro_writer,
    transcript_short_conclusion_writer,
)

# Panel - Summary
from source.prompts.panel.summary import transcript_summary_formatter

# Web Source
from source.prompts.web_source import (
    web_source_builder,
    group_web_sources,
    group_rss_items,
    validate_news_article,
)

# --- End Prompt Imports ---


# Global cache for initialized chains
chains: Dict[str, Union[BaseChain, RunnableSequence]] = {}


def init_chain(
    id: str,
    prompt: PromptFormatter,
    retry_id: str = None,
    validate_id: str = "instruct",
    check_for_hallucinations=False,
    ChainType: type[BaseChain] = Chain,  # Use type hint for class
    sync_mode: bool = False,
) -> BaseChain:
    """Initializes a chain instance with specified LLMs and prompt."""
    if retry_id is None:
        # Default retry LLM based on whether the main LLM ID suggests structured output
        retry_id = "structured_detailed" if "structured" in id else "instruct_detailed"

    # Determine the validation LLM
    validation_llm_instance = None
    if check_for_hallucinations and not DEVMODE:
        validation_llm_instance = get_llm(validate_id)

    # Create the chain instance
    chain_instance = ChainType(
        llm=get_llm(id),
        retry_llm=get_llm(retry_id),
        prompt=prompt,
        validation_llm=validation_llm_instance,
        async_mode=not sync_mode,  # async_mode is the opposite of sync_mode
    )
    # Set a name for easier debugging/tracing if needed
    chain_instance.name = f"chain-{id}"
    return chain_instance


# Configuration mapping chain IDs to their setup parameters
# Format: chain_id: (llm_id, prompt_formatter, check_hallucinations, sync_mode)
CHAIN_CONFIG: Dict[str, tuple[str, PromptFormatter, bool, bool]] = {
    "combine_bullets": ("instruct", combine_description, False, False),
    "summary": (
        "instruct_detailed" if not DEVMODE else "instruct",
        summary,
        True,
        False,
    ),
    "summary_guided": (
        "instruct_detailed" if not DEVMODE else "instruct",
        summary_guided,
        True,
        False,
    ),
    "summary_with_title": (
        "structured_detailed" if not DEVMODE else "structured",
        summary_with_title,
        True,
        False,
    ),
    "action": ("instruct_0", action, False, False),
    "grader": ("structured", grader, False, False),
    "check": ("instruct_0", check, False, False),
    "text_formatter_simple": ("instruct", text_formatter_simple, False, False),
    "text_formatter_simple_sync": ("instruct", text_formatter_simple, False, True),
    "text_formatter": ("instruct", text_formatter, False, False),
    "text_formatter_compress": ("instruct", text_formatter_compress, False, False),
    "text_formatter_guided": (
        "instruct_detailed_0" if not DEVMODE else "instruct_0",
        text_formatter_guided,
        True,
        False,
    ),
    "text_formatter_compress_guided": (
        "instruct_detailed_0" if not DEVMODE else "instruct_0",
        text_formatter_compress_guided,
        True,
        False,
    ),
    "md_formatter": ("instruct", md_formatter, False, False),
    "md_formatter_guided": (
        "instruct_detailed_0" if not DEVMODE else "instruct_0",
        md_formatter_guided,
        True,
        False,
    ),
    "page_formatter": ("instruct", page_formatter, True, False),
    "page_formatter_guided": (
        "instruct_detailed_0" if not DEVMODE else "instruct_0",
        page_formatter_guided,
        True,
        False,
    ),
    "topic_formatter": ("instruct", topic_formatter, True, False),
    "topic_formatter_guided": (
        "instruct_detailed_0" if not DEVMODE else "instruct_0",
        topic_formatter_guided,
        True,
        False,
    ),
    "topic_hierarchy": (
        "structured_detailed" if not DEVMODE else "structured",
        topic_hierarchy,
        False,
        False,
    ),
    "topic_combiner": (
        "structured_detailed" if not DEVMODE else "structured",
        topic_combiner,
        False,
        False,
    ),
    "concept_structured": ("structured", concept_structured, False, False),
    "concept_more": ("structured", concept_more, False, False),
    "concept_hierarchy": (
        "structured_detailed" if not DEVMODE else "structured",
        concept_hierarchy,
        False,
        False,
    ),
    "concept_combiner": (
        "structured_detailed" if not DEVMODE else "structured",
        concept_combiner,
        False,
        False,
    ),
    "question": ("chat", question, True, False),
    "helper": ("chat", helper, False, False),
    "chat": ("chat", chat, False, False),
    "question_classification": (
        "tester",
        question_classifier,
        False,
        False,
    ),  # Assuming 'tester' LLM exists
    "web_source_builder": ("structured", web_source_builder, True, False),
    "web_source_builder_sync": ("structured", web_source_builder, True, True),
    "transcript_writer": (
        "instruct_detailed_warm",
        transcript_writer,
        True,
        True,
    ),
    "verify_transcript_quality": (
        "instruct_detailed",
        verify_transcript_quality,
        False,
        True,
    ),
    "transcript_rewriter": (
        "instruct_detailed",
        transcript_rewriter,
        True,
        True,
    ),
    "transcript_rewriter_extend": (
        "instruct_detailed",
        transcript_rewriter_extend,
        True,
        True,
    ),
    "transcript_rewriter_reduce": (
        "instruct_detailed",
        transcript_rewriter_reduce,
        True,
        True,
    ),
    "transcript_combiner": (
        "instruct_detailed_warm",
        transcript_combiner,
        True,
        True,
    ),
    "transcript_bridge_writer": (
        "instruct",
        transcript_bridge_writer,
        False,
        True,
    ),
    "transcript_intro_writer": (
        "instruct",
        transcript_intro_writer,
        False,
        True,
    ),
    "transcript_conclusion_writer": (
        "instruct",
        transcript_conclusion_writer,
        False,
        True,
    ),
    "transcript_short_intro_writer": (
        "instruct",
        transcript_short_intro_writer,
        False,
        True,
    ),
    "transcript_short_conclusion_writer": (
        "instruct",
        transcript_short_conclusion_writer,
        False,
        True,
    ),
    "transcript_compress": (
        "instruct_detailed",
        transcript_compress,
        False,
        True,
    ),
    "transcript_extend": (
        "instruct_detailed",
        transcript_extend,
        False,
        True,
    ),
    "transcript_translate": (
        "instruct_detailed",
        transcript_translate,
        False,
        True,
    ),
    "transcript_summary_formatter": (
        "structured_warm",
        transcript_summary_formatter,
        True,
        False,
    ),
    "transcript_summary_formatter_sync": (
        "structured_warm",
        transcript_summary_formatter,
        True,
        True,
    ),
    "group_web_sources": (
        "instruct",
        group_web_sources,
        False,
        False,
    ),
    "group_web_sources_sync": (
        "instruct",
        group_web_sources,
        False,
        True,
    ),
    "group_rss_items": (
        "instruct_detailed",
        group_rss_items,
        False,
        False,
    ),
    "group_rss_items_sync": (
        "instruct_detailed",
        group_rss_items,
        False,
        True,
    ),
    "validate_news_article": (
        "instruct",
        validate_news_article,
        False,
        False,
    ),
    "validate_news_article_sync": (
        "instruct",
        validate_news_article,
        False,
        True,
    ),
}


def get_base_chain(chain_id: str) -> Union[BaseChain, RunnableSequence]:
    """Retrieves or initializes and caches a base chain instance (or RunnableSequence for special cases)."""
    global chains
    if chain_id in chains:
        return chains[chain_id]

    if chain_id in CHAIN_CONFIG:
        llm_id, prompt, check_for_hallucinations, sync_mode = CHAIN_CONFIG[chain_id]
        chains[chain_id] = init_chain(
            id=llm_id,  # Pass the LLM ID correctly
            prompt=prompt,
            check_for_hallucinations=check_for_hallucinations,
            sync_mode=sync_mode,
        )
        return chains[chain_id]

    # Handle special chain types that are composed differently
    if chain_id == "stuff_documents":
        # Requires 'text_formatter_compress' chain to be defined in CHAIN_CONFIG
        base_compress_chain = get_base_chain("text_formatter_compress")
        if not isinstance(base_compress_chain, BaseChain):
            raise TypeError(
                "Expected 'text_formatter_compress' to be a BaseChain instance for 'stuff_documents'"
            )

        chains[chain_id] = create_stuff_documents_chain(
            llm=base_compress_chain.llm,  # Pass the LLM from the base chain
            prompt=base_compress_chain.prompt.get_chat_prompt_template(),
            output_parser=base_compress_chain.prompt.parser,
            # document_prompt=..., # Optional: Define how each document is formatted
            # document_separator="\n\n", # Optional: Define separator
        )
        return chains[chain_id]

    if chain_id == "summary_documents":
        # Requires 'stuff_documents' and 'summary' chains
        chains[chain_id] = get_chain("stuff_documents") | get_chain("summary")
        return chains[chain_id]

    if chain_id == "summary_documents_with_title":
        # Requires 'stuff_documents' and 'summary_with_title' chains
        chains[chain_id] = get_chain("stuff_documents") | get_chain(
            "summary_with_title"
        )
        return chains[chain_id]

    raise ValueError(f"Unknown chain identifier: {chain_id}")


def get_chain(
    chain_id: str, custom_prompt: tuple[str, str] | None = None
) -> RunnableSequence:
    """
    Retrieves a runnable chain, potentially configuring it with a custom prompt.

    Args:
        chain_id: The identifier of the chain to retrieve.
        custom_prompt: An optional tuple (system_message, user_message) for custom prompts.

    Returns:
        The configured RunnableSequence.
    """
    base_chain_instance = get_base_chain(chain_id)

    # If it's a BaseChain instance, call it to get the runnable sequence, potentially with custom prompt
    if isinstance(base_chain_instance, BaseChain):
        return base_chain_instance(custom_prompt=custom_prompt)
    # Otherwise (e.g., for composed chains like stuff_documents), return the instance directly
    else:
        # Custom prompts typically don't apply directly to pre-composed sequences
        if custom_prompt:
            # Log a warning or decide how to handle this case
            print(
                f"Warning: Custom prompt provided for non-BaseChain instance '{chain_id}'. Prompt may not be applied."
            )
        return base_chain_instance
