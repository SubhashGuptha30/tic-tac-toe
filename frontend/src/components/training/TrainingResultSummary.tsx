import {
  Database,
  Gauge,
  Trophy,
  Zap,
} from "lucide-react";

import type {
  LucideIcon,
} from "lucide-react";
import type {
  TrainingRun,
} from "../../types/training";


interface TrainingResultSummaryProps {
  run: TrainingRun | null;
}


function TrainingResultSummary({
  run,
}: TrainingResultSummaryProps) {
  if (!run) {
    return (
      <section className="training-results-card">
        <div className="workspace-empty">
          Launch a training run to see outcome,
          throughput, epsilon decay, and Q-table
          growth.
        </div>
      </section>
    );
  }

  const completed =
    run.completed_episodes || 1;

  return (
    <section className="training-results-card">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            TRAINING RESULTS
          </span>
          <h3>Run #{run.id}</h3>
        </div>

        <span
          className={[
            "training-status-badge",
            run.status,
          ].join(" ")}
        >
          {run.status}
        </span>
      </div>

      <div className="training-result-grid">
        <ResultMetric
          icon={Trophy}
          label="Agent wins"
          value={String(run.agent_wins)}
          detail={`${formatPercent(
            run.agent_wins / completed,
          )} win rate`}
        />
        <ResultMetric
          icon={Trophy}
          label="Opponent wins"
          value={String(run.opponent_wins)}
          detail={`${formatPercent(
            run.opponent_wins / completed,
          )} loss rate`}
        />
        <ResultMetric
          icon={Gauge}
          label="Draws"
          value={String(run.draws)}
          detail={`${formatPercent(
            run.draws / completed,
          )} draw rate`}
        />
        <ResultMetric
          icon={Zap}
          label="Mean reward"
          value={run.mean_reward.toFixed(3)}
          detail={`total ${run.cumulative_reward.toFixed(2)}`}
        />
      </div>

      <div className="training-delta-grid">
        <div>
          <span>Epsilon</span>
          <strong>
            {run.epsilon_start.toFixed(4)}
            {" -> "}
            {(
              run.epsilon_end ??
              run.epsilon_start
            ).toFixed(4)}
          </strong>
        </div>

        <div>
          <span>Q states</span>
          <strong>
            {run.q_states_start}
            {" -> "}
            {run.q_states_end ??
              run.q_states_start}
          </strong>
        </div>

        <div>
          <span>Q entries</span>
          <strong>
            {run.q_entries_start}
            {" -> "}
            {run.q_entries_end ??
              run.q_entries_start}
          </strong>
        </div>

        <div>
          <span>Throughput</span>
          <strong>
            {run.episodes_per_second
              ? `${run.episodes_per_second.toFixed(
                  0,
                )} ep/s`
              : "--"}
          </strong>
        </div>
      </div>

      <div className="training-run-meta">
        <Database size={12} />
        <span>
          {run.completed_episodes} /{" "}
          {run.requested_episodes} episodes
          against {formatOpponent(run)}
        </span>
      </div>
    </section>
  );
}


interface ResultMetricProps {
  icon: LucideIcon;
  label: string;
  value: string;
  detail: string;
}


function ResultMetric({
  icon: Icon,
  label,
  value,
  detail,
}: ResultMetricProps) {
  return (
    <div className="training-result-metric">
      <Icon size={13} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </div>
  );
}


function formatPercent(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}


function formatOpponent(run: TrainingRun): string {
  if (run.opponent_type !== "mixed") {
    return run.opponent_type;
  }

  return `mixed ${Math.round(
    (run.tactical_probability ?? 0.7) * 100,
  )}% tactical`;
}


export default TrainingResultSummary;
