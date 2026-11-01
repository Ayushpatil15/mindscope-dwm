import pytest
from backend.app.services.lab_runner import execute_lab, execute_lab_2, execute_lab_3, execute_lab_8


def test_lab_2_parameter_execution():
    """Verify Lab 2 executes exact dynamic dimension, measure, and aggregator without fallback."""
    # Test 1: Academic Level + Sleep Hours + AVG
    res = execute_lab_2({
        "operation": "Roll-up",
        "dimension": "academic_level",
        "measure": "sleep_hours_per_night",
        "aggregator": "AVG"
    })
    assert res["status"] == "success"
    table = res["tables"][0]
    assert "avg_sleep_hours_per_night" in table["columns"]
    assert "academic_level" in table["columns"]
    assert res["metrics"]["Aggregated Measure"] == "sleep_hours_per_night"
    assert res["metrics"]["Aggregate Function"] == "AVG"
    assert "avg_sleep_hours_per_night" in res["sql"].lower()

    # Test 2: Country + Usage Hours + SUM
    res2 = execute_lab_2({
        "operation": "Roll-up",
        "dimension": "country",
        "measure": "avg_daily_usage_hours",
        "aggregator": "SUM"
    })
    assert res2["status"] == "success"
    table2 = res2["tables"][0]
    assert "sum_avg_daily_usage_hours" in table2["columns"]
    assert "country" in table2["columns"]
    assert res2["metrics"]["Aggregate Function"] == "SUM"


def test_lab_3_case_insensitive_matching():
    """Verify Lab 3 matches lowercase parameters to DataFrame columns."""
    res = execute_lab_3({
        "chart": "Bar",
        "x": "academic_level",
        "y": "sleep_hours_per_night"
    })
    assert res["status"] == "success"
    assert res["metrics"]["X-Axis Column"] == "Academic_Level"
    assert res["metrics"]["Y-Axis Column"] == "Sleep_Hours_Per_Night"
    assert res["tables"][0]["columns"][0] == "Academic_Level"


def test_lab_8_full_cohort_clustering():
    """Verify Lab 8 clusters the entire 5,000 cohort and returns rich institutional profiles."""
    res = execute_lab_8({
        "clusters": 4,
        "linkage": "ward"
    })
    assert res["status"] == "success"
    assert res["metrics"]["Analyzed Cohort Size"] in (4998, 5000)
    assert len(res["tables"][0]["rows"]) == 4
    assert "Institutional Interpretation" in res["tables"][0]["columns"]
    assert "Z = linkage" in res["sql"]
    assert res["dendrogram_data"] is not None
    assert "icoord" in res["dendrogram_data"]
