import type {
  PositionPreferenceMetric,
} from "../../types/strategy";


interface PositionPreferencePanelProps {
  center: PositionPreferenceMetric;
  corner: PositionPreferenceMetric;
  edge: PositionPreferenceMetric;
}


function PositionPreferencePanel({
  center,
  corner,
  edge,
}: PositionPreferencePanelProps) {
  const metrics = [
    center,
    corner,
    edge,
  ];

  return (
    <section className="position-preference-panel">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            SPATIAL POLICY
          </span>
          <h3>Position Preference</h3>
        </div>
      </div>

      <div className="preference-list">
        {metrics.map((metric) => {
          const percentage = Math.max(
            0,
            Math.min(
              100,
              metric.preference_rate * 100,
            ),
          );

          return (
            <div
              className="preference-row"
              key={metric.key}
            >
              <div className="preference-label">
                <span>{metric.label}</span>
                <strong>
                  {percentage.toFixed(1)}%
                </strong>
              </div>

              <div className="preference-track">
                <div
                  className="preference-fill"
                  style={{
                    width: `${percentage}%`,
                  }}
                />
              </div>

              <small>
                {metric.eligible_states} eligible
                states
              </small>
            </div>
          );
        })}
      </div>
    </section>
  );
}


export default PositionPreferencePanel;
