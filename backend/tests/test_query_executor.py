import pytest
from backend.app.services.query_executor import QueryExecutor

def test_query_executor_success(test_engine):
    """Verifies safe execution, timing, and structured JSON results."""
    executor = QueryExecutor(readonly_engine=test_engine)
    res = executor.execute_query("SELECT customer_id, name, city FROM customers LIMIT 5")

    assert res["status"] == "success"
    assert res["execution_time_ms"] > 0
    assert len(res["columns"]) == 3
    assert "name" in res["columns"]
    assert len(res["rows"]) == 5
    assert res["row_count"] == 5
    assert res["error"] is None

def test_query_executor_empty_results(test_engine):
    """Verifies execution with zero matching records."""
    executor = QueryExecutor(readonly_engine=test_engine)
    res = executor.execute_query("SELECT * FROM customers WHERE email = 'nonexistent@example.com'")

    assert res["status"] == "success"
    assert res["row_count"] == 0
    assert res["rows"] == []

def test_query_executor_error_handling(test_engine):
    """Verifies that invalid SQL expressions are caught safely without crash."""
    executor = QueryExecutor(readonly_engine=test_engine)
    res = executor.execute_query("SELECT nonexistent_column FROM customers")

    assert res["status"] == "error"
    assert res["error"] is not None
    assert "nonexistent_column" in res["error"]
