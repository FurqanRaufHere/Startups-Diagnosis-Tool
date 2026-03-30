import json
import logging
import shutil
import uuid
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import tempfile
import io

from db import init_db, get_db, Report
from pipeline import run_pipeline
from utils.memo_generator import generate_memo_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Due Diligence Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (permissive for debugging)
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/analyze")
async def analyze(
    pitch_deck: UploadFile = File(...),
    financials: Optional[UploadFile] = File(None),
    founder_name: str = Form(...),
    founder_background: str = Form(...),
    prior_exits: str = Form(default="None"),
    db: AsyncSession = Depends(get_db),
):
    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir()

    # Save uploaded files
    pdf_path = job_dir / "pitch.pdf"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pitch_deck.file, f)

    financial_path = None
    if financials and financials.filename:
        suffix = Path(financials.filename).suffix
        financial_path = job_dir / f"financials{suffix}"
        with open(financial_path, "wb") as f:
            shutil.copyfileobj(financials.file, f)

    founder_info = {
        "name": founder_name,
        "background": founder_background,
        "prior_exits": prior_exits,
    }

    # Run pipeline synchronously (fine for demo)
    try:
        result = await asyncio.to_thread(
            run_pipeline,
            str(pdf_path),
            str(financial_path) if financial_path else None,
            founder_info,
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Persist report
    report = Report(
        id=job_id,
        startup_name=result["startup_name"],
        overall_risk_score=result["overall_risk_score"],
        investment_grade=result["investment_grade"],
        financial_risk=result["financial_risk"],
        market_risk=result["market_risk"],
        founder_risk=result["founder_risk"],
        extracted_claims=json.dumps(result["extracted_claims"]),
        financial_metrics=json.dumps(result["financial_metrics"]),
        red_flags=json.dumps(result["red_flags"]),
        memo_text=result["memo_text"],
    )
    db.add(report)
    await db.commit()

    return {"report_id": job_id, "result": result}


@app.get("/report/{report_id}")
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.to_dict()


@app.get("/report/{report_id}/pdf")
async def download_report_pdf(report_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report_dict = report.to_dict()
    
    # Generate PDF in a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
    
    try:
        generate_memo_pdf(report_dict, pdf_path)
        
        # Read the PDF file into memory
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Clean up temp file
        os.unlink(pdf_path)
        
        # Return as StreamingResponse
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report.startup_name or "startup"}-report.pdf"'}
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")



@app.get("/reports")
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).order_by(Report.created_at.desc()).limit(20))
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "startup_name": r.startup_name,
            "overall_risk_score": float(r.overall_risk_score or 0),
            "investment_grade": r.investment_grade,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]