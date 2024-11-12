from functools import cache
import json
import os
from uuid import UUID
import aiofiles  # Import aiofiles for asynchronous file operations

from app.core.supabase import get_supabase_service_client
from lib.load_env import SETTINGS
from lib.models.structures.journey_template_json import (
    JourneyTemplateIndex,
    JourneyTemplateMapping,
    TemplateKeyToFileMapping,
)
from supabase.client import AsyncClient

from lib.models.supabase.journey_template import JourneyTemplateModel

journey_template_dir = os.path.join(
    SETTINGS.file_repository_path, "llm/journey_structures_json"
)


def get_available_journey_template_roles(
    as_str: bool = False, journey_template_dir: str = journey_template_dir
) -> dict[list] | str:
    with open(
        os.path.join(journey_template_dir, "knowledge_services_roles.json"), "r"
    ) as f:
        roles: dict = json.load(f)

    filtered_roles = {}
    filtered_str = ""
    mapping = get_journey_template_mapping(journey_template_dir)
    for category in roles:
        for role in roles[category]:
            cat_id, role_id = match_title_to_cat_and_key(role, journey_template_dir)
            if any(pair.key == role_id for pair in mapping.pairs):
                if filtered_roles.get(category) is None:
                    filtered_str += f"\nCategory: {category}\n"
                    filtered_roles[category] = []
                filtered_roles[category].append(role)
                filtered_str += f"Role: {role}\n"

    if as_str:
        return filtered_str

    return filtered_roles


@cache
def get_journey_template_index(
    journey_template_dir: str = journey_template_dir,
) -> JourneyTemplateIndex:
    with open(os.path.join(journey_template_dir, "structured/index.json"), "r") as f:
        data = json.load(f)
        return JourneyTemplateIndex(categories=data)


@cache
def get_journey_template_mapping(
    journey_template_dir: str = journey_template_dir,
) -> JourneyTemplateMapping:
    with open(os.path.join(journey_template_dir, "structured/mappings.json"), "r") as f:
        data = json.load(f)
        pairs = [TemplateKeyToFileMapping(key=k, file_path=v) for k, v in data.items()]
        return JourneyTemplateMapping(pairs=pairs)


def match_title_to_cat_and_key(
    title: str, journey_template_dir: str = journey_template_dir
) -> tuple[str, str]:
    index: JourneyTemplateIndex = get_journey_template_index(journey_template_dir)
    for cat in index.categories:
        for item in cat.children:
            if item.title == title:
                return cat.key, item.key
    return None


@cache
async def load_journey_template(
    supabase: AsyncClient,
    item_id: str,
    journey_template_dir: str = journey_template_dir,
) -> tuple[UUID, UUID]:
    mapping = get_journey_template_mapping(journey_template_dir)
    filepath = next(
        (pair.file_path for pair in mapping.pairs if pair.key == item_id), None
    )
    if filepath:
        async with aiofiles.open(
            os.path.join(journey_template_dir, "structured", f"{filepath}"), "r"
        ) as f:
            data = json.loads(await f.read())  # Read file asynchronously
            service_client: AsyncClient = await get_supabase_service_client()
            return await JourneyTemplateModel.from_json(
                service_client, data
            )  # Use the passed supabase
