import pytest
from backend.app.services.schema_service import SchemaService
from backend.app.services.sql_validator import SQLValidator
from backend.app.services.query_executor import QueryExecutor
from backend.app.services.llm_service import LLMService
from backend.app.services.result_explainer import ResultExplainer
from backend.app.services.sql_generator import SQLGenerationPipeline

@pytest.fixture
def pipeline(test_engine):
    schema_service = SchemaService(engine=test_engine)
    sql_validator = SQLValidator(max_limit=100)
    query_executor = QueryExecutor(readonly_engine=test_engine)
    llm_service = LLMService()
    result_explainer = ResultExplainer(llm_service=llm_service)

    return SQLGenerationPipeline(
        schema_service=schema_service,
        sql_validator=sql_validator,
        query_executor=query_executor,
        llm_service=llm_service,
        result_explainer=result_explainer
    )

def test_pipeline_top_products_question(pipeline, test_db_session):
    """Tests end-to-end question processing for top products by revenue."""
    res = pipeline.process_query("What are the top 5 products by revenue?", db_session=test_db_session)

    assert res.execution_status == "success"
    assert res.generated_sql is not None
    assert "products" in res.generated_sql.lower()
    assert res.row_count > 0
    assert len(res.rows) <= 5
    assert res.explanation is not None
    assert res.query_id is not None

def test_pipeline_region_sales_question(pipeline, test_db_session):
    """Tests region sales aggregation."""
    res = pipeline.process_query("Which region generated the highest sales?", db_session=test_db_session)

    assert res.execution_status == "success"
    assert "region" in res.generated_sql.lower()
    assert res.row_count > 0
    assert "region" in res.columns

def test_pipeline_out_of_domain_clarification(pipeline, test_db_session):
    """Tests handling of ambiguous/out-of-domain questions."""
    res = pipeline.process_query("What is the capital of France and who wrote Hamlet?", db_session=test_db_session)

    assert res.execution_status == "clarification_needed"
    assert res.clarification_needed is not None
    assert res.generated_sql is None

def test_pipeline_correction_limit_bound(pipeline, monkeypatch, test_db_session):
    """Tests that SQL correction stops after MAX_SQL_CORRECTION_ATTEMPTS."""
    # Force LLM service to keep returning an invalid SQL
    monkeypatch.setattr(
        pipeline.llm_service,
        "generate_sql",
        lambda *args, **kwargs: {"sql": "SELECT invalid_col FROM nonexistent_tbl", "explanation": "test", "is_mock": True}
    )
    monkeypatch.setattr(
        pipeline.llm_service,
        "correct_sql",
        lambda *args, **kwargs: {"sql": "SELECT still_invalid FROM nonexistent_tbl", "explanation": "test", "is_mock": True}
    )

    res = pipeline.process_query("Sample question", db_session=test_db_session)
    assert res.execution_status == "rejected"
    assert res.correction_attempts == pipeline.max_corrections
