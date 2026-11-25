from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    default: Optional[str] = None

class TableRelationship(BaseModel):
    source_table: str
    source_column: str
    target_table: str
    target_column: str

class TableSchema(BaseModel):
    name: str
    columns: List[ColumnInfo]
    primary_keys: List[str] = []
    foreign_keys: List[TableRelationship] = []
    row_count: int = 0
    sample_values: Dict[str, List[Any]] = Field(default_factory=dict)

class DatabaseSchemaResponse(BaseModel):
    tables: List[TableSchema]
    relationships: List[TableRelationship]
    schema_summary: str
