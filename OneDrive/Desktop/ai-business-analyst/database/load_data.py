import os
import sqlite3

import pandas as pd



BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DATABASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "business.db"
)

SCHEMA_PATH = os.path.join(
    DATABASE_DIR,
    "schema.sql"
)



def load_csv_files():

    print("Loading customers.csv...")

    customers = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "customers.csv"
        )
    )

    print("Loading products.csv...")

    products = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "products.csv"
        )
    )

    print("Loading orders.csv...")

    orders = pd.read_csv(
        os.path.join(
            DATA_DIR,
            "orders.csv"
        )
    )

    return customers, products, orders



def create_database():

    print("\nCreating database...")

    # Remove old database
    if os.path.exists(DATABASE_PATH):

        os.remove(DATABASE_PATH)

        print("Removed existing database.")

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    print("Connected to SQLite.")

    return connection


def create_tables(connection):

    print("\nCreating tables...")

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        schema = file.read()

    connection.executescript(
        schema
    )

    connection.commit()

    print("Tables created successfully.")



def insert_data(
    connection,
    customers,
    products,
    orders
):

    print("\nInserting customers...")

    customers.to_sql(
        "customers",
        connection,
        if_exists="append",
        index=False
    )

    print(
        f"Inserted {len(customers):,} customers."
    )

    print("\nInserting products...")

    products.to_sql(
        "products",
        connection,
        if_exists="append",
        index=False
    )

    print(
        f"Inserted {len(products):,} products."
    )

    print("\nInserting orders...")

    orders.to_sql(
        "orders",
        connection,
        if_exists="append",
        index=False
    )

    print(
        f"Inserted {len(orders):,} orders."
    )


=

def verify_database(connection):

    print("\nVerifying database...")
    print("=" * 50)

    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """,
        connection
    )

    print("\nTables:")

    print(tables)


    for table in [
        "customers",
        "products",
        "orders"
    ]:

        result = pd.read_sql_query(
            f"SELECT COUNT(*) AS count FROM {table}",
            connection
        )

        count = result.iloc[0]["count"]

        print(
            f"{table}: {count:,} rows"
        )




def main():

    print("=" * 50)
    print("AI BUSINESS ANALYST")
    print("DATABASE LOADER")
    print("=" * 50)

    customers, products, orders = (
        load_csv_files()
    )

    connection = create_database()

    try:

        create_tables(
            connection
        )

        insert_data(
            connection,
            customers,
            products,
            orders
        )

        verify_database(
            connection
        )

    finally:

        connection.close()

    print("\n" + "=" * 50)
    print("DATABASE CREATED SUCCESSFULLY")
    print("=" * 50)

    print(
        f"\nDatabase location:\n{DATABASE_PATH}"
    )


if __name__ == "__main__":
    main()