from pathlib import Path
from sqlalchemy.orm import sessionmaker
from backend.app.etl.pipeline import run_etl_pipeline
from backend.app.services.olap.query_generator import OLAPQueryGenerator
from backend.app.services.olap.executor import OLAPExecutor


CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "Student_Social_Media_And_Mental_Health_Impact.csv"


def setup_warehouse(test_engine):
    session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    run_etl_pipeline(CSV_PATH, session_factory)
    return session_factory


def test_olap_rollup_ac_03(test_engine):
    """AC-03: Roll-up hierarchical multi-tier aggregation."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_rollup(dim1="academic_level", dim2="platform")
        res = OLAPExecutor.execute(session, sql, params, operation="Rollup")

        assert res["row_count"] > 0
        assert res["execution_time_ms"] < 250  # Must be fast
        # Find grand total row (academic_level='(All)', platform='(All)')
        grand_total = next(
            (r for r in res["data"] if r["academic_level"] == "(All)" and r["platform"] == "(All)"),
            None
        )
        assert grand_total is not None
        assert grand_total["students"] == 5000
        assert grand_total["agg_value"] == 6.23


def test_olap_drilldown_ac_03(test_engine):
    """AC-03: Drill-down fine-grained multi-dimensional aggregation."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_drilldown(
            dims=["academic_level", "platform", "stress_level"],
            measure="mental_health_score"
        )
        res = OLAPExecutor.execute(session, sql, params, operation="Drilldown")

        assert res["row_count"] > 0
        total_students = sum(r["students"] for r in res["data"])
        assert total_students == 5000


def test_olap_slice_ac_03(test_engine):
    """AC-03: Slice on single dimension."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_slice(
            slice_dim="country",
            slice_val="India",
            group_dims=["platform", "academic_level"]
        )
        res = OLAPExecutor.execute(session, sql, params, operation="Slice")

        assert res["row_count"] > 0
        for r in res["data"]:
            assert "students" in r
            assert "agg_value" in r


def test_olap_dice_ac_03(test_engine):
    """AC-03: Dice multi-attribute sub-cube selection."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_dice(
            dice_filters={
                "academic_level": ["Undergraduate", "Graduate"],
                "platform": ["Instagram", "YouTube"]
            },
            select_dims=["academic_level", "platform"]
        )
        res = OLAPExecutor.execute(session, sql, params, operation="Dice")

        assert res["row_count"] > 0
        for r in res["data"]:
            assert r["academic_level"] in ["Undergraduate", "Graduate"]
            assert r["platform"] in ["Instagram", "YouTube"]


def test_olap_drill_across_ac_03(test_engine):
    """AC-03: Drill-across joining FactSurveyResponse and FactLifestyle at conformed dim."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_drill_across()
        res = OLAPExecutor.execute(session, sql, params, operation="DrillAcross")

        assert res["row_count"] == 3  # 3 Academic levels
        total_students = sum(r["students"] for r in res["data"])
        assert total_students == 5000
        # Columns from both facts present
        assert "avg_screen_hours" in res["columns"]
        assert "avg_sleep_hours" in res["columns"]
        assert "avg_study_hours" in res["columns"]


def test_olap_cube_ac_03(test_engine):
    """AC-03: CUBE semantics across all 4 grouping combinations."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_cube(dim1="academic_level", dim2="platform")
        res = OLAPExecutor.execute(session, sql, params, operation="Cube")

        grouping_ids = {r["grouping_id"] for r in res["data"]}
        assert grouping_ids == {0, 1, 2, 3}


def test_olap_grouping_sets_ac_03(test_engine):
    """AC-03: GROUPING SETS semantics."""
    session_factory = setup_warehouse(test_engine)
    with session_factory() as session:
        sql, params = OLAPQueryGenerator.build_grouping_sets(dims=["academic_level", "platform"])
        res = OLAPExecutor.execute(session, sql, params, operation="GroupingSets")

        dim_types = {r["dimension_type"] for r in res["data"]}
        assert "Academic Level" in dim_types
        assert "Platform" in dim_types
        assert "All" in dim_types

