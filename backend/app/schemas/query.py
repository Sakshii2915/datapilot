from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="Natural language question to analyze")

class QueryValidationRequest(BaseModel):
    sql: str = Field(..., min_length=5, description="SQL query to validate with SQLGlot AST engine")

class ValidationResult(BaseModel):
    is_valid: bool
    error: Optional[str] = None
    sanitized_sql: Optional[str] = None
    tables_accessed: List[str] = []

class QueryResult(BaseModel):
    query_id: Optional[str] = None
    question: str
    generated_sql: Optional[str] = None
    execution_status: str  # "success", "error", "rejected"
    execution_time_ms: float = 0.0
    columns: List[str] = []
    rows: List[Dict[str, Any]] = []
    row_count: int = 0
    explanation: Optional[str] = None
    clarification_needed: Optional[str] = None
    error_message: Optional[str] = None
    correction_attempts: int = 0
    is_mock: bool = False

class QueryHistoryResponse(BaseModel):
    id: str
    question: str
    generated_sql: Optional[str] = None
    execution_status: str
    execution_time_ms: float = 0.0
    row_count: int = 0
    natural_language_explanation: Optional[str] = None
    error_message: Optional[str] = None
    result_columns: Optional[List[str]] = None
    result_preview: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
