import {
  History,
} from "lucide-react";

import type {
  EvaluationRun,
} from "../../types/evaluation";


interface EvaluationHistoryProps {
  runs: EvaluationRun[];
  selectedRunId: number | null;
  loadingRunId: number | null;
  onSelect: (runId: number) => void;
}


function EvaluationHistory({
  runs,
  selectedRunId,
  loadingRunId,
  onSelect,
}: EvaluationHistoryProps) {
  return (
    <section className="evaluation-history-card">
      <div className="training-card-heading">
        <div>
          <span>REPRODUCIBLE RECORD</span>
          <h3>Evaluation Runs</h3>
        </div>
        <History size={15} />
      </div>

      {runs.length === 0 ? (
        <p className="evaluation-empty-copy">
          No evaluation reports have been saved yet.
        </p>
      ) : (
        <div className="evaluation-history-list">
          {runs.map((run) => (
            <button
              className={[
                "evaluation-history-row",
                selectedRunId === run.id
                  ? "selected"
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
              key={run.id}
              type="button"
              onClick={() => onSelect(run.id)}
            >
              <div>
                <strong>#{run.id}</strong>
                <span>Snapshot #{run.snapshot_id}</span>
              </div>
              <div>
                <strong>{run.opponent_type}</strong>
                <span>{run.completed_games} games</span>
              </div>
              <div>
                <strong>
                  {(run.agent_win_rate * 100).toFixed(1)}%
                </strong>
                <span>agent win rate</span>
              </div>
              <div>
                <strong>
                  {run.average_decision_confidence.toFixed(3)}
                </strong>
                <span>confidence</span>
              </div>
              {loadingRunId === run.id && (
                <span className="history-loading-icon" />
              )}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}


export default EvaluationHistory;
