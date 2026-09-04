import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  ReactNode,
} from "react";
import type {
  TrainingEpisode,
  TrainingOutcomePoint,
  TrainingQGrowthPoint,
  TrainingRun,
  TrainingScalarPoint,
} from "../../types/training";


interface TrainingChartsProps {
  run: TrainingRun | null;
  episodes: TrainingEpisode[];
}


function TrainingCharts({
  run,
  episodes,
}: TrainingChartsProps) {
  const outcomeData =
    buildOutcomeData(episodes);
  const epsilonData =
    episodes.map((episode) => ({
      episode: episode.episode_index,
      value: episode.epsilon_after,
    }));
  const rewardData =
    buildMeanRewardData(episodes);
  const qGrowthData =
    buildQGrowthData(run);

  return (
    <section className="training-charts-grid">
      <TrainingChartCard
        eyebrow="OUTCOME MIX"
        title="Win / Loss / Draw"
        emptyText="Outcome curve appears after a run."
      >
        {outcomeData.length > 0 && (
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <LineChart
              data={outcomeData}
              margin={chartMargin}
            >
              <CartesianGrid
                stroke="rgba(148, 163, 184, 0.08)"
                vertical={false}
              />
              <XAxis
                dataKey="episode"
                {...axisProps}
              />
              <YAxis
                domain={[0, 1]}
                tickFormatter={formatAxisPercent}
                {...axisProps}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                formatter={formatTooltipPercent}
              />
              <Line
                type="monotone"
                dataKey="agent_win_rate"
                name="Agent win"
                stroke="#4ade80"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="opponent_win_rate"
                name="Opponent win"
                stroke="#f59e0b"
                strokeWidth={1.5}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="draw_rate"
                name="Draw"
                stroke="#a78bfa"
                strokeWidth={1.5}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </TrainingChartCard>

      <TrainingChartCard
        eyebrow="EXPLORATION"
        title="Epsilon"
        emptyText="Epsilon decay appears after a run."
      >
        {epsilonData.length > 0 && (
          <ScalarAreaChart
            data={epsilonData}
            name="epsilon"
            color="#a78bfa"
            gradientId="trainingEpsilonGradient"
          />
        )}
      </TrainingChartCard>

      <TrainingChartCard
        eyebrow="KNOWLEDGE GROWTH"
        title="Q-Table Growth"
        emptyText="Q-table growth appears after a run."
      >
        {qGrowthData.length > 0 && (
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <LineChart
              data={qGrowthData}
              margin={chartMargin}
            >
              <CartesianGrid
                stroke="rgba(148, 163, 184, 0.08)"
                vertical={false}
              />
              <XAxis
                dataKey="episode"
                {...axisProps}
              />
              <YAxis {...axisProps} />
              <Tooltip
                contentStyle={tooltipStyle}
              />
              <Line
                type="monotone"
                dataKey="q_states"
                name="Q states"
                stroke="#22d3ee"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="q_entries"
                name="Q entries"
                stroke="#4ade80"
                strokeWidth={1.5}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </TrainingChartCard>

      <TrainingChartCard
        eyebrow="RETURN SIGNAL"
        title="Mean Reward"
        emptyText="Reward trajectory appears after a run."
      >
        {rewardData.length > 0 && (
          <ScalarAreaChart
            data={rewardData}
            name="mean reward"
            color="#22d3ee"
            gradientId="trainingRewardGradient"
          />
        )}
      </TrainingChartCard>
    </section>
  );
}


interface TrainingChartCardProps {
  eyebrow: string;
  title: string;
  emptyText: string;
  children: ReactNode;
}


function TrainingChartCard({
  eyebrow,
  title,
  emptyText,
  children,
}: TrainingChartCardProps) {
  return (
    <section className="training-chart-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            {eyebrow}
          </span>
          <h3>{title}</h3>
        </div>
      </div>

      <div className="training-chart-container">
        {children || (
          <div className="empty-chart">
            {emptyText}
          </div>
        )}
      </div>
    </section>
  );
}


interface ScalarAreaChartProps {
  data: TrainingScalarPoint[];
  name: string;
  color: string;
  gradientId: string;
}


function ScalarAreaChart({
  data,
  name,
  color,
  gradientId,
}: ScalarAreaChartProps) {
  return (
    <ResponsiveContainer
      width="100%"
      height="100%"
    >
      <AreaChart
        data={data}
        margin={chartMargin}
      >
        <defs>
          <linearGradient
            id={gradientId}
            x1="0"
            y1="0"
            x2="0"
            y2="1"
          >
            <stop
              offset="0%"
              stopColor={color}
              stopOpacity={0.3}
            />
            <stop
              offset="100%"
              stopColor={color}
              stopOpacity={0}
            />
          </linearGradient>
        </defs>
        <CartesianGrid
          stroke="rgba(148, 163, 184, 0.08)"
          vertical={false}
        />
        <XAxis
          dataKey="episode"
          {...axisProps}
        />
        <YAxis {...axisProps} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(value) => [
            Number(value ?? 0).toFixed(4),
          ]}
        />
        <Area
          type="monotone"
          dataKey="value"
          name={name}
          stroke={color}
          strokeWidth={2}
          fill={`url(#${gradientId})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}


function buildOutcomeData(
  episodes: TrainingEpisode[],
): TrainingOutcomePoint[] {
  let agentWins = 0;
  let opponentWins = 0;
  let draws = 0;

  return episodes.map((episode, index) => {
    if (episode.result === "agent_win") {
      agentWins += 1;
    } else if (
      episode.result === "opponent_win"
    ) {
      opponentWins += 1;
    } else {
      draws += 1;
    }

    const total = index + 1;

    return {
      episode: episode.episode_index,
      agent_win_rate: agentWins / total,
      opponent_win_rate:
        opponentWins / total,
      draw_rate: draws / total,
    };
  });
}


function buildMeanRewardData(
  episodes: TrainingEpisode[],
): TrainingScalarPoint[] {
  let cumulativeReward = 0;

  return episodes.map((episode, index) => {
    cumulativeReward += episode.reward;

    return {
      episode: episode.episode_index,
      value: cumulativeReward / (index + 1),
    };
  });
}


function buildQGrowthData(
  run: TrainingRun | null,
): TrainingQGrowthPoint[] {
  if (!run) {
    return [];
  }

  return [
    {
      episode: 0,
      q_states: run.q_states_start,
      q_entries: run.q_entries_start,
    },
    {
      episode: run.completed_episodes,
      q_states:
        run.q_states_end ??
        run.q_states_start,
      q_entries:
        run.q_entries_end ??
        run.q_entries_start,
    },
  ];
}


const chartMargin = {
  top: 8,
  right: 8,
  left: -18,
  bottom: 0,
};


const axisProps = {
  stroke: "#64748b",
  tick: {
    fontSize: 9,
  },
  tickLine: false,
  axisLine: false,
};


const tooltipStyle = {
  background: "rgba(8, 15, 30, 0.96)",
  border:
    "1px solid rgba(148, 163, 184, 0.16)",
  borderRadius: "10px",
  fontSize: "10px",
};


function formatAxisPercent(
  value: number,
): string {
  return `${Math.round(value * 100)}%`;
}


function formatTooltipPercent(
  value: unknown,
) {
  return [
    `${(
      Number(value ?? 0) * 100
    ).toFixed(1)}%`,
  ];
}


export default TrainingCharts;
