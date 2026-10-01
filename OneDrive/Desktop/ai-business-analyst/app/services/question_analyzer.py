import re


# =========================================================
# QUESTION ANALYZER
# =========================================================


def normalize_question(question):
    """
    Clean and normalize the user's question.
    """

    question = question.strip().lower()

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


# =========================================================
# DETECT METRIC
# =========================================================

def detect_metric(question):
    """
    Identify the main business metric in the question.
    """

    if any(
        word in question
        for word in [
            "revenue",
            "sales",
            "turnover"
        ]
    ):
        return "revenue"

    if any(
        word in question
        for word in [
            "order value",
            "aov",
            "average order"
        ]
    ):
        return "average_order_value"

    if any(
        word in question
        for word in [
            "quantity",
            "units",
            "volume"
        ]
    ):
        return "quantity"

    if any(
        word in question
        for word in [
            "orders",
            "number of orders"
        ]
    ):
        return "orders"

    return "unknown"


# =========================================================
# DETECT TIME PERIOD
# =========================================================

def detect_month(question):
    """
    Identify a month mentioned in the question.
    """

    months = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12"
    }

    for month, month_number in months.items():

        if month in question:
            return {
                "name": month,
                "number": month_number
            }

    return None


# =========================================================
# DETECT COMPARISON
# =========================================================

def detect_comparison(question):
    """
    Identify whether the user wants a comparison.
    """

    if any(
        phrase in question
        for phrase in [
            "compared to",
            "compare",
            "versus",
            "vs",
            "from",
            "against"
        ]
    ):
        return True

    if any(
        word in question
        for word in [
            "drop",
            "decrease",
            "decline",
            "increase",
            "grew",
            "growth",
            "fell",
            "fall"
        ]
    ):
        return True

    return False


# =========================================================
# DETECT ANALYSIS TYPE
# =========================================================

def detect_analysis_type(question):
    """
    Identify what type of business analysis is required.
    """

    if any(
        phrase in question
        for phrase in [
            "why did",
            "why has",
            "why have",
            "reason for",
            "what caused",
            "cause of"
        ]
    ):
        return "root_cause"

    if any(
        phrase in question
        for phrase in [
            "how much",
            "what is",
            "what was",
            "total",
            "calculate"
        ]
    ):
        return "calculation"

    if any(
        phrase in question
        for phrase in [
            "trend",
            "over time",
            "monthly",
            "month by month"
        ]
    ):
        return "trend"

    if any(
        phrase in question
        for phrase in [
            "top",
            "highest",
            "largest",
            "best"
        ]
    ):
        return "ranking"

    if any(
        phrase in question
        for phrase in [
            "lowest",
            "smallest",
            "worst"
        ]
    ):
        return "ranking"

    return "general"
    

# =========================================================
# DETECT DIMENSIONS
# =========================================================

def detect_dimensions(question):
    """
    Identify business dimensions that may be useful
    for breaking down the analysis.
    """

    dimensions = []

    if any(
        word in question
        for word in [
            "category",
            "categories",
            "product"
        ]
    ):
        dimensions.append("category")

    if any(
        word in question
        for word in [
            "customer",
            "customers",
            "client",
            "clients"
        ]
    ):
        dimensions.append("customer")

    if any(
        word in question
        for word in [
            "region",
            "regions",
            "geography",
            "geographic"
        ]
    ):
        dimensions.append("region")

    if any(
        word in question
        for word in [
            "segment",
            "segments"
        ]
    ):
        dimensions.append("segment")

    return dimensions


# =========================================================
# DETECT DIRECTION
# =========================================================

def detect_direction(question):
    """
    Identify whether the question refers to an increase
    or decrease.
    """

    if any(
        word in question
        for word in [
            "drop",
            "decrease",
            "decline",
            "fell",
            "fall",
            "decreased",
            "declined"
        ]
    ):
        return "decrease"

    if any(
        word in question
        for word in [
            "increase",
            "increased",
            "grew",
            "growth",
            "rise",
            "rose"
        ]
    ):
        return "increase"

    return None


# =========================================================
# MAIN QUESTION ANALYZER
# =========================================================

def analyze_question(question):
    """
    Convert a natural-language business question
    into structured analytical intent.
    """

    normalized_question = normalize_question(
        question
    )

    intent = {
        "original_question": question,
        "normalized_question": normalized_question,
        "metric": detect_metric(
            normalized_question
        ),
        "month": detect_month(
            normalized_question
        ),
        "comparison": detect_comparison(
            normalized_question
        ),
        "analysis_type": detect_analysis_type(
            normalized_question
        ),
        "dimensions": detect_dimensions(
            normalized_question
        ),
        "direction": detect_direction(
            normalized_question
        )
    }

    return intent


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_questions = [
        "Why did revenue drop in March?",
        "What was total revenue in March?",
        "Compare revenue by category",
        "Which region had the highest revenue?",
        "Why did sales decrease?",
        "What is the average order value?",
        "Show me the monthly revenue trend"
    ]

    print("=" * 60)
    print("QUESTION ANALYZER")
    print("=" * 60)

    for question in test_questions:

        print("\nQuestion:")
        print(question)

        result = analyze_question(
            question
        )

        print("\nDetected intent:")

        for key, value in result.items():

            print(
                f"{key}: {value}"
            )

        print("-" * 60)