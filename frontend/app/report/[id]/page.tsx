"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import MemoExport from "../../components/MemoExport";
import RedFlagList from "../../components/RedFlagList";
import RiskScoreCard from "../../components/RiskScoreCard";
import type { ReportData } from "../../types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function ReportPage() {
  const params = useParams<{ id: string }>();
  const reportId = params?.id;

  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadReport() {
      if (!reportId) return;
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/report/${reportId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = (await response.json()) as ReportData;
        setReport(data);
      } catch (loadError) {
        const message = loadError instanceof Error ? loadError.message : "Unknown error";
        setError(`Unable to load report: ${message}`);
      } finally {
        setIsLoading(false);
      }
    }

    void loadReport();
  }, [reportId]);

  const breakdown = useMemo(() => {
    if (!report) return [];
    return [
      { label: "Financial", value: report.financial_risk },
      { label: "Market", value: report.market_risk },
      { label: "Founder", value: report.founder_risk },
    ];
  }, [report]);

  if (isLoading) {
    return (
      <main>
        <section className="card loading">Compiling diagnosis report...</section>
      </main>
    );
  }

  if (error || !report) {
    return (
      <main>
        <section className="card loading">
          <p>{error || "Report unavailable"}</p>
          <Link href="/">Return home</Link>
        </section>
      </main>
    );
  }

  return (
    <main>
      <section className="hero card report-title">
        <p className="eyebrow">REPORT #{reportId}</p>
        <h1>{report.startup_name}</h1>
      </section>

      <section className="report-grid stagger">
        <RiskScoreCard score={report.overall_risk_score} grade={report.investment_grade} />

        <article className="breakdown card">
          <h2>Weighted Breakdown</h2>
          <div className="bars">
            {breakdown.map((item) => (
              <div key={item.label} className="bar-row">
                <div>
                  <span>{item.label}</span>
                  <small>{Math.round(item.value)}/100</small>
                </div>
                <div className="bar-track">
                  <div style={{ width: `${Math.max(0, Math.min(100, item.value))}%` }} />
                </div>
              </div>
            ))}
          </div>
        </article>

        <RedFlagList flags={report.red_flags || []} />
        <MemoExport startupName={report.startup_name} memoText={report.memo_text || ""} />
      </section>
    </main>
  );
}
