import {
  GitCompare,
} from "lucide-react";

import type {
  CounterfactualAction,
  DecisionEvent,
} from "../../types/decision";


interface CounterfactualPanelProps {
  decision: DecisionEvent;
  visible: boolean;
}


function CounterfactualPanel({
  decision,
  visible,
}: CounterfactualPanelProps) {
  const actions =
    buildCounterfactuals(decision);
  const selected =
    actions.find((item) => item.is_selected);
  const alternatives =
    actions.filter((item) => !item.is_selected);

  return (
    <section
      className={[
        "counterfactual-card",
        visible ? "revealed" : "concealed",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="workspace-section-header">
        <div>
          <span className="workspace-eyebrow">
            ACTION ALTERNATIVES
          </span>
          <h3>Counterfactuals</h3>
        </div>

        <GitCompare size={14} />
      </div>

      {selected && (
        <article className="counterfactual-selected">
          <span>chosen</span>
          <strong>A{selected.action}</strong>
          <code>
            Q={formatSigned(selected.q_value)}
          </code>
        </article>
      )}

      <div className="counterfactual-list">
        {alternatives.map((item) => (
          <article
            className="counterfactual-row"
            key={item.action}
          >
            <div className="counterfactual-action">
              <strong>A{item.action}</strong>
              <span>{item.position_type}</span>
            </div>

            <code>
              Q={formatSigned(item.q_value)}
            </code>

            <div className="counterfactual-gap">
              <span>vs selected</span>
              <strong>
                {formatSigned(
                  item.gap_from_selected,
                )}
              </strong>
            </div>

            {item.is_greedy && (
              <span className="counterfactual-greedy">
                GREEDY
              </span>
            )}
          </article>
        ))}
      </div>

      <small className="counterfactual-note">
        These gaps are differences between learned
        Q estimates at decision time, not guaranteed
        reward losses.
      </small>
    </section>
  );
}


function buildCounterfactuals(
  decision: DecisionEvent,
): CounterfactualAction[] {
  const selectedQ =
    decision.selected_q;

  return decision.q_values
    .map((item) => ({
      action: item.action,
      q_value: item.q_value,
      gap_from_best:
        decision.best_q - item.q_value,
      gap_from_selected:
        item.q_value - selectedQ,
      is_greedy: item.is_greedy,
      is_selected: item.is_selected,
      position_type:
        getPositionType(item.action),
    }))
    .sort((first, second) => {
      if (first.is_selected) {
        return -1;
      }

      if (second.is_selected) {
        return 1;
      }

      return second.q_value - first.q_value;
    });
}


function getPositionType(
  action: number,
): CounterfactualAction["position_type"] {
  if (action === 4) {
    return "center";
  }

  if ([0, 2, 6, 8].includes(action)) {
    return "corner";
  }

  return "edge";
}


function formatSigned(value: number): string {
  if (value > 0) {
    return `+${value.toFixed(3)}`;
  }

  return value.toFixed(3);
}


export default CounterfactualPanel;
