import json
import os
import re

from dotenv import load_dotenv

from app.services.sql_validator import validate_sql


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# DATABASE SCHEMA
# ============================================================

DATABASE_SCHEMA = """
DATABASE: SQLite

TABLE: customers
COLUMNS:
    customer_id TEXT PRIMARY KEY
    customer_name TEXT NOT NULL
    region TEXT NOT NULL
    segment TEXT NOT NULL

TABLE: products
COLUMNS:
    product_id TEXT PRIMARY KEY
    product_name TEXT NOT NULL
    category TEXT NOT NULL
    unit_price REAL NOT NULL

TABLE: orders
COLUMNS:
    order_id TEXT PRIMARY KEY
    order_date DATE NOT NULL
    customer_id TEXT NOT NULL
    product_id TEXT NOT NULL
    category TEXT NOT NULL
    quantity INTEGER NOT NULL
    unit_price REAL NOT NULL
    revenue REAL NOT NULL

RELATIONSHIPS:
    orders.customer_id = customers.customer_id
    orders.product_id = products.product_id
"""


# ============================================================
# AI INSTRUCTIONS
# ============================================================

SYSTEM_INSTRUCTIONS = f"""
You are an expert business analyst and SQL generator.

{DATABASE_SCHEMA}

Rules:

1. Generate SQLite-compatible SQL.
2. Only generate read-only SELECT or WITH queries.
3. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
   REPLACE, TRUNCATE, ATTACH, DETACH, or PRAGMA.
4. Use only tables and columns that exist in the schema.
5. Do not invent data.
6. Use meaningful aliases.
7. When calculating revenue, use the revenue column.
8. When comparing months, use:
   strftime('%Y-%m', order_date)
9. Return valid JSON.
"""


RESPONSE_SCHEMA = {
    "queries": [
        {
            "name": "query_name",
            "sql": "SELECT ...",
            "purpose": "Explain the purpose of the query."
        }
    ]
}


# ============================================================
# SQL SAFETY
# ============================================================

FORBIDDEN_SQL_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
]


