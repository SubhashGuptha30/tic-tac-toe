import type {
  DecisionEvent,
} from "../../types/decision";


interface QValueSnapshotProps {
  decision: DecisionEvent;
  visible: boolean;
}


function QValueSnapshot({
  decision,
  visible,
}: QValueSnapshotProps) {
  const sorted = [
    ...decision.q_values,
  ].sort(
    (first, second) =>
      second.q_value - first.q_value,
  );
  const values =
    sorted.map((item) => item.q_value);
  const minQ =
    values.length > 0
      ? Math.min(...values)
      : 0;
  const maxQ =
    values.length > 0
      ? Math.max(...values)
      : 0;

  return (
    <section
      className={[
        "q-snapshot-card",
        visible ? "revealed" : "concealed",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            DECISION-TIME SNAPSHOT
          </span>
          <h3>Candidate Q-Values</h3>
        </div>

        <span className="snapshot-count">
          {decision.q_values.length} legal
        </span>
      </div>

      <div className="q-snapshot-list">
        {sorted.map((item, index) => {
          const normalized =
            normalize(item.q_value, minQ, maxQ);

          return (
            <article
              className={[
                "q-snapshot-row",
                item.is_selected
                  ? "selected"
                  : "",
                item.is_greedy
                  ? "greedy"
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
              key={item.action}
              style={{
                transitionDelay:
                  visible
                    ? `${index * 45}ms`
                    : "0ms",
              }}
            >
              <div className="q-action">
                <strong>A{item.action}</strong>
                <span>
                  rank {index + 1}
                </span>
              </div>

              <div className="q-bar-track">
                <div
                  className="q-bar-fill"
                  style={{
                    width: `${normalized}%`,
                  }}
                />
              </div>

              <code>
                {formatQ(item.q_value)}
              </code>

              <div className="q-tags">
                {item.is_greedy && (
                  <span>GREEDY</span>
                )}
                {item.is_selected && (
                  <span>SELECTED</span>
                )}
              </div>
            </article>
          );
        })}
      </div>

      <div className="q-snapshot-footer">
        <div>
          <span>best Q</span>
          <strong>
            {decision.best_q.toFixed(4)}
          </strong>
        </div>

        <div>
          <span>second Q</span>
          <strong>
            {decision.second_best_q.toFixed(4)}
          </strong>
        </div>

        <div>
          <span>action gap</span>
          <strong>
            {decision.action_gap.toFixed(4)}
          </strong>
        </div>
      </div>
    </section>
  );
}


function normalize(
  value: number,
  min: number,
  max: number,
): number {
  if (max === min) {
    return 100;
  }

  return Math.max(
    8,
    ((value - min) / (max - min)) * 92 + 8,
  );
}


function formatQ(value: number): string {
  if (value > 0) {
    return `+${value.toFixed(3)}`;
  }

  return value.toFixed(3);
}


export default QValueSnapshot;
