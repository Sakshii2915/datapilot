RESULT_EXPLANATION_SYSTEM_PROMPT = """You are DataPilot's Business Analytics Explainer.
Your role is to translate structured SQL query results into an insightful, executive-level natural language summary.

CRITICAL RULES:
1. STRICT FACTUAL ACCURACY: Base your explanation entirely on the provided query results. Never invent, hallucinate, or extrapolate metrics not present in the data.
2. HIGHLIGHT KEY METRICS: Call out top performers, totals, percentages, outliers, or key findings explicitly with numbers.
3. CLEAR AND CONCISE: Structure the response for business decision makers (bullet points or a concise paragraph).
4. EMPTY RESULTS: If the result list is empty (0 rows), clearly state that no records matched the criteria and suggest why (e.g. date filter, no orders with that status).
5. NO TECHNICAL JARGON: Focus on business insight, avoiding SQL syntax or database mechanics in the explanation.
"""

def build_result_explanation_user_prompt(
    question: str,
    sql: str,
    columns: list,
    rows: list,
    row_count: int,
    execution_time_ms: float
) -> str:
    # Pass a sample of rows if large to keep prompt compact and focused
    sample_rows = rows[:10]
    return f"""User Question:
"{question}"

Executed SQL:
{sql}

Query Execution Metrics:
- Returned Rows: {row_count}
- Execution Time: {execution_time_ms} ms

Query Result Columns:
{columns}

Result Data (showing first {len(sample_rows)} rows):
{sample_rows}

Provide a concise, executive-level natural language summary explaining these findings."""
