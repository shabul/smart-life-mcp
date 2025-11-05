import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
EXPENSES_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.csv"


def analyze_expenses():
    if not EXPENSES_PATH.exists():
        logger.error("Expense data file missing at %s", EXPENSES_PATH)
        return {"error": f"Expense data file missing at {EXPENSES_PATH}"}

    try:
        df = pd.read_csv(EXPENSES_PATH)
    except Exception as exc:  # pragma: no cover - depends on filesystem state
        logger.exception("Failed to read expense data from %s", EXPENSES_PATH)
        return {"error": f"Unable to read expenses: {exc}"}

    required_columns = {"amount", "category"}
    if not required_columns.issubset(df.columns):
        logger.error("Expense CSV missing required columns %s", required_columns)
        return {"error": "Expense CSV must contain 'amount' and 'category' columns"}

    total = df["amount"].sum()
    by_category = df.groupby("category")["amount"].sum().to_dict()
    logger.debug(
        "Expense summary computed with total=%s and categories=%s",
        total,
        by_category,
    )
    return {"total": float(total), "by_category": by_category}
