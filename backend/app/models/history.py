import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime
from backend.app.models.ecommerce import Base

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    execution_status = Column(String(20), default="pending", nullable=False)  # success, error, rejected
    execution_time_ms = Column(Float, default=0.0)
    row_count = Column(Integer, default=0)
    natural_language_explanation = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    result_columns = Column(Text, nullable=True)  # JSON-encoded list of column names
    result_preview = Column(Text, nullable=True)  # JSON-encoded list of sample result dicts
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
