from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db, primary_engine
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint verifying system, database, and LLM configuration."""
    db_connected = False
    db_type = "unknown"
    try:
        url_str = str(primary_engine.url).lower()
        if "sqlite" in url_str:
            db_type = "SQLite"
            db.execute(text("SELECT 1")).scalar()
        else:
            db_type = "PostgreSQL"
            db.execute(text("SELECT 1")).scalar()
        db_connected = True
    except Exception as e:
        db_connected = False
        db_type = f"Error: {str(e)[:50]}"

    return {
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "database_type": db_type,
        "openai_configured": bool(settings.OPENAI_API_KEY and not settings.is_mock_llm),
        "llm_mode": "Mock Engine" if settings.is_mock_llm else f"Live OpenAI ({settings.OPENAI_MODEL})",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
