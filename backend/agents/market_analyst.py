from pydantic import BaseModel, Field
from utils.llm_client import call_llm


class MarketAnalysis(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    market_size_assessment: str
    competition_level: str  # low / medium / high / saturated
    key_competitors: list[str] = Field(default_factory=list)
    market_red_flags: list[str] = Field(default_factory=list)
    commentary: str


def analyze_market(claims: dict) -> MarketAnalysis:
    system = (
        "You are a market intelligence analyst. Evaluate market risk for an early-stage startup. "
        "Use your knowledge of the industry to assess competition density, market saturation, "
        "and whether TAM claims are realistic. Risk score: 0=low risk, 100=extreme risk."
    )
    user = (
        f"Industry: {claims.get('industry')}\n"
        f"TAM claim: {claims.get('tam_claim')}\n"
        f"Target customer: {claims.get('target_customer')}\n"
        f"Competitive advantage claimed: {claims.get('competitive_advantage')}\n"
        f"Revenue model: {claims.get('revenue_model')}\n\n"
        f"Assess market risk."
    )
    return call_llm(system, user, MarketAnalysis)