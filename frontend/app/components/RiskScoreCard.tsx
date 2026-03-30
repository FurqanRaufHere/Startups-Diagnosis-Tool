type RiskScoreCardProps = {
  score: number;
  grade: string;
};

function getTone(score: number) {
  if (score <= 30) return "Low";
  if (score <= 50) return "Moderate";
  if (score <= 70) return "High";
  return "Critical";
}

export default function RiskScoreCard({ score, grade }: RiskScoreCardProps) {
  const safeScore = Math.max(0, Math.min(100, Math.round(score)));
  const ringStyle = {
    background: `conic-gradient(#0e7490 ${safeScore * 3.6}deg, #d7c9b1 0deg)`,
  };

  return (
    <article className="risk-card card">
      <div className="score-ring" style={ringStyle}>
        <div className="score-core">
          <span>{safeScore}</span>
          <small>/100</small>
        </div>
      </div>
      <div>
        <h2>Composite Risk</h2>
        <p>Grade {grade}</p>
        <strong>{getTone(safeScore)} Risk</strong>
      </div>
    </article>
  );
}
