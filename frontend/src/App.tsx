import {
  useEffect,
  useState,
} from "react";

import {
  BrainCircuit,
  RotateCcw,
  Server,
} from "lucide-react";

import SciencePanel from "./components/brain/SciencePanel";
import GameBoard from "./components/game/GameBoard";
import ScoreBoard from "./components/game/ScoreBoard";
import ScientificConsole from "./components/workspace/ScientificConsole";
import {
  getAnalyticsDataset,
  getAnalyticsOverview,
  getRecentLearningUpdates,
} from "./services/analyticsApi";
import {
  getAgentMetrics,
  getBackendHealth,
  getGameState,
  makeAgentMove,
  makeHumanMove,
  resetAgentBrain,
  resetGame,
  updateAgentParameters,
} from "./services/api";
import type {
  AnalyticsDataset,
  AnalyticsOverview,
  LearningUpdateDetail,
} from "./types/analytics";
import type {
  AgentMetrics,
  AgentParameterUpdate,
  DecisionData,
  GameState,
  LearningUpdateData,
} from "./types/game";

import "./App.css";


const ANALYTICS_ROLLING_WINDOW = 10;
const RECENT_UPDATES_LIMIT = 20;

const EMPTY_ANALYTICS_DATASET: AnalyticsDataset = {
  learning_curve: [],
  outcome_timeline: [],
  td_error_curve: [],
  reward_trajectory: [],
  epsilon_curve: [],
};


