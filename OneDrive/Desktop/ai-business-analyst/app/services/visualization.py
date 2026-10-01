import plotly.express as px
import pandas as pd


# =========================================================
# VISUALIZATION ENGINE
# =========================================================


# ---------------------------------------------------------
# MONTHLY REVENUE TREND
# ---------------------------------------------------------

def create_monthly_revenue_chart(data):
    """
    Create a line chart showing monthly revenue.

    Expected columns:

        month
        revenue
    """

    chart_data = data.copy()

    chart_data["month"] = (
        chart_data["month"]
        .astype(str)
    )

    fig = px.line(
        chart_data,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend",
        labels={
            "month": "Month",
            "revenue": "Revenue"
        }
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified"
    )

    return fig


# ---------------------------------------------------------
# FEBRUARY VS MARCH
# ---------------------------------------------------------

def create_month_comparison_chart(data):
    """
    Create a bar chart comparing February
    and March revenue.

    Expected columns:

        february_revenue
        march_revenue
    """

    february_revenue = float(
        data.loc[
            0,
            "february_revenue"
        ]
    )

    march_revenue = float(
        data.loc[
            0,
            "march_revenue"
        ]
    )

    chart_data = pd.DataFrame({
        "Month": [
            "February",
            "March"
        ],
        "Revenue": [
            february_revenue,
            march_revenue
        ]
    })

    fig = px.bar(
        chart_data,
        x="Month",
        y="Revenue",
        title="February vs March Revenue",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue"
    )

    return fig


# ---------------------------------------------------------
# CATEGORY REVENUE CHANGE
# ---------------------------------------------------------

def create_category_change_chart(data):
    """
    Create a bar chart showing revenue change
    by category.

    Expected columns:

        category
        revenue_change
    """

    chart_data = data.copy()

    chart_data = chart_data.sort_values(
        "revenue_change"
    )

    fig = px.bar(
        chart_data,
        x="revenue_change",
        y="category",
        orientation="h",
        title="Revenue Change by Category",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Revenue Change",
        yaxis_title="Category"
    )

    return fig


# ---------------------------------------------------------
# CATEGORY CONTRIBUTION
# ---------------------------------------------------------

def create_category_contribution_chart(data):
    """
    Create a chart showing how much each category
    contributed to the overall decline.

    Expected columns:

        category
        contribution_to_decline
    """

    chart_data = data[
        data["contribution_to_decline"] > 0
    ].copy()

    chart_data = chart_data.sort_values(
        "contribution_to_decline",
        ascending=True
    )

    fig = px.bar(
        chart_data,
        x="contribution_to_decline",
        y="category",
        orientation="h",
        title="Category Contribution to Revenue Decline",
        text_auto=".1f"
    )

    fig.update_layout(
        xaxis_title="Contribution to Decline (%)",
        yaxis_title="Category"
    )

    return fig


# ---------------------------------------------------------
# CUSTOMER REVENUE CHANGE
# ---------------------------------------------------------

def create_customer_change_chart(
    data,
    number=10
):
    """
    Create a chart showing the largest
    customer revenue declines.

    Expected columns:

        customer_id
        revenue_change
    """

    chart_data = data[
        data["revenue_change"] < 0
    ].copy()

    chart_data = (
        chart_data
        .sort_values(
            "revenue_change"
        )
        .head(number)
    )

    chart_data = chart_data.sort_values(
        "revenue_change",
        ascending=True
    )

    fig = px.bar(
        chart_data,
        x="revenue_change",
        y="customer_id",
        orientation="h",
        title="Top Customer Revenue Declines",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Revenue Change",
        yaxis_title="Customer"
    )

    return fig


# ---------------------------------------------------------
# REGION REVENUE CHANGE
# ---------------------------------------------------------

def create_region_change_chart(data):
    """
    Create a chart showing revenue change
    by region.

    Expected columns:

        region
        revenue_change
    """

    chart_data = data.copy()

    chart_data = chart_data.sort_values(
        "revenue_change"
    )

    fig = px.bar(
        chart_data,
        x="revenue_change",
        y="region",
        orientation="h",
        title="Revenue Change by Region",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Revenue Change",
        yaxis_title="Region"
    )

    return fig


