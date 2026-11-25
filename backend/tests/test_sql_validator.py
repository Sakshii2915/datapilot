import pytest
from backend.app.services.sql_validator import SQLValidator

@pytest.fixture
def validator():
    return SQLValidator(max_limit=100)

def test_valid_select_queries(validator):
    """Verifies that legitimate analytics SELECT queries pass validation."""
    valid_queries = [
        "SELECT * FROM customers",
        "SELECT p.product_name, SUM(oi.quantity) FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_name",
        "SELECT c.region, AVG(o.total_amount) FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.region",
        "SELECT customer_id, name FROM customers WHERE region = 'West' ORDER BY created_at DESC",
    ]
    for q in valid_queries:
        res = validator.validate_and_sanitize(q)
        assert res.is_valid, f"Query failed validation: {q}, error: {res.error}"
        assert res.sanitized_sql is not None
        assert "LIMIT" in res.sanitized_sql.upper()

def test_multiple_statements_rejection(validator):
    """Ensures multiple SQL statements (stacked queries) are blocked."""
    stacked = "SELECT * FROM customers; DROP TABLE orders;"
    res = validator.validate_and_sanitize(stacked)
    assert not res.is_valid
    assert "multiple" in res.error.lower()

def test_insert_rejection(validator):
    res = validator.validate_and_sanitize("INSERT INTO customers (name, email) VALUES ('Eve', 'eve@evil.com')")
    assert not res.is_valid
    assert "security rejection" in res.error.lower()

def test_update_rejection(validator):
    res = validator.validate_and_sanitize("UPDATE customers SET name = 'Hacked' WHERE customer_id = 1")
    assert not res.is_valid
    assert "security rejection" in res.error.lower()

def test_delete_rejection(validator):
    res = validator.validate_and_sanitize("DELETE FROM orders WHERE order_id = 1")
    assert not res.is_valid
    assert "security rejection" in res.error.lower()

def test_drop_rejection(validator):
    res = validator.validate_and_sanitize("DROP TABLE payments")
    assert not res.is_valid
    assert "security rejection" in res.error.lower()

def test_alter_rejection(validator):
    res = validator.validate_and_sanitize("ALTER TABLE products ADD COLUMN secret_key VARCHAR(50)")
    assert not res.is_valid
    assert "security rejection" in res.error.lower()

def test_truncate_rejection(validator):
    res = validator.validate_and_sanitize("TRUNCATE TABLE order_items")
    assert not res.is_valid
    assert "security rejection" in res.error.lower()

def test_system_catalog_rejection(validator):
    """Ensures queries cannot access PostgreSQL or SQLite system catalogs."""
    assert not validator.validate_and_sanitize("SELECT * FROM pg_catalog.pg_tables").is_valid
    assert not validator.validate_and_sanitize("SELECT * FROM information_schema.tables").is_valid
    assert not validator.validate_and_sanitize("SELECT * FROM sqlite_master").is_valid

def test_unauthorized_table_rejection(validator):
    """Ensures queries cannot access unauthorized internal tables."""
    assert not validator.validate_and_sanitize("SELECT * FROM passwords").is_valid
    assert not validator.validate_and_sanitize("SELECT * FROM query_history").is_valid

def test_limit_enforcement(validator):
    """Ensures LIMIT is injected when missing or clamped when too large."""
    # Missing limit -> injected
    res1 = validator.validate_and_sanitize("SELECT * FROM customers")
    assert "LIMIT 100" in res1.sanitized_sql.upper()

    # User limit exceeding max -> clamped to 100
    res2 = validator.validate_and_sanitize("SELECT * FROM customers LIMIT 5000")
    assert "LIMIT 100" in res2.sanitized_sql.upper()

    # User limit within bounds -> preserved
    res3 = validator.validate_and_sanitize("SELECT * FROM customers LIMIT 10")
    assert "LIMIT 10" in res3.sanitized_sql.upper()

def test_malformed_sql_handling(validator):
    """Ensures malformed queries are handled safely without crashing."""
    res = validator.validate_and_sanitize("SELECT FROM WHERE ;;;")
    assert not res.is_valid
    assert "syntax error" in res.error.lower() or "security rejection" in res.error.lower()