function App() {
  const [game, setGame] =
    useState<GameState | null>(null);
  const [metrics, setMetrics] =
    useState<AgentMetrics | null>(null);
  const [decision, setDecision] =
    useState<DecisionData | null>(null);
  const [
    liveDecisionEventId,
    setLiveDecisionEventId,
  ] = useState<number | null>(null);
  const [learningUpdate, setLearningUpdate] =
    useState<LearningUpdateData | null>(null);
  const [backendOnline, setBackendOnline] =
    useState(false);
  const [isBusy, setIsBusy] =
    useState(false);
  const [isAgentThinking, setIsAgentThinking] =
    useState(false);
  const [error, setError] =
    useState<string | null>(null);
  const [analyticsOverview, setAnalyticsOverview] =
    useState<AnalyticsOverview | null>(null);
  const [analyticsDataset, setAnalyticsDataset] =
    useState<AnalyticsDataset>(
      EMPTY_ANALYTICS_DATASET,
    );
  const [learningUpdates, setLearningUpdates] =
    useState<LearningUpdateDetail[]>([]);
  const [analyticsLoading, setAnalyticsLoading] =
    useState(false);
  const [analyticsLastUpdated, setAnalyticsLastUpdated] =
    useState<Date | null>(null);
  const [
    scientificRefreshSignal,
    setScientificRefreshSignal,
  ] = useState(0);

  useEffect(() => {
    async function initialize() {
      try {
        await getBackendHealth();
        setBackendOnline(true);

        const [initialGame, initialMetrics] =
          await Promise.all([
            getGameState(),
            getAgentMetrics(),
            refreshAnalytics(),
          ]);

        setGame(initialGame);
        setMetrics(initialMetrics);
        setError(null);
      } catch {
        setBackendOnline(false);
        setError("Unable to connect to Python backend.");
      }
    }

    void initialize();
  }, []);

  async function refreshAnalytics() {
    try {
      setAnalyticsLoading(true);

      const [
        overview,
        dataset,
        updates,
      ] = await Promise.all([
        getAnalyticsOverview(),
        getAnalyticsDataset(
          ANALYTICS_ROLLING_WINDOW,
        ),
        getRecentLearningUpdates(
          RECENT_UPDATES_LIMIT,
        ),
      ]);

      setAnalyticsOverview(overview);
      setAnalyticsDataset(dataset);
      setLearningUpdates(updates);
      setAnalyticsLastUpdated(new Date());
      setScientificRefreshSignal(
        (current) => current + 1,
      );
    } catch {
      setBackendOnline(false);
    } finally {
      setAnalyticsLoading(false);
    }
  }

  async function handleCellClick(index: number) {
    if (!game || isBusy) {
      return;
    }

    try {
      setIsBusy(true);
      setError(null);

      const humanResponse = await makeHumanMove(index);
      setGame(humanResponse.game);
      setMetrics(humanResponse.agent_metrics);

      if (humanResponse.learning_update) {
        setLearningUpdate(
          humanResponse.learning_update,
        );
      }

      if (humanResponse.game.game_over) {
        await refreshAnalytics();
        return;
      }

      setIsAgentThinking(true);
      await sleep(900);

      const agentResponse = await makeAgentMove();
      setDecision(agentResponse.decision);
      setLiveDecisionEventId(
        agentResponse.decision_event_id,
      );
      setMetrics(agentResponse.agent_metrics);

      if (agentResponse.learning_update) {
        setLearningUpdate(
          agentResponse.learning_update,
        );
      }

      setGame(agentResponse.game);
      await refreshAnalytics();
    } catch {
      setError("A move could not be completed.");
    } finally {
      setIsAgentThinking(false);
      setIsBusy(false);
    }
  }

  async function handleSaveParameters(
    parameters: AgentParameterUpdate,
  ) {
    try {
      setError(null);

      const updatedMetrics =
        await updateAgentParameters(
          parameters,
        );

      setMetrics(updatedMetrics);
      void refreshAnalytics();
    } catch {
      setError(
        "Agent parameters could not be updated.",
      );
    }
  }

  async function handleTrainingComplete() {
    try {
      const updatedMetrics =
        await getAgentMetrics();

      setMetrics(updatedMetrics);
      await refreshAnalytics();
    } catch {
      setError(
        "Training completed, but refreshed metrics could not be loaded.",
      );
    }
  }

  async function handleResetBrain() {
    try {
      setIsBusy(true);
      setError(null);

      const response = await resetAgentBrain();
      setGame(response.game);
      setMetrics(response.agent_metrics);
      setDecision(null);
      setLiveDecisionEventId(null);
      setLearningUpdate(null);

      await refreshAnalytics();
    } catch {
      setError("Agent brain could not be reset.");
    } finally {
      setIsBusy(false);
      setIsAgentThinking(false);
    }
  }

  async function handleReset() {
    try {
      setIsBusy(true);

      const response = await resetGame();
      setGame(response.game);
      setMetrics(response.agent_metrics);
      setDecision(null);
      setLiveDecisionEventId(null);
      setLearningUpdate(null);
      setError(null);
    } catch {
      setError("The board could not be reset.");
    } finally {
      setIsBusy(false);
      setIsAgentThinking(false);
    }
  }

  if (!game) {
    return (
      <main className="loading-screen">
        <BrainCircuit size={34} />

        <h1>AdaptiveRL Lab</h1>

        <p>{error ?? "Connecting to experiment backend..."}</p>
      </main>
    );
  }

  return (
    <main className="rl-lab-shell">
      <section className="game-laboratory">
        <div className="game-lab-inner">
          <header className="topbar topbar-embedded">
            <div className="brand">
              <div className="brand-icon">
                <BrainCircuit size={24} />
              </div>

              <div>
                <h1>AdaptiveRL Lab</h1>
                <p>Online Human-Trained Q-Learning</p>
              </div>
            </div>

            <div className="header-meta">
              <span className="episode-label">
                EPISODE{" "}
                {String(
                  game.stats.episodes + 1,
                ).padStart(3, "0")}
              </span>

              <div
                className={[
                  "backend-status",
                  backendOnline
                    ? "online"
                    : "offline",
                ].join(" ")}
              >
                <Server size={14} />
                <span className="status-dot" />
                {backendOnline
                  ? "Backend Online"
                  : "Backend Offline"}
              </div>
            </div>
          </header>

          <div className="left-lab-stack">
            <section className="game-panel">
              <div className="game-panel-header">
                <div>
                  <span className="eyebrow">
                    LIVE ENVIRONMENT
                  </span>
                  <h2>
                    Human vs Learning Agent
                  </h2>
                </div>

                <div className="player-key">
                  <span className="human-key">
                    X HUMAN
                  </span>
                  <span className="agent-key">
                    O Q-AGENT
                  </span>
                </div>
              </div>

              <div className="game-stage">
                <div
                  className={[
                    "turn-banner",
                    isAgentThinking
                      ? "thinking"
                      : "",
                  ].join(" ")}
                >
                  <span className="turn-indicator" />
                  {getStatusText(
                    game,
                    isAgentThinking,
                  )}
                </div>

                <GameBoard
                  game={game}
                  disabled={isBusy}
                  onCellClick={handleCellClick}
                />

                <button
                  className="reset-button"
                  onClick={handleReset}
                  disabled={isBusy}
                >
                  <RotateCcw size={16} />
                  New Round
                </button>
              </div>

              <ScoreBoard stats={game.stats} />

              {error && (
                <div className="error-banner">
                  {error}
                </div>
              )}
            </section>

            <SciencePanel
              game={game}
              metrics={metrics}
              decision={decision}
              learningUpdate={learningUpdate}
              isAgentThinking={isAgentThinking}
              onSaveParameters={
                handleSaveParameters
              }
              onResetBrain={handleResetBrain}
            />
          </div>
        </div>
      </section>

      <ScientificConsole
        overview={analyticsOverview}
        dataset={analyticsDataset}
        updates={learningUpdates}
        metrics={metrics}
        isAgentThinking={isAgentThinking}
        loading={analyticsLoading}
        lastUpdated={analyticsLastUpdated}
        refreshSignal={scientificRefreshSignal}
        liveDecisionEventId={
          liveDecisionEventId
        }
        onTrainingComplete={
          handleTrainingComplete
        }
      />
    </main>
  );
}


function sleep(milliseconds: number) {
  return new Promise<void>((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}


function getStatusText(
  game: GameState,
  isAgentThinking: boolean,
): string {
  if (isAgentThinking) {
    return "Agent is evaluating epsilon-greedy policy...";
  }

  if (game.winner === "X") {
    return "Human wins - negative reward delivered";
  }

  if (game.winner === "O") {
    return "Agent wins - positive reward delivered";
  }

  if (game.is_draw) {
    return "Draw - terminal reward delivered";
  }

  if (game.current_player === "X") {
    return "Your turn - agent awaits response";
  }

  return "Agent turn";
}


export default App;
