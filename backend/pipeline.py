import logging
from typing import Optional
from parsers.pdf_parser import parse_pdf
from parsers.financial_parser import parse_financials
from agents.claim_extractor import extract_claims
from agents.financial_analyzer import analyze_financials
from agents.market_analyst import analyze_market
from agents.founder_assessor import assess_founder
from agents.risk_aggregator import aggregate_risk

logger = logging.getLogger(__name__)


def run_pipeline(
    pdf_path: str,
    financial_path: Optional[str],
    founder_info: dict,
) -> dict:
    logger.info("Starting pipeline")

    # Parse inputs
    pitch_text = parse_pdf(pdf_path)
    financial_data = parse_financials(financial_path) if financial_path else None

    # Agent 1: Extract claims
    logger.info("Running claim extractor")
    claims = extract_claims(pitch_text)
    claims_dict = claims.model_dump()

    # Agent 2: Financial analysis
    logger.info("Running financial analyzer")
    financial = analyze_financials(claims_dict, financial_data)

    # Agent 3: Market analysis
    logger.info("Running market analyst")
    market = analyze_market(claims_dict)

    # Agent 4: Founder assessment
    logger.info("Running founder assessor")
    founder = assess_founder(founder_info, claims_dict)

    # Collect all red flags
    all_red_flags = (
        claims.red_flag_claims +
        financial.anomalies +
        market.market_red_flags +
        founder.credibility_flags
    )

    # Agent 5: Risk aggregation
    logger.info("Running risk aggregator")
    aggregation = aggregate_risk(
        financial_score=financial.risk_score,
        market_score=market.risk_score,
        founder_score=founder.risk_score,
        all_red_flags=all_red_flags,
        claims=claims_dict,
        financial_commentary=financial.commentary,
        market_commentary=market.commentary,
        founder_commentary=founder.commentary,
    )

    logger.info(f"Pipeline complete. Score: {aggregation.overall_risk_score}")

    return {
        "startup_name": claims.startup_name,
        "overall_risk_score": aggregation.overall_risk_score,
        "investment_grade": aggregation.investment_grade,
        "confidence_score": aggregation.confidence_score,
        "financial_risk": financial.risk_score,
        "market_risk": market.risk_score,
        "founder_risk": founder.risk_score,
        "extracted_claims": claims_dict,
        "financial_metrics": financial.model_dump(),
        "market_analysis": market.model_dump(),
        "founder_assessment": founder.model_dump(),
        "red_flags": aggregation.top_red_flags,
        "memo_text": aggregation.investment_memo,
    }