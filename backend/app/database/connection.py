import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.core.logging import logger

def create_db_engine(url: str, is_readonly: bool = False):
    """
    Creates an optimized SQLAlchemy engine.
    Supports PostgreSQL and SQLite.
    """
    is_sqlite = "sqlite" in url.lower()
    connect_args = {}

    if is_sqlite:
        connect_args["check_same_thread"] = False
        if is_readonly:
            # Enforce read-only at connection level if URI mode is supported
            if "?mode=ro" not in url and "file:" in url:
                url = f"{url}&mode=ro"
        return create_engine(url, connect_args=connect_args)

    # PostgreSQL configuration with connection pooling
    return create_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"connect_timeout": 5}
    )

# Primary Engine (Read-Write for History and Schema Management)
primary_engine = create_db_engine(settings.DATABASE_URL, is_readonly=False)

# Read-Only Engine (Dedicated for LLM Query Execution)
readonly_engine = create_db_engine(settings.effective_readonly_db_url, is_readonly=True)

# Session factory for primary database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=primary_engine)

def get_db():
    """FastAPI Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
