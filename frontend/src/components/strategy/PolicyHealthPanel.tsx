import type {
  LucideIcon,
} from "lucide-react";

import {
  Crosshair,
  Gauge,
  GitBranch,
  Network,
} from "lucide-react";

import type {
  StrategyOverview,
} from "../../types/strategy";


interface PolicyHealthPanelProps {
  overview: StrategyOverview;
}


function PolicyHealthPanel({
  overview,
}: PolicyHealthPanelProps) {
  const uniqueRate =
    overview.states_with_legal_actions > 0
      ? (
          overview.states_with_unique_best_action /
          overview.states_with_legal_actions
        )
      : 0;

  return (
    <section className="policy-health-panel">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            POLICY STRUCTURE
          </span>
          <h3>Learned Policy Health</h3>
        </div>
      </div>

      <div className="policy-health-grid">
        <PolicyStat
          icon={Network}
          label="Analyzed states"
          value={String(overview.analyzed_states)}
        />
        <PolicyStat
          icon={Crosshair}
          label="Non-zero states"
          value={String(overview.states_with_nonzero_q)}
        />
        <PolicyStat
          icon={GitBranch}
          label="Unique policy"
          value={`${(uniqueRate * 100).toFixed(1)}%`}
        />
        <PolicyStat
          icon={Gauge}
          label="Mean action gap"
          value={overview.mean_action_gap.toFixed(4)}
        />
      </div>

      <div className="policy-confidence-strip">
        <div>
          <span>Mean policy separation</span>
          <strong>
            {(
              overview.mean_normalized_confidence * 100
            ).toFixed(1)}
            %
          </strong>
        </div>

        <div className="confidence-track">
          <div
            className="confidence-fill"
            style={{
              width: `${Math.min(
                100,
                overview.mean_normalized_confidence * 100,
              )}%`,
            }}
          />
        </div>

        <small>
          Separation score, not probability of
          correctness.
        </small>
      </div>
    </section>
  );
}


interface PolicyStatProps {
  icon: LucideIcon;
  label: string;
  value: string;
}


function PolicyStat({
  icon: Icon,
  label,
  value,
}: PolicyStatProps) {
  return (
    <div className="policy-stat">
      <Icon size={13} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}


export default PolicyHealthPanel;
