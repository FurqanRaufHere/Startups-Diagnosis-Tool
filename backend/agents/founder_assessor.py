from pydantic import BaseModel, Field
from utils.llm_client import call_llm


class FounderAssessment(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    founder_market_fit: str  # strong / moderate / weak
    execution_risk: str  # low / medium / high
    credibility_flags: list[str] = Field(default_factory=list)
    commentary: str


def assess_founder(founder_info: dict, claims: dict) -> FounderAssessment:
    system = (
        "You are a venture capital partner assessing founder risk. "
        "Evaluate founder-market fit, execution credibility, and background alignment. "
        "Risk score: 0=low risk, 100=extreme risk. Be direct about weaknesses."
    )
    user = (
        f"Founder background: {founder_info}\n\n"
        f"Startup industry: {claims.get('industry')}\n"
        f"Problem being solved: {claims.get('problem_statement')}\n\n"
        f"Assess founder risk."
    )
    return call_llm(system, user, FounderAssessment)