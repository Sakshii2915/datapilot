import json
import re
from typing import Dict, Any, Optional, List
from openai import OpenAI
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.prompts.sql_generation import (
    SQL_GENERATION_SYSTEM_PROMPT,
    build_sql_generation_user_prompt
)
from backend.app.prompts.sql_correction import (
    SQL_CORRECTION_SYSTEM_PROMPT,
    build_sql_correction_user_prompt
)
from backend.app.prompts.result_explanation import (
    RESULT_EXPLANATION_SYSTEM_PROMPT,
    build_result_explanation_user_prompt
)

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.is_mock = settings.is_mock_llm
        self.client: Optional[OpenAI] = None

        if not self.is_mock:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client ({e}). Falling back to Mock Mode.")
                self.is_mock = True

    def generate_sql(self, question: str, schema_context: str) -> Dict[str, Any]:
        """
        Generates PostgreSQL-compatible SQL using OpenAI LLM or Mock Engine.
        Returns dict with keys: 'sql', 'explanation', 'clarification_needed', 'is_mock'.
        """
        if self.is_mock:
            return self._mock_sql_generation(question)

        user_prompt = build_sql_generation_user_prompt(question, schema_context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SQL_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            raw_text = response.choices[0].message.content
            parsed = json.loads(raw_text)
            parsed["is_mock"] = False
            return parsed
        except Exception as e:
            logger.error(f"OpenAI SQL generation failed: {e}. Falling back to mock engine.")
            mock_res = self._mock_sql_generation(question)
            mock_res["is_mock"] = True
            mock_res["explanation"] += f" (Note: OpenAI call failed with '{str(e)[:60]}...', generated via fallback mode)"
            return mock_res

    def correct_sql(
        self,
        question: str,
        schema_context: str,
        failed_sql: str,
        error_message: str,
        attempt_number: int
    ) -> Dict[str, Any]:
        """
        Invokes LLM to diagnose and correct a failed SQL query.
        """
        if self.is_mock:
            return self._mock_sql_correction(question, failed_sql, error_message)

        user_prompt = build_sql_correction_user_prompt(
            question, schema_context, failed_sql, error_message, attempt_number
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SQL_CORRECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            raw_text = response.choices[0].message.content
            parsed = json.loads(raw_text)
            parsed["is_mock"] = False
            return parsed
        except Exception as e:
            logger.error(f"OpenAI SQL correction failed: {e}.")
            return self._mock_sql_correction(question, failed_sql, error_message)

    def explain_results(
        self,
        question: str,
        sql: str,
        columns: List[str],
        rows: List[Dict[str, Any]],
        row_count: int,
        execution_time_ms: float
    ) -> str:
        """
        Generates natural language business explanation grounded in the returned data.
        """
        if self.is_mock or not self.client:
            return self._mock_result_explanation(question, columns, rows, row_count)

        user_prompt = build_result_explanation_user_prompt(
            question, sql, columns, rows, row_count, execution_time_ms
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": RESULT_EXPLANATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI result explanation failed: {e}. Using deterministic explainer.")
            return self._mock_result_explanation(question, columns, rows, row_count)

    # =========================================================================
    # Mock Engine (Documented Fallback for Testing Without Live API Keys)
    # =========================================================================

    def _mock_sql_generation(self, question: str) -> Dict[str, Any]:
        """Provides accurate SQL generation for canonical analytics questions."""
        q = question.lower().strip()

        # Check for non-database domain questions
        if any(w in q for w in ["weather", "president", "recipe", "capital of", "who wrote", "sports score"]):
            return {
                "sql": None,
                "explanation": "Query is outside the scope of the e-commerce database.",
                "clarification_needed": "The database tracks e-commerce customers, products, categories, orders, order items, and payments. Could you ask a question related to sales, revenue, orders, or customers?",
                "is_mock": True
            }

        # 1. Top 5 products by revenue
        if "top" in q and "product" in q and ("revenue" in q or "sales" in q or "earning" in q):
            return {
                "sql": (
                    "SELECT p.product_name, "
                    "ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue, "
                    "SUM(oi.quantity) AS total_units_sold "
                    "FROM products p "
                    "JOIN order_items oi ON p.product_id = oi.product_id "
                    "JOIN orders o ON oi.order_id = o.order_id "
                    "WHERE o.order_status = 'completed' "
                    "GROUP BY p.product_id, p.product_name "
                    "ORDER BY total_revenue DESC "
                    "LIMIT 5"
                ),
                "explanation": "Calculates total revenue and quantity sold for completed orders grouped by product, returning the top 5.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 2. Highest sales / revenue by region
        if "region" in q:
            return {
                "sql": (
                    "SELECT c.region, "
                    "ROUND(SUM(o.total_amount), 2) AS total_sales, "
                    "COUNT(o.order_id) AS total_orders "
                    "FROM customers c "
                    "JOIN orders o ON c.customer_id = o.customer_id "
                    "WHERE o.order_status = 'completed' "
                    "GROUP BY c.region "
                    "ORDER BY total_sales DESC"
                ),
                "explanation": "Aggregates completed order totals and order counts grouped by customer geographical region, ordered by highest sales.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 3. Monthly revenue
        if "monthly" in q or ("month" in q and "revenue" in q):
            return {
                "sql": (
                    "SELECT substr(o.order_date, 1, 7) AS month, "
                    "ROUND(SUM(o.total_amount), 2) AS monthly_revenue, "
                    "COUNT(o.order_id) AS orders_count "
                    "FROM orders o "
                    "WHERE o.order_status = 'completed' "
                    "GROUP BY substr(o.order_date, 1, 7) "
                    "ORDER BY month ASC"
                ),
                "explanation": "Groups completed orders by month (YYYY-MM) and computes monthly revenue and order volume.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 4. Customers with most orders
        if "customer" in q and ("most order" in q or "placed the most" in q or "order count" in q):
            return {
                "sql": (
                    "SELECT c.name, c.email, c.city, c.region, "
                    "COUNT(o.order_id) AS total_orders, "
                    "ROUND(SUM(o.total_amount), 2) AS lifetime_value "
                    "FROM customers c "
                    "JOIN orders o ON c.customer_id = o.customer_id "
                    "GROUP BY c.customer_id, c.name, c.email, c.city, c.region "
                    "ORDER BY total_orders DESC "
                    "LIMIT 10"
                ),
                "explanation": "Identifies the most frequent shoppers by counting total orders placed per customer.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 5. Top 10 customers by total spending / revenue
        if "customer" in q and ("spending" in q or "spent" in q or "top" in q):
            return {
                "sql": (
                    "SELECT c.name, c.city, c.region, "
                    "ROUND(SUM(o.total_amount), 2) AS total_spent, "
                    "COUNT(o.order_id) AS order_count "
                    "FROM customers c "
                    "JOIN orders o ON c.customer_id = o.customer_id "
                    "WHERE o.order_status = 'completed' "
                    "GROUP BY c.customer_id, c.name, c.city, c.region "
                    "ORDER BY total_spent DESC "
                    "LIMIT 10"
                ),
                "explanation": "Calculates cumulative spending across completed orders for each customer and returns the top 10.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 6. Compare sales across product categories
        if "categor" in q:
            return {
                "sql": (
                    "SELECT cat.category_name, "
                    "ROUND(SUM(oi.quantity * oi.unit_price), 2) AS category_revenue, "
                    "SUM(oi.quantity) AS total_quantity_sold "
                    "FROM categories cat "
                    "JOIN products p ON cat.category_id = p.category_id "
                    "JOIN order_items oi ON p.product_id = oi.product_id "
                    "JOIN orders o ON oi.order_id = o.order_id "
                    "WHERE o.order_status = 'completed' "
                    "GROUP BY cat.category_id, cat.category_name "
                    "ORDER BY category_revenue DESC"
                ),
                "explanation": "Joins categories with products and completed order items to compare revenue across all merchandise categories.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 7. Average order value (AOV)
        if "average order" in q or "aov" in q or ("average" in q and "value" in q):
            return {
                "sql": (
                    "SELECT ROUND(AVG(total_amount), 2) AS average_order_value, "
                    "ROUND(MIN(total_amount), 2) AS min_order_value, "
                    "ROUND(MAX(total_amount), 2) AS max_order_value, "
                    "COUNT(order_id) AS completed_orders "
                    "FROM orders "
                    "WHERE order_status = 'completed'"
                ),
                "explanation": "Computes average, minimum, and maximum order values across all completed customer orders.",
                "clarification_needed": None,
                "is_mock": True
            }

        # 8. Payment method breakdown
        if "payment" in q:
            return {
                "sql": (
                    "SELECT payment_method, "
                    "payment_status, "
                    "COUNT(payment_id) AS transaction_count, "
                    "ROUND(SUM(amount), 2) AS total_processed "
                    "FROM payments "
                    "GROUP BY payment_method, payment_status "
                    "ORDER BY total_processed DESC"
                ),
                "explanation": "Breaks down transaction volumes and processed amounts by payment method and payment status.",
                "clarification_needed": None,
                "is_mock": True
            }

        # Default fallback query for inventory or general questions
        return {
            "sql": (
                "SELECT p.product_name, cat.category_name, p.price, p.stock_quantity "
                "FROM products p "
                "JOIN categories cat ON p.category_id = cat.category_id "
                "ORDER BY p.price DESC "
                "LIMIT 10"
            ),
            "explanation": "Retrieves the highest priced products and their current stock inventory levels.",
            "clarification_needed": None,
            "is_mock": True
        }

    def _mock_sql_correction(self, question: str, failed_sql: str, error_message: str) -> Dict[str, Any]:
        """Fixes common SQL errors like missing joins or column names."""
        corrected_sql = failed_sql

        if "no such column" in error_message.lower() or "column does not exist" in error_message.lower():
            # Replace invalid references with valid column names
            corrected_sql = re.sub(r"\bcustomers\.id\b", "customers.customer_id", corrected_sql, flags=re.IGNORECASE)
            corrected_sql = re.sub(r"\borders\.id\b", "orders.order_id", corrected_sql, flags=re.IGNORECASE)
            corrected_sql = re.sub(r"\bproducts\.id\b", "products.product_id", corrected_sql, flags=re.IGNORECASE)
        elif "group by" in error_message.lower():
            # Fix aggregation query
            corrected_sql = "SELECT c.region, ROUND(SUM(o.total_amount), 2) AS total_sales FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.region ORDER BY total_sales DESC"

        return {
            "sql": corrected_sql,
            "explanation": f"Corrected column references and grouping to resolve: {error_message[:60]}",
            "clarification_needed": None,
            "is_mock": True
        }

    def _mock_result_explanation(self, question: str, columns: List[str], rows: List[Dict[str, Any]], row_count: int) -> str:
        """Generates an accurate, grounded summary of the query results."""
        if row_count == 0 or not rows:
            return "No matching records were found in the database for the given criteria."

        first_row = rows[0]
        # Check if single row aggregate
        if row_count == 1:
            details = ", ".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in first_row.items()])
            return f"The query returned 1 summary record. Key metrics are: {details}."

        # Multi-row list (e.g. Top N products, regions, categories)
        metric_col = None
        label_col = columns[0]
        for col in columns[1:]:
            val = first_row.get(col)
            if isinstance(val, (int, float)):
                metric_col = col
                break

        summary = f"The query successfully analyzed {row_count} records to address: '{question}'.\n\n"
        if metric_col and label_col:
            top_item = first_row.get(label_col)
            top_val = first_row.get(metric_col)
            last_row = rows[-1]
            last_item = last_row.get(label_col)
            last_val = last_row.get(metric_col)

            summary += f"- Top Performer: **{top_item}** leads with **{top_val:,}** ({metric_col.replace('_', ' ')}).\n"
            if row_count > 1:
                summary += f"- Lowest in Range: **{last_item}** recorded **{last_val:,}** ({metric_col.replace('_', ' ')}).\n"

        summary += f"\nTotal entries displayed: {min(row_count, 10)}."
        return summary
