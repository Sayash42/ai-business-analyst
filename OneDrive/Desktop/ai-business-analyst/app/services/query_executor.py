import sqlite3
from pathlib import Path

import pandas as pd

from app.services.sql_validator import validate_sql


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "business.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create a connection to the SQLite database.
    """

    return sqlite3.connect(
        DATABASE_PATH
    )


# =========================================================
# EXECUTE VALIDATED SQL
# =========================================================

def execute_query(sql):
    """
    Validate and execute a SQL query.

    The query is executed only if it passes
    the SQL validation layer.

    Returns:
        pandas.DataFrame
    """

    # -----------------------------------------------------
    # Validate SQL
    # -----------------------------------------------------

    validation_result = validate_sql(sql)

    if not validation_result["valid"]:

        errors = validation_result["errors"]

        error_message = (
            "SQL validation failed:\n"
            + "\n".join(
                f"- {error}"
                for error in errors
            )
        )

        raise ValueError(
            error_message
        )

    # -----------------------------------------------------
    # Get cleaned SQL
    # -----------------------------------------------------

    cleaned_sql = validation_result["sql"]

    # -----------------------------------------------------
    # Connect to database
    # -----------------------------------------------------

    connection = get_connection()

    try:

        # -------------------------------------------------
        # Execute query
        # -------------------------------------------------

        result = pd.read_sql_query(
            cleaned_sql,
            connection
        )

        return result

    finally:

        connection.close()


# =========================================================
# EXECUTE MULTIPLE QUERIES
# =========================================================

def execute_queries(queries):
    """
    Execute multiple validated SQL queries.

    Args:
        queries: list of dictionaries containing:
            name
            sql

    Returns:
        dictionary containing DataFrames.
    """

    results = {}

    for query in queries:

        name = query["name"]
        sql = query["sql"]

        results[name] = execute_query(
            sql
        )

    return results


# =========================================================
# TEST QUERY EXECUTION
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("QUERY EXECUTOR")
    print("=" * 60)


    # -----------------------------------------------------
    # Test 1: Total Revenue
    # -----------------------------------------------------

    print("\nTOTAL REVENUE")

    total_revenue_sql = """
    SELECT
        SUM(revenue) AS total_revenue
    FROM orders;
    """

    result = execute_query(
        total_revenue_sql
    )

    print(
        result.to_string(
            index=False
        )
    )


    # -----------------------------------------------------
    # Test 2: Revenue by Category
    # -----------------------------------------------------

    print("\nREVENUE BY CATEGORY")

    category_sql = """
    SELECT
        category,
        SUM(revenue) AS revenue
    FROM orders
    GROUP BY category
    ORDER BY revenue DESC;
    """

    result = execute_query(
        category_sql
    )

    print(
        result.to_string(
            index=False
        )
    )


    # -----------------------------------------------------
    # Test 3: Invalid SQL
    # -----------------------------------------------------

    print("\nINVALID SQL TEST")

    invalid_sql = """
    DELETE FROM orders;
    """

    try:

        execute_query(
            invalid_sql
        )

    except ValueError as error:

        print(
            "Query rejected successfully."
        )

        print(
            error
        )


    # -----------------------------------------------------
    # Finished
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("QUERY EXECUTOR TEST COMPLETE")
    print("=" * 60)