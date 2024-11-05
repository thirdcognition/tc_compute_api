from typing import Any, Dict, List, Optional, Union
from fastapi import Request
from supabase import AsyncClient

from app.core.supabase import get_oath2, get_supabase_client

async def per_req_config_modifier(config: Dict, request: Request) -> Dict:
    """Modify the config for each request."""
    token = await get_oath2(request)
    supa_client: AsyncClient = await get_supabase_client(token)
    config["configurable"] = {}
    # Attention: Make sure that the user ID is over-ridden for each request.
    # We should not be accepting a user ID from the user in this case!
    config["configurable"]["supa_client"] = supa_client
    return config