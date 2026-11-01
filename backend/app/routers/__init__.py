from .dashboard import router as dashboard_router
from .warehouse import router as warehouse_router
from .olap import router as olap_router
from .predict import router as predict_router
from .analytics import router as analytics_router
from .etl import router as etl_router
from .labs import router as labs_router

__all__ = [
    "dashboard_router",
    "warehouse_router",
    "olap_router",
    "predict_router",
    "analytics_router",
    "etl_router",
    "labs_router"
]

