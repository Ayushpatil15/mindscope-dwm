import io
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.routers import (
    dashboard_router,
    warehouse_router,
    olap_router,
    predict_router,
    analytics_router,
    etl_router,
    labs_router
)
from backend.app.routers.exploration import router as exploration_router
import backend.labs as labs

app = FastAPI(
    title="Student Social Media & Mental Health Analytical Platform",
    description="Enterprise-grade dimensional data warehouse, SQL OLAP engine, and educational laboratory suite.",
    version="1.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modern Analytical Routers
app.include_router(dashboard_router, prefix="/api")
app.include_router(warehouse_router, prefix="/api")
app.include_router(olap_router, prefix="/api")
app.include_router(predict_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(etl_router, prefix="/api")
app.include_router(labs_router, prefix="/api")
app.include_router(exploration_router, prefix="/api")

from backend.app.routers.dashboard import get_insights
from backend.app.db.session import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/api/insights")
def api_insights(db: Session = Depends(get_db)):
    return get_insights(db=db)



# ─── Legacy Lab Endpoints (100% Backward Compatibility) ───
def run_legacy(fn, *a, **kw):
    try:
        return JSONResponse(fn(*a, **kw))
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))


@app.get("/api/eda")
def eda(): return run_legacy(labs.eda)

@app.get("/api/regression")
def regression(x: str = "Avg_Daily_Usage_Hours"):
    return run_legacy(labs.regression, "Mental_Health_Score", x)

@app.get("/api/tree")
def tree(max_depth: int = 4): return run_legacy(labs.tree, max(1, min(max_depth, 15)))

@app.get("/api/naive-bayes")
def nb(): return run_legacy(labs.naive_bayes)

@app.get("/api/kmeans")
def kmeans(k: int = 3): return run_legacy(labs.kmeans, max(2, min(k, 10)))

@app.get("/api/hierarchical")
def hier(k: int = 3, linkage: str = "ward"): return run_legacy(labs.hierarchical, max(2, min(k, 10)), linkage)

@app.get("/api/apriori")
def apriori(min_support: float = 0.1, min_confidence: float = 0.6):
    return run_legacy(labs.apriori_rules, max(0.01, min(min_support, 1)), max(0.0, min(min_confidence, 1)))

@app.get("/api/schema")
def schema(): return run_legacy(labs.schema)

@app.get("/api/meta")
def meta(): return run_legacy(labs.meta)

@app.get("/api/chart")
def chart(x: str, y: str = "", agg: str = "mean", hue: str = ""):
    return run_legacy(labs.chart, x, y or None, agg, hue or None)

@app.get("/api/cube")
def cube(x: str = "Academic_Level", y: str = "Most_Used_Platform", z: str = "Stress_Level",
         measure: str = "Mental_Health_Score", agg: str = "mean", fdim: str = "none", fval: str = "",
         dice_dims: str = "", dice_vals: str = ""):
    return run_legacy(labs.cube, x, y, z, measure, agg, fdim, fval, dice_dims, dice_vals)

@app.get("/api/olap-explorer")
def olap_explorer(op: str = "Explore", x: str = "Country", y: str = "Most_Used_Platform", z: str = "Stress_Level",
                  measure: str = "Mental_Health_Score", agg: str = "Average", sdim: str = "none", sval: str = "",
                  dice_filters: str = "", across_dim: str = "Academic_Level"):
    return run_legacy(labs.olap_explorer, op, x, y, z, measure, agg, sdim, sval, dice_filters, across_dim)

@app.get("/api/olap2")
def olap2(op: str = "cube", measure: str = "Mental_Health_Score", dims: str = "Academic_Level,Most_Used_Platform"):
    return run_legacy(labs.olap2, op, measure, dims)

@app.get("/api/viz")
def viz(x: str = "Avg_Daily_Usage_Hours", y: str = "Mental_Health_Score", cat: str = "Most_Used_Platform"):
    return run_legacy(labs.viz, x, y, cat)

@app.get("/api/lab4")
def lab4(x: str = "Avg_Daily_Usage_Hours"):
    return run_legacy(labs.regression4, x)

@app.get("/api/tree12")
def tree12(max_depth: int = 5): return run_legacy(labs.tree12, max(1, min(max_depth, 15)))

@app.get("/api/nb12")
def nb12(): return run_legacy(labs.nb12)

@app.get("/api/weka")
def weka(): return run_legacy(labs.weka)


# Static Files Mount: Prefer React build (frontend/dist), fallback to frontend/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
RAW_FRONTEND = PROJECT_ROOT / "frontend"

if DIST_DIR.exists() and (DIST_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")
elif RAW_FRONTEND.exists():
    app.mount("/", StaticFiles(directory=RAW_FRONTEND, html=True), name="static")

