import enum
import json
from typing import Any, Dict, List, Optional, TypeVar
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from supabase.client import AsyncClient
from postgrest import APIResponse

from lib.load_env import logger

T = TypeVar("T", bound="SupabaseModel")


class SupabaseModel(BaseModel):
    # Constant table name for each subclass
    TABLE_NAME: str = ""

    dirty: bool = Field(default=True)

    def __setattr__(self, name: str, value: Any):
        if name != "dirty":
            current_value = getattr(self, name, None)
            if current_value != value:
                self.dirty = True
        super().__setattr__(name, value)

    async def save_to_supabase(
        self: T, supabase: AsyncClient, on_conflict: List[str] = ["id"]
    ) -> T:
        if self.dirty:
            data = self._model_dump(exclude_none=True, exclude_unset=True)
            # Convert enum types to strings
            for key, value in data.items():
                if isinstance(value, enum.Enum):
                    data[key] = value.name

            # Ensure TABLE_NAME is set
            assert self.TABLE_NAME, "TABLE_NAME must be set for the model."

            if len(on_conflict) == 1:
                response = (
                    await supabase.table(self.TABLE_NAME)
                    .upsert(data, on_conflict=on_conflict)
                    .execute()
                )
            else:
                query = supabase.table(self.TABLE_NAME).select("*")
                for key in on_conflict:
                    query = query.eq(key, data[key])
                response: APIResponse = await query.execute()
                if response.data:
                    query = supabase.table(self.TABLE_NAME).update(data)
                    for key in on_conflict:
                        query = query.eq(key, data[key])
                    response = await query.execute()
                else:
                    response = (
                        await supabase.table(self.TABLE_NAME).insert(data).execute()
                    )

            # Update the model with the data from the response
            if response.data:
                for key, value in response.data[0].items():
                    self._set_attribute(key, value)
                self.dirty = False

        return self

    async def fetch_from_supabase(
        self: T, supabase: AsyncClient, value: Any = None, id_field_name: str = "id"
    ) -> T:
        # Ensure TABLE_NAME is set
        assert self.TABLE_NAME, "TABLE_NAME must be set for the model."

        query = supabase.table(self.TABLE_NAME).select("*")
        if value is None:
            # When value is None, use the id_field_name's current instance value
            value = getattr(self, id_field_name, None)
            if value is None:
                raise ValueError(
                    f"Value for '{id_field_name}' is not set in the instance."
                )
            query = query.eq(id_field_name, value)
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_field_name, value)

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

    async def exists_in_supabase(
        self, supabase: AsyncClient, value: Any = None, id_field_name: str = "id"
    ) -> bool:
        # Ensure TABLE_NAME is set
        assert self.TABLE_NAME, "TABLE_NAME must be set for the model."

        # Determine fields to select
        selected_fields = [id_field_name]
        if isinstance(value, dict):
            selected_fields.extend(value.keys())
        query = supabase.table(self.TABLE_NAME).select(*selected_fields)

        # Adjust query based on whether value is a dict or a single value
        if value is None:
            # When value is None, use the id_field_name's current instance value
            value = getattr(self, id_field_name, None)
            print(f"{value=}")
            if value is None:
                raise ValueError(
                    f"Value for '{id_field_name}' is not set in the instance."
                )
            query = query.eq(id_field_name, value)
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_field_name, value)

        response: APIResponse = await query.execute()
        return bool(response.data)

    async def delete_from_supabase(
        self: T, supabase: AsyncClient, value: Any = None, id_field_name: str = "id"
    ) -> bool:
        # Ensure TABLE_NAME is set
        assert self.TABLE_NAME, "TABLE_NAME must be set for the model."

        # Prepare the query to delete the item
        query = supabase.table(self.TABLE_NAME).delete()

        # Adjust query based on whether value is a dict or a single value
        if value is None:
            # When value is None, use the id_field_name's current instance value
            value = getattr(self, id_field_name, None)
            if value is None:
                raise ValueError(
                    f"Value for '{id_field_name}' is not set in the instance."
                )
            query = query.eq(id_field_name, value)
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_field_name, value)

        # Execute the delete operation
        await query.execute()

        # Return True if the item was successfully deleted
        return True

    def _model_dump(self, **kwargs) -> Dict[str, Any]:
        """Custom dump method to ensure TABLE_NAME is always excluded."""
        data = self.model_dump_json(
            exclude={
                "TABLE_NAME",
                "created_at",
                "disabled_at",
                "dirty",
                "updated_by",
                "updated_at",
            },
            **kwargs,
        )
        data = json.loads(data)
        return data