def clean_sql(sql):
    """Remove Markdown formatting around SQL."""

    if not sql:
        return ""

    sql = sql.strip()

    sql = re.sub(
        r"^```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"^```\s*",
        "",
        sql,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
    )

    return sql.strip()


def basic_sql_safety_check(sql):
    """Perform basic read-only SQL validation."""

    if not sql or not sql.strip():
        raise ValueError("SQL query is empty.")

    sql = clean_sql(sql)

    sql = sql.rstrip(";").strip()

    if not sql:
        raise ValueError("SQL query is empty.")

    if not re.match(
        r"^(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE,
    ):
        raise ValueError(
            "Only SELECT or WITH statements are allowed."
        )

    if ";" in sql:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    upper_sql = sql.upper()

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        if re.search(
            rf"\b{re.escape(keyword)}\b",
            upper_sql,
        ):
            raise ValueError(
                f"Forbidden SQL keyword detected: {keyword}"
            )

    return sql


# ============================================================
# OFFLINE SQL GENERATOR
# ============================================================

def generate_sql_offline(question):
    """
    Generate SQL without an OpenAI API.

    This allows the application to work without API credits.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()
    q = question.lower()

    # --------------------------------------------------------
    # WHY DID REVENUE DROP IN MARCH?
    # --------------------------------------------------------

    if (
        "why did revenue drop" in q
        or "why did revenue fall" in q
        or "why did revenue decline" in q
        or "revenue dropped" in q
        or "revenue fell" in q
        or "revenue decline" in q
        or "revenue decreased" in q
        or (
            "revenue" in q
            and "march" in q
            and (
                "why" in q
                or "drop" in q
                or "fall" in q
                or "decline" in q
                or "decrease" in q
            )
        )
    ):

        return {
            "queries": [
                {
                    "name": "overall_month_comparison",
                    "sql": """
SELECT
    SUM(
        CASE
            WHEN strftime('%Y-%m', order_date) = '2024-02'
            THEN revenue
            ELSE 0
        END
    ) AS february_revenue,

    SUM(
        CASE
            WHEN strftime('%Y-%m', order_date) = '2024-03'
            THEN revenue
            ELSE 0
        END
    ) AS march_revenue

FROM orders

WHERE strftime('%Y-%m', order_date)
IN ('2024-02', '2024-03');
""",
                    "purpose": (
                        "Compare February and March total revenue."
                    ),
                },
                {
                    "name": "category_month_comparison",
                    "sql": """
SELECT
    category,

    SUM(
        CASE
            WHEN strftime('%Y-%m', order_date) = '2024-02'
            THEN revenue
            ELSE 0
        END
    ) AS february_revenue,

    SUM(
        CASE
            WHEN strftime('%Y-%m', order_date) = '2024-03'
            THEN revenue
            ELSE 0
        END
    ) AS march_revenue

FROM orders

WHERE strftime('%Y-%m', order_date)
IN ('2024-02', '2024-03')

GROUP BY category

ORDER BY march_revenue DESC;
""",
                    "purpose": (
                        "Compare February and March revenue by category."
                    ),
                },
                {
                    "name": "customer_month_comparison",
                    "sql": """
SELECT
    customers.customer_id,
    customers.customer_name,

    SUM(
        CASE
            WHEN strftime('%Y-%m', orders.order_date) = '2024-02'
            THEN orders.revenue
            ELSE 0
        END
    ) AS february_revenue,

    SUM(
        CASE
            WHEN strftime('%Y-%m', orders.order_date) = '2024-03'
            THEN orders.revenue
            ELSE 0
        END
    ) AS march_revenue

FROM orders

JOIN customers
    ON orders.customer_id = customers.customer_id

WHERE strftime('%Y-%m', orders.order_date)
IN ('2024-02', '2024-03')

GROUP BY
    customers.customer_id,
    customers.customer_name

ORDER BY march_revenue DESC;
""",
                    "purpose": (
                        "Compare February and March revenue by customer."
                    ),
                },
                {
                    "name": "region_month_comparison",
                    "sql": """
SELECT
    customers.region,

    SUM(
        CASE
            WHEN strftime('%Y-%m', orders.order_date) = '2024-02'
            THEN orders.revenue
            ELSE 0
        END
    ) AS february_revenue,

    SUM(
        CASE
            WHEN strftime('%Y-%m', orders.order_date) = '2024-03'
            THEN orders.revenue
            ELSE 0
        END
    ) AS march_revenue

FROM orders

JOIN customers
    ON orders.customer_id = customers.customer_id

WHERE strftime('%Y-%m', orders.order_date)
IN ('2024-02', '2024-03')

GROUP BY customers.region

ORDER BY march_revenue DESC;
""",
                    "purpose": (
                        "Compare February and March revenue by region."
                    ),
                },
            ]
        }

    # --------------------------------------------------------
    # REVENUE BY CATEGORY
    # --------------------------------------------------------

    if (
        "revenue by category" in q
        or "revenue per category" in q
        or "category revenue" in q
    ):

        return {
            "queries": [
                {
                    "name": "revenue_by_category",
                    "sql": """
SELECT
    category,
    SUM(revenue) AS total_revenue
FROM orders
GROUP BY category
ORDER BY total_revenue DESC;
""",
                    "purpose": "Show revenue by category.",
                }
            ]
        }

    # --------------------------------------------------------
    # REVENUE BY REGION
    # --------------------------------------------------------

    if (
        "revenue by region" in q
        or "revenue per region" in q
        or "region revenue" in q
    ):

        return {
            "queries": [
                {
                    "name": "revenue_by_region",
                    "sql": """
SELECT
    customers.region,
    SUM(orders.revenue) AS total_revenue
FROM orders
JOIN customers
    ON orders.customer_id = customers.customer_id
GROUP BY customers.region
ORDER BY total_revenue DESC;
""",
                    "purpose": "Show revenue by region.",
                }
            ]
        }

    # --------------------------------------------------------
    # REVENUE BY CUSTOMER
    # --------------------------------------------------------

    if (
        "revenue by customer" in q
        or "revenue per customer" in q
        or "customer revenue" in q
    ):

        return {
            "queries": [
                {
                    "name": "revenue_by_customer",
                    "sql": """
SELECT
    customers.customer_id,
    customers.customer_name,
    SUM(orders.revenue) AS total_revenue
FROM orders
JOIN customers
    ON orders.customer_id = customers.customer_id
GROUP BY
    customers.customer_id,
    customers.customer_name
ORDER BY total_revenue DESC;
""",
                    "purpose": "Show revenue by customer.",
                }
            ]
        }

    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------

    if (
        "monthly revenue" in q
        or "revenue by month" in q
        or "revenue each month" in q
        or "revenue over time" in q
        or "revenue trend" in q
    ):

        return {
            "queries": [
                {
                    "name": "monthly_revenue",
                    "sql": """
SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(revenue) AS total_revenue
FROM orders
GROUP BY month
ORDER BY month;
""",
                    "purpose": "Show monthly revenue.",
                }
            ]
        }

    # --------------------------------------------------------
    # TOTAL REVENUE
    # --------------------------------------------------------

    if (
        "total revenue" in q
        or "overall revenue" in q
        or "how much revenue" in q
        or q == "revenue"
    ):

        return {
            "queries": [
                {
                    "name": "total_revenue",
                    "sql": """
SELECT
    SUM(revenue) AS total_revenue
FROM orders;
""",
                    "purpose": "Calculate total revenue.",
                }
            ]
        }

    # --------------------------------------------------------
    # QUANTITY BY CATEGORY
    # --------------------------------------------------------

    if (
        "quantity by category" in q
        or "units by category" in q
        or "units sold by category" in q
    ):

        return {
            "queries": [
                {
                    "name": "quantity_by_category",
                    "sql": """
SELECT
    category,
    SUM(quantity) AS total_quantity
FROM orders
GROUP BY category
ORDER BY total_quantity DESC;
""",
                    "purpose": "Show units sold by category.",
                }
            ]
        }

    # --------------------------------------------------------
    # AVERAGE ORDER VALUE
    # --------------------------------------------------------

    if (
        "average order value" in q
        or "aov" in q
        or "average order" in q
    ):

        return {
            "queries": [
                {
                    "name": "average_order_value",
                    "sql": """
SELECT
    AVG(order_revenue) AS average_order_value
FROM (
    SELECT
        order_id,
        SUM(revenue) AS order_revenue
    FROM orders
    GROUP BY order_id
);
""",
                    "purpose": "Calculate average order value.",
                }
            ]
        }

    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    if (
        "top products" in q
        or "best products" in q
        or "highest revenue products" in q
        or "top product" in q
    ):

        return {
            "queries": [
                {
                    "name": "top_products",
                    "sql": """
SELECT
    products.product_id,
    products.product_name,
    products.category,
    SUM(orders.revenue) AS total_revenue

FROM orders

JOIN products
    ON orders.product_id = products.product_id

GROUP BY
    products.product_id,
    products.product_name,
    products.category

ORDER BY total_revenue DESC

LIMIT 10;
""",
                    "purpose": "Show top 10 products by revenue.",
                }
            ]
        }

    raise ValueError(
        "Offline SQL generation does not understand this question.\n\n"
        f"Question: {question}\n\n"
        "Try one of these:\n"
        "- Why did revenue drop in March?\n"
        "- Show monthly revenue.\n"
        "- Show revenue by category.\n"
        "- Show revenue by region.\n"
        "- Show revenue by customer.\n"
        "- What is total revenue?\n"
        "- What is the average order value?\n"
        "- Show the top products."
    )


# ============================================================
# OPENAI SQL GENERATOR
# ============================================================

def generate_sql_openai(question):
    """
    Generate SQL using OpenAI when an API key is available.
    """

    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(api_key=api_key)

    prompt = f"""
Business question:

{question}

Generate safe, read-only SQLite SQL.

Return JSON using this structure:

{json.dumps(RESPONSE_SCHEMA, indent=2)}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    output_text = response.output_text.strip()

    if not output_text:
        raise ValueError(
            "OpenAI returned an empty response."
        )

    output_text = re.sub(
        r"^```json\s*",
        "",
        output_text,
        flags=re.IGNORECASE,
    )

    output_text = re.sub(
        r"^```\s*",
        "",
        output_text,
    )

    output_text = re.sub(
        r"\s*```$",
        "",
        output_text,
    )

    try:
        result = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "OpenAI returned invalid JSON."
        ) from error

    if not isinstance(result, dict):
        raise ValueError(
            "OpenAI response must be a JSON object."
        )

    queries = result.get("queries")

    if not isinstance(queries, list) or not queries:
        raise ValueError(
            "OpenAI response does not contain queries."
        )

    validated_queries = []

    for query in queries:

        if not isinstance(query, dict):
            raise ValueError(
                "Each query must be an object."
            )

        name = query.get(
            "name",
            "generated_query",
        )

        sql = query.get("sql")

        purpose = query.get(
            "purpose",
            "",
        )

        if not sql:
            raise ValueError(
                f"Query '{name}' has no SQL."
            )

        sql = basic_sql_safety_check(sql)

        validate_sql(sql)

        validated_queries.append(
            {
                "name": name,
                "sql": sql,
                "purpose": purpose,
            }
        )

    return {
        "queries": validated_queries
    }


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def generate_sql(question):
    """
    Main SQL generation function.

    OpenAI is attempted only when an API key exists.
    If OpenAI is unavailable, the offline generator is used.

    No print statements are used here.
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()

    api_key = os.getenv("OPENAI_API_KEY")

    # Try OpenAI if available.
    if api_key:

        try:

            result = generate_sql_openai(question)

            for query in result["queries"]:

                sql = basic_sql_safety_check(
                    query["sql"]
                )

                validate_sql(sql)

                query["sql"] = sql

            return result

        except Exception:
            # Fall back to offline generation.
            pass

    # Offline generation.
    result = generate_sql_offline(question)

    # Validate offline queries.
    for query in result["queries"]:

        sql = basic_sql_safety_check(
            query["sql"]
        )

        validate_sql(sql)

        query["sql"] = sql

    return result