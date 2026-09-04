import {
  BrainCircuit,
  CircleCheck,
  Gauge,
  ScanLine,
  Shield,
  Trophy,
} from "lucide-react";

import type {
  EvaluationRun,
  PolicySnapshot,
} from "../../types/evaluation";


interface EvaluationReportProps {
  run: EvaluationRun | null;
  snapshot: PolicySnapshot | null;
}


function percentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}


function EvaluationReport({
  run,
  snapshot,
}: EvaluationReportProps) {
  if (!run) {
    return (
      <section className="evaluation-report-card empty">
        <ScanLine size={18} />
        <div>
          <span>EVALUATION REPORT</span>
          <p>
            Run a frozen-policy benchmark to generate
            a reproducible performance report.
          </p>
        </div>
      </section>
    );
  }

  const snapshotHash = snapshot?.q_table_hash.slice(
    0,
    12,
  );

  return (
    <section className="evaluation-report-card">
      <div className="training-card-heading">
        <div>
          <span>EVALUATION REPORT</span>
          <h3>Run #{run.id}</h3>
        </div>
        <span className="evaluation-status-badge">
          {run.status}
        </span>
      </div>

      <div className="evaluation-report-grid">
        <ReportMetric
          icon={Trophy}
          label="Agent wins"
          value={run.agent_wins}
          detail={`${percentage(run.agent_win_rate)} win rate`}
        />
        <ReportMetric
          icon={Shield}
          label="Opponent wins"
          value={run.opponent_wins}
          detail={`${percentage(run.opponent_win_rate)} loss rate`}
        />
        <ReportMetric
          icon={CircleCheck}
          label="Draws"
          value={run.draws}
          detail={`${percentage(run.draw_rate)} draw rate`}
        />
        <ReportMetric
          icon={Gauge}
          label="Avg moves"
          value={run.average_moves.toFixed(2)}
          detail={`${run.completed_games} completed games`}
        />
        <ReportMetric
          icon={BrainCircuit}
          label="Decision confidence"
          value={run.average_decision_confidence.toFixed(3)}
          detail={`mean gap ${run.average_action_gap.toFixed(3)}`}
        />
        <ReportMetric
          icon={ScanLine}
          label="States visited"
          value={run.unique_states_visited}
          detail={`${run.total_decisions} greedy decisions`}
        />
      </div>

      <div className="evaluation-tactics-grid">
        <div>
          <span>Immediate win conversion</span>
          <strong>
            {percentage(
              run.immediate_win_conversion_rate,
            )}
          </strong>
          <small>
            {run.immediate_win_successes} / {run.immediate_win_opportunities}
          </small>
        </div>
        <div>
          <span>Immediate block success</span>
          <strong>
            {percentage(
              run.immediate_block_success_rate,
            )}
          </strong>
          <small>
            {run.immediate_block_successes} / {run.immediate_block_opportunities}
          </small>
        </div>
      </div>

      <div className="evaluation-provenance">
        <span>
          Snapshot #{run.snapshot_id}
          {snapshotHash ? ` | ${snapshotHash}` : ""}
        </span>
        <span>vs {run.opponent_type}</span>
        <span>seed {run.seed ?? "unseeded"}</span>
        <span>{run.tie_breaking_policy}</span>
      </div>
    </section>
  );
}


interface ReportMetricProps {
  icon: typeof Trophy;
  label: string;
  value: number | string;
  detail: string;
}


function ReportMetric({
  icon: Icon,
  label,
  value,
  detail,
}: ReportMetricProps) {
  return (
    <div className="evaluation-report-metric">
      <Icon size={13} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </div>
  );
}


export default EvaluationReport;
