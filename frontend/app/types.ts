export type ReportData = {
  id?: string;
  startup_name: string;
  overall_risk_score: number;
  investment_grade: string;
  financial_risk: number;
  market_risk: number;
  founder_risk: number;
  red_flags: string[];
  memo_text: string;
  extracted_claims?: Record<string, string>;
};
