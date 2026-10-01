from app.services.sql_generator import generate_sql


def test_monthly_revenue_question():

    result = generate_sql(
        "What was our monthly revenue?"
    )

    assert isinstance(result, dict)
    assert "queries" in result
    assert len(result["queries"]) > 0


def test_category_revenue_question():

    result = generate_sql(
        "Show revenue by category."
    )

    assert isinstance(result, dict)
    assert "queries" in result
    assert len(result["queries"]) > 0


def test_march_revenue_drop_question():

    result = generate_sql(
        "Why did revenue drop in March?"
    )

    assert isinstance(result, dict)
    assert "queries" in result

    query_names = [
        query["name"]
        for query in result["queries"]
    ]

    assert "overall_month_comparison" in query_names
    assert "category_month_comparison" in query_names
    assert "customer_month_comparison" in query_names
    assert "region_month_comparison" in query_names