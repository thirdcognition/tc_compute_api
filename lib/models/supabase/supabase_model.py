import enum
import json
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from supabase.client import AsyncClient
from postgrest import APIResponse

from lib.load_env import logger

T = TypeVar("T", bound="SupabaseModel")


class SupabaseModel(BaseModel):
    # Constant table name for each subclass
    TABLE_NAME: ClassVar[str] = ""

    dirty: bool = Field(default=True)

    def __setattr__(self, name: str, value: Any):
        if name != "dirty":
            current_value = getattr(self, name, None)
            if current_value != value:
                self.dirty = True
        super().__setattr__(name, value)

    async def create(self, supabase: AsyncClient) -> "SupabaseModel":
        """Create a new record in the database."""
        return await self.save_to_supabase(supabase, self)

    async def read(
        self, supabase: AsyncClient, value: Any, id_column: str = "id"
    ) -> Optional["SupabaseModel"]:
        """Read a record from the database."""
        return await self.fetch_from_supabase(supabase, value, id_column, instance=self)

    async def update(self, supabase: AsyncClient) -> "SupabaseModel":
        """Update the record in the database if it has changed."""
        return await self.save_to_supabase(supabase, self)

    async def delete(
        self, supabase: AsyncClient, value: Any, id_column: str = "id"
    ) -> bool:
        """Delete a record from the database."""
        return await self.delete_from_supabase(supabase, value, id_column)

    @classmethod
    async def upsert_to_supabase(
        cls: Type[T],
        supabase: AsyncClient,
        instances: Iterable[T],
        on_conflict: List[str] = ["id"],
        id_column: Union[str, List[str]] = "id",
    ) -> List[T]:
        """Upsert multiple records in the database."""
        # Ensure TABLE_NAME is set
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        upsert_data = []
        # Collect data from each instance, ensuring to convert enums to strings
        for instance in instances:
            if instance.dirty:
                data = instance._model_dump(exclude_none=True, exclude_unset=True)
                for key, value in data.items():
                    if isinstance(value, enum.Enum):
                        data[key] = value.name
                upsert_data.append(data)

        # Perform a batch upsert if there is any data to upsert
        if upsert_data:
            response = (
                await supabase.table(cls.TABLE_NAME)
                .upsert(upsert_data, on_conflict=on_conflict)
                .execute()
            )

            # Map response data to instances by their IDs
            id_to_updated_data = {}
            if isinstance(id_column, list):
                # For composite keys, use tuples as dictionary keys
                for item in response.data:
                    id_keys = tuple(item[field] for field in id_column)
                    id_to_updated_data[id_keys] = item
            else:
                # For single key case
                id_to_updated_data = {item[id_column]: item for item in response.data}

                # Update local instances using response data
                for instance in instances:
                    if isinstance(id_column, list):
                        # Build the tuple key for the current instance
                        instance_id = tuple(
                            instance.model_fields.get(field) for field in id_column
                        )
                    else:
                        # Single key case
                        instance_id = instance.model_fields.get(id_column)

                    if (
                        instance.dirty
                        and instance_id
                        and instance_id in id_to_updated_data
                    ):
                        updated_data = id_to_updated_data[instance_id]
                        for key, value in updated_data.items():
                            instance._set_attribute(key, value)

                # Mark all instances as not dirty
                for instance in instances:
                    instance.dirty = False

        return instances

    @classmethod
    async def save_to_supabase(
        cls: Type[T],
        supabase: AsyncClient,
        instance: T,
        on_conflict: List[str] = ["id"],
    ) -> T:
        if instance.dirty:
            data = instance._model_dump(exclude_none=True, exclude_unset=True)
            # Convert enum types to strings
            for key, value in data.items():
                if isinstance(value, enum.Enum):
                    data[key] = value.name

            # Ensure TABLE_NAME is set
            assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

            if len(on_conflict) == 1:
                response = (
                    await supabase.table(cls.TABLE_NAME)
                    .upsert(data, on_conflict=on_conflict)
                    .execute()
                )
            else:
                query = supabase.table(cls.TABLE_NAME).select("*")
                for key in on_conflict:
                    query = query.eq(key, data[key])
                response: APIResponse = await query.execute()
                if response.data:
                    query = supabase.table(cls.TABLE_NAME).update(data)
                    for key in on_conflict:
                        query = query.eq(key, data[key])
                    response = await query.execute()
                else:
                    response = (
                        await supabase.table(cls.TABLE_NAME).insert(data).execute()
                    )

            # Update the instance with the data from the response
            if response.data:
                for key, value in response.data[0].items():
                    instance._set_attribute(key, value)
                instance.dirty = False

        return instance

    @classmethod
    async def fetch_from_supabase(
        cls: Type[T],
        supabase: AsyncClient,
        value: Any = None,
        id_column: str = "id",
        instance: Optional[T] = None,  # Optional instance parameter
    ) -> T:
        # Ensure TABLE_NAME is set
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        query = supabase.table(cls.TABLE_NAME).select("*")
        if value is None:
            raise ValueError(f"Value for '{id_column}' must be provided.")

        if isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column, value)

        response: APIResponse = await query.execute()
        data: Optional[Dict[str, Any]] = response.data[0] if response.data else None

        if data is not None:
            if not instance:
                # Directly pass the data to the class constructor
                instance = cls(**data)
            else:
                for key, val in data.items():
                    instance._set_attribute(key, val)

            instance.dirty = False
            return instance

        return None

    @classmethod
    async def fetch_existing_from_supabase(
        cls,
        supabase: AsyncClient,
        filter: Any = None,
        values: List[Any] = None,
        id_column: str = "id",
    ):
        # Ensure TABLE_NAME is set
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        query = supabase.table(cls.TABLE_NAME).select("*")

        if filter is not None:
            if isinstance(filter, dict):
                for key, item in filter.items():
                    query = query.eq(key, item)
            else:
                query.eq(id_column, filter)

        if values is not None:
            for value in values:
                if isinstance(value, dict):
                    for key, item in value.items():
                        query.in_(key, item)
                else:
                    query.in_(id_column, value)

        response: APIResponse = await query.execute()
        if not response.data:
            return []

        return [cls(**data) for data in response.data]

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

    @classmethod
    async def exists_in_supabase(
        cls, supabase: AsyncClient, value: Any = None, id_column: str = "id"
    ) -> bool:
        # Ensure TABLE_NAME is set
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        # Determine fields to select
        selected_fields = [id_column]
        if isinstance(value, dict):
            selected_fields.extend(value.keys())
        query = supabase.table(cls.TABLE_NAME).select(*selected_fields)

        # Adjust query based on whether value is a dict or a single value
        if value is None:
            # When value is None, use the id_column's current instance value
            raise ValueError("Value must be provided when using class method.")
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column, value)

        response: APIResponse = await query.execute()
        return bool(response.data)

    @classmethod
    async def delete_from_supabase(
        cls, supabase: AsyncClient, value: Any = None, id_column: str = "id"
    ) -> bool:
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        query = supabase.table(cls.TABLE_NAME).delete()

        if value is None:
            raise ValueError(
                f"Value must be provided to delete an item based on '{id_column}'."
            )
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column, value)

        await query.execute()

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
