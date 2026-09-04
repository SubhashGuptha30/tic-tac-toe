import {
  Activity,
  Radio,
} from "lucide-react";


interface AnalyticsHeaderProps {
  loading: boolean;
  lastUpdated: Date | null;
}


function AnalyticsHeader({
  loading,
  lastUpdated,
}: AnalyticsHeaderProps) {
  return (
    <header className="analytics-header">
      <div>
        <div className="analytics-title">
          <Activity size={16} />

          <span>
            LIVE RL LABORATORY
          </span>
        </div>

        <p>
          Online Q-learning telemetry
        </p>
      </div>

      <div
        className={
          loading
            ? "live-indicator syncing"
            : "live-indicator"
        }
      >
        <Radio size={12} />

        <span>
          {loading ? "SYNC" : "LIVE"}
        </span>

        {lastUpdated && (
          <small>
            {lastUpdated.toLocaleTimeString(
              [],
              {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              },
            )}
          </small>
        )}
      </div>
    </header>
  );
}


export default AnalyticsHeader;
