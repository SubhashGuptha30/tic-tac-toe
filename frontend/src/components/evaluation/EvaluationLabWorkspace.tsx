import {
  FlaskConical,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  createEvaluationRun,
  getEvaluationHealth,
  getEvaluationRun,
  getSnapshotComparison,
  listEvaluationRuns,
  listPolicySnapshots,
} from "../../services/evaluationApi";
import type {
  EvaluationComparison,
  EvaluationEngineHealth,
  EvaluationOpponentType,
  EvaluationRun,
  PolicySnapshot,
} from "../../types/evaluation";
import EvaluationComparisonPanel from "./EvaluationComparison";
import EvaluationHistory from "./EvaluationHistory";
import EvaluationReport from "./EvaluationReport";
import EvaluationRunForm from "./EvaluationRunForm";


interface EvaluationLabWorkspaceProps {
  refreshSignal: number;
}


const DEFAULT_HEALTH: EvaluationEngineHealth = {
  engine_ready: false,
  active_run_id: null,
  supported_opponents: [
    "random",
    "tactical",
    "mixed",
  ],
  tie_breaking_policy: "lowest_action_index",
  message: "Evaluation engine status unknown.",
};


function EvaluationLabWorkspace({
  refreshSignal,
}: EvaluationLabWorkspaceProps) {
  const [opponentType, setOpponentType] =
    useState<EvaluationOpponentType>("tactical");
  const [games, setGames] = useState("1000");
  const [seed, setSeed] = useState("42");
  const [tacticalProbability, setTacticalProbability] =
    useState(0.7);
  const [snapshotId, setSnapshotId] = useState<
    number | null
  >(null);
  const [health, setHealth] =
    useState<EvaluationEngineHealth>(DEFAULT_HEALTH);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [snapshots, setSnapshots] = useState<
    PolicySnapshot[]
  >([]);
  const [selectedRun, setSelectedRun] = useState<
    EvaluationRun | null
  >(null);
  const [comparison, setComparison] = useState<
    EvaluationComparison | null
  >(null);
  const [loading, setLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [loadingRunId, setLoadingRunId] = useState<
    number | null
  >(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadLabData();
  }, [refreshSignal]);

  async function loadLabData(
    preferredRunId?: number,
  ) {
    try {
      setLoading(true);
      setError(null);

      const [
        nextHealth,
        nextRuns,
        nextSnapshots,
      ] = await Promise.all([
        getEvaluationHealth(),
        listEvaluationRuns(50, 0),
        listPolicySnapshots(50),
      ]);

      setHealth(nextHealth);
      setRuns(nextRuns);
      setSnapshots(nextSnapshots);

      const targetRunId =
        preferredRunId ??
        selectedRun?.id ??
        nextRuns[0]?.id;

      if (targetRunId) {
        await loadRun(targetRunId);
      } else {
        setSelectedRun(null);
        setComparison(null);
      }
    } catch {
      setError(
        "Evaluation Lab data could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadRun(runId: number) {
    try {
      setLoadingRunId(runId);
      setError(null);

      const run = await getEvaluationRun(runId);
      const nextComparison =
        await getSnapshotComparison(run.snapshot_id);

      setSelectedRun(run);
      setComparison(nextComparison);
    } catch {
      setError(
        "Selected evaluation run could not be loaded.",
      );
    } finally {
      setLoadingRunId(null);
    }
  }

  async function handleRunEvaluation() {
    const gameCount = Number(games);
    const trimmedSeed = seed.trim();
    const parsedSeed =
      trimmedSeed === ""
        ? null
        : Number(trimmedSeed);

    if (
      !Number.isInteger(gameCount) ||
      gameCount < 1 ||
      gameCount > 100000
    ) {
      setError(
        "Games must be an integer from 1 to 100000.",
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

      const run = await createEvaluationRun({
        games: gameCount,
        opponent_type: opponentType,
        tactical_probability: tacticalProbability,
        seed: parsedSeed,
        snapshot_id: snapshotId,
      });
      const [nextRuns, nextSnapshots, nextComparison] =
        await Promise.all([
          listEvaluationRuns(50, 0),
          listPolicySnapshots(50),
          getSnapshotComparison(run.snapshot_id),
        ]);

      setRuns(nextRuns);
      setSnapshots(nextSnapshots);
      setSelectedRun(run);
      setComparison(nextComparison);
      setSnapshotId(run.snapshot_id);
    } catch {
      setError(
        "Evaluation run could not be completed.",
      );
    } finally {
      setIsRunning(false);
    }
  }

  const selectedSnapshot = snapshots.find(
    (snapshot) => snapshot.id === selectedRun?.snapshot_id,
  ) ?? null;

  if (loading && runs.length === 0) {
    return (
      <div className="workspace-status">
        <span className="workspace-spinner" />
        Loading Evaluation Lab...
      </div>
    );
  }

  return (
    <div className="evaluation-workspace">
      <header className="workspace-hero evaluation-hero">
        <div>
          <span className="workspace-eyebrow">
            FROZEN POLICY BENCHMARKING
          </span>
          <h2>Evaluation Lab</h2>
          <p>
            Capture an immutable Q-table snapshot, then
            measure its greedy policy without learning,
            exploration, or shared-brain mutation.
          </p>
        </div>

        <div className="evaluation-engine-badge">
          <FlaskConical size={14} />
          <span>
            {health.engine_ready
              ? "EVALUATOR READY"
              : "EVALUATOR BUSY"}
          </span>
        </div>
      </header>

      {error && (
        <div className="workspace-error">{error}</div>
      )}

      <section className="evaluation-lab-grid">
        <div className="evaluation-left-stack">
          <EvaluationRunForm
            opponentType={opponentType}
            games={games}
            seed={seed}
            tacticalProbability={tacticalProbability}
            snapshotId={snapshotId}
            snapshots={snapshots}
            isRunning={isRunning}
            supportedOpponents={
              health.supported_opponents
            }
            onOpponentChange={setOpponentType}
            onGamesChange={setGames}
            onSeedChange={setSeed}
            onTacticalProbabilityChange={
              setTacticalProbability
            }
            onSnapshotChange={setSnapshotId}
            onSubmit={handleRunEvaluation}
          />

          <EvaluationHistory
            runs={runs}
            selectedRunId={selectedRun?.id ?? null}
            loadingRunId={loadingRunId}
            onSelect={(runId) => void loadRun(runId)}
          />
        </div>

        <div className="evaluation-right-stack">
          <EvaluationReport
            run={selectedRun}
            snapshot={selectedSnapshot}
          />
          <EvaluationComparisonPanel
            comparison={comparison}
          />
        </div>
      </section>

      <section className="scientific-caution evaluation-caution">
        <strong>Evaluation is policy measurement</strong>
        <p>
          This report uses epsilon = 0 and an immutable
          policy snapshot. Reuse the same snapshot when
          comparing opponent strength.
        </p>
      </section>
    </div>
  );
}


export default EvaluationLabWorkspace;
