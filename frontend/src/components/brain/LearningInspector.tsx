import type { LearningUpdateData } from "../../types/game";


interface LearningInspectorProps {
  update: LearningUpdateData | null;
}


function LearningInspector({
  update,
}: LearningInspectorProps) {
  if (!update) {
    return (
      <div className="empty-science-state">
        No Q-update recorded yet.
      </div>
    );
  }

  return (
    <div className="learning-inspector">
      <Metric
        label="Reward r"
        value={signed(update.reward)}
      />
      <Metric
        label="Previous Q"
        value={update.old_q.toFixed(4)}
      />
      <Metric
        label="Best future Q"
        value={update.best_future_q.toFixed(4)}
      />
      <Metric
        label="TD target"
        value={update.td_target.toFixed(4)}
      />
      <Metric
        label="TD error"
        value={signed(update.td_error)}
      />
      <Metric
        label="Updated Q"
        value={update.new_q.toFixed(4)}
      />

      <div className="delta-panel">
        <span>Delta Q</span>

        <strong
          className={
            update.delta_q >= 0
              ? "positive-value"
              : "negative-value"
          }
        >
          {signed(update.delta_q)}
        </strong>
      </div>
    </div>
  );
}


interface MetricProps {
  label: string;
  value: string;
}


function Metric({ label, value }: MetricProps) {
  return (
    <div className="metric-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}


function signed(value: number): string {
  if (value > 0) {
    return `+${value.toFixed(4)}`;
  }

  return value.toFixed(4);
}


export default LearningInspector;
