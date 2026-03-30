"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

type AnalyzeResponse = {
  report_id: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

export default function UploadForm() {
  const router = useRouter();

  const [pitchDeck, setPitchDeck] = useState<File | null>(null);
  const [financials, setFinancials] = useState<File | null>(null);
  const [founderName, setFounderName] = useState("");
  const [founderBackground, setFounderBackground] = useState("");
  const [priorExits, setPriorExits] = useState("None");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => {
    return !!pitchDeck && founderName.trim() && founderBackground.trim() && !isLoading;
  }, [pitchDeck, founderName, founderBackground, isLoading]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit || !pitchDeck) return;

    setError(null);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("pitch_deck", pitchDeck);
      if (financials) formData.append("financials", financials);
      formData.append("founder_name", founderName.trim());
      formData.append("founder_background", founderBackground.trim());
      formData.append("prior_exits", priorExits.trim() || "None");

      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const details = await response.text();
        throw new Error(details || "Upload failed");
      }

      const data = (await response.json()) as AnalyzeResponse;
      router.push(`/report/${data.report_id}`);
    } catch (uploadError) {
      const message = uploadError instanceof Error ? uploadError.message : "Unknown error";
      console.error("Upload error details:", uploadError);
      console.error("API_BASE:", API_BASE);
      setError(`Could not complete analysis: ${message}`);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form className="upload-form card" onSubmit={onSubmit}>
      <div className="field-grid">
        <label>
          <span>Pitch Deck (PDF)</span>
          <input
            type="file"
            accept=".pdf"
            required
            onChange={(event) => setPitchDeck(event.target.files?.[0] || null)}
          />
        </label>

        <label>
          <span>Financials (optional)</span>
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.json,.txt"
            onChange={(event) => setFinancials(event.target.files?.[0] || null)}
          />
        </label>

        <label>
          <span>Founder Name</span>
          <input value={founderName} onChange={(event) => setFounderName(event.target.value)} required />
        </label>

        <label>
          <span>Founder Background</span>
          <textarea
            value={founderBackground}
            rows={4}
            onChange={(event) => setFounderBackground(event.target.value)}
            required
          />
        </label>

        <label>
          <span>Prior Exits</span>
          <input value={priorExits} onChange={(event) => setPriorExits(event.target.value)} />
        </label>
      </div>

      {error && <p className="form-error">{error}</p>}

      <button className="cta" type="submit" disabled={!canSubmit}>
        {isLoading ? "Analyzing startup..." : "Run Full Diagnosis"}
      </button>
    </form>
  );
}
