import pytest

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "llm_mode" in data

def test_schema_endpoints(client):
    res = client.get("/api/schema")
    assert res.status_code == 200
    data = res.json()
    assert "tables" in data
    assert len(data["tables"]) > 0

    res_tables = client.get("/api/schema/tables")
    assert res_tables.status_code == 200
    tables = res_tables.json()
    assert "customers" in tables
    assert "orders" in tables

    res_single = client.get("/api/schema/tables/customers")
    assert res_single.status_code == 200
    cust = res_single.json()
    assert cust["name"] == "customers"
    assert len(cust["columns"]) > 0

def test_query_validation_endpoint(client):
    # Valid SELECT
    res = client.post("/api/query/validate", json={"sql": "SELECT name FROM customers LIMIT 10"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert "customers" in data["tables_accessed"]

    # Malicious DROP TABLE
    res_bad = client.post("/api/query/validate", json={"sql": "DROP TABLE customers"})
    assert res_bad.status_code == 200
    data_bad = res_bad.json()
    assert data_bad["is_valid"] is False
    assert "security rejection" in data_bad["error"].lower()

def test_query_execution_and_history_lifecycle(client):
    # 1. Submit Question
    res = client.post("/api/query", json={"question": "What is the average order value?"})
    assert res.status_code == 200
    data = res.json()
    assert data["execution_status"] == "success"
    assert data["query_id"] is not None
    assert len(data["rows"]) > 0
    query_id = data["query_id"]

    # 2. Retrieve in History
    res_hist = client.get("/api/query/history")
    assert res_hist.status_code == 200
    history_items = res_hist.json()
    assert len(history_items) > 0
    found = any(item["id"] == query_id for item in history_items)
    assert found

    # 3. Retrieve single history item
    res_single = client.get(f"/api/query/history/{query_id}")
    assert res_single.status_code == 200
    single = res_single.json()
    assert single["id"] == query_id
    assert single["question"] == "What is the average order value?"

    # 4. Delete single history item
    res_del = client.delete(f"/api/query/history/{query_id}")
    assert res_del.status_code == 204

    # 5. Verify deleted
    res_after = client.get(f"/api/query/history/{query_id}")
    assert res_after.status_code == 404
