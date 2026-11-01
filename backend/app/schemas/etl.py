from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ETLStatusResponse(BaseModel):
    active_dataset_version: Optional[int]
    row_count: int
    sha256_checksum: Optional[str]
    is_active: bool
    last_run_status: Optional[str]
    last_run_completed_at: Optional[datetime]


class ETLVersionItem(BaseModel):
    version_id: int
    version_number: int
    batch_id: str
    source_filename: str
    row_count: int
    sha256_checksum: str
    is_active: bool
    created_at: datetime
    activated_at: Optional[datetime]


class ETLRunItem(BaseModel):
    run_id: int
    batch_id: str
    source_file: str
    status: str
    rows_extracted: int
    rows_staged: int
    rows_loaded: int
    rows_rejected: int
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]


class ETLRejectionItem(BaseModel):
    rejection_id: int
    run_id: int
    source_row_num: int
    column_name: Optional[str]
    invalid_value: Optional[str]
    rejection_reason: str
    rejected_at: datetime

