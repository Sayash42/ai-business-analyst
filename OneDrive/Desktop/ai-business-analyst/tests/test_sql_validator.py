from app.services.sql_validator import validate_sql


def test_valid_select_query():
    result = validate_sql("SELECT * FROM orders;")

    assert result["valid"] is True
    assert result["errors"] == []


def test_reject_delete_query():
    result = validate_sql("DELETE FROM orders;")

    assert result["valid"] is False


def test_reject_drop_query():
    result = validate_sql("DROP TABLE orders;")

    assert result["valid"] is False


def test_reject_update_query():
    result = validate_sql(
        "UPDATE orders SET revenue = 0;"
    )

    assert result["valid"] is False


def test_reject_insert_query():
    result = validate_sql(
        "INSERT INTO orders VALUES ('1');"
    )

    assert result["valid"] is False