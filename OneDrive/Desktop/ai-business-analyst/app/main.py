import sys
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from app.services.sql_generator import generate_sql
from app.services.query_executor import execute_queries
from app.services.analysis_engine import analyze_revenue_drop
from app.services.insight_generator import generate_business_report

from app.services.visualization import (
    create_monthly_revenue_chart,
    create_month_comparison_chart,
    create_category_change_chart,
    create_category_contribution_chart,
    create_customer_change_chart,
    create_region_change_chart,
)


st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide",
)


st.title("📊 AI Business Analyst")

st.markdown(
    """
Ask a business question and the system will:

1. Understand the business question
2. Generate SQL
3. Validate the SQL
4. Query the database
5. Analyze the results
6. Generate business insights
7. Create visualizations
"""
)


with st.sidebar:

    st.header("About")

    st.write(
        """
        AI Business Analyst is an end-to-end analytics application
        combining SQL, Python, Pandas, SQLite, business analysis,
        visualization, and AI-powered SQL generation.
        """
    )

    st.divider()

    st.subheader("Example questions")

    st.write("• Why did revenue drop in March?")
    st.write("• Show monthly revenue.")
    st.write("• Show revenue by category.")
    st.write("• Show revenue by region.")
    st.write("• Show revenue by customer.")
    st.write("• What is our average order value?")
    st.write("• What are our top products?")


st.header("Ask a business question")

question = st.text_input(
    "Business question",
    placeholder="Example: Why did revenue drop in March?",
)


analyze_button = st.button(
    "🔍 Analyze",
    type="primary",
    use_container_width=True,
)


