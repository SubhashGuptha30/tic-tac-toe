import type {
  DecisionInspection,
  PolicyConfidenceResponse,
} from "../../types/strategy";


interface PolicyConfidencePanelProps {
  confidence:
    PolicyConfidenceResponse;
  decision:
    DecisionInspection | null;
}


function PolicyConfidencePanel({
  confidence,
  decision,
}: PolicyConfidencePanelProps) {
  const percentage = Math.max(
    0,
    Math.min(
      100,
      confidence.normalized_confidence * 100,
    ),
  );

  return (
    <section className="q-confidence-panel">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            POLICY SEPARATION
          </span>
          <h3>Decision Confidence</h3>
        </div>

        <strong>
          {percentage.toFixed(1)}%
        </strong>
      </div>

      <div className="confidence-track">
        <div
          className="confidence-fill"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>

      <div className="confidence-metrics">
        <div>
          <span>Best Q</span>
          <strong>
            {confidence.best_q.toFixed(4)}
          </strong>
        </div>
        <div>
          <span>Second Q</span>
          <strong>
            {confidence.second_best_q.toFixed(4)}
          </strong>
        </div>
        <div>
          <span>Action gap</span>
          <strong>
            {confidence.action_gap.toFixed(4)}
          </strong>
        </div>
      </div>

      {decision &&
        decision.tactical_labels.length > 0 && (
          <div className="decision-labels">
            {decision.tactical_labels.map(
              (label) => (
                <span key={label}>
                  {label}
                </span>
              ),
            )}
          </div>
        )}

      <small className="confidence-disclaimer">
        This score measures Q-value separation.
        It is not a probability that the
        selected move is correct.
      </small>
    </section>
  );
}


export default PolicyConfidencePanel;
