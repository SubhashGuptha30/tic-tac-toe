import {
  BrainCircuit,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  createTrainingRun,
  getTrainingEpisodes,
  getTrainingHealth,
  getTrainingRun,
  listTrainingRuns,
} from "../../services/trainingApi";
import type {
  TrainingEngineHealth,
  TrainingEpisode,
  TrainingOpponentType,
  TrainingRun,
} from "../../types/training";
import TrainingCharts from "./TrainingCharts";
import TrainingResultSummary from "./TrainingResultSummary";
import TrainingRunForm from "./TrainingRunForm";
import TrainingRunHistory from "./TrainingRunHistory";


interface TrainingArenaWorkspaceProps {
  refreshSignal: number;
  onTrainingComplete: () => void | Promise<void>;
}


const DEFAULT_HEALTH: TrainingEngineHealth = {
  engine_ready: false,
  supported_opponents: [
    "random",
    "tactical",
    "mixed",
  ],
  active_run_id: null,
  agent_available: false,
  message: "Training engine status unknown.",
};


function TrainingArenaWorkspace({
  refreshSignal,
  onTrainingComplete,
}: TrainingArenaWorkspaceProps) {
  const [
    opponentType,
    setOpponentType,
  ] = useState<TrainingOpponentType>("mixed");
  const [episodes, setEpisodes] =
    useState("1000");
  const [seed, setSeed] = useState("42");
  const [
    tacticalProbability,
    setTacticalProbability,
  ] = useState(0.7);
  const [health, setHealth] =
    useState<TrainingEngineHealth>(
      DEFAULT_HEALTH,
    );
  const [runs, setRuns] =
    useState<TrainingRun[]>([]);
  const [selectedRun, setSelectedRun] =
    useState<TrainingRun | null>(null);
  const [selectedEpisodes, setSelectedEpisodes] =
    useState<TrainingEpisode[]>([]);
  const [loading, setLoading] =
    useState(true);
  const [isRunning, setIsRunning] =
    useState(false);
  const [error, setError] = useState<
    string | null
  >(null);
  const [
    loadingRunId,
    setLoadingRunId,
  ] = useState<number | null>(null);

  useEffect(() => {
    void loadArenaData();
  }, [refreshSignal]);

  async function loadArenaData(
    preferredRunId?: number,
  ) {
    try {
      setLoading(true);
      setError(null);

      const [
        nextHealth,
        nextRuns,
      ] = await Promise.all([
        getTrainingHealth(),
        listTrainingRuns(50, 0),
      ]);

      setHealth(nextHealth);
      setRuns(nextRuns);

      const targetRunId =
        preferredRunId ??
        selectedRun?.id ??
        nextRuns[0]?.id;

      if (targetRunId) {
        await loadRun(targetRunId);
      } else {
        setSelectedRun(null);
        setSelectedEpisodes([]);
      }
    } catch {
      setError(
        "Training Arena data could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadRun(
    runId: number,
  ) {
    try {
      setError(null);
      setLoadingRunId(runId);

      const [
        run,
        runEpisodes,
      ] = await Promise.all([
        getTrainingRun(runId),
        getTrainingEpisodes(runId, 1000, 0),
      ]);

      setSelectedRun(run);
      setSelectedEpisodes(runEpisodes);
    } catch {
      setError(
        "Selected training run could not be loaded.",
      );
    } finally {
      setLoadingRunId(null);
    }
  }

  async function handleStartTraining() {
    const episodeCount = Number(episodes);
    const trimmedSeed = seed.trim();
    const parsedSeed =
      trimmedSeed === ""
        ? null
        : Number(trimmedSeed);

    if (
      !Number.isInteger(episodeCount) ||
      episodeCount < 1 ||
      episodeCount > 100000
    ) {
      setError(
        "Episodes must be an integer from 1 to 100000.",
      );
      return;
    }

    if (
      parsedSeed !== null &&
      !Number.isInteger(parsedSeed)
    ) {
      setError(
        "Seed must be an integer or left blank.",
      );
      return;
    }

    try {
      setIsRunning(true);
      setError(null);

      const run = await createTrainingRun({
        episodes: episodeCount,
        opponent_type: opponentType,
        tactical_probability:
          tacticalProbability,
        seed: parsedSeed,
      });

      const runEpisodes =
        await getTrainingEpisodes(
          run.id,
          1000,
          0,
        );

      setSelectedRun(run);
      setSelectedEpisodes(runEpisodes);

      const nextRuns =
        await listTrainingRuns(50, 0);
      setRuns(nextRuns);

      await onTrainingComplete();
    } catch {
      setError(
        "Training run could not be completed.",
      );
    } finally {
      setIsRunning(false);
    }
  }

  if (loading && runs.length === 0) {
    return (
      <div className="workspace-status">
        <span className="workspace-spinner" />
        Loading Training Arena...
      </div>
    );
  }

  return (
    <div className="training-workspace">
      <header className="workspace-hero training-hero">
        <div>
          <span className="workspace-eyebrow">
            AUTONOMOUS CURRICULUM
          </span>
          <h2>Training Arena</h2>
          <p>
            Launch headless experiments against
            random, tactical, or mixed opponents.
            Each run updates the same shared
            Q-table used by the human game.
          </p>
        </div>

        <div className="training-engine-badge">
          <BrainCircuit size={14} />
          <span>
            {health.engine_ready
              ? "ENGINE READY"
              : "ENGINE BUSY"}
          </span>
        </div>
      </header>

      {error && (
        <div className="workspace-error">
          {error}
        </div>
      )}

      <section className="training-arena-grid">
        <div className="training-left-stack">
          <TrainingRunForm
            opponentType={opponentType}
            episodes={episodes}
            seed={seed}
            tacticalProbability={
              tacticalProbability
            }
            isRunning={isRunning}
            supportedOpponents={
              health.supported_opponents
            }
            onOpponentChange={setOpponentType}
            onEpisodesChange={setEpisodes}
            onSeedChange={setSeed}
            onTacticalProbabilityChange={
              setTacticalProbability
            }
            onSubmit={handleStartTraining}
          />

          <TrainingRunHistory
            runs={runs}
            selectedRunId={selectedRun?.id ?? null}
            loadingRunId={loadingRunId}
            onSelect={(runId) =>
              void loadRun(runId)
            }
          />
        </div>

        <div className="training-right-stack">
          <TrainingResultSummary
            run={selectedRun}
          />

          <TrainingCharts
            run={selectedRun}
            episodes={selectedEpisodes}
          />
        </div>
      </section>

      <section className="scientific-caution">
        <strong>Training is not evaluation</strong>
        <p>
          These curves describe exploratory
          training performance. A later Evaluation
          Lab should freeze learning and run
          epsilon-zero benchmark games to measure
          policy quality.
        </p>
      </section>
    </div>
  );
}


export default TrainingArenaWorkspace;
