from pydantic import BaseModel, Field
from utils.llm_client import call_llm


class RiskAggregation(BaseModel):
    overall_risk_score: float = Field(ge=0, le=100)
    investment_grade: str  # A / B / C / D
    confidence_score: float = Field(ge=0, le=100)
    top_red_flags: list[str] = Field(default_factory=list)
    investment_memo: str  # 3-5 paragraph structured memo


def aggregate_risk(
    financial_score: float,
    market_score: float,
    founder_score: float,
    all_red_flags: list[str],
    claims: dict,
    financial_commentary: str,
    market_commentary: str,
    founder_commentary: str,
) -> RiskAggregation:
    # Deterministic weighted score — not LLM
    weighted_score = round(
        (financial_score * 0.40) +
        (market_score * 0.35) +
        (founder_score * 0.25),
        2
    )

    if weighted_score <= 30:
        grade = "A"
    elif weighted_score <= 50:
        grade = "B"
    elif weighted_score <= 70:
        grade = "C"
    else:
        grade = "D"

    system = (
        "You are a senior venture capital partner writing a due diligence memo. "
        "Write a structured, professional investment memo based on the analysis provided. "
        "Be specific, cite the actual findings, and give a clear recommendation."
    )
    user = (
        f"Startup: {claims.get('startup_name')} | Industry: {claims.get('industry')}\n"
        f"Overall Risk Score: {weighted_score}/100 | Grade: {grade}\n\n"
        f"Financial Risk ({financial_score}/100): {financial_commentary}\n"
        f"Market Risk ({market_score}/100): {market_commentary}\n"
        f"Founder Risk ({founder_score}/100): {founder_commentary}\n\n"
        f"All red flags identified: {all_red_flags}\n"
        f"Key claims: {claims}\n\n"
        f"Write the investment memo and list the top 5 most critical red flags."
    )

    result = call_llm(system, user, RiskAggregation, max_tokens=3000)
    result.overall_risk_score = weighted_score
    result.investment_grade = grade
    return result