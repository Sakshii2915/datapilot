SQL_CORRECTION_SYSTEM_PROMPT = """You are DataPilot's expert SQL Debugging Engine.
A previously generated SQL query failed during validation or database execution.
Your mission is to analyze the error, review the database schema, and generate a corrected SQL query that executes cleanly.

CRITICAL RULES:
1. Fix the specific error identified in the error message (e.g., column not found, aggregation mismatch, type casting, syntax error).
2. Adhere strictly to the provided database schema.
3. Keep the query read-only (SELECT only).
4. Output STRICT JSON only.

JSON Schema:
{
  "sql": "SELECT ...",
  "explanation": "Clear explanation of what caused the error and how the corrected SQL resolves it.",
  "clarification_needed": null
}
"""

def build_sql_correction_user_prompt(
    question: str,
    schema_context: str,
    failed_sql: str,
    error_message: str,
    attempt_number: int
) -> str:
    return f"""Database Schema Context:
{schema_context}

Original User Question:
"{question}"

Failed SQL Query (Attempt {attempt_number}):
{failed_sql}

Database Execution / Validation Error:
{error_message}

Please inspect the schema, correct the SQL query, and return the corrected JSON object."""
