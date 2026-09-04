import type {
  ActionValue,
} from "../../types/strategy";


interface ActionValueListProps {
  actions: ActionValue[];
  selectedAction: number | null;
  onSelect: (
    action: number,
  ) => void;
}


function ActionValueList({
  actions,
  selectedAction,
  onSelect,
}: ActionValueListProps) {
  const sorted = [...actions].sort(
    (left, right) =>
      left.rank - right.rank,
  );

  return (
    <div className="action-value-list">
      {sorted.map((action) => (
        <button
          type="button"
          key={action.action}
          className={
            selectedAction === action.action
              ? "action-value-row selected"
              : "action-value-row"
          }
          onClick={() =>
            onSelect(action.action)
          }
        >
          <div className="action-rank">
            #{action.rank}
          </div>

          <div className="action-main">
            <div>
              <strong>
                Action {action.action}
              </strong>
              <span>
                {action.position_type}
              </span>
            </div>

            <code>
              Q {action.q_value.toFixed(4)}
            </code>
          </div>

          <div className="action-tags">
            {action.is_best && (
              <span className="tag-best">
                BEST
              </span>
            )}
            {action.is_immediate_win && (
              <span>WIN</span>
            )}
            {action.is_immediate_block && (
              <span>BLOCK</span>
            )}
            {action.is_fork_creation && (
              <span>FORK</span>
            )}
            {action.is_fork_prevention && (
              <span>DEFEND</span>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}


export default ActionValueList;
