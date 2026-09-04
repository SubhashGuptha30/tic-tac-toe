import {
  ArrowRight,
} from "lucide-react";

import type {
  EpisodeInspection,
} from "../../types/strategy";


interface EpisodeDetailProps {
  episode: EpisodeInspection;
}


function EpisodeDetail({
  episode,
}: EpisodeDetailProps) {
  return (
    <div className="episode-detail">
      <header className="episode-detail-header">
        <div>
          <span className="workspace-eyebrow">
            EPISODE TRACE
          </span>
          <h3>
            Episode {episode.episode_number}
          </h3>
        </div>

        <span
          className={`episode-outcome ${episode.outcome}`}
        >
          {formatOutcome(episode.outcome)}
        </span>
      </header>

      <div className="episode-detail-metrics">
        <div>
          <span>Epsilon after</span>
          <strong>
            {episode.epsilon_after.toFixed(4)}
          </strong>
        </div>
        <div>
          <span>Total updates</span>
          <strong>
            {episode.total_updates_after}
          </strong>
        </div>
        <div>
          <span>Episode events</span>
          <strong>
            {episode.learning_events.length}
          </strong>
        </div>
      </div>

      <div className="bellman-trace">
        {episode.learning_events.length === 0 ? (
          <div className="workspace-empty">
            No recorded learning events for this
            episode.
          </div>
        ) : (
          episode.learning_events.map((event) => (
            <article
              className="bellman-trace-row"
              key={event.id}
            >
              <div className="trace-row-top">
                <code>{event.state}</code>
                <strong>A{event.action}</strong>
                {event.terminal && (
                  <span>TERMINAL</span>
                )}
              </div>

              <div className="trace-q-transition">
                <code>
                  {event.old_q.toFixed(4)}
                </code>
                <ArrowRight size={12} />
                <code>
                  {event.new_q.toFixed(4)}
                </code>
              </div>

              <div className="trace-equation-values">
                <span>
                  r = {event.reward.toFixed(3)}
                </span>
                <span>
                  d = {event.td_error.toFixed(4)}
                </span>
                <span>
                  dQ = {event.delta_q.toFixed(4)}
                </span>
              </div>

              <div className="trace-parameters">
                <span>
                  a {event.alpha.toFixed(3)}
                </span>
                <span>
                  g {event.gamma.toFixed(3)}
                </span>
                <span>
                  max Q'{" "}
                  {event.best_future_q.toFixed(3)}
                </span>
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  );
}


function formatOutcome(
  outcome: EpisodeInspection["outcome"],
) {
  if (outcome === "agent") {
    return "AGENT WIN";
  }

  if (outcome === "human") {
    return "HUMAN WIN";
  }

  if (outcome === "draw") {
    return "DRAW";
  }

  return "UNKNOWN";
}


export default EpisodeDetail;
