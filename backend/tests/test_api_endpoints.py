import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_static_index_serving_ac_15():
    """AC-15: Root path serves index.html with HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_dashboard_overview_endpoint_ac_06():
    """AC-06: Dashboard overview returns verified KPIs and chart data."""
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()

    kpis = data["kpis"]
    assert kpis["total_students"] == 5000
    assert kpis["avg_mental_health_score"] == 6.23
    assert kpis["avg_daily_usage_hours"] == 5.08
    assert kpis["avg_sleep_hours"] in [6.63, 6.64]

    # Verify stress distribution
    stress_dist = data["stress_distribution"]
    assert len(stress_dist) == 4
    total_pct = sum(item["percentage"] for item in stress_dist)
    assert round(total_pct, 1) == 100.0


def test_dashboard_global_filters_ac_06():
    """AC-06: Dashboard overview responds to global filters correctly."""
    response = client.get("/api/dashboard/overview?country=India")
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"]["total_students"] > 0
    assert data["kpis"]["total_students"] < 5000


def test_warehouse_schema_endpoint_ac_07():
    """AC-07: Warehouse schemas returns table catalog with keys and constraints."""
    response = client.get("/api/warehouse/schemas")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    table_names = [t["name"] for t in data["tables"]]
    assert "fact_survey_response" in table_names
    assert "fact_lifestyle" in table_names
    assert "dim_respondent" in table_names
    assert "v_star_schema_denormalized" in table_names


def test_warehouse_sql_lab_endpoint_ac_08():
    """AC-08: SQL Lab executes valid SELECT queries and returns rows."""
    payload = {
        "sql": "SELECT platform_name, COUNT(*) as cnt FROM dim_platform GROUP BY platform_name ORDER BY cnt DESC;",
        "limit": 10
    }
    response = client.post("/api/warehouse/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["columns"] == ["platform_name", "cnt"]
    assert len(data["rows"]) > 0


def test_warehouse_sql_lab_blocks_mutations_ac_05():
    """AC-05: SQL Lab blocks malicious mutations with HTTP 403."""
    payload = {
        "sql": "DROP TABLE dim_gender;",
        "limit": 10
    }
    response = client.post("/api/warehouse/query", json=payload)
    assert response.status_code == 403


def test_olap_execute_endpoint():
    """OLAP execute endpoint returns tabular rows and chart series."""
    response = client.get("/api/olap/execute?op=Roll-up&x=academic_level&y=platform")
    assert response.status_code == 200
    data = response.json()
    assert data["op"] == "Roll-up"
    assert "columns" in data
    assert "rows" in data
    assert "chart" in data
    assert len(data["rows"]) > 0


def test_predict_endpoint_ac_09_and_ac_22():
    """AC-09 & AC-22: Prediction endpoint returns score and transparent ensemble tree spread."""
    payload = {
        "age": 22,
        "gender": "Female",
        "country": "India",
        "academic_level": "Undergraduate",
        "most_used_platform": "Instagram",
        "purpose_of_use": "Entertainment",
        "avg_daily_usage_hours": 5.5,
        "daily_unlocks": 150,
        "study_hours": 4.0,
        "physical_activity_hours": 1.5,
        "sleep_hours_per_night": 7.0,
        "stress_level": "Medium"
    }
    response = client.post("/api/predict/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_score" in data
    assert 0.0 <= data["predicted_score"] <= 10.0

    # AC-22 Ensemble tree spread verification
    spread = data["ensemble_tree_spread"]
    assert "tree_percentile_10" in spread
    assert "tree_percentile_90" in spread
    assert spread["tree_percentile_10"] <= spread["tree_percentile_90"]
    assert "Ensemble disagreement range" in spread["metric_description"]


def test_educational_labs_unified_endpoint():
    """Verify that all 10 educational DWM labs return valid experiment payloads."""
    for lab_id in range(1, 11):
        response = client.get(f"/api/labs/{lab_id}")
        assert response.status_code == 200, f"Lab {lab_id} returned status {response.status_code}"


def test_association_rules_no_undefined_and_contract():
    """Verify Bug Fix: Association rules contain valid mapped antecedents and consequents without undefined."""
    response = client.get("/api/analytics/associations?min_support=0.1&min_confidence=0.6")
    assert response.status_code == 200
    data = response.json()
    assert "rules" in data
    assert len(data["rules"]) > 0
    for r in data["rules"]:
        assert "antecedents" in r
        assert "consequents" in r
        assert "if" in r
        assert "then" in r
        assert r["antecedents"] is not None
        assert r["consequents"] is not None
        assert str(r["antecedents"]) != "undefined"
        assert str(r["consequents"]) != "undefined"
        assert len(r["antecedents"]) > 0
        assert len(r["consequents"]) > 0


def test_segmentation_clusters_and_pca_coordinates():
    """Verify Bug Fix: Clustering returns non-empty cluster profiles and 2D PCA points."""
    response = client.get("/api/analytics/clusters?k=3")
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data
    assert "profile" in data
    assert len(data["clusters"]) == 3
    assert "points" in data
    assert len(data["points"]) > 0
    # Check PCA point structure: [x, y, cluster_id]
    pt0 = data["points"][0]
    assert len(pt0) == 3
    assert isinstance(pt0[0], (int, float))
    assert isinstance(pt0[1], (int, float))
    assert isinstance(pt0[2], int)


def test_lab_runner_post_and_catalog():
    """Verify DMart-benchmark LabRunner endpoints: GET /api/labs catalog and POST /api/labs/{n}/run."""
    cat_res = client.get("/api/labs")
    assert cat_res.status_code == 200
    catalog = cat_res.json()
    assert catalog["total_labs"] == 10

    # Test running Lab 1, Lab 2, Lab 7, Lab 8 via POST
    for lab_num in [1, 2, 7, 8]:
        run_res = client.post(f"/api/labs/{lab_num}/run", json={"params": {}})
        assert run_res.status_code == 200
        run_data = run_res.json()
        assert run_data["status"] == "success"
        assert "tables" in run_data and len(run_data["tables"]) > 0
        assert "charts" in run_data and len(run_data["charts"]) > 0
        assert "metrics" in run_data and len(run_data["metrics"]) > 0
        assert "observations" in run_data and len(run_data["observations"]) > 0


def test_lab_8_agglomerative_clustering():
    """Verify Lab 8: Agglomerative Hierarchical Clustering returns dendrogram and cluster tables."""
    res = client.post("/api/labs/8/run", json={"params": {"linkage": "Ward", "clusters": 4}})
    assert res.status_code == 200
    data = res.json()
    assert data["special"] == "dendrogram"
    assert "dendrogram_data" in data
    assert "icoord" in data["dendrogram_data"]
    assert "dcoord" in data["dendrogram_data"]
    assert "points" in data
    assert data["metrics"]["Linkage Criterion"] == "Ward"


def test_lab_9_apriori_association_mining():
    """Verify Lab 9: Apriori Association Rule Mining returns rules and network edges."""
    res = client.post("/api/labs/9/run", json={"params": {"support": 0.08, "confidence": 0.5}})
    assert res.status_code == 200
    data = res.json()
    assert data["special"] == "network"
    assert "network_edges" in data
    assert len(data["network_edges"]) > 0
    assert "tables" in data
    assert len(data["tables"]) == 2  # rules and frequent itemsets


def test_lab_10_step_scoping():
    """Verify Lab 10: Integrated Pipeline step scoping executes step-specific logic."""
    for step in ["Preprocess", "Classify", "Cluster", "Associate"]:
        res = client.post("/api/labs/10/run", json={"params": {"step": step, "classifier": "Decision Tree"}})
        assert res.status_code == 200
        data = res.json()
        assert data["special"] == "pipeline"
        assert data["step"] == step
        assert len(data["tables"]) > 0
        assert len(data["charts"]) > 0
        if step == "Classify":
            assert data["tree_data"] is not None
        elif step == "Cluster":
            assert len(data["points"]) > 0
        elif step == "Associate":
            assert len(data["network_edges"]) > 0


def test_insights_endpoints():
    """Verify Insights endpoints return data-derived signals and recommendations."""
    for path in ["/api/insights", "/api/dashboard/insights"]:
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert "insights" in data and len(data["insights"]) >= 4
        assert "recommendations" in data and len(data["recommendations"]) >= 4
        for item in data["insights"]:
            assert "title" in item
            assert "sentence" in item
            assert "metric" in item
            assert item["tone"] in ["positive", "attention", "neutral"]


