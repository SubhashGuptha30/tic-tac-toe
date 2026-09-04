import type { DecisionData } from "../../types/game";


interface QValueHeatmapProps {
  decision: DecisionData | null;
}


function QValueHeatmap({
  decision,
}: QValueHeatmapProps) {
  if (!decision) {
    return (
      <div className="empty-science-state">
        Waiting for first agent decision...
      </div>
    );
  }

  return (
    <div className="q-grid">
      {decision.q_values.map((value, index) => {
        const legal = decision.legal_actions.includes(index);
        const selected = decision.action === index;
        const best = decision.best_action === index;

        return (
          <div
            key={index}
            className={[
              "q-cell",
              !legal ? "illegal" : "",
              selected ? "selected" : "",
              best ? "best" : "",
            ].join(" ")}
          >
            <span className="q-index">A{index + 1}</span>

            <strong>
              {legal ? formatSigned(value) : "-"}
            </strong>

            {selected && <small>SELECTED</small>}
            {!selected && best && <small>BEST Q</small>}
          </div>
        );
      })}
    </div>
  );
}


function formatSigned(value: number): string {
  if (value > 0) {
    return `+${value.toFixed(3)}`;
  }

  return value.toFixed(3);
}


export default QValueHeatmap;
