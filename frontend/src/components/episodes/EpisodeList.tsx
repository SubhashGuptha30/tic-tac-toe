import type {
  EpisodeSummary,
} from "../../types/strategy";


interface EpisodeListProps {
  episodes: EpisodeSummary[];
  selectedEpisode: number | null;
  onSelect: (
    episodeNumber: number,
  ) => void;
}


function EpisodeList({
  episodes,
  selectedEpisode,
  onSelect,
}: EpisodeListProps) {
  return (
    <div className="episode-list">
      {episodes.map((episode) => (
        <button
          type="button"
          key={episode.episode_number}
          className={
            selectedEpisode ===
            episode.episode_number
              ? "episode-row selected"
              : "episode-row"
          }
          onClick={() =>
            onSelect(episode.episode_number)
          }
        >
          <div className="episode-number">
            EP {episode.episode_number}
          </div>

          <span
            className={`episode-outcome ${episode.outcome}`}
          >
            {formatOutcome(episode.outcome)}
          </span>

          <div className="episode-meta">
            <span>
              eps {episode.epsilon_after.toFixed(3)}
            </span>
            <span>
              {episode.learning_event_count} events
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}


function formatOutcome(
  outcome: EpisodeSummary["outcome"],
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


export default EpisodeList;