# ---------------------------------------------------------
# CREATE ALL ROOT-CAUSE CHARTS
# ---------------------------------------------------------

def create_revenue_drop_charts(
    monthly_data,
    overall_data,
    category_data,
    customer_data,
    region_data
):
    """
    Create all charts needed for revenue
    root-cause analysis.
    """

    charts = {}

    charts["monthly_revenue"] = (
        create_monthly_revenue_chart(
            monthly_data
        )
    )

    charts["month_comparison"] = (
        create_month_comparison_chart(
            overall_data
        )
    )

    charts["category_change"] = (
        create_category_change_chart(
            category_data
        )
    )

    charts["category_contribution"] = (
        create_category_contribution_chart(
            category_data
        )
    )

    charts["customer_change"] = (
        create_customer_change_chart(
            customer_data
        )
    )

    charts["region_change"] = (
        create_region_change_chart(
            region_data
        )
    )

    return charts


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("VISUALIZATION ENGINE")
    print("=" * 60)


    # -----------------------------------------------------
    # Import existing project functions
    # -----------------------------------------------------

    from app.services.query_executor import (
        execute_query
    )


    # -----------------------------------------------------
    # Monthly revenue query
    # -----------------------------------------------------

    monthly_sql = """
    SELECT
        strftime('%m', order_date) AS month,
        SUM(revenue) AS revenue
    FROM orders
    GROUP BY month
    ORDER BY month;
    """

    monthly_data = execute_query(
        monthly_sql
    )


    # -----------------------------------------------------
    # Overall February vs March query
    # -----------------------------------------------------

    overall_sql = """
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

    overall_data = execute_query(
        overall_sql
    )


    # -----------------------------------------------------
    # Category query
    # -----------------------------------------------------

    category_sql = """
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

    GROUP BY category;
    """

    category_data = execute_query(
        category_sql
    )

    category_data["revenue_change"] = (
        category_data["march_revenue"]
        - category_data["february_revenue"]
    )

    total_decline = abs(
        overall_data.loc[
            0,
            "march_revenue"
        ]
        -
        overall_data.loc[
            0,
            "february_revenue"
        ]
    )

    if total_decline > 0:

        category_data[
            "contribution_to_decline"
        ] = (
            category_data[
                "revenue_change"
            ]
            .clip(upper=0)
            .abs()
            / total_decline
        ) * 100

    else:

        category_data[
            "contribution_to_decline"
        ] = 0


    # -----------------------------------------------------
    # Customer query
    # -----------------------------------------------------

    customer_sql = """
    SELECT
        customer_id,

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

    GROUP BY customer_id;
    """

    customer_data = execute_query(
        customer_sql
    )

    customer_data["revenue_change"] = (
        customer_data["march_revenue"]
        - customer_data["february_revenue"]
    )


    # -----------------------------------------------------
    # Region query
    # -----------------------------------------------------

    region_sql = """
    SELECT
        c.region,

        SUM(
            CASE
                WHEN strftime('%m', o.order_date) = '02'
                THEN o.revenue
                ELSE 0
            END
        ) AS february_revenue,

        SUM(
            CASE
                WHEN strftime('%m', o.order_date) = '03'
                THEN o.revenue
                ELSE 0
            END
        ) AS march_revenue

    FROM orders o

    JOIN customers c
        ON o.customer_id = c.customer_id

    WHERE strftime('%m', o.order_date)
        IN ('02', '03')

    GROUP BY c.region;
    """

    region_data = execute_query(
        region_sql
    )

    region_data["revenue_change"] = (
        region_data["march_revenue"]
        - region_data["february_revenue"]
    )


    # -----------------------------------------------------
    # Create charts
    # -----------------------------------------------------

    charts = create_revenue_drop_charts(
        monthly_data,
        overall_data,
        category_data,
        customer_data,
        region_data
    )


    # -----------------------------------------------------
    # Save charts as HTML
    # -----------------------------------------------------

    output_directory = "charts"

    import os

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    for name, figure in charts.items():

        file_path = (
            f"{output_directory}"
            f"/{name}.html"
        )

        figure.write_html(
            file_path
        )

        print(
            f"Created: {file_path}"
        )


    # -----------------------------------------------------
    # Finished
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("VISUALIZATION ENGINE TEST COMPLETE")
    print("=" * 60)