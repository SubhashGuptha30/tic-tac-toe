import {
  History,
  LoaderCircle,
} from "lucide-react";

import type {
  TrainingRun,
} from "../../types/training";


interface TrainingRunHistoryProps {
  runs: TrainingRun[];
  selectedRunId: number | null;
  loadingRunId: number | null;
  onSelect: (runId: number) => void;
}


function TrainingRunHistory({
  runs,
  selectedRunId,
  loadingRunId,
  onSelect,
}: TrainingRunHistoryProps) {
  return (
    <section className="training-history-card">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            EXPERIMENT LOG
          </span>
          <h3>Training Runs</h3>
        </div>

        <History size={14} />
      </div>

      {runs.length === 0 ? (
        <div className="workspace-empty">
          No autonomous training runs yet.
        </div>
      ) : (
        <div className="training-history-list">
          {runs.map((run) => {
            const isSelected =
              selectedRunId === run.id;
            const isLoading =
              loadingRunId === run.id;

            return (
              <button
                key={run.id}
                type="button"
                className={[
                  "training-history-row",
                  isSelected
                    ? "selected"
                    : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                onClick={() => onSelect(run.id)}
              >
                <div>
                  <strong>#{run.id}</strong>
                  <span>
                    {formatOpponent(run)}
                  </span>
                </div>

                <div>
                  <strong>
                    {run.completed_episodes}
                  </strong>
                  <span>episodes</span>
                </div>

                <div>
                  <strong>
                    {run.agent_wins} /{" "}
                    {run.opponent_wins} /{" "}
                    {run.draws}
                  </strong>
                  <span>W / L / D</span>
                </div>

                <div>
                  <strong>
                    {run.mean_reward.toFixed(2)}
                  </strong>
                  <span>reward</span>
                </div>

                {isLoading && (
                  <LoaderCircle
                    className="history-loading-icon"
                    size={11}
                  />
                )}
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}


function formatOpponent(
  run: TrainingRun,
): string {
  if (run.opponent_type !== "mixed") {
    return run.opponent_type;
  }

  return `mixed ${Math.round(
    (run.tactical_probability ?? 0.7) * 100,
  )}%`;
}


export default TrainingRunHistory;
