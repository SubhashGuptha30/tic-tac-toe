import {
  Brain,
  Crosshair,
  Dices,
  Play,
  ShieldCheck,
} from "lucide-react";

import type {
  EvaluationOpponentType,
  PolicySnapshot,
} from "../../types/evaluation";


interface EvaluationRunFormProps {
  opponentType: EvaluationOpponentType;
  games: string;
  seed: string;
  tacticalProbability: number;
  snapshotId: number | null;
  snapshots: PolicySnapshot[];
  isRunning: boolean;
  supportedOpponents: EvaluationOpponentType[];
  onOpponentChange: (
    opponent: EvaluationOpponentType,
  ) => void;
  onGamesChange: (value: string) => void;
  onSeedChange: (value: string) => void;
  onTacticalProbabilityChange: (
    value: number,
  ) => void;
  onSnapshotChange: (
    snapshotId: number | null,
  ) => void;
  onSubmit: () => void;
}


const opponentOptions = [
  {
    id: "random" as const,
    label: "Random",
    description: "Broad baseline coverage",
    icon: Dices,
  },
  {
    id: "tactical" as const,
    label: "Tactical",
    description: "Win, block, center, corners",
    icon: Crosshair,
  },
  {
    id: "mixed" as const,
    label: "Mixed",
    description: "Stochastic tactical blend",
    icon: Brain,
  },
];


function EvaluationRunForm({
  opponentType,
  games,
  seed,
  tacticalProbability,
  snapshotId,
  snapshots,
  isRunning,
  supportedOpponents,
  onOpponentChange,
  onGamesChange,
  onSeedChange,
  onTacticalProbabilityChange,
  onSnapshotChange,
  onSubmit,
}: EvaluationRunFormProps) {
  return (
    <section className="evaluation-form-card">
      <div className="training-card-heading">
        <div>
          <span>POLICY BENCHMARK</span>
          <h3>Evaluation Protocol</h3>
        </div>
        <span className="evaluation-mode-badge">
          EPSILON 0
        </span>
      </div>

      <div className="evaluation-guardrail">
        <ShieldCheck size={14} />
        <p>
          Greedy actions only. No Bellman updates,
          epsilon decay, or live-agent mutation.
        </p>
      </div>

      <label className="evaluation-field">
        <span>POLICY SOURCE</span>
        <select
          value={snapshotId ?? ""}
          disabled={isRunning}
          onChange={(event) => {
            const value = event.target.value;
            onSnapshotChange(
              value === "" ? null : Number(value),
            );
          }}
        >
          <option value="">
            Capture current policy snapshot
          </option>
          {snapshots.map((snapshot) => (
            <option
              key={snapshot.id}
              value={snapshot.id}
            >
              Snapshot #{snapshot.id} - {snapshot.q_states} states
            </option>
          ))}
        </select>
      </label>

      <div className="training-opponent-grid">
        {opponentOptions.map((option) => {
          const Icon = option.icon;
          const isSelected =
            opponentType === option.id;
          const isSupported =
            supportedOpponents.includes(option.id);

          return (
            <button
              key={option.id}
              type="button"
              disabled={isRunning || !isSupported}
              className={[
                "training-opponent-card",
                isSelected ? "selected" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              onClick={() =>
                onOpponentChange(option.id)
              }
            >
              <Icon size={14} />
              <strong>{option.label}</strong>
              <span>{option.description}</span>
            </button>
          );
        })}
      </div>

      <label className="training-field">
        <span>GAMES</span>
        <input
          min="1"
          max="100000"
          type="number"
          value={games}
          disabled={isRunning}
          onChange={(event) =>
            onGamesChange(event.target.value)
          }
        />
      </label>

      {opponentType === "mixed" && (
        <label className="training-field">
          <span>
            TACTICAL PROBABILITY
            <strong>
              {Math.round(
                tacticalProbability * 100,
              )}%
            </strong>
          </span>
          <input
            min="0"
            max="1"
            step="0.05"
            type="range"
            value={tacticalProbability}
            disabled={isRunning}
            onChange={(event) =>
              onTacticalProbabilityChange(
                Number(event.target.value),
              )
            }
          />
        </label>
      )}

      <label className="training-field">
        <span>SEED OPTIONAL</span>
        <input
          type="number"
          value={seed}
          disabled={isRunning}
          onChange={(event) =>
            onSeedChange(event.target.value)
          }
        />
      </label>

      <button
        className="evaluation-start-button"
        type="button"
        disabled={isRunning}
        onClick={onSubmit}
      >
        <Play size={14} />
        <span>
          {isRunning
            ? "EVALUATING FROZEN POLICY"
            : "RUN EVALUATION"}
        </span>
      </button>
    </section>
  );
}


export default EvaluationRunForm;
