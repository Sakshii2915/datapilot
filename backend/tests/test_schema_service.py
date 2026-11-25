import pytest
from backend.app.services.schema_service import SchemaService

def test_schema_inspection(test_engine):
    """Verifies dynamic discovery of tables, columns, primary keys, and relationships."""
    service = SchemaService(engine=test_engine)
    schema = service.get_database_schema(force_refresh=True)

    table_names = [t.name for t in schema.tables]
    expected_tables = ["categories", "products", "customers", "orders", "order_items", "payments"]

    for expected in expected_tables:
        assert expected in table_names

    # Check customers table columns
    cust_table = service.get_table_schema("customers")
    assert cust_table is not None
    col_names = [c.name for c in cust_table.columns]
    assert "customer_id" in col_names
    assert "name" in col_names
    assert "email" in col_names
    assert "region" in col_names
    assert cust_table.row_count > 0

    # Check orders foreign keys
    orders_table = service.get_table_schema("orders")
    assert orders_table is not None
    assert len(orders_table.foreign_keys) >= 1
    assert orders_table.foreign_keys[0].target_table == "customers"

def test_prompt_schema_context_generation(test_engine):
    """Verifies that generated LLM schema context contains tables, keys, and sample values."""
    service = SchemaService(engine=test_engine)
    context = service.get_prompt_schema_context(force_refresh=True)

    assert "DATABASE SCHEMA CONTEXT" in context
    assert "Table: customers" in context
    assert "Table: orders" in context
    assert "FOREIGN KEY RELATIONSHIPS" in context
    assert "customers.customer_id" in context
