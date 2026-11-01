from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class OLAPResponse(BaseModel):
    op: str
    generated_sql: str
    columns: List[str]
    rows: List[List[Any]]
    execution_time_ms: float
    chart: Dict[str, Any]
    explanation: str

