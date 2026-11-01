from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    name: str
    type: str
    nullable: bool


class ForeignKeyMetadata(BaseModel):
    column: str
    ref_table: str
    ref_column: str


class TableMetadata(BaseModel):
    name: str
    type: str  # FACT, DIMENSION, STAGING, AUDIT, VIEW
    row_count: int
    primary_key: List[str]
    foreign_keys: List[ForeignKeyMetadata]
    columns: List[ColumnMetadata]


class WarehouseSchemaResponse(BaseModel):
    dialect: str
    active_dataset_version: Optional[int]
    tables: List[TableMetadata]


class SQLQueryRequest(BaseModel):
    sql: str
    limit: int = Field(default=100, ge=1, le=500)


class SQLQueryResponse(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float
    is_truncated: bool

