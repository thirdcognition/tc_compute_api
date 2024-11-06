import enum
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from supabase.client import AsyncClient
from postgrest import APIResponse

from lib.load_env import logger


class SupabaseModel(BaseModel):
    dirty: bool = Field(default=True)

    def __setattr__(self, name: str, value: Any):
        if name != "dirty":
            current_value = getattr(self, name, None)
            if current_value != value:
                self.dirty = True
        super().__setattr__(name, value)

    async def save_to_supabase(
        self, supabase: AsyncClient, table_name: str, on_conflict: List[str] = ["id"]
    ) -> "SupabaseModel":
        if self.dirty:
            data = self.model_dump_json(
                exclude_none=True,
                exclude_unset=True,
                exclude={
                    "created_at",
                    "disabled_at",
                    "dirty",
                    "updated_by",
                    "updated_at",
                },
            )
            data = json.loads(data)

            # Convert enum types to strings
            for key, value in data.items():
                if isinstance(value, enum.Enum):
                    data[key] = value.name

            # print(f"{data =}")
            if len(on_conflict) == 1:
                response = (
                    await supabase.table(table_name)
                    .upsert(data, on_conflict=on_conflict)
                    .execute()
                )
            else:
                query = supabase.table(table_name).select("*")
                for key in on_conflict:
                    query = query.eq(key, data[key])
                response: APIResponse = await query.execute()
                if response.data:
                    query = supabase.table(table_name).update(data)
                    for key in on_conflict:
                        query = query.eq(key, data[key])
                    response = await query.execute()
                else:
                    response = await supabase.table(table_name).insert(data).execute()

            # Update the model with the data from the response
            if response.data:
                for key, value in response.data[0].items():
                    self._set_attribute(key, value)
                self.dirty = False

        return self

    async def fetch_from_supabase(
        self, supabase: AsyncClient, table_name: str, value: Any
    ) -> "SupabaseModel":
        query = supabase.table(table_name).select("*")
        if isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq("id", value)
        response: APIResponse = await query.execute()
        data: Optional[Dict[str, Any]] = response.data[0] if response.data else None

        if isinstance(data, Dict):
            for key, value in data.items():
                # Check if the attribute type is an enum
                self._set_attribute(key, value)

            self.dirty = False
        return self

    def _set_attribute(self, key: str, value: Any):
        if key in self.model_fields:
            field_info: FieldInfo = self.model_fields[key]

            # Check if the attribute type is an enum
            if isinstance(field_info.annotation, enum.EnumMeta):
                try:
                    value = field_info.annotation(value)
                except ValueError:
                    # Log the inability to match the enum value
                    logger.warning(
                        f"Value '{value}' for '{key}' is not a valid {field_info.annotation}. Using default value if defined."
                    )

                    # Use the default value if it's defined, otherwise set to None
                    value = (
                        field_info.get_default()
                        if field_info.default is not None
                        else None
                    )

        setattr(self, key, value)
