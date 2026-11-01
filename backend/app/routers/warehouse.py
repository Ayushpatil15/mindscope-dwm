from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db, DEFAULT_DB_PATH
from backend.app.schemas.warehouse import (
    WarehouseSchemaResponse, TableMetadata, ColumnMetadata, ForeignKeyMetadata,
    SQLQueryRequest, SQLQueryResponse
)
from backend.app.security.authorizer import execute_safe_query, SecurityException

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])


@router.get("/schemas", response_model=WarehouseSchemaResponse)
def get_warehouse_schemas(db: Session = Depends(get_db)):
    """Returns database schema metadata, table types, column definitions, and relationships."""
    active_version = db.execute(
        text("SELECT version_id FROM dataset_versions WHERE is_active = 1")
    ).scalar()

    table_names = [
        ("fact_survey_response", "FACT"),
        ("fact_lifestyle", "FACT"),
        ("dim_respondent", "DIMENSION"),
        ("dim_gender", "DIMENSION"),
        ("dim_academic", "DIMENSION"),
        ("dim_country", "DIMENSION"),
        ("dim_platform", "DIMENSION"),
        ("dim_purpose", "DIMENSION"),
        ("dim_stress", "DIMENSION"),
        ("stg_survey_responses", "STAGING"),
        ("etl_runs", "AUDIT"),
        ("etl_rejections", "AUDIT"),
        ("dataset_versions", "METADATA"),
        ("v_star_schema_denormalized", "VIEW"),
    ]

    tables_meta: List[TableMetadata] = []

    for name, tbl_type in table_names:
        # Check row count
        try:
            cnt = db.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar() or 0
        except Exception:
            cnt = 0

        # Columns
        col_rows = db.execute(text(f"PRAGMA table_info({name});")).fetchall()
        columns = [
            ColumnMetadata(name=r[1], type=r[2], nullable=not bool(r[3]))
            for r in col_rows
        ]
        pk_cols = [r[1] for r in col_rows if r[5] > 0]

        # Foreign keys
        fk_rows = db.execute(text(f"PRAGMA foreign_key_list({name});")).fetchall()
        foreign_keys = [
            ForeignKeyMetadata(column=r[3], ref_table=r[2], ref_column=r[4])
            for r in fk_rows
        ]

        tables_meta.append(
            TableMetadata(
                name=name,
                type=tbl_type,
                row_count=cnt,
                primary_key=pk_cols,
                foreign_keys=foreign_keys,
                columns=columns
            )
        )

    return WarehouseSchemaResponse(
        dialect="SQLite 3.x with WAL & Foreign Keys Enforced",
        active_dataset_version=active_version,
        tables=tables_meta
    )


@router.post("/query", response_model=SQLQueryResponse)
def run_sql_lab_query(req: SQLQueryRequest):
    """Executes a protected, read-only SQL query via SQLite C-level authorizer and read-only connection."""
    try:
        result = execute_safe_query(
            sql=req.sql,
            db_path=DEFAULT_DB_PATH,
            limit=req.limit
        )
        return SQLQueryResponse(**result)
    except SecurityException as sec_err:
        raise HTTPException(status_code=403, detail=str(sec_err))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Query error: {str(exc)}")

