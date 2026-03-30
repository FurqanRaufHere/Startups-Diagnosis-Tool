"use client";

import { useParams } from "next/navigation";

type MemoExportProps = {
  startupName: string;
  memoText: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

export default function MemoExport({ startupName, memoText }: MemoExportProps) {
  const params = useParams<{ id: string }>();
  const reportId = params?.id;

  async function downloadPdf() {
    if (!reportId) return;

    try {
      const response = await fetch(`${API_BASE}/report/${reportId}/pdf`);
      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${startupName || "startup"}-report.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("PDF download error:", error);
      alert("Failed to download PDF report");
    }
  }

  return (
    <article className="memo card">
      <h2>Investment Memo</h2>
      <p>Export the generated memo as a professional PDF report.</p>
      <button onClick={downloadPdf} disabled={!reportId}>
        Download PDF Report
      </button>
    </article>
  );
}
