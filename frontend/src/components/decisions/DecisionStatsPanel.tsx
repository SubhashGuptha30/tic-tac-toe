import {
  BarChart3,
  BrainCircuit,
  Gauge,
  GitBranch,
} from "lucide-react";

import type {
  LucideIcon,
} from "lucide-react";
import type {
  DecisionStats,
} from "../../types/decision";


interface DecisionStatsPanelProps {
  stats: DecisionStats | null;
}


function DecisionStatsPanel({
  stats,
}: DecisionStatsPanelProps) {
  if (!stats) {
    return (
      <section className="decision-stats-card">
        <div className="workspace-empty">
          Decision statistics unavailable.
        </div>
      </section>
    );
  }

  return (
    <section className="decision-stats-card">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            POLICY HEALTH
          </span>
          <h3>Decision Stats</h3>
        </div>
      </div>

      <div className="decision-stats-grid">
        <Stat
          icon={BrainCircuit}
          label="decisions"
          value={String(stats.total_decisions)}
        />
        <Stat
          icon={Gauge}
          label="mean epsilon"
          value={stats.mean_epsilon.toFixed(3)}
        />
        <Stat
          icon={BarChart3}
          label="greedy rate"
          value={`${(
            stats.greedy_selection_rate * 100
          ).toFixed(0)}%`}
        />
        <Stat
          icon={GitBranch}
          label="ties"
          value={String(stats.decisions_with_ties)}
        />
      </div>

      <div className="decision-mode-distribution">
        <div className="mode-distribution-header">
          <span>
            explore{" "}
            {(
              stats.exploration_rate * 100
            ).toFixed(0)}
            %
          </span>
          <span>
            exploit{" "}
            {(
              stats.exploitation_rate * 100
            ).toFixed(0)}
            %
          </span>
        </div>

        <div className="mode-distribution-track">
          <span
            className="mode-explore-fill"
            style={{
              width: `${stats.exploration_rate * 100}%`,
            }}
          />
          <span
            className="mode-exploit-fill"
            style={{
              width: `${stats.exploitation_rate * 100}%`,
            }}
          />
        </div>
      </div>

      <div className="decision-stats-footer">
        <span>mean action gap</span>
        <strong>
          {stats.mean_action_gap.toFixed(4)}
        </strong>
      </div>
    </section>
  );
}


interface StatProps {
  icon: LucideIcon;
  label: string;
  value: string;
}


function Stat({
  icon: Icon,
  label,
  value,
}: StatProps) {
  return (
    <div className="decision-stat">
      <Icon size={13} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}


export default DecisionStatsPanel;
