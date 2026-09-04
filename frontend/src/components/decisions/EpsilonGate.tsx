import {
  Dices,
} from "lucide-react";

import type {
  DecisionEvent,
} from "../../types/decision";


interface EpsilonGateProps {
  decision: DecisionEvent;
  visible: boolean;
}


function EpsilonGate({
  decision,
  visible,
}: EpsilonGateProps) {
  const isExploration =
    decision.decision_mode === "exploration";
  const epsilonPercent =
    clamp01(decision.epsilon) * 100;
  const drawPercent =
    clamp01(decision.exploration_draw) * 100;

  return (
    <section
      className={[
        "epsilon-gate-card",
        isExploration
          ? "explore"
          : "exploit",
        visible ? "revealed" : "concealed",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            STOCHASTIC POLICY GATE
          </span>
          <h3>Epsilon-Greedy Test</h3>
        </div>

        <span
          className={[
            "decision-mode-badge",
            isExploration
              ? "explore"
              : "exploit",
          ].join(" ")}
        >
          {isExploration
            ? "EXPLORE"
            : "EXPLOIT"}
        </span>
      </div>

      <div className="epsilon-number-grid">
        <div>
          <Dices size={12} />
          <span>epsilon threshold</span>
          <strong>
            {decision.epsilon.toFixed(4)}
          </strong>
        </div>

        <div>
          <Dices size={12} />
          <span>random draw</span>
          <strong>
            {decision.exploration_draw.toFixed(4)}
          </strong>
        </div>
      </div>

      <div className="epsilon-axis">
        <span className="epsilon-axis-line" />
        <span
          className="epsilon-threshold-marker"
          style={{
            left: `${epsilonPercent}%`,
          }}
        >
          <span>eps</span>
        </span>
        <span
          className="epsilon-draw-marker"
          style={{
            left: `${drawPercent}%`,
          }}
        >
          <span>u</span>
        </span>

        <div className="epsilon-axis-labels">
          <span>0</span>
          <span>1</span>
        </div>
      </div>

      <div className="gate-equation">
        <code>
          {decision.exploration_draw.toFixed(4)}
          {" < "}
          {decision.epsilon.toFixed(4)}
        </code>

        <strong>
          {isExploration ? "TRUE" : "FALSE"}
        </strong>
      </div>

      <p className="gate-result">
        {isExploration
          ? "The policy allowed a random legal action. This may still land on a greedy action by chance."
          : "The exploration draw exceeded epsilon, so the policy selected from the greedy action set."}
      </p>
    </section>
  );
}


function clamp01(value: number): number {
  return Math.min(
    1,
    Math.max(0, value),
  );
}


export default EpsilonGate;
