import type {
  LucideIcon,
} from "lucide-react";


interface MetricCardProps {
  label: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  tone?: "cyan" | "green" | "amber" | "violet";
}


function MetricCard({
  label,
  value,
  subtitle,
  icon: Icon,
  tone = "cyan",
}: MetricCardProps) {
  return (
    <div
      className={
        `analytics-metric-card tone-${tone}`
      }
    >
      <div className="metric-card-top">
        <span>{label}</span>

        <Icon size={14} />
      </div>

      <strong>{value}</strong>

      {subtitle && (
        <small>{subtitle}</small>
      )}
    </div>
  );
}


export default MetricCard;
