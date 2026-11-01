import pytest
from pathlib import Path
from backend.app.security.authorizer import execute_safe_query, SecurityException, validate_single_statement
from backend.app.db.session import DEFAULT_DB_PATH


def test_select_queries_allowed_ac_20():
    """Verify that legitimate SELECT queries execute cleanly."""
    res = execute_safe_query("SELECT 1 AS val, 'hello' AS msg;", db_path=DEFAULT_DB_PATH)
    assert res["columns"] == ["val", "msg"]
    assert res["rows"] == [[1, "hello"]]
    assert res["row_count"] == 1


def test_single_statement_enforcement_ac_20():
    """Verify multiple semicolon-separated statements are rejected."""
    with pytest.raises(SecurityException, match="Multiple SQL statements"):
        execute_safe_query("SELECT 1; SELECT 2;", db_path=DEFAULT_DB_PATH)


def test_mutation_authorizer_blocked_ac_05_and_ac_20():
    """AC-05 & AC-20: Verify that INSERT, UPDATE, DELETE, DROP are blocked at authorizer level."""
    # INSERT
    with pytest.raises(SecurityException, match="rejected"):
        execute_safe_query(
            "INSERT INTO dim_country (country_name, region) VALUES ('FakeCountry', 'Nowhere');",
            db_path=DEFAULT_DB_PATH
        )

    # UPDATE
    with pytest.raises(SecurityException, match="rejected"):
        execute_safe_query(
            "UPDATE fact_survey_response SET mental_health_score = 10.0 WHERE survey_key = 1;",
            db_path=DEFAULT_DB_PATH
        )

    # DELETE
    with pytest.raises(SecurityException, match="rejected"):
        execute_safe_query(
            "DELETE FROM fact_survey_response WHERE survey_key = 1;",
            db_path=DEFAULT_DB_PATH
        )

    # DROP TABLE
    with pytest.raises(SecurityException, match="rejected"):
        execute_safe_query(
            "DROP TABLE dim_gender;",
            db_path=DEFAULT_DB_PATH
        )

    # PRAGMA
    with pytest.raises(SecurityException, match="rejected"):
        execute_safe_query(
            "PRAGMA user_version = 42;",
            db_path=DEFAULT_DB_PATH
        )


def test_row_clamping_and_limit():
    """Verify limit clamping to maximum 500 rows."""
    res = execute_safe_query(
        "SELECT * FROM v_star_schema_denormalized;",
        db_path=DEFAULT_DB_PATH,
        limit=50
    )
    assert res["row_count"] == 50
    assert res["is_truncated"] is True

