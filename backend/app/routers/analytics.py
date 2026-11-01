from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
import backend.labs as labs

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/clusters")
def get_clusters(k: int = Query(3, ge=2, le=8)):
    """Runs K-Means clustering across student behavioral attributes (Lab 7)."""
    try:
        return labs.kmeans(k=k)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Clustering failed: {str(exc)}")


@router.get("/associations")
def get_associations(
    min_support: float = Query(0.1, ge=0.01, le=1.0),
    min_confidence: float = Query(0.6, ge=0.1, le=1.0),
    top: int = Query(25, ge=1, le=100)
):
    """Computes Apriori association rules among student social media behaviors (Lab 8)."""
    try:
        return labs.apriori_rules(min_support=min_support, min_confidence=min_confidence, top=top)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Association rule mining failed: {str(exc)}")


@router.get("/regression")
def get_regression_analysis(x: str = Query("Avg_Daily_Usage_Hours")):
    """Compares Simple, Multiple, and Random Forest Regression against Mental Health Score (Lab 4)."""
    try:
        return labs.regression4(x=x)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Regression analysis failed: {str(exc)}")


@router.get("/classifiers")
def get_classifiers_comparison():
    """Compares Decision Tree, Naive Bayes, and Random Forest classifiers (Lab 6)."""
    try:
        return labs.classifier_comparison()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Classifier comparison failed: {str(exc)}")

