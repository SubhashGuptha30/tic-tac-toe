import {
  useEffect,
  useState,
} from "react";

import {
  getEpisodes,
  inspectEpisode,
} from "../../services/strategyApi";
import type {
  EpisodeInspection,
  EpisodeSummary,
} from "../../types/strategy";
import EpisodeDetail from "./EpisodeDetail";
import EpisodeList from "./EpisodeList";


interface EpisodesWorkspaceProps {
  refreshSignal: number;
}


function EpisodesWorkspace({
  refreshSignal,
}: EpisodesWorkspaceProps) {
  const [episodes, setEpisodes] =
    useState<EpisodeSummary[]>([]);
  const [
    selectedEpisode,
    setSelectedEpisode,
  ] = useState<number | null>(null);
  const [inspection, setInspection] =
    useState<EpisodeInspection | null>(null);
  const [loading, setLoading] =
    useState(true);
  const [error, setError] = useState<
    string | null
  >(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);

        const nextEpisodes =
          await getEpisodes(100, 0);

        setEpisodes(nextEpisodes);

        const targetEpisode =
          selectedEpisode ??
          nextEpisodes[0]?.episode_number;

        if (targetEpisode !== undefined) {
          await loadEpisode(targetEpisode);
        } else {
          setInspection(null);
        }
      } catch {
        setError(
          "Episode history could not be loaded.",
        );
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [refreshSignal]);

  async function loadEpisode(
    episodeNumber: number,
  ) {
    try {
      setError(null);

      const data =
        await inspectEpisode(episodeNumber);

      setInspection(data);
      setSelectedEpisode(episodeNumber);
    } catch {
      setError("Episode inspection failed.");
    }
  }

  if (loading && episodes.length === 0) {
    return (
      <div className="workspace-status">
        <span className="workspace-spinner" />
        Loading experiment history...
      </div>
    );
  }

  return (
    <div className="episodes-workspace">
      <header className="workspace-hero">
        <div>
          <span className="workspace-eyebrow">
            EXPERIMENT HISTORY
          </span>
          <h2>Episode Inspector</h2>
          <p>
            Browse completed games and
            reconstruct their recorded Bellman
            learning events.
          </p>
        </div>
      </header>

      {error && (
        <div className="workspace-error">
          {error}
        </div>
      )}

      {episodes.length === 0 ? (
        <div className="workspace-empty large">
          Complete at least one episode to
          create experiment history.
        </div>
      ) : (
        <section className="episode-browser">
          <aside className="episode-browser-list">
            <EpisodeList
              episodes={episodes}
              selectedEpisode={selectedEpisode}
              onSelect={(episodeNumber) =>
                void loadEpisode(episodeNumber)
              }
            />
          </aside>

          <div className="episode-browser-detail">
            {inspection ? (
              <EpisodeDetail episode={inspection} />
            ) : (
              <div className="workspace-empty">
                Select an episode.
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}


export default EpisodesWorkspace;
