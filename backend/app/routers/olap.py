from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.olap.query_generator import OLAPQueryGenerator
from backend.app.services.olap.executor import OLAPExecutor
from backend.app.schemas.olap import OLAPResponse

router = APIRouter(prefix="/olap", tags=["OLAP"])


@router.get("/execute", response_model=OLAPResponse)
def execute_olap(
    op: str = Query("Roll-up", description="OLAP operation name"),
    x: str = Query("academic_level", description="Primary dimension"),
    y: str = Query("platform", description="Secondary dimension"),
    z: Optional[str] = Query(None, description="Tertiary dimension"),
    measure: str = Query("mental_health_score", description="Target measure"),
    agg: str = Query("AVG", description="Aggregation function"),
    slice_dim: Optional[str] = Query(None),
    slice_val: Optional[str] = Query(None),
    dice_filters: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Executes parameterized SQL OLAP operations and returns formatted results with visual chart data."""
    op_clean = op.lower().replace("-", "").replace("_", "").replace(" ", "")

    try:
        if op_clean in ["rollup", "explore"]:
            sql, params = OLAPQueryGenerator.build_rollup(dim1=x, dim2=y, measure=measure, agg=agg)
            explanation = f"Roll-up aggregates upward from detailed {y} to {x} summary and Grand Total using multi-tier SQL aggregation."
        elif op_clean in ["drilldown"]:
            dims = [x, y]
            if z:
                dims.append(z)
            sql, params = OLAPQueryGenerator.build_drilldown(dims=dims, measure=measure, agg=agg)
            explanation = f"Drill-down expands aggregation granularity across {', '.join(dims)}."
        elif op_clean in ["slice"]:
            s_dim = slice_dim or "country"
            s_val = slice_val or "India"
            sql, params = OLAPQueryGenerator.build_slice(slice_dim=s_dim, slice_val=s_val, group_dims=[x, y], measure=measure, agg=agg)
            explanation = f"Slice fixes {s_dim} = '{s_val}' and aggregates over remaining axes ({x}, {y})."
        elif op_clean in ["dice"]:
            # Default dice filters if none supplied
            parsed_filters = {
                "academic_level": ["Undergraduate", "Graduate"],
                "platform": ["Instagram", "YouTube", "TikTok"]
            }
            if dice_filters:
                # Format: "dim1:val1,val2|dim2:val3,val4"
                parsed_filters = {}
                for part in dice_filters.split("|"):
                    if ":" in part:
                        d, vals = part.split(":", 1)
                        parsed_filters[d.strip()] = [v.strip() for v in vals.split(",")]

            sql, params = OLAPQueryGenerator.build_dice(dice_filters=parsed_filters, select_dims=[x, y], measure=measure, agg=agg)
            explanation = f"Dice isolates a sub-cube restricted across multiple specified attribute dimensions."
        elif op_clean in ["pivot"]:
            # Cross-tabulate x against stress_level or y
            col_dim = y if y != x else "stress_level"
            col_vals = ["Low", "Medium", "High", "Very High"] if col_dim == "stress_level" else ["Instagram", "YouTube", "TikTok", "Facebook"]
            sql, params = OLAPQueryGenerator.build_pivot(row_dim=x, col_dim=col_dim, col_values=col_vals, measure=measure, agg=agg)
            explanation = f"Pivot rotates {col_dim} into column headers via SQL CASE WHEN conditional aggregation, guaranteeing zero NaN values."
        elif op_clean in ["drillacross", "across"]:
            sql, params = OLAPQueryGenerator.build_drill_across()
            explanation = "Drill-across aggregates Fact_Usage and Fact_Lifestyle independently at the conformed academic dimension, then joins them side-by-side."
        elif op_clean in ["cube"]:
            sql, params = OLAPQueryGenerator.build_cube(dim1=x, dim2=y, measure=measure, agg=agg)
            explanation = f"CUBE generates all 2^2 = 4 grouping subsets of ({x}, {y}) via UNION ALL."
        elif op_clean in ["groupingsets", "groupingset"]:
            sql, params = OLAPQueryGenerator.build_grouping_sets(dims=[x, y], measure=measure, agg=agg)
            explanation = f"GROUPING SETS computes individual dimensional totals and grand totals without all combinatorial cross-products."
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported OLAP operation '{op}'.")

        res = OLAPExecutor.execute(db, sql, params, operation=op)
        columns = res["columns"]
        data = res["data"]

        # Build chart projection
        labels = [str(r.get(columns[0], "")) for r in data[:15]]
        val_col = next((c for c in columns if c in ["agg_value", "agg_val", "students", "low_stress_avg_score", "avg_screen_hours"]), columns[-1])
        values = [r.get(val_col, 0) for r in data[:15]]
        chart = {
            "labels": labels,
            "series": [{"name": val_col, "values": values}]
        }

        # Convert dict rows to ordered list of lists
        table_rows = [[r.get(c) for c in columns] for r in data]

        return OLAPResponse(
            op=op,
            generated_sql=res["sql_query"],
            columns=columns,
            rows=table_rows,
            execution_time_ms=res["execution_time_ms"],
            chart=chart,
            explanation=explanation
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

