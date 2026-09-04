import type {
  DecisionEvent,
  ReconstructedDecisionCell,
} from "../../types/decision";


interface DecisionStateBoardProps {
  decision: DecisionEvent;
  revealSelection: boolean;
}


function DecisionStateBoard({
  decision,
  revealSelection,
}: DecisionStateBoardProps) {
  const board =
    reconstructBoard(decision.state_key);
  const legalSet =
    new Set(decision.legal_actions);
  const qLookup =
    new Map(
      decision.q_values.map(
        (item) => [
          item.action,
          item.q_value,
        ],
      ),
    );

  return (
    <section className="decision-state-card">
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            PRE-ACTION STATE
          </span>
          <h3>Decision State</h3>
        </div>

        <code className="decision-state-key">
          {decision.state_key}
        </code>
      </div>

      <div className="decision-board">
        {board.map((cell) => {
          const isLegal =
            legalSet.has(cell.index);
          const isSelected =
            revealSelection &&
            cell.index === decision.selected_action;
          const qValue =
            qLookup.get(cell.index);

          return (
            <div
              className={[
                "decision-board-cell",
                cell.symbol === "X"
                  ? "human"
                  : "",
                cell.symbol === "O"
                  ? "agent"
                  : "",
                isLegal ? "legal" : "",
                isSelected ? "selected" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              key={cell.index}
            >
              {cell.symbol ? (
                <strong>{cell.symbol}</strong>
              ) : (
                <>
                  <span>A{cell.index}</span>

                  {qValue !== undefined && (
                    <code>{qValue.toFixed(3)}</code>
                  )}
                </>
              )}

              {isSelected && (
                <em>CHOSEN</em>
              )}
            </div>
          );
        })}
      </div>

      <div className="decision-board-legend">
        <span>X human</span>
        <span>O agent</span>
        <span>A# legal action</span>
      </div>
    </section>
  );
}


function reconstructBoard(
  stateKey: string,
): ReconstructedDecisionCell[] {
  return stateKey
    .split("")
    .map((character, index) => {
      const value =
        Number(character);

      return {
        index,
        value,
        symbol:
          value === 1
            ? "X"
            : value === 2
              ? "O"
              : null,
      };
    });
}


export default DecisionStateBoard;
