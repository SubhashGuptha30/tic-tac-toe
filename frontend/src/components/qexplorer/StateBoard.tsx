import type {
  CSSProperties,
} from "react";

import type {
  ActionValue,
  BoardCell,
} from "../../types/strategy";


interface StateBoardProps {
  board: BoardCell[];
  actionValues: ActionValue[];
  selectedAction: number | null;
  onActionSelect: (
    action: number,
  ) => void;
}


function StateBoard({
  board,
  actionValues,
  selectedAction,
  onActionSelect,
}: StateBoardProps) {
  const actionLookup = new Map(
    actionValues.map((item) => [
      item.action,
      item,
    ]),
  );

  const qValues = actionValues.map(
    (item) => item.q_value,
  );

  const minQ =
    qValues.length > 0
      ? Math.min(...qValues)
      : 0;
  const maxQ =
    qValues.length > 0
      ? Math.max(...qValues)
      : 0;

  return (
    <div className="state-board">
      {board.map((cell) => {
        const action = actionLookup.get(
          cell.index,
        );
        const isEmpty = cell.value === 0;
        const intensity = action
          ? normalizeQ(
              action.q_value,
              minQ,
              maxQ,
            )
          : 0;

        return (
          <button
            key={cell.index}
            type="button"
            className={[
              "state-board-cell",
              cell.symbol === "X"
                ? "human-cell"
                : "",
              cell.symbol === "O"
                ? "agent-cell"
                : "",
              action?.is_best
                ? "best-action"
                : "",
              selectedAction === cell.index
                ? "selected-action"
                : "",
              isEmpty && action
                ? "legal-action"
                : "",
            ]
              .filter(Boolean)
              .join(" ")}
            disabled={!action}
            onClick={() => {
              if (action) {
                onActionSelect(cell.index);
              }
            }}
            style={
              action
                ? ({
                    "--q-intensity": intensity,
                  } as CSSProperties)
                : undefined
            }
          >
            {cell.symbol ? (
              <strong>{cell.symbol}</strong>
            ) : action ? (
              <>
                <span className="cell-action-index">
                  A{cell.index}
                </span>
                <span className="cell-q-value">
                  {action.q_value.toFixed(3)}
                </span>
              </>
            ) : null}

            {action?.is_best && <em>BEST</em>}
          </button>
        );
      })}
    </div>
  );
}


function normalizeQ(
  value: number,
  min: number,
  max: number,
) {
  if (Math.abs(max - min) <= 1e-12) {
    return 0.5;
  }

  return (value - min) / (max - min);
}


export default StateBoard;
