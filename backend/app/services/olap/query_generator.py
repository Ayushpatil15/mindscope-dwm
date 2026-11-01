from typing import List, Dict, Any, Tuple, Optional


ALLOWED_DIMENSIONS = {
    "academic_level": "academic_level",
    "platform": "platform",
    "most_used_platform": "platform",
    "country": "country",
    "gender": "gender",
    "purpose": "purpose",
    "purpose_of_use": "purpose",
    "stress_level": "stress_level",
    "age": "age",
}

ALLOWED_MEASURES = {
    "mental_health_score": "mental_health_score",
    "avg_daily_usage_hours": "avg_daily_usage_hours",
    "daily_unlocks": "daily_unlocks",
    "study_hours": "study_hours",
    "physical_activity_hours": "physical_activity_hours",
    "sleep_hours_per_night": "sleep_hours_per_night",
}

ALLOWED_AGGS = {
    "AVG": "AVG",
    "COUNT": "COUNT",
    "SUM": "SUM",
    "MIN": "MIN",
    "MAX": "MAX",
}


def sanitize_dim(dim: str) -> str:
    key = dim.lower().strip()
    if key not in ALLOWED_DIMENSIONS:
        raise ValueError(f"Invalid dimension '{dim}'. Allowed: {list(ALLOWED_DIMENSIONS.keys())}")
    return ALLOWED_DIMENSIONS[key]


def sanitize_measure(m: str) -> str:
    key = m.lower().strip()
    if key not in ALLOWED_MEASURES:
        raise ValueError(f"Invalid measure '{m}'. Allowed: {list(ALLOWED_MEASURES.keys())}")
    return ALLOWED_MEASURES[key]


def sanitize_agg(agg: str) -> str:
    key = agg.upper().strip()
    if key not in ALLOWED_AGGS:
        raise ValueError(f"Invalid aggregation '{agg}'. Allowed: {list(ALLOWED_AGGS.keys())}")
    return ALLOWED_AGGS[key]


