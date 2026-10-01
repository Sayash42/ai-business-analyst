import pandas as pd


# =========================================================
# ANALYSIS ENGINE
# =========================================================


# ---------------------------------------------------------
# SAFE PERCENTAGE CHANGE
# ---------------------------------------------------------

def calculate_percentage_change(
    old_value,
    new_value
):
    """
    Calculate percentage change between two values.

    Formula:

        ((new - old) / old) * 100

    Returns:
        float
    """

    if old_value == 0:
        return 0.0

    return (
        (new_value - old_value)
        / old_value
    ) * 100


# ---------------------------------------------------------
# OVERALL REVENUE ANALYSIS
# ---------------------------------------------------------

def analyze_overall_revenue(
    data
):
    """
    Analyze February vs March overall revenue.

    Expected columns:

        february_revenue
        march_revenue

    Returns:
        dictionary containing summary metrics.
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

    revenue_change = (
        march_revenue
        - february_revenue
    )

    percentage_change = (
        calculate_percentage_change(
            february_revenue,
            march_revenue
        )
    )

    return {
        "february_revenue": february_revenue,
        "march_revenue": march_revenue,
        "revenue_change": revenue_change,
        "percentage_change": percentage_change
    }


# ---------------------------------------------------------
# CATEGORY ANALYSIS
# ---------------------------------------------------------

def analyze_category_changes(
    data,
    total_decline
):
    """
    Analyze revenue changes by category.

    Expected columns:

        category
        february_revenue
        march_revenue

    Adds:

        revenue_change
        percentage_change
        contribution_to_decline
    """

    result = data.copy()

    result["revenue_change"] = (
        result["march_revenue"]
        - result["february_revenue"]
    )

    result["percentage_change"] = (
        (
            result["revenue_change"]
            / result["february_revenue"]
        ) * 100
    )

    # Only negative changes contribute to a decline.
    if total_decline > 0:

        result["contribution_to_decline"] = (
            result["revenue_change"]
            .clip(upper=0)
            .abs()
            / total_decline
        ) * 100

    else:

        result["contribution_to_decline"] = 0.0

    result = result.sort_values(
        "revenue_change"
    )

    return result


# ---------------------------------------------------------
# CUSTOMER ANALYSIS
# ---------------------------------------------------------

def analyze_customer_changes(
    data,
    total_decline
):
    """
    Analyze revenue changes by customer.

    Expected columns:

        customer_id
        february_revenue
        march_revenue
    """

    result = data.copy()

    result["revenue_change"] = (
        result["march_revenue"]
        - result["february_revenue"]
    )

    result["percentage_change"] = (
        (
            result["revenue_change"]
            / result["february_revenue"]
        ) * 100
    )

    if total_decline > 0:

        result["contribution_to_decline"] = (
            result["revenue_change"]
            .clip(upper=0)
            .abs()
            / total_decline
        ) * 100

    else:

        result["contribution_to_decline"] = 0.0

    result = result.sort_values(
        "revenue_change"
    )

    return result


# ---------------------------------------------------------
# REGION ANALYSIS
# ---------------------------------------------------------

def analyze_region_changes(
    data,
    total_decline
):
    """
    Analyze revenue changes by region.

    Expected columns:

        region
        february_revenue
        march_revenue
    """

    result = data.copy()

    result["revenue_change"] = (
        result["march_revenue"]
        - result["february_revenue"]
    )

    result["percentage_change"] = (
        (
            result["revenue_change"]
            / result["february_revenue"]
        ) * 100
    )

    if total_decline > 0:

        result["contribution_to_decline"] = (
            result["revenue_change"]
            .clip(upper=0)
            .abs()
            / total_decline
        ) * 100

    else:

        result["contribution_to_decline"] = 0.0

    result = result.sort_values(
        "revenue_change"
    )

    return result


# ---------------------------------------------------------
# FIND TOP DECLINING CATEGORIES
# ---------------------------------------------------------

def get_top_declining_categories(
    data,
    number=5
):
    """
    Return the categories with the largest
    revenue declines.
    """

    declining = data[
        data["revenue_change"] < 0
    ]

    return (
        declining
        .sort_values(
            "revenue_change"
        )
        .head(number)
    )


# ---------------------------------------------------------
# FIND TOP DECLINING CUSTOMERS
# ---------------------------------------------------------

def get_top_declining_customers(
    data,
    number=10
):
    """
    Return customers with the largest
    revenue declines.
    """

    declining = data[
        data["revenue_change"] < 0
    ]

    return (
        declining
        .sort_values(
            "revenue_change"
        )
        .head(number)
    )


# ---------------------------------------------------------
# FIND TOP DECLINING REGIONS
# ---------------------------------------------------------

def get_top_declining_regions(
    data,
    number=5
):
    """
    Return regions with the largest
    revenue declines.
    """

    declining = data[
        data["revenue_change"] < 0
    ]

    return (
        declining
        .sort_values(
            "revenue_change"
        )
        .head(number)
    )


# ---------------------------------------------------------
# ROOT CAUSE ANALYSIS
# ---------------------------------------------------------

def analyze_revenue_drop(
    overall_data,
    category_data,
    customer_data,
    region_data
):
    """
    Perform a complete February vs March
    revenue root-cause analysis.
    """

    # -----------------------------------------------------
    # Overall analysis
    # -----------------------------------------------------

    overall = analyze_overall_revenue(
        overall_data
    )

    february_revenue = (
        overall["february_revenue"]
    )

    march_revenue = (
        overall["march_revenue"]
    )

    revenue_change = (
        overall["revenue_change"]
    )

    # Total decline expressed as a positive number.
    total_decline = max(
        0,
        -revenue_change
    )

    # -----------------------------------------------------
    # Category analysis
    # -----------------------------------------------------

    categories = analyze_category_changes(
        category_data,
        total_decline
    )

    # -----------------------------------------------------
    # Customer analysis
    # -----------------------------------------------------

    customers = analyze_customer_changes(
        customer_data,
        total_decline
    )

    # -----------------------------------------------------
    # Region analysis
    # -----------------------------------------------------

    regions = analyze_region_changes(
        region_data,
        total_decline
    )

    # -----------------------------------------------------
    # Top contributors
    # -----------------------------------------------------

    top_categories = (
        get_top_declining_categories(
            categories
        )
    )

    top_customers = (
        get_top_declining_customers(
            customers
        )
    )

    top_regions = (
        get_top_declining_regions(
            regions
        )
    )

    # -----------------------------------------------------
    # Final analysis result
    # -----------------------------------------------------

    return {
        "overall": overall,
        "categories": categories,
        "customers": customers,
        "regions": regions,
        "top_declining_categories": (
            top_categories
        ),
        "top_declining_customers": (
            top_customers
        ),
        "top_declining_regions": (
            top_regions
        )
    }


# =========================================================
# FORMAT BUSINESS SUMMARY
# =========================================================

def create_business_summary(
    analysis
):
    """
    Convert analysis results into a concise
    business-oriented summary.

    This is not the final AI insight layer.
    It simply summarizes the calculated numbers.
    """

    overall = analysis["overall"]

    percentage_change = (
        overall["percentage_change"]
    )

    revenue_change = (
        overall["revenue_change"]
    )

    if percentage_change < 0:

        direction = "decreased"

    elif percentage_change > 0:

        direction = "increased"

    else:

        direction = "did not change"

    summary = []

    summary.append(
        f"Revenue {direction} by "
        f"{abs(percentage_change):.2f}% "
        f"from February to March."
    )

    summary.append(
        f"Revenue change: "
        f"${revenue_change:,.2f}."
    )

    # -----------------------------------------------------
    # Top category
    # -----------------------------------------------------

    categories = (
        analysis[
            "top_declining_categories"
        ]
    )

    if not categories.empty:

        top_category = categories.iloc[0]

        summary.append(
            f"Largest category decline: "
            f"{top_category['category']} "
            f"with a change of "
            f"${top_category['revenue_change']:,.2f}."
        )

    # -----------------------------------------------------
    # Top customer
    # -----------------------------------------------------

    customers = (
        analysis[
            "top_declining_customers"
        ]
    )

    if not customers.empty:

        top_customer = customers.iloc[0]

        summary.append(
            f"Largest customer decline: "
            f"{top_customer['customer_id']} "
            f"with a change of "
            f"${top_customer['revenue_change']:,.2f}."
        )

    # -----------------------------------------------------
    # Top region
    # -----------------------------------------------------

    regions = (
        analysis[
            "top_declining_regions"
        ]
    )

    if not regions.empty:

        top_region = regions.iloc[0]

        summary.append(
            f"Largest regional decline: "
            f"{top_region['region']} "
            f"with a change of "
            f"${top_region['revenue_change']:,.2f}."
        )

    return summary


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PYTHON ANALYSIS ENGINE")
    print("=" * 60)


    # -----------------------------------------------------
    # Import query execution functions
    # -----------------------------------------------------

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
    # Execute SQL
    # -----------------------------------------------------

    results = execute_queries(
        queries
    )


    # -----------------------------------------------------
    # Get individual results
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
    # Analyze results
    # -----------------------------------------------------

    analysis = analyze_revenue_drop(
        overall_data,
        category_data,
        customer_data,
        region_data
    )


    # -----------------------------------------------------
    # Display overall result
    # -----------------------------------------------------

    print("\nOVERALL ANALYSIS")
    print("-" * 60)

    print(
        analysis["overall"]
    )


    # -----------------------------------------------------
    # Display category analysis
    # -----------------------------------------------------

    print(
        "\nCATEGORY ANALYSIS"
    )
    print("-" * 60)

    print(
        analysis["categories"]
        .to_string(index=False)
    )


    # -----------------------------------------------------
    # Display top declining customers
    # -----------------------------------------------------

    print(
        "\nTOP DECLINING CUSTOMERS"
    )
    print("-" * 60)

    print(
        analysis[
            "top_declining_customers"
        ].to_string(index=False)
    )


    # -----------------------------------------------------
    # Display region analysis
    # -----------------------------------------------------

    print(
        "\nREGION ANALYSIS"
    )
    print("-" * 60)

    print(
        analysis["regions"]
        .to_string(index=False)
    )


    # -----------------------------------------------------
    # Business summary
    # -----------------------------------------------------

    print(
        "\nBUSINESS SUMMARY"
    )
    print("-" * 60)

    summary = create_business_summary(
        analysis
    )

    for item in summary:

        print(
            f"- {item}"
        )


    # -----------------------------------------------------
    # Finished
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("ANALYSIS ENGINE TEST COMPLETE")
    print("=" * 60)