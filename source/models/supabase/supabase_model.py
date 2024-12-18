import enum
import json
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from supabase.client import AsyncClient, Client
from postgrest import APIResponse

from source.models.config.logging import logger

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

    async def create(self, supabase: AsyncClient) -> T:
        """Create a new record in the database."""
        return await self.save_to_supabase(supabase, self)

    def create_sync(self, supabase: Client) -> T:
        """Create a new record in the database (synchronous)."""
        return self.save_to_supabase_sync(supabase, self)

    async def read(self, supabase: AsyncClient, id_column=None) -> T:
        """
        Read a record from the database based on the instance's id or a specified field,
        and then update the current instance with the values.
        """
        if id_column is not None:
            return await self.fetch_from_supabase(
                supabase, id_column=id_column, instance=self
            )

        return await self.fetch_from_supabase(supabase, instance=self)

    def read_sync(self, supabase: Client, id_column=None) -> T:
        """
        Read a record from the database based on the instance's id or a specified field,
        and then update the current instance with the values (synchronous).
        """
        if id_column is not None:
            return self.fetch_from_supabase_sync(
                supabase, id_column=id_column, instance=self
            )

        return self.fetch_from_supabase_sync(supabase, instance=self)

    async def update(self, supabase: AsyncClient) -> T:
        """Update the record in the database if it has changed."""
        return await self.save_to_supabase(supabase, self)

    def update_sync(self, supabase: Client) -> T:
        """Update the record in the database if it has changed (synchronous)."""
        return self.save_to_supabase_sync(supabase, self)

    async def delete(self, supabase: AsyncClient, id_column: str = "id") -> bool:
        """Delete the record from the database."""
        value = getattr(self, id_column, None)
        if value is None:
            raise ValueError(f"'{id_column}' is not set for this instance.")
        return await self.delete_from_supabase(supabase, value, id_column)

    def delete_sync(self, supabase: Client, id_column: str = "id") -> bool:
        """Delete the record from the database (synchronous)."""
        value = getattr(self, id_column, None)
        if value is None:
            raise ValueError(f"'{id_column}' is not set for this instance.")
        return self.delete_from_supabase_sync(supabase, value, id_column)

    async def exists(self, supabase: AsyncClient, id_column: str = None) -> bool:
        """Check if a record with the instance's id exists in the database."""
        value = getattr(self, id_column, None)
        if value is None:
            raise ValueError(f"'{id_column}' is not set for this instance.")
        return await self.exists_in_supabase(supabase, value, id_column)

    def exists_sync(self, supabase: Client, id_column: str = None) -> bool:
        """Check if a record with the instance's id exists in the database (synchronous)."""
        value = getattr(self, id_column, None)
        if value is None:
            raise ValueError(f"'{id_column}' is not set for this instance.")
        return self.exists_in_supabase_sync(supabase, value, id_column)

    @classmethod
    async def upsert_to_supabase(
        cls: Type[T],
        supabase: AsyncClient,
        instances: Iterable[T],
        on_conflict: List[str] = ["id"],
        id_column: Union[str, List[str]] = "id",
    ) -> List[T]:
        """Upsert multiple records in the database."""
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        upsert_data = []
        for instance in instances:
            if instance.dirty:
                data = instance._model_dump(exclude_none=True, exclude_unset=True)
                for key, value in data.items():
                    if isinstance(value, enum.Enum):
                        data[key] = value.name
                upsert_data.append(data)

        if upsert_data:
            response = (
                await supabase.table(cls.TABLE_NAME)
                .upsert(upsert_data, on_conflict=on_conflict)
                .execute()
            )

            id_to_updated_data = {}
            if isinstance(id_column, list):
                for item in response.data:
                    id_keys = tuple(item[field] for field in id_column)
                    id_to_updated_data[id_keys] = item
            else:
                id_to_updated_data = {item[id_column]: item for item in response.data}

                for instance in instances:
                    if isinstance(id_column, list):
                        instance_id = tuple(
                            instance.model_fields.get(field) for field in id_column
                        )
                    else:
                        instance_id = instance.model_fields.get(id_column)

                    if (
                        instance.dirty
                        and instance_id
                        and instance_id in id_to_updated_data
                    ):
                        updated_data = id_to_updated_data[instance_id]
                        for key, value in updated_data.items():
                            instance._set_attribute(key, value)

                for instance in instances:
                    instance.dirty = False

        return instances

    @classmethod
    def upsert_to_supabase_sync(
        cls: Type[T],
        supabase: Client,
        instances: Iterable[T],
        on_conflict: List[str] = ["id"],
        id_column: Union[str, List[str]] = "id",
    ) -> List[T]:
        """Upsert multiple records in the database (synchronous)."""
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        upsert_data = []
        for instance in instances:
            if instance.dirty:
                data = instance._model_dump(exclude_none=True, exclude_unset=True)
                for key, value in data.items():
                    if isinstance(value, enum.Enum):
                        data[key] = value.name
                upsert_data.append(data)

        if upsert_data:
            response = (
                supabase.table(cls.TABLE_NAME)
                .upsert(upsert_data, on_conflict=on_conflict)
                .execute()
            )

            id_to_updated_data = {}
            if isinstance(id_column, list):
                for item in response.data:
                    id_keys = tuple(item[field] for field in id_column)
                    id_to_updated_data[id_keys] = item
            else:
                id_to_updated_data = {item[id_column]: item for item in response.data}

                for instance in instances:
                    if isinstance(id_column, list):
                        instance_id = tuple(
                            instance.model_fields.get(field) for field in id_column
                        )
                    else:
                        instance_id = instance.model_fields.get(id_column)

                    if (
                        instance.dirty
                        and instance_id
                        and instance_id in id_to_updated_data
                    ):
                        updated_data = id_to_updated_data[instance_id]
                        for key, value in updated_data.items():
                            instance._set_attribute(key, value)

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
            for key, value in data.items():
                if isinstance(value, enum.Enum):
                    data[key] = value.name

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

            if response.data:
                for key, value in response.data[0].items():
                    instance._set_attribute(key, value)
                instance.dirty = False

        return instance

    @classmethod
    def save_to_supabase_sync(
        cls: Type[T],
        supabase: Client,
        instance: T,
        on_conflict: List[str] = ["id"],
    ) -> T:
        if instance.dirty:
            data = instance._model_dump(exclude_none=True, exclude_unset=True)
            for key, value in data.items():
                if isinstance(value, enum.Enum):
                    data[key] = value.name

            assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

            if len(on_conflict) == 1:
                response = (
                    supabase.table(cls.TABLE_NAME)
                    .upsert(data, on_conflict=on_conflict)
                    .execute()
                )
            else:
                query = supabase.table(cls.TABLE_NAME).select("*")
                for key in on_conflict:
                    query = query.eq(key, data[key])
                response: APIResponse = query.execute()
                if response.data:
                    query = supabase.table(cls.TABLE_NAME).update(data)
                    for key in on_conflict:
                        query = query.eq(key, data[key])
                    response = query.execute()
                else:
                    response = supabase.table(cls.TABLE_NAME).insert(data).execute()

            if response.data:
                for key, value in response.data[0].items():
                    instance._set_attribute(key, value)
                instance.dirty = False

        return instance

    @classmethod
    async def fetch_from_supabase(
        cls: Type[T],
        supabase: AsyncClient,
        value: Optional[Any] = None,
        id_column: str = "id",
        instance: Optional[T] = None,
    ) -> T:
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        query = supabase.table(cls.TABLE_NAME).select("*")
        if instance and value is None:
            value = getattr(instance, id_column, None)
            if value is None:
                raise ValueError(f"'{id_column}' is not set for the provided instance.")

        if isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column, value)

        response: APIResponse = await query.execute()
        data: Optional[Dict[str, Any]] = response.data[0] if response.data else None

        if data is not None:
            if not instance:
                instance = cls(**data)
            else:
                for key, val in data.items():
                    instance._set_attribute(key, val)

            instance.dirty = False
            return instance

        return None

    @classmethod
    def fetch_from_supabase_sync(
        cls: Type[T],
        supabase: Client,
        value: Optional[Any] = None,
        id_column: str = "id",
        instance: Optional[T] = None,
    ) -> T:
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        query = supabase.table(cls.TABLE_NAME).select("*")
        if instance and value is None:
            value = getattr(instance, id_column, None)
            if value is None:
                raise ValueError(f"'{id_column}' is not set for the provided instance.")

        if isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column, value)

        response: APIResponse = query.execute()
        data: Optional[Dict[str, Any]] = response.data[0] if response.data else None

        if data is not None:
            if not instance:
                instance = cls(**data)
            else:
                for key, val in data.items():
                    instance._set_attribute(key, val)

            instance.dirty = False
            return instance

        return None

    @classmethod
    async def fetch_existing_from_supabase(
        cls: Type[T],
        supabase: AsyncClient,
        filter: Any = None,
        values: List[Any] = None,
        id_column: str = "id",
    ) -> List[T]:
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

    @classmethod
    def fetch_existing_from_supabase_sync(
        cls: Type[T],
        supabase: Client,
        filter: Any = None,
        values: List[Any] = None,
        id_column: str = "id",
    ) -> List[T]:
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

        response: APIResponse = query.execute()
        if not response.data:
            return []

        return [cls(**data) for data in response.data]

    def _set_attribute(self, key: str, value: Any):
        if key in self.model_fields:
            field_info: FieldInfo = self.model_fields[key]

            if isinstance(field_info.annotation, enum.EnumMeta):
                try:
                    value = field_info.annotation(value)
                except ValueError:
                    logger.warning(
                        f"Value '{value}' for '{key}' is not a valid {field_info.annotation}. Using default value if defined."
                    )

                    value = (
                        field_info.get_default()
                        if field_info.default is not None
                        else None
                    )

        setattr(self, key, value)

    @classmethod
    async def exists_in_supabase(
        cls: Type[T], supabase: AsyncClient, value: Any = None, id_column: str = "id"
    ) -> bool:
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        selected_fields = []
        if id_column is not None:
            selected_fields = [id_column]

        if isinstance(value, type(T)):
            value = getattr(value, id_column)
        elif isinstance(value, dict):
            selected_fields.extend(value.keys())

        if len(selected_fields) > 0:
            query = supabase.table(cls.TABLE_NAME).select(*selected_fields)
        else:
            query = supabase.table(cls.TABLE_NAME).select('"')

        if value is None:
            raise ValueError("Value must be provided when using class method.")
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column or "id", value)

        response: APIResponse = await query.execute()
        return len(response.data) > 0

    @classmethod
    def exists_in_supabase_sync(
        cls: Type[T], supabase: Client, value: Any = None, id_column: str = "id"
    ) -> bool:
        assert cls.TABLE_NAME, "TABLE_NAME must be set for the model."

        selected_fields = []
        if id_column is not None:
            selected_fields = [id_column]

        if isinstance(value, type(T)):
            value = getattr(value, id_column)
        elif isinstance(value, dict):
            selected_fields.extend(value.keys())

        if len(selected_fields) > 0:
            query = supabase.table(cls.TABLE_NAME).select(*selected_fields)
        else:
            query = supabase.table(cls.TABLE_NAME).select('"')

        if value is None:
            raise ValueError("Value must be provided when using class method.")
        elif isinstance(value, dict):
            for key, val in value.items():
                query = query.eq(key, val)
        else:
            query = query.eq(id_column or "id", value)

        response: APIResponse = query.execute()
        return len(response.data) > 0

    @classmethod
    async def delete_from_supabase(
        cls: Type[T], supabase: AsyncClient, value: Any = None, id_column: str = "id"
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

        response = await query.execute()

        if hasattr(response, "data") and len(response.data) > 0:
            print(response.data)
            return True

        return False

    @classmethod
    def delete_from_supabase_sync(
        cls: Type[T], supabase: Client, value: Any = None, id_column: str = "id"
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

        response = query.execute()

        if hasattr(response, "data") and len(response.data) > 0:
            print(response.data)
            return True

        return False

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
