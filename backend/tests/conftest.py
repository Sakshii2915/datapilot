import sys
import os
sys.path.insert(0, os.path.abspath("."))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.ecommerce import Base
import backend.app.models.history
from database.seed import seed_database
from backend.app.database.connection import get_db

TEST_DB_URL = "sqlite:///./test_datapilot.db"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    seed_database(database_url=TEST_DB_URL)
    yield engine
    # Cleanup after tests
    import os
    if os.path.exists("./test_datapilot.db"):
        try:
            os.remove("./test_datapilot.db")
        except Exception:
            pass

@pytest.fixture(scope="function")
def test_db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
