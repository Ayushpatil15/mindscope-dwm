from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Body
import backend.labs as labs
from backend.app.services.lab_runner import execute_lab

router = APIRouter(tags=["Educational Labs"])

LAB_CATALOG = [
    {
        "number": 1,
        "title": "Data Warehouse Design",
        "subtitle": "Dimensional Modeling: Star, Snowflake & Fact Constellation Schemas",
        "technologies": "SQLite, SQLAlchemy, Star Schema, Fact Constellation"
    },
    {
        "number": 2,
        "title": "OLAP Operations",
        "subtitle": "Multidimensional Aggregation: Roll-up, Drill-down, Slice, Dice, Pivot & CUBE",
        "technologies": "SQL GROUP BY, Aggregate Functions, Cross-Tabulation"
    },
    {
        "number": 3,
        "title": "Data Visualization",
        "subtitle": "Visual Encodings, Distribution Profiling & Variance Analysis",
        "technologies": "Visual Encodings, Boxplot IQR, Grouped Aggregations, Histograms"
    },
    {
        "number": 4,
        "title": "Linear Regression",
        "subtitle": "Predictive Modeling of Continuous Mental Health Score & Residual Analysis",
        "technologies": "OLS Regression, Multiple Regression, Random Forest, MAE/RMSE/R²"
    },
    {
        "number": 5,
        "title": "Attribute Relevance + Decision Tree",
        "subtitle": "Mutual Information Attribute Ranking & Interactive Tree Induction",
        "technologies": "DecisionTreeClassifier, Mutual Information, Interactive SVG Tree"
    },
    {
        "number": 6,
        "title": "Naive Bayes",
        "subtitle": "Probabilistic Classification & Multi-Algorithm Benchmarks",
        "technologies": "Gaussian Naive Bayes, Confusion Matrix Heatmap, Macro F1, Priors"
    },
    {
        "number": 7,
        "title": "K-Means (Student DWM)",
        "subtitle": "Unsupervised Behavioral Partitioning via K-Means & PCA Projection",
        "technologies": "K-Means Lloyd, Elbow Inertia, Silhouette Score, 2D PCA Scatter"
    },
    {
        "number": 8,
        "title": "Agglomerative Clustering",
        "subtitle": "Bottom-Up Hierarchical Clustering with Linkage Criteria & Dendrogram",
        "technologies": "Scipy Linkage, Hierarchical Dendrogram, ARI vs K-Means"
    },
    {
        "number": 9,
        "title": "Apriori",
        "subtitle": "Frequent Itemsets, Association Rules & Behavior Affinity Network",
        "technologies": "Apriori Downward Closure, Support, Confidence, Lift, Network Graph"
    },
    {
        "number": 10,
        "title": "Lab 10: Integrated Data Mining Pipeline",
        "subtitle": "End-to-End CRISP-DM Workflow: Preprocess -> Classify -> Cluster -> Associate",
        "technologies": "Quantile Discretization, 10-Fold CV Tree/NB, K-Means, Apriori"
    }
]


@router.get("/labs")
def list_labs():
    """Lists all 10 available educational DWM laboratories."""
    return {"total_labs": len(LAB_CATALOG), "labs": LAB_CATALOG}


@router.post("/labs/{lab_number}/run")
def run_lab_post(
    lab_number: int,
    payload: Optional[Dict[str, Any]] = Body(default=None)
):
    """
    Executes a laboratory with dynamic parameter controls and returns a standardized
    RunResult containing tables, visual charts, metrics, observations, and opt-in SQL.
    """
    if lab_number < 1 or lab_number > 10:
        raise HTTPException(status_code=404, detail=f"Lab {lab_number} not found. Available labs: 1 to 10.")
    
    params = {}
    if payload:
        params = payload.get("params", payload)
        
    try:
        return execute_lab(lab_number, params)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error executing Lab {lab_number}: {str(exc)}")


@router.get("/labs/{lab_id}")
def get_lab_data(
    lab_id: int,
    x: Optional[str] = Query(None),
    y: Optional[str] = Query(None),
    k: Optional[int] = Query(None),
    op: Optional[str] = Query(None),
    schema: Optional[str] = Query(None),
    min_support: Optional[float] = Query(None),
    min_confidence: Optional[float] = Query(None),
    max_depth: Optional[int] = Query(None)
):
    """
    Unified endpoint for all 10 educational DWM Labs.
    Returns rich RunResult format with backwards compatibility.
    """
    if lab_id < 1 or lab_id > 10:
        raise HTTPException(status_code=404, detail=f"Lab {lab_id} not found. Available labs: 1 to 10.")
        
    params: Dict[str, Any] = {}
    if x: params["x"] = x; params["predictor"] = x
    if y: params["y"] = y
    if k is not None: params["k"] = k
    if op: params["op"] = op
    if schema: params["schema"] = schema
    if min_support is not None: params["min_support"] = min_support
    if min_confidence is not None: params["min_confidence"] = min_confidence
    if max_depth is not None: params["max_depth"] = max_depth
    
    try:
        res = execute_lab(lab_id, params)
        # Ensure any legacy tests expecting specific keys find them directly or nested
        if lab_id == 1:
            raw_eda = labs.eda()
            res.update({k: v for k, v in raw_eda.items() if k not in res})
        elif lab_id == 2:
            raw_schema = labs.schema()
            res.update({k: v for k, v in raw_schema.items() if k not in res})
        elif lab_id == 3:
            raw_olap = labs.olap2(op=op or "cube")
            res.update({k: v for k, v in raw_olap.items() if k not in res})
        elif lab_id == 7:
            raw_km = labs.kmeans(k=k or 3)
            res.update({k: v for k, v in raw_km.items() if k not in res})
        elif lab_id == 8:
            raw_ap = labs.apriori_rules()
            res.update({k: v for k, v in raw_ap.items() if k not in res})
        return res
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error executing Lab {lab_id}: {str(exc)}")
