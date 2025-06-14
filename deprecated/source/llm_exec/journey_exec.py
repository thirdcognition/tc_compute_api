import asyncio
from source.chains import get_chain  # Updated import
from source.helpers.journey import match_title_to_cat_and_key
from source.load_env import SETTINGS


async def get_journey_template_id_with_role(role_title, role_description) -> str:
    matching_ids = None
    retry_count = 0

    matching_ids = ["", "digital_marketing_specialist"]
    while not matching_ids and retry_count < SETTINGS.langchain_retries.max_count:
        result = await get_chain("journey_template_selector").ainvoke(
            {
                "job_description": f"Title:\n{role_title.strip()}\n\nDescription:\n{role_description.strip()}"
            }
        )

        matching_ids = match_title_to_cat_and_key(result)

        if not matching_ids:
            await asyncio.sleep(
                SETTINGS.langchain_retries.retry_timeout if retry_count > 1 else 1
            )

    return matching_ids[1]  # Pass supabase
