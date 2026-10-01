import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "business.db"

connection = sqlite3.connect(DATABASE_PATH)




print("=" * 60)
print("BASIC DATABASE TESTS")
print("=" * 60)


# 1. Total Revenue
query_total_revenue = """
SELECT
    SUM(revenue) AS total_revenue
FROM orders;
"""

total_revenue = pd.read_sql_query(
    query_total_revenue,
    connection
)

print("\nTOTAL REVENUE")
print(total_revenue)


# 2. Monthly Revenue
query_monthly_revenue = """
SELECT
    strftime('%m', order_date) AS month,
    SUM(revenue) AS revenue
FROM orders
GROUP BY month
ORDER BY month;
"""

monthly_revenue = pd.read_sql_query(
    query_monthly_revenue,
    connection
)

print("\nMONTHLY REVENUE")
print(monthly_revenue)


# 3. Revenue by Category
query_category_revenue = """
SELECT
    category,
    SUM(revenue) AS revenue
FROM orders
GROUP BY category
ORDER BY revenue DESC;
"""

category_revenue = pd.read_sql_query(
    query_category_revenue,
    connection
)

print("\nREVENUE BY CATEGORY")
print(category_revenue)



print("\n" + "=" * 60)
print("FEBRUARY VS MARCH REVENUE")
print("=" * 60)


query_february_march = """
SELECT
    (
        SELECT SUM(revenue)
        FROM orders
        WHERE strftime('%m', order_date) = '02'
    ) AS february_revenue,

    (
        SELECT SUM(revenue)
        FROM orders
        WHERE strftime('%m', order_date) = '03'
    ) AS march_revenue;
"""

february_march = pd.read_sql_query(
    query_february_march,
    connection
)

print("\nFEBRUARY VS MARCH")
print(february_march)


february_revenue = february_march.loc[
    0, "february_revenue"
]

march_revenue = february_march.loc[
    0, "march_revenue"
]

percentage_change = (
    (march_revenue - february_revenue)
    / february_revenue
) * 100

print(
    f"\nRevenue change from February to March: "
    f"{percentage_change:.2f}%"
)



print("\n" + "=" * 60)
print("FEBRUARY VS MARCH BY CATEGORY")
print("=" * 60)


query_category_comparison = """
SELECT
    category,

    SUM(
        CASE
            WHEN strftime('%m', order_date) = '02'
            THEN revenue
            ELSE 0
        END
    ) AS february_revenue,

    SUM(
        CASE
            WHEN strftime('%m', order_date) = '03'
            THEN revenue
            ELSE 0
        END
    ) AS march_revenue

FROM orders

WHERE strftime('%m', order_date)
    IN ('02', '03')

GROUP BY category

ORDER BY
    march_revenue - february_revenue;
"""

category_comparison = pd.read_sql_query(
    query_category_comparison,
    connection
)

category_comparison["revenue_change"] = (
    category_comparison["march_revenue"]
    - category_comparison["february_revenue"]
)

category_comparison["percentage_change"] = (
    category_comparison["revenue_change"]
    / category_comparison["february_revenue"]
) * 100

print("\nCATEGORY COMPARISON")
print(category_comparison)




connection.close()

print("\n" + "=" * 60)
print("ALL DATABASE TESTS COMPLETED")
print("=" * 60)