if analyze_button:

    if not question.strip():

        st.warning("Please enter a business question.")
        st.stop()

    try:

        # ====================================================
        # STEP 1 — SQL GENERATION
        # ====================================================

        with st.spinner("Generating SQL..."):

            sql_result = generate_sql(question)


        # ====================================================
        # GENERATED SQL
        # ====================================================

        st.header("Generated SQL")

        with st.expander(
            "View generated SQL",
            expanded=False,
        ):

            for query in sql_result.get("queries", []):

                st.markdown(
                    f"### {query.get('name', 'Query')}"
                )

                if query.get("purpose"):

                    st.caption(query["purpose"])

                st.code(
                    query.get("sql", ""),
                    language="sql",
                )


        # ====================================================
        # STEP 2 — EXECUTE SQL
        # ====================================================

        with st.spinner("Running database queries..."):

            query_results = execute_queries(
                sql_result["queries"]
            )


        # ====================================================
        # RAW RESULTS
        # ====================================================

        with st.expander(
            "View raw query results",
            expanded=False,
        ):

            for name, dataframe in query_results.items():

                st.markdown(
                    f"### {name}"
                )

                if isinstance(
                    dataframe,
                    pd.DataFrame,
                ):

                    st.dataframe(
                        dataframe,
                        use_container_width=True,
                    )

                else:

                    st.write(dataframe)


        # ====================================================
        # DETERMINE ANALYSIS TYPE
        # ====================================================

        required_analysis_keys = [
            "overall_month_comparison",
            "category_month_comparison",
            "customer_month_comparison",
            "region_month_comparison",
        ]

        is_revenue_drop_analysis = all(
            key in query_results
            for key in required_analysis_keys
        )


        # ====================================================
        # FULL REVENUE-DROP ANALYSIS
        # ====================================================

        if is_revenue_drop_analysis:

            # ------------------------------------------------
            # STEP 3 — BUSINESS ANALYSIS
            # ------------------------------------------------

            with st.spinner(
                "Analyzing business performance..."
            ):

                analysis = analyze_revenue_drop(
                    query_results[
                        "overall_month_comparison"
                    ],
                    query_results[
                        "category_month_comparison"
                    ],
                    query_results[
                        "customer_month_comparison"
                    ],
                    query_results[
                        "region_month_comparison"
                    ],
                )


            # ------------------------------------------------
            # STEP 4 — BUSINESS INSIGHTS
            # ------------------------------------------------

            with st.spinner(
                "Generating business insights..."
            ):

                business_report = generate_business_report(
                    analysis
                )


            # =================================================
            # EXECUTIVE SUMMARY
            # =================================================

            st.header("📋 Executive Summary")

            executive_summary = business_report.get(
                "executive_summary",
                "",
            )

            if executive_summary:

                st.info(executive_summary)


            # =================================================
            # KEY METRICS
            # =================================================

            st.header("📈 Key Metrics")

            overall = analysis.get(
                "overall",
                {},
            )

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                previous_revenue = overall.get(
                    "previous_revenue",
                    overall.get(
                        "february_revenue",
                        0,
                    ),
                )

                st.metric(
                    "February Revenue",
                    f"${previous_revenue:,.2f}",
                )


            with col2:

                current_revenue = overall.get(
                    "current_revenue",
                    overall.get(
                        "march_revenue",
                        0,
                    ),
                )

                st.metric(
                    "March Revenue",
                    f"${current_revenue:,.2f}",
                )


            with col3:

                revenue_change = overall.get(
                    "revenue_change",
                    current_revenue - previous_revenue,
                )

                st.metric(
                    "Revenue Change",
                    f"${revenue_change:,.2f}",
                )


            with col4:

                percentage_change = overall.get(
                    "percentage_change",
                    overall.get(
                        "revenue_change_percentage",
                        0,
                    ),
                )

                st.metric(
                    "Percentage Change",
                    f"{percentage_change:.2f}%",
                )


            # =================================================
            # BUSINESS INSIGHTS
            # =================================================

            st.header("💡 Business Insights")


            overall_insight = business_report.get(
                "overall_insight",
                "",
            )

            if overall_insight:

                st.subheader(
                    "Overall Performance"
                )

                st.write(overall_insight)


            category_insight = business_report.get(
                "category_insight",
                "",
            )

            if category_insight:

                st.subheader(
                    "Category Performance"
                )

                st.write(category_insight)


            customer_insight = business_report.get(
                "customer_insight",
                "",
            )

            if customer_insight:

                st.subheader(
                    "Customer Performance"
                )

                st.write(customer_insight)


            region_insight = business_report.get(
                "region_insight",
                "",
            )

            if region_insight:

                st.subheader(
                    "Regional Performance"
                )

                st.write(region_insight)


            root_cause_insight = business_report.get(
                "root_cause_insight",
                "",
            )

            if root_cause_insight:

                st.subheader(
                    "Root Cause Analysis"
                )

                st.write(root_cause_insight)


            # =================================================
            # VISUALIZATIONS
            # =================================================

            st.header("📊 Visual Analysis")


            # -------------------------------------------------
            # MONTHLY REVENUE
            # -------------------------------------------------

            monthly_sql = """
SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(revenue) AS revenue
FROM orders
GROUP BY month
ORDER BY month;
"""


            with st.spinner(
                "Creating revenue charts..."
            ):

                monthly_result = execute_queries(
                    [
                        {
                            "name": "monthly_revenue",
                            "sql": monthly_sql,
                            "purpose": "Monthly revenue trend.",
                        }
                    ]
                )


            monthly_data = monthly_result.get(
                "monthly_revenue"
            )


            if (
                isinstance(
                    monthly_data,
                    pd.DataFrame,
                )
                and not monthly_data.empty
            ):

                st.subheader(
                    "Monthly Revenue"
                )

                fig = create_monthly_revenue_chart(
                    monthly_data
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )


            # -------------------------------------------------
            # FEBRUARY VS MARCH
            # -------------------------------------------------

            overall_data = query_results.get(
                "overall_month_comparison"
            )


            if (
                isinstance(
                    overall_data,
                    pd.DataFrame,
                )
                and not overall_data.empty
            ):

                st.subheader(
                    "February vs March Revenue"
                )

                fig = create_month_comparison_chart(
                    overall_data
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )


            # -------------------------------------------------
            # CATEGORY ANALYSIS
            # -------------------------------------------------

            category_data = analysis.get(
                "categories"
            )


            if (
                isinstance(
                    category_data,
                    pd.DataFrame,
                )
                and not category_data.empty
            ):

                st.subheader(
                    "Revenue Change by Category"
                )

                fig = create_category_change_chart(
                    category_data
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )


                st.subheader(
                    "Category Contribution to Revenue Change"
                )

                fig = create_category_contribution_chart(
                    category_data
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )


                with st.expander(
                    "View category analysis"
                ):

                    st.dataframe(
                        category_data,
                        use_container_width=True,
                    )


            # -------------------------------------------------
            # CUSTOMER ANALYSIS
            # -------------------------------------------------

            customer_data = analysis.get(
                "customers"
            )


            if (
                isinstance(
                    customer_data,
                    pd.DataFrame,
                )
                and not customer_data.empty
            ):

                st.subheader(
                    "Top Customer Revenue Changes"
                )

                fig = create_customer_change_chart(
                    customer_data,
                    number=10,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )


                with st.expander(
                    "View customer analysis"
                ):

                    st.dataframe(
                        customer_data.head(20),
                        use_container_width=True,
                    )


            # -------------------------------------------------
            # REGION ANALYSIS
            # -------------------------------------------------

            region_data = analysis.get(
                "regions"
            )


            if (
                isinstance(
                    region_data,
                    pd.DataFrame,
                )
                and not region_data.empty
            ):

                st.subheader(
                    "Revenue Change by Region"
                )

                fig = create_region_change_chart(
                    region_data
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )


                with st.expander(
                    "View regional analysis"
                ):

                    st.dataframe(
                        region_data,
                        use_container_width=True,
                    )


        # ====================================================
        # GENERAL QUERY
        # ====================================================

        else:

            st.header("📊 Analysis Result")

            st.info(
                "The question was answered using the generated SQL query."
            )

            for name, dataframe in query_results.items():

                st.subheader(
                    name.replace(
                        "_",
                        " ",
                    ).title()
                )

                if isinstance(
                    dataframe,
                    pd.DataFrame,
                ):

                    st.dataframe(
                        dataframe,
                        use_container_width=True,
                    )

                else:

                    st.write(dataframe)


        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            "Analysis completed successfully."
        )


    except Exception as error:

        st.error(
            "Something went wrong while analyzing the question."
        )

        with st.expander(
            "Technical error details"
        ):

            st.exception(error)