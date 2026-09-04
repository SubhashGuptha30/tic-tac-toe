import {
  Info,
} from "lucide-react";

import type {
  DecisionEvent,
} from "../../types/decision";


interface DecisionExplanationProps {
  decision: DecisionEvent;
  visible: boolean;
}


function DecisionExplanation({
  decision,
  visible,
}: DecisionExplanationProps) {
  return (
    <section
      className={[
        "decision-explanation-card",
        visible ? "revealed" : "concealed",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            DETERMINISTIC NARRATIVE
          </span>
          <h3>Why This Move?</h3>
        </div>

        <Info size={14} />
      </div>

      <p className="decision-explanation-text">
        {decision.explanation}
      </p>

      <div className="decision-tactical-labels">
        {decision.tactical_labels.length === 0 ? (
          <span>NO TACTICAL LABEL</span>
        ) : (
          decision.tactical_labels.map((label) => (
            <span key={label}>
              {label.replaceAll("_", " ")}
            </span>
          ))
        )}
      </div>

      <div className="decision-interpretation-note">
        <Info size={12} />
        <p>
          This explains the policy-selection
          mechanism and stored values at decision
          time. It does not claim human-like
          reasoning or symbolic understanding.
        </p>
      </div>
    </section>
  );
}


export default DecisionExplanation;
