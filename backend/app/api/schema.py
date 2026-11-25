from typing import List
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.schema import DatabaseSchemaResponse, TableSchema
from backend.app.services.schema_service import SchemaService
from backend.app.database.connection import primary_engine

router = APIRouter(prefix="/schema", tags=["Schema Intelligence"])

def get_schema_service() -> SchemaService:
    return SchemaService(engine=primary_engine)

@router.get("", response_model=DatabaseSchemaResponse)
def get_full_schema(schema_service: SchemaService = Depends(get_schema_service)):
    """Returns the full dynamic database schema including tables, columns, relations, and sample values."""
    return schema_service.get_database_schema()

@router.get("/tables", response_model=List[str])
def list_tables(schema_service: SchemaService = Depends(get_schema_service)):
    """Returns the list of all discoverable business tables in the database."""
    schema = schema_service.get_database_schema()
    return [t.name for t in schema.tables]

@router.get("/tables/{table_name}", response_model=TableSchema)
def get_table_details(table_name: str, schema_service: SchemaService = Depends(get_schema_service)):
    """Returns detailed schema, columns, constraints, and sample values for a single table."""
    table = schema_service.get_table_schema(table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in database.")
    return table

@router.post("/refresh")
def refresh_schema_cache(schema_service: SchemaService = Depends(get_schema_service)):
    """Forces cache invalidation and re-inspects the live database schema."""
    schema_service.refresh_cache()
    schema = schema_service.get_database_schema(force_refresh=True)
    return {"message": "Schema cache refreshed successfully", "table_count": len(schema.tables)}
