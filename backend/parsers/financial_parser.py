import pandas as pd
from pathlib import Path
from typing import Optional


def parse_financials(file_path: str) -> Optional[dict]:
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix == ".csv":
            df = pd.read_csv(file_path)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(file_path)
        else:
            return None
    except Exception:
        return None

    if df.empty:
        return None

    df = df.dropna(how="all").fillna(0)

    # Look for revenue/expense columns heuristically
    revenue_col = _find_column(df, ["revenue", "sales", "income"])
    expense_col = _find_column(df, ["expense", "cost", "burn", "expenditure"])

    result = {"raw_summary": df.head(20).to_dict(orient="records")}

    if revenue_col:
        values = pd.to_numeric(df[revenue_col], errors="coerce").dropna()
        result["revenue_series"] = values.tolist()
        result["revenue_cagr"] = _compute_cagr(values.tolist())

    if expense_col:
        values = pd.to_numeric(df[expense_col], errors="coerce").dropna()
        result["expense_series"] = values.tolist()
        result["avg_monthly_burn"] = values.mean()

    if revenue_col and expense_col:
        rev = pd.to_numeric(df[revenue_col], errors="coerce").fillna(0)
        exp = pd.to_numeric(df[expense_col], errors="coerce").fillna(0)
        result["net_series"] = (rev - exp).tolist()

    return result


def _find_column(df: pd.DataFrame, keywords: list[str]) -> Optional[str]:
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None


def _compute_cagr(values: list[float]) -> Optional[float]:
    if len(values) < 2 or values[0] == 0:
        return None
    n = len(values) - 1
    try:
        return round((values[-1] / values[0]) ** (1 / n) - 1, 4)
    except (ZeroDivisionError, ValueError):
        return None