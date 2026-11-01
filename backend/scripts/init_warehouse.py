import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.session import get_engine, get_session_factory
from backend.app.models.base import Base
from backend.app.models.views import create_views
import backend.app.models  # Register all models
from backend.app.etl.pipeline import run_etl_pipeline


def main():
    csv_path = PROJECT_ROOT / "data" / "Student_Social_Media_And_Mental_Health_Impact.csv"
    if not csv_path.exists():
        print(f"Error: CSV not found at {csv_path}")
        sys.exit(1)

    print(f"Initializing SQLite Warehouse schema and views...")
    engine = get_engine()
    Base.metadata.create_all(engine)
    create_views(engine)
    print("Schema created successfully.")

    session_factory = get_session_factory(engine)

    print(f"Executing ETL pipeline for {csv_path.name}...")
    result = run_etl_pipeline(csv_path, session_factory)
    print("ETL Pipeline completed successfully:")
    for k, v in result.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

