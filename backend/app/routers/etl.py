import shutil
import tempfile
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from backend.app.db.session import get_db, get_session_factory
from backend.app.models.versioning import DatasetVersion
from backend.app.models.staging import ETLRun, ETLRejection
from backend.app.schemas.etl import ETLStatusResponse, ETLVersionItem, ETLRunItem, ETLRejectionItem
from backend.app.etl.pipeline import run_etl_pipeline

router = APIRouter(prefix="/etl", tags=["ETL"])


@router.get("/status", response_model=ETLStatusResponse)
def get_etl_status(db: Session = Depends(get_db)):
    """Returns current active dataset version status and last ETL run results."""
    active_v = db.scalar(
        select(DatasetVersion).where(DatasetVersion.is_active == True)  # noqa: E712
    )
    last_run = db.scalar(
        select(ETLRun).order_by(desc(ETLRun.run_id)).limit(1)
    )

    return ETLStatusResponse(
        active_dataset_version=active_v.version_id if active_v else None,
        row_count=active_v.row_count if active_v else 0,
        sha256_checksum=active_v.sha256_checksum if active_v else None,
        is_active=bool(active_v),
        last_run_status=last_run.status if last_run else None,
        last_run_completed_at=last_run.completed_at if last_run else None
    )


@router.get("/versions", response_model=List[ETLVersionItem])
def get_dataset_versions(db: Session = Depends(get_db)):
    """Returns audit log of all dataset versions."""
    versions = db.scalars(
        select(DatasetVersion).order_by(desc(DatasetVersion.version_number))
    ).all()
    return [
        ETLVersionItem(
            version_id=v.version_id,
            version_number=v.version_number,
            batch_id=v.batch_id,
            source_filename=v.source_filename,
            row_count=v.row_count,
            sha256_checksum=v.sha256_checksum,
            is_active=v.is_active,
            created_at=v.created_at,
            activated_at=v.activated_at
        )
        for v in versions
    ]


@router.get("/history", response_model=List[ETLRunItem])
def get_etl_history(db: Session = Depends(get_db)):
    """Returns audit history of all ETL batch executions."""
    runs = db.scalars(select(ETLRun).order_by(desc(ETLRun.run_id))).all()
    return [
        ETLRunItem(
            run_id=r.run_id,
            batch_id=r.batch_id,
            source_file=r.source_file,
            status=r.status,
            rows_extracted=r.rows_extracted,
            rows_staged=r.rows_staged,
            rows_loaded=r.rows_loaded,
            rows_rejected=r.rows_rejected,
            error_message=r.error_message,
            started_at=r.started_at,
            completed_at=r.completed_at
        )
        for r in runs
    ]


@router.get("/rejections", response_model=List[ETLRejectionItem])
def get_etl_rejections(
    run_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns itemized records rejected during validation."""
    stmt = select(ETLRejection).order_by(desc(ETLRejection.rejection_id))
    if run_id is not None:
        stmt = stmt.where(ETLRejection.run_id == run_id)
    rejections = db.scalars(stmt.limit(200)).all()

    return [
        ETLRejectionItem(
            rejection_id=rj.rejection_id,
            run_id=rj.run_id,
            source_row_num=rj.source_row_num,
            column_name=rj.column_name,
            invalid_value=rj.invalid_value,
            rejection_reason=rj.rejection_reason,
            rejected_at=rj.rejected_at
        )
        for rj in rejections
    ]


@router.post("/upload")
def upload_csv_and_run_etl(file: UploadFile = File(...)):
    """Uploads replacement survey dataset, runs the 3-transaction ETL pipeline, and activates it."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    session_factory = get_session_factory()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        result = run_etl_pipeline(tmp_path, session_factory)
        return {
            "message": "ETL pipeline successfully completed and activated.",
            "details": result
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"ETL pipeline failed: {str(exc)}")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

