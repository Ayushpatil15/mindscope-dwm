import csv
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple


EXPECTED_COLUMNS = [
    "Age",
    "Gender",
    "Country",
    "Academic_Level",
    "Most_Used_Platform",
    "Purpose_Of_Use",
    "Avg_Daily_Usage_Hours",
    "Daily_Unlocks",
    "Study_Hours",
    "Physical_Activity_Hours",
    "Sleep_Hours_Per_Night",
    "Stress_Level",
    "Mental_Health_Score",
]


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_csv(file_path: str | Path) -> Tuple[List[Dict[str, str]], str, int, str]:
    """
    Extracts raw rows from CSV.
    Returns:
        (rows, sha256_checksum, row_count, filename)
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Source file not found: {path}")

    sha256_hash = compute_sha256(path)
    rows: List[Dict[str, str]] = []

    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [col for col in EXPECTED_COLUMNS if col not in headers]
        if missing:
            raise ValueError(f"CSV header missing required columns: {missing}")

        for row in reader:
            rows.append(row)

    return rows, sha256_hash, len(rows), path.name

