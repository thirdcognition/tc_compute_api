import re
from typing import List, Optional
from google.cloud import translate_v2 as translate
from google.auth.credentials import AnonymousCredentials
from source.load_env import SETTINGS
from source.prompts.panel.base import TranscriptParser


LANGUAGE_NAME_TO_ISO: dict
translate_client: translate.Client = None


def string_to_iso_code(language_name: str) -> Optional[str]:
    """
    Converts a language name to its ISO language code.

    Args:
        language_name (str): The name of the language (e.g., 'Spanish', 'French').

    Returns:
        Optional[str]: The ISO language code (e.g., 'es', 'fr') if found, otherwise None.
    """
    global translate_client
    # Initialize the Google Translate client
    translate_client = translate_client or translate.Client(
        credentials=AnonymousCredentials(),
        client_options={"api_key": SETTINGS.google_translate_api_key},
    )

    # Fetch supported languages and build the mapping
    global LANGUAGE_NAME_TO_ISO
    LANGUAGE_NAME_TO_ISO = LANGUAGE_NAME_TO_ISO or {
        str(lang["name"]).lower(): lang["language"]
        for lang in translate_client.get_languages()
    }

    return LANGUAGE_NAME_TO_ISO.get(language_name.lower())


def translate_transcript(transcript: str, target_language: str) -> str:
    lang_code = string_to_iso_code(target_language)
    blocks = TranscriptParser.split_blocks(transcript)
    stripped_ids = []
    stripped_blocks = []
    for block in blocks:
        matches = re.findall(r"<person\[(.*?)\]>\((.*?)\)</person\[\1\]>", block)
        for match1, match2 in matches:
            stripped_blocks.append(match2)
            stripped_ids.append(match1)

    translated_blocks = translate_strings(
        target_language=lang_code,
        strings=stripped_blocks,
    )

    return "\n".join(
        [
            f"<Person{stripped_ids[i]}>{translated_blocks[i]}</Person{stripped_ids[i]}>"
            for i in range(len(translated_blocks))
        ]
    )


def translate_strings(strings: List[str], target_language: str) -> List[str]:
    """
    Translates a list of strings from English to the target language using Google Translate v3.

    Args:
        strings (List[str]): List of strings to translate.
        target_language (str): Target language code (e.g., 'es' for Spanish, 'fr' for French).

    Returns:
        List[str]: List of translated strings.
    """

    # Initialize the Google Translate client
    global translate_client
    # Initialize the Google Translate client
    translate_client = translate_client or translate.Client(
        credentials=AnonymousCredentials(),
        client_options={"api_key": SETTINGS.google_translate_api_key},
    )

    # Perform batch translation
    response = translate_client.translate(strings, target_language=target_language)

    # Extract and return the translated texts
    return [result["translatedText"] for result in response]
