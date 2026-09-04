import {
  GitCompareArrows,
} from "lucide-react";

import type {
  EvaluationComparison as EvaluationComparisonData,
} from "../../types/evaluation";


interface EvaluationComparisonProps {
  comparison: EvaluationComparisonData | null;
}


function percentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}


function EvaluationComparison({
  comparison,
}: EvaluationComparisonProps) {
  return (
    <section className="evaluation-comparison-card">
      <div className="training-card-heading">
        <div>
          <span>CONTROLLED COMPARISON</span>
          <h3>Opponent Performance</h3>
        </div>
        <GitCompareArrows size={15} />
      </div>

      {!comparison ? (
        <p className="evaluation-empty-copy">
          Select an evaluation to compare this policy
          snapshot across opponent types.
        </p>
      ) : (
        <>
          <p className="evaluation-comparison-note">
            Snapshot #{comparison.snapshot.id}. Rows use
            the latest completed evaluation for this exact
            immutable policy.
          </p>
          <div className="evaluation-comparison-table">
            <div className="evaluation-comparison-heading">
              <span>Opponent</span>
              <span>Win</span>
              <span>Draw</span>
              <span>Loss</span>
              <span>Confidence</span>
            </div>
            {comparison.rows.map((row) => (
              <div
                className="evaluation-comparison-row"
                key={row.opponent_type}
              >
                <strong>{row.opponent_type}</strong>
                {row.is_available ? (
                  <>
                    <span>{percentage(row.agent_win_rate)}</span>
                    <span>{percentage(row.draw_rate)}</span>
                    <span>{percentage(row.opponent_win_rate)}</span>
                    <span>
                      {row.average_decision_confidence.toFixed(3)}
                    </span>
                  </>
                ) : (
                  <em>Not evaluated</em>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}


export default EvaluationComparison;
