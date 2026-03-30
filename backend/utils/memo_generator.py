from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER
from pathlib import Path
import datetime


GRADE_COLORS = {
    "A": colors.HexColor("#16a34a"),
    "B": colors.HexColor("#2563eb"),
    "C": colors.HexColor("#d97706"),
    "D": colors.HexColor("#dc2626"),
}


def _risk_label(score: float) -> str:
    if score <= 30:
        return "Low"
    elif score <= 50:
        return "Moderate"
    elif score <= 70:
        return "High"
    return "Critical"


def generate_memo_pdf(report: dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", parent=styles["Normal"],
        fontSize=22, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111827"), spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#6b7280"), spaceAfter=2,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader", parent=styles["Normal"],
        fontSize=13, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111827"), spaceBefore=16, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#374151"), leading=16, spaceAfter=6,
    )
    flag_style = ParagraphStyle(
        "Flag", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#dc2626"), leading=15,
        leftIndent=12, spaceAfter=3,
    )

    story = []

    startup_name = report.get("startup_name", "Unknown Startup")
    grade = report.get("investment_grade", "N/A")
    overall_score = float(report.get("overall_risk_score", 0))
    generated_at = datetime.datetime.now().strftime("%B %d, %Y")

    story.append(Paragraph("Due Diligence Report", title_style))
    story.append(Paragraph(startup_name, ParagraphStyle(
        "StartupName", parent=styles["Normal"],
        fontSize=15, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2563eb"), spaceAfter=2,
    )))
    story.append(Paragraph(f"Generated: {generated_at}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 12))

    grade_color = GRADE_COLORS.get(grade, colors.gray)

    summary_data = [
        [
            Paragraph("<b>Overall Risk Score</b>", body_style),
            Paragraph("<b>Investment Grade</b>", body_style),
            Paragraph("<b>Risk Level</b>", body_style),
        ],
        [
            Paragraph(f"<font size=20><b>{overall_score:.0f}/100</b></font>", ParagraphStyle(
                "Score", parent=styles["Normal"], fontSize=20,
                fontName="Helvetica-Bold", textColor=colors.HexColor("#111827"),
            )),
            Paragraph(f"<font size=20><b>{grade}</b></font>", ParagraphStyle(
                "Grade", parent=styles["Normal"], fontSize=20,
                fontName="Helvetica-Bold", textColor=grade_color,
            )),
            Paragraph(f"<font size=14><b>{_risk_label(overall_score)}</b></font>", ParagraphStyle(
                "RiskLabel", parent=styles["Normal"], fontSize=14,
                fontName="Helvetica-Bold", textColor=colors.HexColor("#dc2626"),
            )),
        ],
    ]

    summary_table = Table(summary_data, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Risk Breakdown", section_header_style))

    fin_score = float(report.get("financial_risk", 0))
    mkt_score = float(report.get("market_risk", 0))
    fnd_score = float(report.get("founder_risk", 0))

    breakdown_data = [
        ["Risk Category", "Score", "Level", "Weight"],
        ["Financial Risk", f"{fin_score:.0f}/100", _risk_label(fin_score), "40%"],
        ["Market Risk", f"{mkt_score:.0f}/100", _risk_label(mkt_score), "35%"],
        ["Founder Risk", f"{fnd_score:.0f}/100", _risk_label(fnd_score), "25%"],
    ]

    breakdown_table = Table(breakdown_data, colWidths=[5 * cm, 3.5 * cm, 4 * cm, 3 * cm])
    breakdown_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 16))

    red_flags = report.get("red_flags", [])
    if red_flags:
        story.append(Paragraph("Red Flags", section_header_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#fca5a5")))
        story.append(Spacer(1, 6))
        for flag in red_flags:
            story.append(Paragraph(f"⚠ {flag}", flag_style))
        story.append(Spacer(1, 8))

    claims = report.get("extracted_claims", {})
    if claims:
        story.append(Paragraph("Key Business Claims", section_header_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
        story.append(Spacer(1, 6))

        claim_fields = [
            ("Industry", "industry"),
            ("Problem Statement", "problem_statement"),
            ("Proposed Solution", "proposed_solution"),
            ("Revenue Model", "revenue_model"),
            ("Target Customer", "target_customer"),
            ("TAM Claim", "tam_claim"),
            ("Growth Assumption", "growth_assumption"),
            ("Competitive Advantage", "competitive_advantage"),
        ]

        for label, key in claim_fields:
            value = claims.get(key, "N/A")
            if value and value != "N/A":
                story.append(Paragraph(f"<b>{label}:</b> {value}", body_style))

    memo_text = report.get("memo_text", "")
    if memo_text:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Investment Memo", section_header_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
        story.append(Spacer(1, 6))
        for para in memo_text.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 4))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This report is AI-generated and intended as a decision-support tool only. "
        "It does not constitute financial or investment advice.",
        ParagraphStyle(
            "Disclaimer", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#9ca3af"),
            alignment=TA_CENTER,
        )
    ))

    doc.build(story)
    return str(path)