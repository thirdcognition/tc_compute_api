import json
from datetime import datetime
from typing import ClassVar, Dict, Optional
from lib.models.supabase.supabase_model import SupabaseModel
from uuid import UUID
from pydantic import Field, field_validator


class ContextQuery(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "context_query"
    id: UUID
    params: Optional[Dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @field_validator("params", mode="before")
    def validate_params(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class ContextQueryResponse(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "context_query_response"
    id: UUID
    query_id: Optional[UUID] = Field(default=None)
    response_data: Optional[Dict] = Field(default=None)
    disabled: bool = Field(default=False)
    disabled_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @field_validator("response_data", mode="before")
    def validate_response_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v


class ContextQueryResult(SupabaseModel):
    TABLE_NAME: ClassVar[str] = "context_query_result"
    id: UUID
    query_id: Optional[UUID] = Field(default=None)
    result_data: Optional[Dict] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    owner_id: Optional[UUID] = Field(default=None)
    organization_id: Optional[UUID] = Field(default=None)

    @field_validator("result_data", mode="before")
    def validate_result_data(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return json.dumps(v)
        return v
