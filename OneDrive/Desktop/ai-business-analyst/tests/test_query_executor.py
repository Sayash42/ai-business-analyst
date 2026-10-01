from app.services.query_executor import execute_query


def test_total_revenue_query():
    sql = """
    SELECT SUM(revenue) AS total_revenue
    FROM orders;
    """

    result = execute_query(sql)

    assert not result.empty
    assert "total_revenue" in result.columns
    assert result.iloc[0]["total_revenue"] > 0


def test_revenue_by_category():
    sql = """
    SELECT
        category,
        SUM(revenue) AS revenue
    FROM orders
    GROUP BY category
    ORDER BY revenue DESC;
    """

    result = execute_query(sql)

    assert not result.empty
    assert "category" in result.columns
    assert "revenue" in result.columns
    assert len(result) > 1