class OLAPQueryGenerator:
    """Generates parameterized SQL queries for the 8 analytical OLAP operations."""

    @staticmethod
    def build_rollup(
        dim1: str = "academic_level",
        dim2: str = "platform",
        measure: str = "mental_health_score",
        agg: str = "AVG"
    ) -> Tuple[str, Dict[str, Any]]:
        d1 = sanitize_dim(dim1)
        d2 = sanitize_dim(dim2)
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)

        sql = f"""
        SELECT 
            {d1} AS {d1},
            {d2} AS {d2},
            COUNT(*) AS students,
            ROUND({ag}({m}), 2) AS agg_value,
            0 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {d1}, {d2}
        
        UNION ALL
        
        SELECT 
            {d1} AS {d1},
            '(All)' AS {d2},
            COUNT(*) AS students,
            ROUND({ag}({m}), 2) AS agg_value,
            1 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {d1}
        
        UNION ALL
        
        SELECT 
            '(All)' AS {d1},
            '(All)' AS {d2},
            COUNT(*) AS students,
            ROUND({ag}({m}), 2) AS agg_value,
            3 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1);
        """
        return sql.strip(), {}

    @staticmethod
    def build_drilldown(
        dims: List[str],
        measure: str = "mental_health_score",
        agg: str = "AVG",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> Tuple[str, Dict[str, Any]]:
        safe_dims = [sanitize_dim(d) for d in dims]
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)

        where_clauses = ["version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)"]
        params: Dict[str, Any] = {}

        if filters:
            for idx, (k, v) in enumerate(filters.items()):
                sk = sanitize_dim(k)
                param_name = f"filter_{idx}"
                if isinstance(v, (list, tuple)):
                    placeholders = [f":p_{idx}_{j}" for j in range(len(v))]
                    where_clauses.append(f"{sk} IN ({', '.join(placeholders)})")
                    for j, item in enumerate(v):
                        params[f"p_{idx}_{j}"] = item
                else:
                    where_clauses.append(f"{sk} = :{param_name}")
                    params[param_name] = v

        dim_cols = ", ".join(safe_dims)
        where_stmt = " AND ".join(where_clauses)

        sql = f"""
        SELECT 
            {dim_cols},
            COUNT(*) AS students,
            ROUND({ag}({m}), 2) AS agg_value
        FROM v_star_schema_denormalized
        WHERE {where_stmt}
        GROUP BY {dim_cols}
        ORDER BY students DESC
        LIMIT {int(limit)};
        """
        return sql.strip(), params

    @staticmethod
    def build_slice(
        slice_dim: str,
        slice_val: Any,
        group_dims: List[str],
        measure: str = "mental_health_score",
        agg: str = "AVG"
    ) -> Tuple[str, Dict[str, Any]]:
        s_dim = sanitize_dim(slice_dim)
        g_dims = [sanitize_dim(d) for d in group_dims]
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)

        dim_cols = ", ".join(g_dims)
        params = {"slice_val": slice_val}

        sql = f"""
        SELECT 
            {dim_cols},
            COUNT(*) AS students,
            ROUND({ag}({m}), 2) AS agg_value
        FROM v_star_schema_denormalized
        WHERE {s_dim} = :slice_val
          AND version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {dim_cols}
        ORDER BY students DESC;
        """
        return sql.strip(), params

    @staticmethod
    def build_dice(
        dice_filters: Dict[str, List[Any]],
        select_dims: List[str],
        measure: str = "mental_health_score",
        agg: str = "AVG"
    ) -> Tuple[str, Dict[str, Any]]:
        s_dims = [sanitize_dim(d) for d in select_dims]
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)

        where_clauses = ["version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)"]
        params: Dict[str, Any] = {}

        for idx, (dim, vals) in enumerate(dice_filters.items()):
            s_d = sanitize_dim(dim)
            placeholders = []
            for j, val in enumerate(vals):
                p_name = f"dice_{idx}_{j}"
                placeholders.append(f":{p_name}")
                params[p_name] = val
            where_clauses.append(f"{s_d} IN ({', '.join(placeholders)})")

        dim_cols = ", ".join(s_dims)
        where_stmt = " AND ".join(where_clauses)

        sql = f"""
        SELECT 
            {dim_cols},
            COUNT(*) AS students,
            ROUND({ag}({m}), 2) AS agg_value
        FROM v_star_schema_denormalized
        WHERE {where_stmt}
        GROUP BY {dim_cols}
        ORDER BY students DESC;
        """
        return sql.strip(), params

    @staticmethod
    def build_pivot(
        row_dim: str,
        col_dim: str,
        col_values: List[str],
        measure: str = "mental_health_score",
        agg: str = "AVG"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Cross-tabulation via SQL conditional aggregation.
        Replaces Pandas pivot_table to guarantee NO NaN values are ever produced!
        """
        r_dim = sanitize_dim(row_dim)
        c_dim = sanitize_dim(col_dim)
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)

        case_expressions = []
        params: Dict[str, Any] = {}

        for idx, val in enumerate(col_values):
            clean_alias = val.replace(" ", "_").replace("-", "_").lower()
            p_name = f"col_{idx}"
            params[p_name] = val
            case_expressions.append(
                f"ROUND({ag}(CASE WHEN {c_dim} = :{p_name} THEN {m} END), 2) AS {clean_alias}_val"
            )

        cases_sql = ",\n            ".join(case_expressions)

        sql = f"""
        SELECT 
            {r_dim},
            {cases_sql},
            COUNT(*) AS total_students
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {r_dim}
        ORDER BY {r_dim} ASC;
        """
        return sql.strip(), params

    @staticmethod
    def build_drill_across() -> Tuple[str, Dict[str, Any]]:
        """
        Aggregates metrics from both fact tables joined across their shared conformed academic dimension.
        """
        sql = """
        WITH fact1_usage AS (
            SELECT 
                a.academic_key,
                COUNT(*) AS students,
                ROUND(AVG(f.avg_daily_usage_hours), 2) AS avg_screen_hours,
                ROUND(AVG(f.daily_unlocks), 1) AS avg_unlocks,
                ROUND(AVG(f.mental_health_score), 2) AS avg_score
            FROM fact_survey_response f
            JOIN dim_academic a ON f.academic_key = a.academic_key
            WHERE f.version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
            GROUP BY a.academic_key
        ),
        fact2_lifestyle AS (
            SELECT 
                l.academic_key,
                ROUND(AVG(l.study_hours), 2) AS avg_study_hours,
                ROUND(AVG(l.physical_activity_hours), 2) AS avg_activity_hours,
                ROUND(AVG(l.sleep_hours_per_night), 2) AS avg_sleep_hours
            FROM fact_lifestyle l
            WHERE l.version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
            GROUP BY l.academic_key
        )
        SELECT 
            a.academic_level,
            u.students,
            u.avg_screen_hours,
            u.avg_unlocks,
            l.avg_sleep_hours,
            l.avg_study_hours,
            l.avg_activity_hours,
            u.avg_score
        FROM fact1_usage u
        JOIN fact2_lifestyle l ON u.academic_key = l.academic_key
        JOIN dim_academic a ON u.academic_key = a.academic_key
        ORDER BY u.students DESC;
        """
        return sql.strip(), {}

    @staticmethod
    def build_cube(
        dim1: str = "academic_level",
        dim2: str = "platform",
        measure: str = "mental_health_score",
        agg: str = "AVG"
    ) -> Tuple[str, Dict[str, Any]]:
        d1 = sanitize_dim(dim1)
        d2 = sanitize_dim(dim2)
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)

        sql = f"""
        SELECT {d1} AS {d1}, {d2} AS {d2}, COUNT(*) AS students, ROUND({ag}({m}), 2) AS agg_val, 0 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {d1}, {d2}

        UNION ALL

        SELECT {d1} AS {d1}, '(All)' AS {d2}, COUNT(*) AS students, ROUND({ag}({m}), 2) AS agg_val, 1 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {d1}

        UNION ALL

        SELECT '(All)' AS {d1}, {d2} AS {d2}, COUNT(*) AS students, ROUND({ag}({m}), 2) AS agg_val, 2 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        GROUP BY {d2}

        UNION ALL

        SELECT '(All)' AS {d1}, '(All)' AS {d2}, COUNT(*) AS students, ROUND({ag}({m}), 2) AS agg_val, 3 AS grouping_id
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1);
        """
        return sql.strip(), {}

    @staticmethod
    def build_grouping_sets(
        dims: List[str],
        measure: str = "mental_health_score",
        agg: str = "AVG"
    ) -> Tuple[str, Dict[str, Any]]:
        m = sanitize_measure(measure)
        ag = sanitize_agg(agg)
        safe_dims = [sanitize_dim(d) for d in dims]

        union_queries = []
        for d in safe_dims:
            label = d.replace("_", " ").title()
            q = f"""
            SELECT {d} AS dimension_value, '{label}' AS dimension_type, COUNT(*) AS students, ROUND({ag}({m}), 2) AS agg_val
            FROM v_star_schema_denormalized
            WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
            GROUP BY {d}
            """
            union_queries.append(q.strip())

        grand_total = f"""
        SELECT '(Grand Total)' AS dimension_value, 'All' AS dimension_type, COUNT(*) AS students, ROUND({ag}({m}), 2) AS agg_val
        FROM v_star_schema_denormalized
        WHERE version_id IN (SELECT version_id FROM dataset_versions WHERE is_active = 1)
        """
        union_queries.append(grand_total.strip())

        sql = "\n\nUNION ALL\n\n".join(union_queries) + ";"
        return sql, {}
