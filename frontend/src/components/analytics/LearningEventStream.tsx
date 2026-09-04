import type {
  LearningUpdateDetail,
} from "../../types/analytics";


interface LearningEventStreamProps {
  updates: LearningUpdateDetail[];
}


function LearningEventStream({
  updates,
}: LearningEventStreamProps) {
  const recentUpdates = [...updates].sort(
    (left, right) => right.id - left.id,
  );

  return (
    <section className="learning-stream-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            LIVE LEARNING EVENTS
          </span>

          <h3>
            Bellman Update Stream
          </h3>
        </div>

        <span className="episode-count">
          {recentUpdates.length} rows
        </span>
      </div>

      {recentUpdates.length === 0 ? (
        <div className="empty-stream">
          Recent learning updates will
          appear here.
        </div>
      ) : (
        <div className="learning-event-list">
          {recentUpdates.map((update) => (
            <article
              className="learning-event"
              key={update.id}
            >
              <div className="event-top">
                <span>
                  {formatTime(update.created_at)}
                </span>
                <strong>
                  EP {update.episode}
                </strong>
                <span>
                  A{update.action + 1}
                </span>
                <em>
                  {update.terminal
                    ? "TERMINAL"
                    : "STEP"}
                </em>
              </div>

              <div className="event-q-change">
                <code>
                  Q: {update.old_q.toFixed(3)}
                </code>
                <code>
                  -&gt; {update.new_q.toFixed(3)}
                </code>
              </div>

              <div className="event-bottom">
                <span>
                  r {update.reward.toFixed(2)}
                </span>
                <span>
                  d {update.td_error.toFixed(3)}
                </span>
                <span>
                  tgt{" "}
                  {update.td_target.toFixed(3)}
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}


function formatTime(
  timestamp: string,
) {
  return new Date(timestamp)
    .toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
}


export default LearningEventStream;
