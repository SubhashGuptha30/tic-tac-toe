import {
  LoaderCircle,
} from "lucide-react";

import type {
  DecisionEventSummary,
} from "../../types/decision";


interface DecisionHistoryProps {
  history: DecisionEventSummary[];
  selectedDecisionId: number | null;
  loadingDecisionId: number | null;
  onSelect: (decisionId: number) => void;
}


function DecisionHistory({
  history,
  selectedDecisionId,
  loadingDecisionId,
  onSelect,
}: DecisionHistoryProps) {
  return (
    <section className="decision-history-card">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            FORENSIC LOG
          </span>
          <h3>Decision Replay</h3>
        </div>

        <span className="snapshot-count">
          {history.length} events
        </span>
      </div>

      {history.length === 0 ? (
        <div className="workspace-empty">
          No agent decisions captured yet.
        </div>
      ) : (
        <div className="decision-history-list">
          {history.map((item) => {
            const isSelected =
              selectedDecisionId === item.id;
            const isLoading =
              loadingDecisionId === item.id;

            return (
              <button
                type="button"
                key={item.id}
                className={
                  isSelected
                    ? "decision-history-row selected"
                    : "decision-history-row"
                }
                onClick={() => onSelect(item.id)}
              >
                <div className="history-decision-id">
                  <span>#{item.id}</span>
                  <small>
                    ep{" "}
                    {item.episode_number ?? "-"}
                  </small>
                </div>

                <span
                  className={[
                    "history-mode",
                    modeTone(item.decision_mode),
                  ].join(" ")}
                >
                  {modeLabel(item.decision_mode)}
                </span>

                <div className="history-selection">
                  <strong>
                    A{item.selected_action}
                  </strong>
                  <code>
                    gap {item.action_gap.toFixed(3)}
                  </code>
                </div>

                <div className="history-state">
                  <code>{item.state_key}</code>
                  <small>
                    {formatTime(item.created_at)}
                  </small>
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


function modeTone(
  mode: DecisionEventSummary["decision_mode"],
): string {
  return mode === "exploration"
    ? "explore"
    : "exploit";
}


function modeLabel(
  mode: DecisionEventSummary["decision_mode"],
): string {
  return mode === "exploration"
    ? "EXPLORE"
    : "EXPLOIT";
}


function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString(
    [],
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    },
  );
}


export default DecisionHistory;
