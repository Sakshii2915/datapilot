from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.database.connection import primary_engine
from backend.app.models.ecommerce import Base
import backend.app.models.history  # Ensures history model is registered with Base
from backend.app.api.health import router as health_router
from backend.app.api.schema import router as schema_router
from backend.app.api.query import router as query_router

setup_logging()

# Ensure tables exist
try:
    Base.metadata.create_all(bind=primary_engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Database initialization warning: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Natural Language to SQL Analytics Agent API powered by GenAI and SQLGlot AST validation.",
)

# Configure CORS
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(schema_router, prefix=settings.API_V1_STR)
app.include_router(query_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }
