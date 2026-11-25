import json
from typing import Dict, List, Any, Optional
from sqlalchemy import inspect, text, Engine
from backend.app.schemas.schema import ColumnInfo, TableRelationship, TableSchema, DatabaseSchemaResponse
from backend.app.core.logging import logger

# Business tables allowed for analytics
ALLOWED_TABLES = {"categories", "products", "customers", "orders", "order_items", "payments"}
INTERNAL_SYSTEM_TABLES = {"query_history", "alembic_version", "sqlite_sequence"}

class SchemaService:
    def __init__(self, engine: Engine):
        self.engine = engine
        self._cached_schema: Optional[DatabaseSchemaResponse] = None
        self._cached_prompt_context: Optional[str] = None

    def refresh_cache(self) -> None:
        """Forces a refresh of cached schema metadata."""
        self._cached_schema = None
        self._cached_prompt_context = None

    def get_database_schema(self, force_refresh: bool = False) -> DatabaseSchemaResponse:
        """
        Dynamically inspects the database schema using SQLAlchemy Inspector.
        Extracts table columns, types, primary keys, foreign keys, row counts,
        and high-signal sample values for categorical columns.
        """
        if self._cached_schema and not force_refresh:
            return self._cached_schema

        inspector = inspect(self.engine)
        all_table_names = inspector.get_table_names()

        # Focus inspection on permitted business tables
        tables_to_inspect = [t for t in all_table_names if t in ALLOWED_TABLES]
        if not tables_to_inspect:
            tables_to_inspect = [t for t in all_table_names if t not in INTERNAL_SYSTEM_TABLES]

        table_schemas: List[TableSchema] = []
        relationships: List[TableRelationship] = []

        with self.engine.connect() as conn:
            for table_name in tables_to_inspect:
                # 1. Primary keys
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint.get("constrained_columns", []) if pk_constraint else []

                # 2. Foreign keys
                fks = inspector.get_foreign_keys(table_name)
                fk_lookup = {}
                table_relations: List[TableRelationship] = []

                for fk in fks:
                    referred_table = fk.get("referred_table")
                    constrained_cols = fk.get("constrained_columns", [])
                    referred_cols = fk.get("referred_columns", [])
                    for sc, tc in zip(constrained_cols, referred_cols):
                        fk_lookup[sc] = f"{referred_table}.{tc}"
                        rel = TableRelationship(
                            source_table=table_name,
                            source_column=sc,
                            target_table=referred_table,
                            target_column=tc
                        )
                        table_relations.append(rel)
                        relationships.append(rel)

                # 3. Columns
                columns_meta = inspector.get_columns(table_name)
                columns: List[ColumnInfo] = []
                for col in columns_meta:
                    c_name = col["name"]
                    c_type = str(col["type"])
                    c_nullable = col.get("nullable", True)
                    c_default = str(col.get("default")) if col.get("default") is not None else None
                    columns.append(ColumnInfo(
                        name=c_name,
                        type=c_type,
                        nullable=c_nullable,
                        primary_key=c_name in primary_keys,
                        foreign_key=fk_lookup.get(c_name),
                        default=c_default
                    ))

                # 4. Row count
                try:
                    count_res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                    row_count = int(count_res) if count_res else 0
                except Exception as e:
                    logger.warning(f"Could not count rows for {table_name}: {e}")
                    row_count = 0

                # 5. Sample categorical values (for high-signal filtering)
                sample_values: Dict[str, List[Any]] = {}
                categorical_cols = [
                    c["name"] for c in columns_meta 
                    if any(t in str(c["type"]).lower() for t in ["char", "varchar", "text", "string"])
                    and not any(x in c["name"].lower() for x in ["email", "name", "id", "password"])
                ]

                for col_name in categorical_cols[:4]:
                    try:
                        vals_res = conn.execute(
                            text(f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 8")
                        ).fetchall()
                        sample_values[col_name] = [r[0] for r in vals_res if r[0] is not None]
                    except Exception as e:
                        logger.debug(f"Could not sample column {table_name}.{col_name}: {e}")

                table_schemas.append(TableSchema(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=table_relations,
                    row_count=row_count,
                    sample_values=sample_values
                ))

        schema_summary = f"Database contains {len(table_schemas)} tables: " + ", ".join([t.name for t in table_schemas])
        self._cached_schema = DatabaseSchemaResponse(
            tables=table_schemas,
            relationships=relationships,
            schema_summary=schema_summary
        )
        return self._cached_schema

    def get_prompt_schema_context(self, force_refresh: bool = False) -> str:
        """
        Formats the dynamic schema into concise, high-context DDL specification
        specifically optimized for LLM SQL generation.
        Includes exact column types, primary/foreign key join paths, and distinct categorical values.
        """
        if self._cached_prompt_context and not force_refresh:
            return self._cached_prompt_context

        schema = self.get_database_schema(force_refresh=force_refresh)
        lines = ["# DATABASE SCHEMA CONTEXT"]
        lines.append(f"Database contains tables: {', '.join([t.name for t in schema.tables])}\n")

        for table in schema.tables:
            lines.append(f"Table: {table.name} ({table.row_count} rows)")
            col_lines = []
            for col in table.columns:
                pk_tag = " [PRIMARY KEY]" if col.primary_key else ""
                fk_tag = f" [REFERENCES {col.foreign_key}]" if col.foreign_key else ""
                col_lines.append(f"  - {col.name} ({col.type}){pk_tag}{fk_tag}")
            lines.extend(col_lines)

            if table.sample_values:
                sample_str = ", ".join([f"{k}: {json.dumps(v)}" for k, v in table.sample_values.items() if v])
                if sample_str:
                    lines.append(f"  Sample Values: {sample_str}")
            lines.append("")

        lines.append("# FOREIGN KEY RELATIONSHIPS (JOIN PATHS)")
        for rel in schema.relationships:
            lines.append(f"- {rel.source_table}.{rel.source_column} -> {rel.target_table}.{rel.target_column}")

        self._cached_prompt_context = "\n".join(lines)
        return self._cached_prompt_context

    def get_table_schema(self, table_name: str) -> Optional[TableSchema]:
        """Returns schema for a specific table."""
        schema = self.get_database_schema()
        for t in schema.tables:
            if t.name.lower() == table_name.lower():
                return t
        return None
