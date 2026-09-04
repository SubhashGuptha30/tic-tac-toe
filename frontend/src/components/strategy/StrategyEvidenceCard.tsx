import type {
  LucideIcon,
} from "lucide-react";

import type {
  StrategyMetric,
} from "../../types/strategy";


interface StrategyEvidenceCardProps {
  metric: StrategyMetric;
  icon: LucideIcon;
  selected: boolean;
  onSelect: () => void;
}


function StrategyEvidenceCard({
  metric,
  icon: Icon,
  selected,
  onSelect,
}: StrategyEvidenceCardProps) {
  const percentage = Math.max(
    0,
    Math.min(
      100,
      metric.evidence_rate * 100,
    ),
  );

  return (
    <button
      type="button"
      className={
        selected
          ? "strategy-evidence-card selected"
          : "strategy-evidence-card"
      }
      onClick={onSelect}
    >
      <div className="strategy-card-top">
        <div className="strategy-card-label">
          <Icon size={14} />
          <span>{metric.label}</span>
        </div>

        <strong>
          {percentage.toFixed(1)}%
        </strong>
      </div>

      <div className="strategy-progress-track">
        <div
          className="strategy-progress-fill"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>

      <div className="strategy-card-bottom">
        <span>
          {metric.opportunities} opportunities
        </span>
        <span>
          {metric.aligned_states.toFixed(1)} aligned
        </span>
      </div>
    </button>
  );
}


export default StrategyEvidenceCard;
