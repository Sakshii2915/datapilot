import re
from typing import List, Set, Optional, Tuple
import sqlglot
from sqlglot import exp, parse_one, errors
from backend.app.schemas.query import ValidationResult
from backend.app.core.config import settings
from backend.app.core.logging import logger

# Permitted analytics business tables
PERMITTED_TABLES: Set[str] = {
    "categories",
    "products",
    "customers",
    "orders",
    "order_items",
    "payments"
}

# Strictly forbidden AST expression classes
FORBIDDEN_AST_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
    exp.TruncateTable,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
    exp.Grant,
    exp.Revoke,
)

FORBIDDEN_KEYWORDS = {
    "pg_catalog",
    "information_schema",
    "sqlite_master",
    "sqlite_schema",
    "sqlite_sequence",
    "pg_tables",
    "pg_stat",
    "pg_user",
    "current_user",
    "session_user",
    "version()",
    "pg_sleep",
}

class SQLValidator:
    def __init__(self, permitted_tables: Optional[Set[str]] = None, max_limit: int = 100, dialect: Optional[str] = None):
        self.permitted_tables = permitted_tables or PERMITTED_TABLES
        self.max_limit = max_limit or settings.MAX_RESULT_ROWS
        self.dialect = dialect or ("sqlite" if "sqlite" in settings.DATABASE_URL.lower() else "postgres")

    def validate_and_sanitize(self, sql_query: str) -> ValidationResult:
        """
        Performs comprehensive AST-based SQL security validation using SQLGlot.
        Returns ValidationResult with is_valid, sanitized SQL, and tables accessed.
        """
        if not sql_query or not sql_query.strip():
            return ValidationResult(is_valid=False, error="Empty SQL query provided.")

        raw_sql = sql_query.strip()
        # Clean markdown codeblocks if accidentally included
        if raw_sql.startswith("```"):
            lines = raw_sql.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_sql = "\n".join(lines).strip()

        # Step 1: Detect multiple statements
        # SQLGlot parse returns a list of AST expressions
        try:
            parsed_expressions = sqlglot.parse(raw_sql, read="postgres")
        except errors.ParseError as e:
            # Fallback parse check with generic dialect
            try:
                parsed_expressions = sqlglot.parse(raw_sql)
            except Exception as e2:
                return ValidationResult(
                    is_valid=False,
                    error=f"SQL syntax error: Unable to parse query AST ({str(e2)})"
                )

        # Filter out empty statements
        parsed_expressions = [e for e in parsed_expressions if e is not None]

        if not parsed_expressions:
            return ValidationResult(is_valid=False, error="No executable SQL statements found.")

        if len(parsed_expressions) > 1:
            return ValidationResult(
                is_valid=False,
                error="Security rejection: Multiple SQL statements are strictly prohibited."
            )

        root_expr = parsed_expressions[0]

        # Step 2: Validate root statement is a SELECT query (or UNION of SELECTs)
        if not isinstance(root_expr, (exp.Select, exp.Union)):
            return ValidationResult(
                is_valid=False,
                error=f"Security rejection: Only read-only SELECT queries are permitted (received {root_expr.__class__.__name__})."
            )

        # Step 3: Check for forbidden AST node types anywhere in the expression tree
        for node in root_expr.walk():
            if isinstance(node, FORBIDDEN_AST_NODES):
                return ValidationResult(
                    is_valid=False,
                    error=f"Security rejection: Data-modifying statement '{node.__class__.__name__}' is prohibited."
                )

        # Step 4: Check for forbidden system catalogs, functions, or schema access
        sql_lower = root_expr.sql().lower()
        for forbidden in FORBIDDEN_KEYWORDS:
            if forbidden in sql_lower:
                return ValidationResult(
                    is_valid=False,
                    error=f"Security rejection: Access to system catalog or restricted construct '{forbidden}' is prohibited."
                )

        # Step 5: Validate accessed tables against permitted business tables
        # Collect CTE aliases defined in the query (they are valid local tables)
        cte_aliases: Set[str] = set()
        for with_node in root_expr.find_all(exp.With):
            for cte in with_node.expressions:
                if isinstance(cte, exp.CTE) and cte.alias:
                    cte_aliases.add(cte.alias.lower())

        tables_accessed: Set[str] = set()
        for table_node in root_expr.find_all(exp.Table):
            t_name = table_node.name.lower()
            if not t_name:
                continue

            # Skip CTE aliases
            if t_name in cte_aliases:
                continue

            # Check schema qualification
            if table_node.db and table_node.db.lower() not in ("public", ""):
                return ValidationResult(
                    is_valid=False,
                    error=f"Security rejection: Unauthorized schema '{table_node.db}' access."
                )

            if t_name not in self.permitted_tables:
                return ValidationResult(
                    is_valid=False,
                    error=f"Security rejection: Access to unauthorized table '{t_name}' is forbidden."
                )

            tables_accessed.add(t_name)

        if not tables_accessed and not cte_aliases:
            # Query didn't access any valid table
            return ValidationResult(
                is_valid=False,
                error="Security rejection: Query does not reference any authorized tables."
            )

        # Step 6: Enforce query execution limits (LIMIT clause)
        sanitized_expr = root_expr.copy()
        existing_limit = sanitized_expr.find(exp.Limit)

        if existing_limit:
            # If user provided LIMIT, clamp it to maximum allowed
            try:
                limit_val = int(existing_limit.expression.sql())
                if limit_val > self.max_limit:
                    existing_limit.set("expression", exp.Literal.number(self.max_limit))
            except Exception:
                existing_limit.set("expression", exp.Literal.number(self.max_limit))
        else:
            # Inject LIMIT clause
            sanitized_expr = sanitized_expr.limit(self.max_limit)

        # Generate clean dialect-compatible SQL (PostgreSQL or SQLite)
        sanitized_sql = sanitized_expr.sql(dialect=self.dialect)

        return ValidationResult(
            is_valid=True,
            sanitized_sql=sanitized_sql,
            tables_accessed=sorted(list(tables_accessed))
        )
