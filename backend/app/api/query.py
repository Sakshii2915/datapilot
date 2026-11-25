import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.schemas.query import (
    QueryRequest,
    QueryResult,
    QueryValidationRequest,
    ValidationResult,
    QueryHistoryResponse
)
from backend.app.services.schema_service import SchemaService
from backend.app.services.sql_validator import SQLValidator
from backend.app.services.query_executor import QueryExecutor
from backend.app.services.llm_service import LLMService
from backend.app.services.result_explainer import ResultExplainer
from backend.app.services.sql_generator import SQLGenerationPipeline
from backend.app.database.connection import get_db, primary_engine, readonly_engine
from backend.app.models.history import QueryHistory
from backend.app.core.config import settings

router = APIRouter(prefix="/query", tags=["Query Engine"])

# Pipeline Dependency Providers
def get_pipeline() -> SQLGenerationPipeline:
    schema_service = SchemaService(engine=primary_engine)
    sql_validator = SQLValidator(max_limit=settings.MAX_RESULT_ROWS)
    query_executor = QueryExecutor(
        readonly_engine=readonly_engine,
        timeout_seconds=settings.QUERY_TIMEOUT_SECONDS,
        max_rows=settings.MAX_RESULT_ROWS
    )
    llm_service = LLMService()
    result_explainer = ResultExplainer(llm_service=llm_service)

    return SQLGenerationPipeline(
        schema_service=schema_service,
        sql_validator=sql_validator,
        query_executor=query_executor,
        llm_service=llm_service,
        result_explainer=result_explainer
    )

def get_sql_validator() -> SQLValidator:
    return SQLValidator(max_limit=settings.MAX_RESULT_ROWS)

@router.post("", response_model=QueryResult)
def process_natural_language_query(
    request: QueryRequest,
    pipeline: SQLGenerationPipeline = Depends(get_pipeline),
    db: Session = Depends(get_db)
):
    """
    Submits a natural language analytics question.
    Coordinates schema intelligence, SQL generation, AST validation, execution,
    error correction, result explanation, and query history persistence.
    """
    return pipeline.process_query(question=request.question, db_session=db)

@router.post("/validate", response_model=ValidationResult)
def validate_custom_sql(
    request: QueryValidationRequest,
    validator: SQLValidator = Depends(get_sql_validator)
):
    """
    Validates any custom SQL query using the SQLGlot AST security engine.
    Ensures query is read-only SELECT, references authorized tables, and injects LIMIT.
    """
    return validator.validate_and_sanitize(request.sql)

@router.get("/history", response_model=List[QueryHistoryResponse])
def get_query_history(
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """Returns paginated query execution history with questions, generated SQL, status, and metrics."""
    query = db.query(QueryHistory)
    if status_filter:
        query = query.filter(QueryHistory.execution_status == status_filter)

    records = query.order_by(desc(QueryHistory.created_at)).offset(offset).limit(limit).all()

    response = []
    for r in records:
        cols = json.loads(r.result_columns) if r.result_columns else None
        preview = json.loads(r.result_preview) if r.result_preview else None
        response.append(QueryHistoryResponse(
            id=r.id,
            question=r.question,
            generated_sql=r.generated_sql,
            execution_status=r.execution_status,
            execution_time_ms=r.execution_time_ms or 0.0,
            row_count=r.row_count or 0,
            natural_language_explanation=r.natural_language_explanation,
            error_message=r.error_message,
            result_columns=cols,
            result_preview=preview,
            created_at=r.created_at
        ))
    return response

@router.get("/history/{query_id}", response_model=QueryHistoryResponse)
def get_history_detail(query_id: str, db: Session = Depends(get_db)):
    """Retrieves full details for a single query history item."""
    record = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Query history record not found.")

    cols = json.loads(record.result_columns) if record.result_columns else None
    preview = json.loads(record.result_preview) if record.result_preview else None

    return QueryHistoryResponse(
        id=record.id,
        question=record.question,
        generated_sql=record.generated_sql,
        execution_status=record.execution_status,
        execution_time_ms=record.execution_time_ms or 0.0,
        row_count=record.row_count or 0,
        natural_language_explanation=record.natural_language_explanation,
        error_message=record.error_message,
        result_columns=cols,
        result_preview=preview,
        created_at=record.created_at
    )

@router.delete("/history/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(query_id: str, db: Session = Depends(get_db)):
    """Deletes a specific query history item."""
    record = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Query history record not found.")
    db.delete(record)
    db.commit()
    return None

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_history(db: Session = Depends(get_db)):
    """Clears all query history records."""
    db.query(QueryHistory).delete()
    db.commit()
    return None
