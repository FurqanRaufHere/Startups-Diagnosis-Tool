from pydantic import BaseModel, Field
from typing import Optional
from utils.llm_client import call_llm


class FinancialAnalysis(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    revenue_cagr_percent: Optional[float] = None
    avg_monthly_burn: Optional[float] = None
    runway_months: Optional[float] = None
    anomalies: list[str] = Field(default_factory=list)
    commentary: str


def analyze_financials(claims: dict, financial_data: Optional[dict]) -> FinancialAnalysis:
    fin_context = ""
    computed_metrics = {}

    if financial_data:
        cagr = financial_data.get("revenue_cagr")
        burn = financial_data.get("avg_monthly_burn")
        net = financial_data.get("net_series", [])

        computed_metrics = {
            "revenue_cagr": f"{cagr * 100:.1f}%" if cagr else "N/A",
            "avg_monthly_burn": f"${burn:,.0f}" if burn else "N/A",
            "periods_of_data": len(financial_data.get("revenue_series", [])),
        }

        # Detect unrealistic CAGR deterministically
        anomalies = []
        if cagr and cagr > 3.0:  # >300% CAGR
            anomalies.append(f"Unrealistic revenue CAGR of {cagr*100:.0f}%")

        fin_context = f"Computed metrics: {computed_metrics}\nPre-detected anomalies: {anomalies}"
    else:
        fin_context = "No financial spreadsheet provided. Assess based on pitch deck claims only."

    system = (
        "You are a financial risk analyst specializing in early-stage startups. "
        "Assess financial risk score (0=no risk, 100=extreme risk). "
        "Be critical of unrealistic projections. Flag specific anomalies."
    )
    user = (
        f"Startup claims: {claims}\n\n"
        f"Financial data: {fin_context}\n\n"
        f"Provide financial risk assessment."
    )

    result = call_llm(system, user, FinancialAnalysis)

    # Inject computed values from deterministic analysis
    if financial_data:
        result.revenue_cagr_percent = round((financial_data.get("revenue_cagr") or 0) * 100, 2)
        result.avg_monthly_burn = financial_data.get("avg_monthly_burn")

    return result