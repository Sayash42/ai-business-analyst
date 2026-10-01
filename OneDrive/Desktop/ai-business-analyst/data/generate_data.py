import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)

NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 200
NUM_ORDERS = 100000

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)


# ============================================================
# BUSINESS CONFIGURATION
# ============================================================

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central"
]

SEGMENTS = [
    "Consumer",
    "Small Business",
    "Enterprise"
]

CATEGORIES = [
    "Electronics",
    "Furniture",
    "Clothing",
    "Home & Kitchen",
    "Sports",
    "Books"
]

CATEGORY_MULTIPLIERS = {
    "Electronics": 1.8,
    "Furniture": 1.4,
    "Clothing": 0.8,
    "Home & Kitchen": 1.0,
    "Sports": 0.9,
    "Books": 0.6
}


# ============================================================
# 1. GENERATE CUSTOMERS
# ============================================================

def generate_customers():

    customers = []

    first_names = [
        "Aarav",
        "Vivaan",
        "Aditya",
        "Arjun",
        "Rahul",
        "Rohan",
        "Priya",
        "Ananya",
        "Sneha",
        "Kavya",
        "Neha",
        "Meera",
        "David",
        "Daniel",
        "Emma",
        "Sophia"
    ]

    last_names = [
        "Sharma",
        "Patel",
        "Kumar",
        "Singh",
        "Gupta",
        "Mehta",
        "Verma",
        "Reddy",
        "Brown",
        "Smith",
        "Wilson",
        "Johnson"
    ]

    for i in range(1, NUM_CUSTOMERS + 1):

        customer_id = f"C{i:05d}"

        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        customers.append({
            "customer_id": customer_id,
            "customer_name": f"{first_name} {last_name}",
            "region": random.choice(REGIONS),
            "segment": random.choice(SEGMENTS)
        })

    return pd.DataFrame(customers)


# ============================================================
# 2. GENERATE PRODUCTS
# ============================================================

def generate_products():

    products = []

    product_names = {
        "Electronics": [
            "Laptop",
            "Smartphone",
            "Tablet",
            "Monitor",
            "Keyboard",
            "Headphones",
            "Smart Watch",
            "Camera"
        ],
        "Furniture": [
            "Office Chair",
            "Desk",
            "Bookshelf",
            "Dining Table",
            "Sofa",
            "Bed"
        ],
        "Clothing": [
            "T-Shirt",
            "Jeans",
            "Jacket",
            "Sneakers",
            "Dress",
            "Sweater"
        ],
        "Home & Kitchen": [
            "Coffee Maker",
            "Blender",
            "Cookware Set",
            "Vacuum Cleaner",
            "Toaster",
            "Air Fryer"
        ],
        "Sports": [
            "Football",
            "Cricket Bat",
            "Yoga Mat",
            "Running Shoes",
            "Dumbbells",
            "Tennis Racket"
        ],
        "Books": [
            "Business Book",
            "Technology Book",
            "Novel",
            "Science Book",
            "History Book",
            "Finance Book"
        ]
    }

    for i in range(1, NUM_PRODUCTS + 1):

        product_id = f"P{i:04d}"

        category = random.choice(CATEGORIES)

        base_price = random.uniform(20, 1000)

        price = (
            base_price
            * CATEGORY_MULTIPLIERS[category]
        )

        product_name = random.choice(
            product_names[category]
        )

        products.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "unit_price": round(price, 2)
        })

    return pd.DataFrame(products)


# ============================================================
# 3. GENERATE ORDERS
# ============================================================

def generate_orders(customers, products):

    orders = []

    customer_ids = customers["customer_id"].tolist()
    product_ids = products["product_id"].tolist()

    customer_weights = np.random.exponential(
        scale=1.0,
        size=len(customer_ids)
    )

    customer_weights = (
        customer_weights
        / customer_weights.sum()
    )

    for i in range(1, NUM_ORDERS + 1):

        order_id = f"O{i:06d}"

        customer_id = np.random.choice(
            customer_ids,
            p=customer_weights
        )

        product_id = random.choice(product_ids)

        product = products[
            products["product_id"] == product_id
        ].iloc[0]

        category = product["category"]

        # Random date throughout 2024
        days_range = (
            END_DATE - START_DATE
        ).days

        random_day = random.randint(
            0,
            days_range
        )

        order_date = (
            START_DATE
            + timedelta(days=random_day)
        )

        quantity = random.randint(1, 5)

        unit_price = product["unit_price"]

        orders.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_id": customer_id,
            "product_id": product_id,
            "category": category,
            "quantity": quantity,
            "unit_price": round(unit_price, 2)
        })

    return pd.DataFrame(orders)


# ============================================================
# 4. APPLY BUSINESS EVENTS
# ============================================================

def apply_business_events(orders):

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    # --------------------------------------------------------
    # March Electronics decline
    # --------------------------------------------------------

    march_electronics = (
        (orders["order_date"].dt.month == 3)
        & (orders["category"] == "Electronics")
    )

    orders.loc[
        march_electronics,
        "quantity"
    ] = np.maximum(
        1,
        (
            orders.loc[
                march_electronics,
                "quantity"
            ] * 0.75
        ).round().astype(int)
    )

    # --------------------------------------------------------
    # Major customer decline
    # --------------------------------------------------------

    major_customers = [
        "C00001",
        "C00002",
        "C00003",
        "C00004"
    ]

    march_major_customers = (
        (orders["order_date"].dt.month == 3)
        & (orders["customer_id"].isin(
            major_customers
        ))
    )

    orders.loc[
        march_major_customers,
        "quantity"
    ] = np.maximum(
        1,
        (
            orders.loc[
                march_major_customers,
                "quantity"
            ] * 0.60
        ).round().astype(int)
    )

    # --------------------------------------------------------
    # March average order value reduction
    # --------------------------------------------------------

    march = (
        orders["order_date"].dt.month == 3
    )

    orders.loc[
        march,
        "unit_price"
    ] = (
        orders.loc[
            march,
            "unit_price"
        ] * 0.92
    ).round(2)

    # --------------------------------------------------------
    # Calculate revenue
    # --------------------------------------------------------

    orders["revenue"] = (
        orders["quantity"]
        * orders["unit_price"]
    ).round(2)

    return orders


# ============================================================
# 5. MAIN
# ============================================================

def main():

    print("Generating customers...")

    customers = generate_customers()

    print("Generating products...")

    products = generate_products()

    print("Generating orders...")

    orders = generate_orders(
        customers,
        products
    )

    print("Applying business events...")

    orders = apply_business_events(
        orders
    )

    # Save CSV files

    customers.to_csv(
        "data/customers.csv",
        index=False
    )

    products.to_csv(
        "data/products.csv",
        index=False
    )

    orders.to_csv(
        "data/orders.csv",
        index=False
    )

    print()
    print("=" * 50)
    print("DATASET GENERATED SUCCESSFULLY")
    print("=" * 50)

    print(
        f"Customers: {len(customers):,}"
    )

    print(
        f"Products:  {len(products):,}"
    )

    print(
        f"Orders:    {len(orders):,}"
    )

    print()
    print("Files created:")
    print("data/customers.csv")
    print("data/products.csv")
    print("data/orders.csv")


if __name__ == "__main__":
    main()