import json
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from backend.app.etl.pipeline import run_etl_pipeline
from backend.app.services.olap.query_generator import OLAPQueryGenerator
from backend.app.services.olap.executor import OLAPExecutor


CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "Student_Social_Media_And_Mental_Health_Impact.csv"


def test_pivot_nan_bug_fix_ac_04(test_engine):
    """
    AC-04: Pivot operation handles sparse cross-tabulation cells cleanly.
    Guarantees that no float('nan') values are ever produced, eliminating the Starlette JSON crash.
    """
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    run_etl_pipeline(CSV_PATH, session_factory)

    with session_factory() as session:
        # Cross-tabulate platform by stress_level
        col_values = ["Low", "Medium", "High", "Very High"]
        sql, params = OLAPQueryGenerator.build_pivot(
            row_dim="platform",
            col_dim="stress_level",
            col_values=col_values,
            measure="mental_health_score",
            agg="AVG"
        )
        res = OLAPExecutor.execute(session, sql, params, operation="Pivot")

        assert res["row_count"] > 0
        # Check every cell value
        for row in res["data"]:
            for col, val in row.items():
                if isinstance(val, float):
                    import math
                    assert not math.isnan(val), f"Found NaN in column {col}"
                    assert not math.isinf(val), f"Found Inf in column {col}"

        # Standard strict JSON serializer (with allow_nan=False) must serialize cleanly
        json_str = json.dumps(res, allow_nan=False)
        assert len(json_str) > 0
        assert "NaN" not in json_str

