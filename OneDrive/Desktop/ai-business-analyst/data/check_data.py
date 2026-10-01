import pandas as pd


orders = pd.read_csv(
    "data/orders.csv",
    parse_dates=["order_date"]
)


orders["month"] = (
    orders["order_date"]
    .dt.month
)


# Monthly revenue
monthly_revenue = (
    orders
    .groupby("month")["revenue"]
    .sum()
)


print("\nMONTHLY REVENUE")
print("=" * 40)

print(monthly_revenue)


# February vs March
february = monthly_revenue.loc[2]
march = monthly_revenue.loc[3]

change = march - february

percentage_change = (
    change / february
) * 100


print("\nFEBRUARY VS MARCH")
print("=" * 40)

print(
    f"February Revenue: ${february:,.2f}"
)

print(
    f"March Revenue:    ${march:,.2f}"
)

print(
    f"Change:           ${change:,.2f}"
)

print(
    f"Percentage:       {percentage_change:.2f}%"
)


# Category analysis
orders["month_name"] = (
    orders["order_date"]
    .dt.strftime("%B")
)


feb_category = (
    orders[
        orders["month"] == 2
    ]
    .groupby("category")["revenue"]
    .sum()
)


march_category = (
    orders[
        orders["month"] == 3
    ]
    .groupby("category")["revenue"]
    .sum()
)


category_comparison = pd.DataFrame({
    "February": feb_category,
    "March": march_category
})


category_comparison["change_%"] = (
    (
        category_comparison["March"]
        - category_comparison["February"]
    )
    / category_comparison["February"]
) * 100


print("\nCATEGORY ANALYSIS")
print("=" * 40)

print(
    category_comparison
    .sort_values("change_%")
)