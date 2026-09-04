import {
  Activity,
  BrainCircuit,
  Database,
  Gauge,
  Sigma,
  Target,
} from "lucide-react";

import type {
  AnalyticsOverview,
} from "../../types/analytics";
import type {
  AgentMetrics,
} from "../../types/game";


interface BrainActivityProps {
  overview: AnalyticsOverview | null;
  metrics: AgentMetrics | null;
  isAgentThinking: boolean;
}


function BrainActivity({
  overview,
  metrics,
  isAgentThinking,
}: BrainActivityProps) {
  const knownStates =
    overview?.known_states ??
    metrics?.states_known ??
    0;
  const persistedActions =
    overview?.persisted_state_actions ?? 0;
  const learnedNonZeroActions =
    metrics?.learned_state_actions ??
    getLearnedActionCount(overview);
  const explorationRate =
    overview?.exploration_rate ?? null;
  const exploitationRate =
    overview?.exploitation_rate ?? null;
  const meanAbsoluteQ =
    overview?.q_value_health.mean_absolute_q ??
    null;
  const recentMeanAbsoluteTDError =
    overview?.td_error_health
      .recent_mean_absolute_td_error ??
    overview?.td_error_health
      .mean_absolute_td_error ??
    null;

  return (
    <section
      className={[
        "brain-activity-card",
        isAgentThinking ? "thinking" : "",
      ].join(" ")}
    >
      <div className="brain-activity-header">
        <div>
          <span className="chart-eyebrow">
            EVOLVING BRAIN
          </span>

          <h3>
            Agent Memory Topology
          </h3>
        </div>

        <div className="brain-status">
          <span />
          {isAgentThinking
            ? "PROCESSING"
            : "STABLE"}
        </div>
      </div>

      <div className="brain-core">
        <div className="brain-orbit orbit-one">
          <div className="brain-node node-a" />
          <div className="brain-node node-b" />
        </div>

        <div className="brain-orbit orbit-two">
          <div className="brain-node node-c" />
          <div className="brain-node node-d" />
        </div>

        <div className="brain-center">
          <span>KNOWN STATES</span>
          <strong>{knownStates}</strong>
        </div>
      </div>

      <div className="brain-stat-grid">
        <BrainStat
          icon={Database}
          label="Persisted actions"
          value={String(persistedActions)}
        />

        <BrainStat
          icon={BrainCircuit}
          label="Non-zero Q"
          value={String(learnedNonZeroActions)}
        />

        <BrainStat
          icon={Gauge}
          label="Explore rate"
          value={formatPercent(explorationRate)}
        />

        <BrainStat
          icon={Target}
          label="Exploit rate"
          value={formatPercent(exploitationRate)}
        />

        <BrainStat
          icon={Sigma}
          label="Mean |Q|"
          value={formatFloat(meanAbsoluteQ, 4)}
        />

        <BrainStat
          icon={Activity}
          label="Recent |d|"
          value={formatFloat(
            recentMeanAbsoluteTDError,
            4,
          )}
        />
      </div>
    </section>
  );
}


interface BrainStatProps {
  icon: typeof Database;
  label: string;
  value: string;
}


function BrainStat({
  icon: Icon,
  label,
  value,
}: BrainStatProps) {
  return (
    <div className="brain-stat">
      <Icon size={14} />

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}


function getLearnedActionCount(
  overview: AnalyticsOverview | null,
) {
  if (!overview) {
    return 0;
  }

  return (
    overview.q_value_health
      .positive_q_values +
    overview.q_value_health
      .negative_q_values
  );
}


function formatPercent(
  value: number | null,
) {
  if (value === null) {
    return "--";
  }

  return `${(value * 100).toFixed(1)}%`;
}


function formatFloat(
  value: number | null,
  digits: number,
) {
  if (value === null) {
    return "--";
  }

  return value.toFixed(digits);
}


export default BrainActivity;
