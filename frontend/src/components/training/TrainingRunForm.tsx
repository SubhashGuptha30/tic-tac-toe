import {
  LoaderCircle,
  Play,
  Shuffle,
  Target,
} from "lucide-react";

import type {
  TrainingOpponentType,
} from "../../types/training";


interface TrainingRunFormProps {
  opponentType: TrainingOpponentType;
  episodes: string;
  seed: string;
  tacticalProbability: number;
  isRunning: boolean;
  supportedOpponents: TrainingOpponentType[];
  onOpponentChange: (
    opponentType: TrainingOpponentType,
  ) => void;
  onEpisodesChange: (value: string) => void;
  onSeedChange: (value: string) => void;
  onTacticalProbabilityChange: (
    value: number,
  ) => void;
  onSubmit: () => void;
}


const opponentOptions: Array<{
  id: TrainingOpponentType;
  label: string;
  description: string;
}> = [
  {
    id: "random",
    label: "Random",
    description: "Broad state coverage",
  },
  {
    id: "tactical",
    label: "Tactical",
    description: "Win, block, center, corners",
  },
  {
    id: "mixed",
    label: "Mixed",
    description: "Curriculum-style blend",
  },
];


function TrainingRunForm({
  opponentType,
  episodes,
  seed,
  tacticalProbability,
  isRunning,
  supportedOpponents,
  onOpponentChange,
  onEpisodesChange,
  onSeedChange,
  onTacticalProbabilityChange,
  onSubmit,
}: TrainingRunFormProps) {
  const supportedSet =
    new Set(supportedOpponents);

  return (
    <section className="training-form-card">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            EXPERIMENT LAUNCHER
          </span>
          <h3>Training Arena</h3>
        </div>

        <span className="training-mode-badge">
          HEADLESS
        </span>
      </div>

      <div className="training-opponent-grid">
        {opponentOptions.map((option) => {
          const isSelected =
            opponentType === option.id;
          const isSupported =
            supportedSet.has(option.id);

          return (
            <button
              key={option.id}
              type="button"
              className={[
                "training-opponent-card",
                isSelected ? "selected" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              disabled={
                isRunning || !isSupported
              }
              onClick={() =>
                onOpponentChange(option.id)
              }
            >
              {option.id === "mixed" ? (
                <Shuffle size={15} />
              ) : (
                <Target size={15} />
              )}
              <strong>{option.label}</strong>
              <span>{option.description}</span>
            </button>
          );
        })}
      </div>

      <label className="training-field">
        <span>Episodes</span>
        <input
          value={episodes}
          type="number"
          min={1}
          max={100000}
          disabled={isRunning}
          onChange={(event) =>
            onEpisodesChange(
              event.target.value,
            )
          }
        />
      </label>

      {opponentType === "mixed" && (
        <label className="training-field probability-field">
          <span>
            Tactical probability{" "}
            <strong>
              {Math.round(
                tacticalProbability * 100,
              )}
              %
            </strong>
          </span>
          <input
            value={tacticalProbability}
            type="range"
            min={0}
            max={1}
            step={0.05}
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
        <span>Seed optional</span>
        <input
          value={seed}
          type="number"
          disabled={isRunning}
          placeholder="e.g. 42"
          onChange={(event) =>
            onSeedChange(event.target.value)
          }
        />
      </label>

      <button
        type="button"
        className="training-start-button"
        disabled={isRunning}
        onClick={onSubmit}
      >
        {isRunning ? (
          <LoaderCircle size={14} />
        ) : (
          <Play size={14} />
        )}
        {isRunning
          ? "Training in progress..."
          : "Start Training"}
      </button>
    </section>
  );
}


export default TrainingRunForm;
