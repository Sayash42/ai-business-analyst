import pandas as pd

from app.services.analysis_engine import (
    calculate_percentage_change,
    analyze_revenue_drop,
)


def test_percentage_change():
    result = calculate_percentage_change(
        100,
        80,
    )

    assert result == -20.0


def test_percentage_change_from_zero():
    result = calculate_percentage_change(
        0,
        100,
    )

    assert result == 0


def test_revenue_drop_analysis():

    overall_data = pd.DataFrame(
        {
            "february_revenue": [100000],
            "march_revenue": [80000],
        }
    )

    category_data = pd.DataFrame(
        {
            "category": [
                "Electronics",
                "Furniture",
            ],
            "february_revenue": [
                50000,
                50000,
            ],
            "march_revenue": [
                30000,
                50000,
            ],
        }
    )

    customer_data = pd.DataFrame(
        {
            "customer_id": [
                "C00001",
                "C00002",
            ],
            "february_revenue": [
                30000,
                20000,
            ],
            "march_revenue": [
                10000,
                15000,
            ],
        }
    )

    region_data = pd.DataFrame(
        {
            "region": [
                "North",
                "South",
            ],
            "february_revenue": [
                50000,
                50000,
            ],
            "march_revenue": [
                40000,
                40000,
            ],
        }
    )

    result = analyze_revenue_drop(
        overall_data,
        category_data,
        customer_data,
        region_data,
    )

    assert isinstance(result, dict)

    assert "overall" in result
    assert "categories" in result
    assert "customers" in result
    assert "regions" in result
    overall = result["overall"]

    assert isinstance(overall, dict)

    assert overall["february_revenue"] == 100000
    assert overall["march_revenue"] == 80000
    assert overall["revenue_change"] == -20000