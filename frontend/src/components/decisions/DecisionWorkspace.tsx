import {
  Pause,
  Play,
  RotateCcw,
  SkipForward,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getDecisionById,
  getDecisionHistory,
  getDecisionStats,
  getLatestDecision,
} from "../../services/decisionApi";
import type {
  DecisionEvent,
  DecisionEventSummary,
  DecisionPipelineStage,
  DecisionStats,
} from "../../types/decision";
import CounterfactualPanel from "./CounterfactualPanel";
import DecisionExplanation from "./DecisionExplanation";
import DecisionHistory from "./DecisionHistory";
import DecisionPipeline from "./DecisionPipeline";
import DecisionStateBoard from "./DecisionStateBoard";
import DecisionStatsPanel from "./DecisionStatsPanel";
import EpsilonGate from "./EpsilonGate";
import QValueSnapshot from "./QValueSnapshot";


interface DecisionWorkspaceProps {
  liveDecisionEventId: number | null;
  refreshSignal: number;
}


const stages: DecisionPipelineStage[] = [
  "state",
  "q-values",
  "epsilon-gate",
  "policy",
  "selection",
];


function DecisionWorkspace({
  liveDecisionEventId,
  refreshSignal,
}: DecisionWorkspaceProps) {
  const [decision, setDecision] =
    useState<DecisionEvent | null>(null);
  const [history, setHistory] =
    useState<DecisionEventSummary[]>([]);
  const [stats, setStats] =
    useState<DecisionStats | null>(null);
  const [stageIndex, setStageIndex] =
    useState(0);
  const [isPlaying, setIsPlaying] =
    useState(true);
  const [loading, setLoading] =
    useState(true);
  const [error, setError] = useState<
    string | null
  >(null);
  const [
    loadingDecisionId,
    setLoadingDecisionId,
  ] = useState<number | null>(null);
  const lastLoadedLiveId =
    useRef<number | null>(null);

  useEffect(() => {
    async function loadInitialDecision() {
      try {
        setLoading(true);
        setError(null);

        const [
          latest,
          historyData,
          statsData,
        ] = await Promise.all([
          getLatestDecision(),
          getDecisionHistory(60, 0),
          getDecisionStats(),
        ]);

        setDecision(latest);
        setHistory(historyData);
        setStats(statsData);
        setStageIndex(0);
        setIsPlaying(true);
      } catch {
        setError(
          "Decision microscope data could not be loaded.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadInitialDecision();
  }, [refreshSignal]);

  useEffect(() => {
    if (
      liveDecisionEventId === null ||
      liveDecisionEventId ===
        lastLoadedLiveId.current
    ) {
      return;
    }

    const eventId =
      liveDecisionEventId;

    async function loadLiveDecision() {
      try {
        setError(null);

        const data =
          await getDecisionById(eventId);

        lastLoadedLiveId.current =
          eventId;

        setDecision(data);
        setStageIndex(0);
        setIsPlaying(true);

        const [
          historyData,
          statsData,
        ] = await Promise.all([
          getDecisionHistory(60, 0),
          getDecisionStats(),
        ]);

        setHistory(historyData);
        setStats(statsData);
      } catch {
        setError(
          "The live decision event could not be loaded.",
        );
      }
    }

    void loadLiveDecision();
  }, [liveDecisionEventId]);

  useEffect(() => {
    if (!isPlaying) {
      return;
    }

    if (stageIndex >= stages.length - 1) {
      setIsPlaying(false);
      return;
    }

    const timerId =
      window.setTimeout(() => {
        setStageIndex(
          (current) =>
            Math.min(
              current + 1,
              stages.length - 1,
            ),
        );
      }, 850);

    return () =>
      window.clearTimeout(timerId);
  }, [
    isPlaying,
    stageIndex,
  ]);

  async function loadDecision(
    decisionId: number,
  ) {
    try {
      setError(null);
      setLoadingDecisionId(decisionId);

      const data =
        await getDecisionById(decisionId);

      setDecision(data);
      setStageIndex(0);
      setIsPlaying(true);
    } catch {
      setError(
        "Selected decision event could not be loaded.",
      );
    } finally {
      setLoadingDecisionId(null);
    }
  }

  function restartReplay() {
    setStageIndex(0);
    setIsPlaying(true);
  }

  function togglePlayback() {
    setIsPlaying(
      (current) => !current,
    );
  }

  function nextStage() {
    setIsPlaying(false);
    setStageIndex(
      (current) =>
        Math.min(
          current + 1,
          stages.length - 1,
        ),
    );
  }

  if (loading && decision === null) {
    return (
      <div className="workspace-status">
        <span className="workspace-spinner" />
        Loading decision microscope...
      </div>
    );
  }

  const activeStage =
    stages[stageIndex];
  const showQValues =
    stageIndex >=
    stages.indexOf("q-values");
  const showGate =
    stageIndex >=
    stages.indexOf("epsilon-gate");
  const showPolicy =
    stageIndex >=
    stages.indexOf("policy");
  const showSelection =
    stageIndex >=
    stages.indexOf("selection");

  return (
    <div className="decision-workspace">
      <header className="workspace-hero decision-hero">
        <div>
          <span className="workspace-eyebrow">
            LIVE DECISION MICROSCOPE
          </span>
          <h2>
            Epsilon-Greedy Forensics
          </h2>
          <p>
            Replay the exact state, Q-values,
            random draw, policy mode, and selected
            action persisted for each real agent
            move.
          </p>
        </div>

        <div className="decision-event-badge">
          <span>EVENT</span>
          <strong>
            {decision ? `#${decision.id}` : "-"}
          </strong>
        </div>
      </header>

      {error && (
        <div className="workspace-error">
          {error}
        </div>
      )}

      {decision ? (
        <>
          <section className="decision-control-bar">
            <DecisionPipeline
              activeStage={activeStage}
            />

            <div className="decision-replay-controls">
              <button
                type="button"
                onClick={togglePlayback}
              >
                {isPlaying ? (
                  <Pause size={12} />
                ) : (
                  <Play size={12} />
                )}
                {isPlaying ? "Pause" : "Play"}
              </button>

              <button
                type="button"
                onClick={restartReplay}
              >
                <RotateCcw size={12} />
                Restart
              </button>

              <button
                type="button"
                onClick={nextStage}
                disabled={
                  stageIndex ===
                  stages.length - 1
                }
              >
                <SkipForward size={12} />
                Next
              </button>
            </div>
          </section>

          <section className="decision-microscope-grid">
            <div className="decision-primary-stack">
              <DecisionStateBoard
                decision={decision}
                revealSelection={showSelection}
              />

              <DecisionExplanation
                decision={decision}
                visible={showPolicy}
              />

              <DecisionStatsPanel stats={stats} />
            </div>

            <div className="decision-secondary-stack">
              <QValueSnapshot
                decision={decision}
                visible={showQValues}
              />

              <EpsilonGate
                decision={decision}
                visible={showGate}
              />

              <CounterfactualPanel
                decision={decision}
                visible={showSelection}
              />

              <DecisionHistory
                history={history}
                selectedDecisionId={
                  decision.id
                }
                loadingDecisionId={
                  loadingDecisionId
                }
                onSelect={(decisionId) =>
                  void loadDecision(
                    decisionId,
                  )
                }
              />
            </div>
          </section>
        </>
      ) : (
        <div className="workspace-empty large">
          Play at least one agent move to capture
          a decision event.
        </div>
      )}
    </div>
  );
}


export default DecisionWorkspace;
