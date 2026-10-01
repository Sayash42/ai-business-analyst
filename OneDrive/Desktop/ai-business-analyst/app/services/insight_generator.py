import pandas as pd


# =========================================================
# INSIGHT GENERATOR
# =========================================================


# ---------------------------------------------------------
# FORMAT CURRENCY
# ---------------------------------------------------------

def format_currency(value):
    """
    Format a number as currency.
    """

    return f"${value:,.2f}"


# ---------------------------------------------------------
# FORMAT PERCENTAGE
# ---------------------------------------------------------

def format_percentage(value):
    """
    Format a number as a percentage.
    """

    return f"{value:.2f}%"


# ---------------------------------------------------------
# OVERALL INSIGHT
# ---------------------------------------------------------

def generate_overall_insight(overall):
    """
    Generate an insight about the overall revenue change.
    """

    february = overall["february_revenue"]
    march = overall["march_revenue"]
    change = overall["revenue_change"]
    percentage = overall["percentage_change"]

    if change < 0:

        return (
            f"Revenue decreased from "
            f"{format_currency(february)} in February "
            f"to {format_currency(march)} in March, "
            f"a decline of "
            f"{format_percentage(abs(percentage))}."
        )

    elif change > 0:

        return (
            f"Revenue increased from "
            f"{format_currency(february)} in February "
            f"to {format_currency(march)} in March, "
            f"an increase of "
            f"{format_percentage(percentage)}."
        )

    else:

        return (
            f"Revenue remained unchanged at "
            f"{format_currency(march)} "
            f"from February to March."
        )


# ---------------------------------------------------------
# CATEGORY INSIGHT
# ---------------------------------------------------------

def generate_category_insight(
    category_data
):
    """
    Identify the largest category-level
    revenue decline.
    """

    declining = category_data[
        category_data["revenue_change"] < 0
    ].copy()

    if declining.empty:

        return (
            "No category showed a revenue decline "
            "between February and March."
        )

    declining = declining.sort_values(
        "revenue_change"
    )

    top_category = declining.iloc[0]

    category = top_category["category"]
    change = top_category["revenue_change"]
    percentage = top_category["percentage_change"]

    contribution = (
        top_category[
            "contribution_to_decline"
        ]
    )

    return (
        f"{category} had the largest category-level "
        f"revenue decline, decreasing by "
        f"{format_currency(abs(change))} "
        f"({format_percentage(abs(percentage))}). "
        f"It accounted for approximately "
        f"{format_percentage(contribution)} "
        f"of the total revenue decline."
    )


# ---------------------------------------------------------
# CUSTOMER INSIGHT
# ---------------------------------------------------------

def generate_customer_insight(
    customer_data,
    number=3
):
    """
    Identify the customers with the largest
    revenue declines.
    """

    declining = customer_data[
        customer_data["revenue_change"] < 0
    ].copy()

    if declining.empty:

        return (
            "No customers showed a revenue decline "
            "between February and March."
        )

    declining = (
        declining
        .sort_values(
            "revenue_change"
        )
        .head(number)
    )

    customer_parts = []

    for _, row in declining.iterrows():

        customer_id = row["customer_id"]

        change = row["revenue_change"]

        customer_parts.append(
            f"{customer_id} "
            f"({format_currency(abs(change))} decline)"
        )

    customers_text = ", ".join(
        customer_parts
    )

    return (
        "The largest customer-level declines "
        f"were observed for {customers_text}."
    )


# ---------------------------------------------------------
# REGION INSIGHT
# ---------------------------------------------------------

def generate_region_insight(
    region_data
):
    """
    Identify the region with the largest
    revenue decline.
    """

    declining = region_data[
        region_data["revenue_change"] < 0
    ].copy()

    if declining.empty:

        return (
            "No region showed a revenue decline "
            "between February and March."
        )

    declining = declining.sort_values(
        "revenue_change"
    )

    top_region = declining.iloc[0]

    region = top_region["region"]
    change = top_region["revenue_change"]
    percentage = top_region["percentage_change"]

    return (
        f"{region} had the largest regional "
        f"revenue decline, decreasing by "
        f"{format_currency(abs(change))} "
        f"({format_percentage(abs(percentage))})."
    )


# ---------------------------------------------------------
# BUILD ROOT-CAUSE INSIGHT
# ---------------------------------------------------------

def generate_root_cause_insight(
    analysis
):
    """
    Generate a complete business explanation
    from the calculated analysis results.
    """

    overall = analysis["overall"]

    categories = analysis["categories"]

    customers = analysis["customers"]

    regions = analysis["regions"]

    insights = []

    # -----------------------------------------------------
    # Overall
    # -----------------------------------------------------

    insights.append(
        generate_overall_insight(
            overall
        )
    )

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    insights.append(
        generate_category_insight(
            categories
        )
    )

    # -----------------------------------------------------
    # Customer
    # -----------------------------------------------------

    insights.append(
        generate_customer_insight(
            customers
        )
    )

    # -----------------------------------------------------
    # Region
    # -----------------------------------------------------

    insights.append(
        generate_region_insight(
            regions
        )
    )

    return insights


