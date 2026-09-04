import type {
  OutcomeCounts,
  OutcomeTimelinePoint,
} from "../../types/analytics";


interface OutcomeDistributionProps {
  outcomes: OutcomeCounts | null;
  timeline: OutcomeTimelinePoint[];
}


function OutcomeDistribution({
  outcomes,
  timeline,
}: OutcomeDistributionProps) {
  const totalEpisodes =
    outcomes?.total_episodes ?? 0;
  const recentOutcomes = [...timeline]
    .sort((left, right) =>
      left.episode - right.episode,
    )
    .slice(-18);

  return (
    <section className="outcome-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            EPISODE OUTCOMES
          </span>

          <h3>
            Outcome Distribution
          </h3>
        </div>

        <span className="episode-count">
          {totalEpisodes} eps
        </span>
      </div>

      {totalEpisodes === 0 ? (
        <div className="empty-chart">
          Finish a few games to build the
          outcome distribution.
        </div>
      ) : (
        <>
          <div className="outcome-bars">
            <OutcomeBar
              label="Agent O"
              count={outcomes?.agent_wins ?? 0}
              total={totalEpisodes}
              tone="agent"
            />

            <OutcomeBar
              label="Human X"
              count={outcomes?.human_wins ?? 0}
              total={totalEpisodes}
              tone="human"
            />

            <OutcomeBar
              label="Draw"
              count={outcomes?.draws ?? 0}
              total={totalEpisodes}
              tone="draw"
            />
          </div>

          <div className="outcome-timeline">
            <div className="outcome-timeline-header">
              <span>Recent episodes</span>
              <strong>
                {recentOutcomes.length}
              </strong>
            </div>

            <div className="outcome-dot-row">
              {recentOutcomes.length === 0 ? (
                <span className="timeline-empty">
                  Timeline pending.
                </span>
              ) : (
                recentOutcomes.map((point) => (
                  <span
                    key={point.episode}
                    className={
                      `outcome-dot ${point.outcome}`
                    }
                    title={
                      `Episode ${point.episode}: ` +
                      getOutcomeLabel(point)
                    }
                  />
                ))
              )}
            </div>
          </div>
        </>
      )}
    </section>
  );
}


interface OutcomeBarProps {
  label: string;
  count: number;
  total: number;
  tone: "agent" | "human" | "draw";
}


function OutcomeBar({
  label,
  count,
  total,
  tone,
}: OutcomeBarProps) {
  const percentage =
    total === 0 ? 0 : (count / total) * 100;

  return (
    <div>
      <div className="outcome-label">
        <span>{label}</span>
        <strong>
          {count} / {percentage.toFixed(1)}%
        </strong>
      </div>

      <div className="outcome-track">
        <div
          className={`outcome-fill ${tone}`}
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}


function getOutcomeLabel(
  point: OutcomeTimelinePoint,
) {
  if (point.outcome === "agent") {
    return "Agent win";
  }

  if (point.outcome === "human") {
    return "Human win";
  }

  return "Draw";
}


export default OutcomeDistribution;
