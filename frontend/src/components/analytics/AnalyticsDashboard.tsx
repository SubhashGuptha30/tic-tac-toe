import {
  Activity,
  BrainCircuit,
  Database,
  Gauge,
  Target,
  TrendingUp,
} from "lucide-react";

import AnalyticsHeader from "./AnalyticsHeader";
import BrainActivity from "./BrainActivity";
import EpsilonChart from "./EpsilonChart";
import LearningCurveChart from "./LearningCurveChart";
import LearningEventStream from "./LearningEventStream";
import MetricCard from "./MetricCard";
import OutcomeDistribution from "./OutcomeDistribution";
import RewardChart from "./RewardChart";
import TDErrorChart from "./TDErrorChart";
import type {
  AnalyticsDataset,
  AnalyticsOverview,
  LearningUpdateDetail,
} from "../../types/analytics";
import type {
  AgentMetrics,
} from "../../types/game";


interface AnalyticsDashboardProps {
  overview: AnalyticsOverview | null;
  dataset: AnalyticsDataset;
  updates: LearningUpdateDetail[];
  metrics: AgentMetrics | null;
  isAgentThinking: boolean;
  loading: boolean;
  lastUpdated: Date | null;
}


function AnalyticsDashboard({
  overview,
  dataset,
  updates,
  metrics,
  isAgentThinking,
  loading,
  lastUpdated,
}: AnalyticsDashboardProps) {
  const currentEpsilon =
    overview?.current_epsilon ??
    metrics?.epsilon ??
    null;
  const learnedStateActions =
    metrics?.learned_state_actions ??
    getLearnedActionCount(overview);
  const agentWinRate =
    overview?.win_rates.agent_win_rate ??
    null;
  const humanWinRate =
    overview?.win_rates.human_win_rate ??
    null;
  const drawRate =
    overview?.win_rates.draw_rate ??
    null;
  const recentMeanAbsoluteTDError =
    overview?.td_error_health
      .recent_mean_absolute_td_error ??
    overview?.td_error_health
      .mean_absolute_td_error ??
    null;
  const explorationRate =
    overview?.exploration_rate ?? null;
  const exploitationRate =
    overview?.exploitation_rate ?? null;

  return (
    <div className="analytics-dashboard">
      <AnalyticsHeader
        loading={loading}
        lastUpdated={lastUpdated}
      />

      <div className="analytics-scroll-area">
        <section className="analytics-metric-grid">
          <MetricCard
            label="Known states"
            value={formatInteger(
              overview?.known_states ??
                metrics?.states_known,
            )}
            subtitle={`${formatInteger(
              overview?.persisted_state_actions,
            )} persisted actions`}
            icon={BrainCircuit}
            tone="cyan"
          />

          <MetricCard
            label="Learned actions"
            value={formatInteger(
              learnedStateActions,
            )}
            subtitle="non-zero Q(s, a) memory"
            icon={Database}
            tone="green"
          />

          <MetricCard
            label="Agent win rate"
            value={formatPercent(agentWinRate)}
            subtitle={`${formatPercent(
              humanWinRate,
            )} human / ${formatPercent(
              drawRate,
            )} draw`}
            icon={TrendingUp}
            tone="violet"
          />

          <MetricCard
            label="Current epsilon"
            value={formatFloat(
              currentEpsilon,
              4,
            )}
            subtitle={`${formatInteger(
              overview?.exploration_moves ??
                metrics?.exploration_moves,
            )} explore / ${formatInteger(
              overview?.exploitation_moves ??
                metrics?.exploitation_moves,
            )} exploit`}
            icon={Gauge}
            tone="amber"
          />

          <MetricCard
            label="Total updates"
            value={formatInteger(
              overview?.td_error_health
                .total_updates ??
                metrics?.total_updates,
            )}
            subtitle={`recent |d| ${formatFloat(
              recentMeanAbsoluteTDError,
              4,
            )}`}
            icon={Activity}
            tone="cyan"
          />

          <MetricCard
            label="Exploration rate"
            value={formatPercent(
              explorationRate,
            )}
            subtitle={`${formatPercent(
              exploitationRate,
            )} exploit share`}
            icon={Target}
            tone="green"
          />
        </section>

        <BrainActivity
          overview={overview}
          metrics={metrics}
          isAgentThinking={isAgentThinking}
        />

        <LearningCurveChart
          data={dataset.learning_curve}
        />

        <OutcomeDistribution
          outcomes={overview?.outcomes ?? null}
          timeline={dataset.outcome_timeline}
        />

        <TDErrorChart
          data={dataset.td_error_curve}
        />

        <RewardChart
          data={dataset.reward_trajectory}
        />

        <EpsilonChart
          data={dataset.epsilon_curve}
          currentEpsilon={currentEpsilon}
        />

        <LearningEventStream
          updates={updates}
        />
      </div>
    </div>
  );
}


function getLearnedActionCount(
  overview: AnalyticsOverview | null,
) {
  if (!overview) {
    return null;
  }

  return (
    overview.q_value_health
      .positive_q_values +
    overview.q_value_health
      .negative_q_values
  );
}


function formatInteger(
  value: number | null | undefined,
) {
  if (value === null || value === undefined) {
    return "--";
  }

  return value.toLocaleString();
}


function formatPercent(
  value: number | null | undefined,
) {
  if (value === null || value === undefined) {
    return "--";
  }

  return `${(value * 100).toFixed(1)}%`;
}


function formatFloat(
  value: number | null | undefined,
  digits: number,
) {
  if (value === null || value === undefined) {
    return "--";
  }

  return value.toFixed(digits);
}


export default AnalyticsDashboard;
