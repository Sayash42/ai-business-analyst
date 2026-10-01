import re


# =========================================================
# SQL VALIDATOR
# =========================================================


# Tables that our Business Analyst is allowed to access.
ALLOWED_TABLES = {
    "orders",
    "customers",
    "products"
}


# SQL commands that are not allowed.
FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "detach",
    "pragma",
    "vacuum",
    "reindex"
}


# =========================================================
# CLEAN SQL
# =========================================================

def clean_sql(sql):
    """
    Clean whitespace and remove unnecessary
    whitespace at the beginning and end.
    """

    if not isinstance(sql, str):
        return ""

    sql = sql.strip()

    sql = re.sub(
        r"\s+",
        " ",
        sql
    )

    return sql


# =========================================================
# CHECK EMPTY SQL
# =========================================================

def check_not_empty(sql):
    """
    Make sure SQL was actually provided.
    """

    if not sql:
        return False, "SQL query is empty."

    return True, None


# =========================================================
# CHECK SELECT ONLY
# =========================================================

def check_select_only(sql):
    """
    Only SELECT statements are allowed.
    """

    normalized_sql = sql.strip().lower()

    if not normalized_sql.startswith("select"):
        return (
            False,
            "Only SELECT statements are allowed."
        )

    return True, None


# =========================================================
# CHECK MULTIPLE STATEMENTS
# =========================================================

def check_single_statement(sql):
    """
    Prevent multiple SQL statements from being
    submitted at once.
    """

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:
        return (
            False,
            "Multiple SQL statements are not allowed."
        )

    return True, None


# =========================================================
# CHECK FORBIDDEN KEYWORDS
# =========================================================

def check_forbidden_keywords(sql):
    """
    Reject SQL commands that can modify the database.
    """

    normalized_sql = sql.lower()

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(
            pattern,
            normalized_sql
        ):
            return (
                False,
                f"Forbidden SQL keyword detected: "
                f"{keyword.upper()}"
            )

    return True, None


# =========================================================
# CHECK SQL COMMENTS
# =========================================================

def check_comments(sql):
    """
    Reject SQL comments.

    Comments are unnecessary for our generated SQL
    and removing them makes validation simpler.
    """

    if "--" in sql:
        return (
            False,
            "SQL comments are not allowed."
        )

    if "/*" in sql or "*/" in sql:
        return (
            False,
            "SQL block comments are not allowed."
        )

    return True, None


# =========================================================
# FIND TABLES
# =========================================================

def find_tables(sql):
    """
    Find table names used after FROM and JOIN.
    """

    matches = re.findall(
        r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
        sql,
        flags=re.IGNORECASE
    )

    return {
        table.lower()
        for table in matches
    }


# =========================================================
# CHECK ALLOWED TABLES
# =========================================================

def check_allowed_tables(sql):
    """
    Make sure only approved database tables are used.
    """

    tables = find_tables(sql)

    unauthorized_tables = (
        tables - ALLOWED_TABLES
    )

    if unauthorized_tables:

        table_list = ", ".join(
            sorted(unauthorized_tables)
        )

        return (
            False,
            "Unauthorized table(s): "
            + table_list
        )

    return True, None


# =========================================================
# CHECK BASIC SQL STRUCTURE
# =========================================================

def check_basic_structure(sql):
    """
    Perform a few basic checks on the SQL structure.
    """

    normalized_sql = sql.strip().lower()

    if "from" not in normalized_sql:

        return (
            False,
            "SQL query must contain a FROM clause."
        )

    return True, None


# =========================================================
# MAIN VALIDATOR
# =========================================================

def validate_sql(sql):
    """
    Validate a SQL query.

    Returns:
        {
            "valid": True/False,
            "sql": cleaned_sql,
            "errors": [...]
        }
    """

    cleaned_sql = clean_sql(sql)

    errors = []

    checks = [
        check_not_empty,
        check_select_only,
        check_single_statement,
        check_forbidden_keywords,
        check_comments,
        check_allowed_tables,
        check_basic_structure
    ]

    for check in checks:

        valid, error = check(
            cleaned_sql
        )

        if not valid:
            errors.append(error)

    return {
        "valid": len(errors) == 0,
        "sql": cleaned_sql,
        "errors": errors
    }


# =========================================================
# TEST VALID QUERIES
# =========================================================

if __name__ == "__main__":

    valid_queries = [

        """
        SELECT
            SUM(revenue) AS total_revenue
        FROM orders;
        """,

        """
        SELECT
            category,
            SUM(revenue) AS revenue
        FROM orders
        GROUP BY category
        ORDER BY revenue DESC;
        """,

        """
        SELECT
            c.region,
            SUM(o.revenue) AS revenue
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        GROUP BY c.region;
        """
    ]


    invalid_queries = [

        """
        DELETE FROM orders;
        """,

        """
        UPDATE orders
        SET revenue = 0;
        """,

        """
        DROP TABLE orders;
        """,

        """
        INSERT INTO orders
        VALUES ('TEST');
        """,

        """
        SELECT *
        FROM employees;
        """,

        """
        SELECT *
        FROM orders;

        DELETE FROM orders;
        """,

        """
        SELECT *
        FROM orders
        -- delete everything
        ;
        """
    ]


    print("=" * 60)
    print("SQL VALIDATOR TEST")
    print("=" * 60)


    # -----------------------------------------------------
    # VALID QUERY TESTS
    # -----------------------------------------------------

    print("\nVALID QUERIES")
    print("-" * 60)

    for number, query in enumerate(
        valid_queries,
        start=1
    ):

        result = validate_sql(query)

        print(
            f"\nQuery {number}"
        )

        print(
            f"Valid: {result['valid']}"
        )

        if result["errors"]:

            print(
                "Errors:"
            )

            for error in result["errors"]:

                print(
                    f"- {error}"
                )


    # -----------------------------------------------------
    # INVALID QUERY TESTS
    # -----------------------------------------------------

    print("\nINVALID QUERIES")
    print("-" * 60)

    for number, query in enumerate(
        invalid_queries,
        start=1
    ):

        result = validate_sql(query)

        print(
            f"\nQuery {number}"
        )

        print(
            f"Valid: {result['valid']}"
        )

        if result["errors"]:

            print(
                "Errors:"
            )

            for error in result["errors"]:

                print(
                    f"- {error}"
                )


    print("\n" + "=" * 60)
    print("VALIDATOR TEST COMPLETE")
    print("=" * 60)