import json
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.schemas.query import QueryResult, ValidationResult
from backend.app.services.schema_service import SchemaService
from backend.app.services.sql_validator import SQLValidator
from backend.app.services.query_executor import QueryExecutor
from backend.app.services.llm_service import LLMService
from backend.app.services.result_explainer import ResultExplainer
from backend.app.models.history import QueryHistory
from backend.app.core.config import settings
from backend.app.core.logging import logger

class SQLGenerationPipeline:
    def __init__(
        self,
        schema_service: SchemaService,
        sql_validator: SQLValidator,
        query_executor: QueryExecutor,
        llm_service: LLMService,
        result_explainer: ResultExplainer
    ):
        self.schema_service = schema_service
        self.sql_validator = sql_validator
        self.query_executor = query_executor
        self.llm_service = llm_service
        self.result_explainer = result_explainer
        self.max_corrections = settings.MAX_SQL_CORRECTION_ATTEMPTS

    def process_query(self, question: str, db_session: Optional[Session] = None) -> QueryResult:
        """
        Executes the full end-to-end Natural Language to SQL analytics pipeline:
        1. Dynamic Schema Context extraction
        2. LLM-based SQL Generation
        3. SQLGlot AST Security Validation
        4. Bounded Error-Aware SQL Correction (if validation or execution fails)
        5. Safe Read-Only Execution
        6. AI Result Explanation
        7. Query History Persistence
        """
        query_id = str(uuid.uuid4())
        logger.info(f"Processing question [{query_id}]: '{question}'")

        # Step 1: Dynamic Schema Context
        schema_context = self.schema_service.get_prompt_schema_context()

        # Step 2: LLM SQL Generation
        llm_gen = self.llm_service.generate_sql(question, schema_context)
        is_mock = llm_gen.get("is_mock", False)

        # Handle ambiguity / clarification needed
        if llm_gen.get("clarification_needed"):
            clarification = llm_gen["clarification_needed"]
            logger.info(f"Clarification needed: {clarification}")
            result = QueryResult(
                query_id=query_id,
                question=question,
                generated_sql=None,
                execution_status="clarification_needed",
                clarification_needed=clarification,
                is_mock=is_mock
            )
            self._save_history(db_session, result)
            return result

        raw_sql = llm_gen.get("sql", "")
        sql_explanation = llm_gen.get("explanation", "")
        current_sql = raw_sql
        correction_attempts = 0
        validation_result: Optional[ValidationResult] = None
        exec_result: Optional[Dict[str, Any]] = None

        # Step 3 & 4: Validation and Error-Aware Correction Loop
        while correction_attempts <= self.max_corrections:
            validation_result = self.sql_validator.validate_and_sanitize(current_sql)

            if not validation_result.is_valid:
                logger.warning(
                    f"SQL Validation failed (Attempt {correction_attempts}/{self.max_corrections}): {validation_result.error}"
                )
                if correction_attempts >= self.max_corrections:
                    break

                correction_attempts += 1
                correction_resp = self.llm_service.correct_sql(
                    question=question,
                    schema_context=schema_context,
                    failed_sql=current_sql,
                    error_message=validation_result.error or "Validation failed",
                    attempt_number=correction_attempts
                )
                current_sql = correction_resp.get("sql", current_sql)
                continue

            # SQL passed validation! Now execute safely
            sanitized_sql = validation_result.sanitized_sql
            exec_result = self.query_executor.execute_query(sanitized_sql)

            if exec_result["status"] == "success":
                # Successfully executed!
                current_sql = sanitized_sql
                break

            # Database execution error occurred: Trigger error correction
            db_error = exec_result.get("error", "Database execution error")
            logger.warning(
                f"SQL Execution failed (Attempt {correction_attempts}/{self.max_corrections}): {db_error}"
            )

            if correction_attempts >= self.max_corrections:
                break

            correction_attempts += 1
            correction_resp = self.llm_service.correct_sql(
                question=question,
                schema_context=schema_context,
                failed_sql=current_sql,
                error_message=db_error,
                attempt_number=correction_attempts
            )
            current_sql = correction_resp.get("sql", current_sql)

        # Evaluate final outcome
        if validation_result and not validation_result.is_valid:
            # Query was rejected by security layer
            res = QueryResult(
                query_id=query_id,
                question=question,
                generated_sql=current_sql,
                execution_status="rejected",
                error_message=f"Security/Validation Rejection: {validation_result.error}",
                correction_attempts=correction_attempts,
                is_mock=is_mock
            )
            self._save_history(db_session, res)
            return res

        if exec_result and exec_result["status"] != "success":
            # Query failed execution after exhausting corrections
            res = QueryResult(
                query_id=query_id,
                question=question,
                generated_sql=current_sql,
                execution_status="error",
                execution_time_ms=exec_result.get("execution_time_ms", 0.0),
                error_message=f"Query Execution Error: {exec_result.get('error')}",
                correction_attempts=correction_attempts,
                is_mock=is_mock
            )
            self._save_history(db_session, res)
            return res

        # Step 5: Successful Execution -> Step 6: Natural Language Explanation
        columns = exec_result.get("columns", [])
        rows = exec_result.get("rows", [])
        row_count = exec_result.get("row_count", 0)
        execution_time_ms = exec_result.get("execution_time_ms", 0.0)

        nl_explanation = self.result_explainer.explain(
            question=question,
            sql=current_sql,
            columns=columns,
            rows=rows,
            row_count=row_count,
            execution_time_ms=execution_time_ms
        )

        res = QueryResult(
            query_id=query_id,
            question=question,
            generated_sql=current_sql,
            execution_status="success",
            execution_time_ms=execution_time_ms,
            columns=columns,
            rows=rows,
            row_count=row_count,
            explanation=nl_explanation,
            correction_attempts=correction_attempts,
            is_mock=is_mock
        )

        # Step 7: Persist history
        self._save_history(db_session, res)
        return res

    def _save_history(self, db_session: Optional[Session], result: QueryResult) -> None:
        """Persists query execution and outcome into the query_history table."""
        if not db_session:
            return

        try:
            preview_rows = result.rows[:5] if result.rows else []
            history_record = QueryHistory(
                id=result.query_id or str(uuid.uuid4()),
                question=result.question,
                generated_sql=result.generated_sql,
                execution_status=result.execution_status,
                execution_time_ms=result.execution_time_ms,
                row_count=result.row_count,
                natural_language_explanation=result.explanation,
                error_message=result.error_message,
                result_columns=json.dumps(result.columns) if result.columns else None,
                result_preview=json.dumps(preview_rows) if preview_rows else None
            )
            db_session.add(history_record)
            db_session.commit()
        except Exception as e:
            logger.error(f"Failed to persist query history: {e}")
            db_session.rollback()
