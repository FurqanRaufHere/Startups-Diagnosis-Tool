from pydantic import BaseModel, Field
from typing import Optional
from utils.llm_client import call_llm


class ExtractedClaims(BaseModel):
    startup_name: str
    industry: str
    problem_statement: str
    proposed_solution: str
    target_customer: str
    revenue_model: str
    tam_claim: str  # Total Addressable Market as stated
    growth_assumption: str
    competitive_advantage: str
    key_metrics_mentioned: list[str] = Field(default_factory=list)
    red_flag_claims: list[str] = Field(default_factory=list)  # Suspicious or vague claims


def extract_claims(pitch_text: str) -> ExtractedClaims:
    system = (
        "You are a senior venture capital analyst. Extract structured business claims "
        "from pitch deck text. Be skeptical. Flag vague, unsubstantiated, or inflated claims "
        "in red_flag_claims. Do not invent information not present in the text."
    )
    user = f"Extract structured claims from this pitch deck:\n\n{pitch_text}"
    return call_llm(system, user, ExtractedClaims)