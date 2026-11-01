from datetime import datetime, timezone
from sqlalchemy import update
from sqlalchemy.orm import Session
from backend.app.models.versioning import DatasetVersion
from backend.app.models.staging import ETLRun
from backend.app.core.cache import CacheManager


def activate_version_and_finalize_run(
    session: Session,
    version_id: int,
    run_id: int,
    loaded_count: int,
    rejected_count: int
) -> None:
    """
    Executes Transaction 3:
    - Atomically deactivates previous versions and activates new version_id
    - Marks etl_runs record as COMPLETED
    - Evicts application caches
    """
    now = datetime.now(timezone.utc)

    # 1. Deactivate all existing active versions
    session.execute(
        update(DatasetVersion)
        .where(DatasetVersion.is_active == True)  # noqa: E712
        .values(is_active=False)
    )

    # 2. Activate the target version
    session.execute(
        update(DatasetVersion)
        .where(DatasetVersion.version_id == version_id)
        .values(is_active=True, activated_at=now)
    )

    # 3. Finalize ETLRun
    session.execute(
        update(ETLRun)
        .where(ETLRun.run_id == run_id)
        .values(
            status="COMPLETED",
            completed_at=now,
            rows_loaded=loaded_count,
            rows_rejected=rejected_count,
            error_message=None
        )
    )

    session.commit()

    # 4. Invalidate all model and query caches
    CacheManager.evict_all()