# ---------------------------------------------------------
# GENERATE EXECUTIVE SUMMARY
# ---------------------------------------------------------

def generate_executive_summary(
    analysis
):
    """
    Create a concise executive summary.
    """

    overall = analysis["overall"]

    categories = analysis["categories"]

    customers = analysis["customers"]

    regions = analysis["regions"]

    summary_parts = []

    # -----------------------------------------------------
    # Overall change
    # -----------------------------------------------------

    percentage = overall[
        "percentage_change"
    ]

    if percentage < 0:

        summary_parts.append(
            f"Revenue declined by "
            f"{format_percentage(abs(percentage))} "
            f"from February to March."
        )

    elif percentage > 0:

        summary_parts.append(
            f"Revenue increased by "
            f"{format_percentage(percentage)} "
            f"from February to March."
        )

    else:

        summary_parts.append(
            "Revenue remained unchanged "
            "from February to March."
        )

    # -----------------------------------------------------
    # Largest category
    # -----------------------------------------------------

    declining_categories = categories[
        categories["revenue_change"] < 0
    ]

    if not declining_categories.empty:

        top_category = (
            declining_categories
            .sort_values(
                "revenue_change"
            )
            .iloc[0]
        )

        summary_parts.append(
            f"The largest category decline "
            f"was in {top_category['category']}."
        )

    # -----------------------------------------------------
    # Customer concentration
    # -----------------------------------------------------

    declining_customers = customers[
        customers["revenue_change"] < 0
    ]

    if not declining_customers.empty:

        top_customer = (
            declining_customers
            .sort_values(
                "revenue_change"
            )
            .iloc[0]
        )

        summary_parts.append(
            f"The largest customer-level decline "
            f"was from {top_customer['customer_id']}."
        )

    # -----------------------------------------------------
    # Regional concentration
    # -----------------------------------------------------

    declining_regions = regions[
        regions["revenue_change"] < 0
    ]

    if not declining_regions.empty:

        top_region = (
            declining_regions
            .sort_values(
                "revenue_change"
            )
            .iloc[0]
        )

        summary_parts.append(
            f"The largest regional decline "
            f"was in {top_region['region']}."
        )

    return " ".join(
        summary_parts
    )


# =========================================================
# BUILD COMPLETE BUSINESS REPORT
# =========================================================

def generate_business_report(
    analysis
):
    """
    Generate the complete business report.
    """

    executive_summary = (
        generate_executive_summary(
            analysis
        )
    )

    insights = (
        generate_root_cause_insight(
            analysis
        )
    )

    return {
        "executive_summary": (
            executive_summary
        ),
        "insights": insights
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("INSIGHT GENERATOR")
    print("=" * 60)


    # -----------------------------------------------------
    # Import analysis engine
    # -----------------------------------------------------

    from app.services.analysis_engine import (
        analyze_revenue_drop
    )

    from app.services.sql_generator import (
        generate_sql
    )

    from app.services.query_executor import (
        execute_queries
    )


    # -----------------------------------------------------
    # Business question
    # -----------------------------------------------------

    question = (
        "Why did revenue drop in March?"
    )

    print("\nQUESTION:")
    print(question)


    # -----------------------------------------------------
    # Generate SQL
    # -----------------------------------------------------

    generated = generate_sql(
        question
    )

    queries = generated["queries"]


    # -----------------------------------------------------
    # Execute queries
    # -----------------------------------------------------

    results = execute_queries(
        queries
    )


    # -----------------------------------------------------
    # Extract results
    # -----------------------------------------------------

    overall_data = results[
        "overall_month_comparison"
    ]

    category_data = results[
        "category_month_comparison"
    ]

    customer_data = results[
        "customer_month_comparison"
    ]

    region_data = results[
        "region_month_comparison"
    ]


    # -----------------------------------------------------
    # Analyze data
    # -----------------------------------------------------

    analysis = analyze_revenue_drop(
        overall_data,
        category_data,
        customer_data,
        region_data
    )


    # -----------------------------------------------------
    # Generate business report
    # -----------------------------------------------------

    report = generate_business_report(
        analysis
    )


    # -----------------------------------------------------
    # Executive summary
    # -----------------------------------------------------

    print("\nEXECUTIVE SUMMARY")
    print("-" * 60)

    print(
        report["executive_summary"]
    )


    # -----------------------------------------------------
    # Detailed insights
    # -----------------------------------------------------

    print("\nINSIGHTS")
    print("-" * 60)

    for insight in report["insights"]:

        print(
            f"- {insight}"
        )


    # -----------------------------------------------------
    # Finished
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("INSIGHT GENERATOR TEST COMPLETE")
    print("=" * 60)