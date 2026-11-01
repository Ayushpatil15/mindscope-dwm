import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

from backend.app.models.staging import ETLRun
from .extractor import extract_csv
from .stager import stage_raw_records
from .loader import load_staging_to_warehouse
from .reconciler import reconcile_load
from .activator import activate_version_and_finalize_run


def record_etl_failure(session_factory: sessionmaker, run_id: int, error_message: str) -> None:
    """Autonomous audit transaction recording failure details without destroying staging records."""
    with session_factory() as session:
        session.execute(
            update(ETLRun)
            .where(ETLRun.run_id == run_id)
            .values(
                status="FAILED",
                error_message=error_message,
                completed_at=datetime.now(timezone.utc)
            )
        )
        session.commit()


def run_etl_pipeline(file_path: str | Path, session_factory: sessionmaker) -> Dict[str, Any]:
    """
    Executes the 3-transaction ETL pipeline:
    Tx 1: Staging & Run creation
    Tx 2: Validation, Dimension upsert, Fact loading, Reconciliation
    Tx 3: Atomic Version Activation & Cache Invalidation
    """
    # Extraction
    raw_rows, sha256_hash, extracted_count, filename = extract_csv(file_path)
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"

    # Transaction 1: Staging
    with session_factory() as session:
        run_id, staged_count = stage_raw_records(session, batch_id, filename, raw_rows)

    # Transaction 2: Warehouse Loading
    try:
        with session_factory() as session:
            version_id, loaded_count, rejected_count = load_staging_to_warehouse(
                session=session,
                batch_id=batch_id,
                run_id=run_id,
                source_filename=filename,
                sha256_checksum=sha256_hash
            )
            reconcile_load(session, version_id, staged_count, loaded_count, rejected_count)
            session.commit()
    except Exception as exc:
        record_etl_failure(session_factory, run_id, str(exc))
        raise

    # Transaction 3: Activation
    with session_factory() as session:
        activate_version_and_finalize_run(
            session=session,
            version_id=version_id,
            run_id=run_id,
            loaded_count=loaded_count,
            rejected_count=rejected_count
        )

    return {
        "run_id": run_id,
        "batch_id": batch_id,
        "version_id": version_id,
        "rows_extracted": extracted_count,
        "rows_staged": staged_count,
        "rows_loaded": loaded_count,
        "rows_rejected": rejected_count,
        "sha256": sha256_hash,
        "status": "COMPLETED"
    }

