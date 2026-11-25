from typing import List, Dict, Any
from backend.app.services.llm_service import LLMService

class ResultExplainer:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def explain(
        self,
        question: str,
        sql: str,
        columns: List[str],
        rows: List[Dict[str, Any]],
        row_count: int,
        execution_time_ms: float
    ) -> str:
        return self.llm_service.explain_results(
            question=question,
            sql=sql,
            columns=columns,
            rows=rows,
            row_count=row_count,
            execution_time_ms=execution_time_ms
        )
