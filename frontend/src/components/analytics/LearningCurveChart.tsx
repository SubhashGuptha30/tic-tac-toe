import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  LearningCurvePoint,
} from "../../types/analytics";


interface LearningCurveChartProps {
  data: LearningCurvePoint[];
}


function LearningCurveChart({
  data,
}: LearningCurveChartProps) {
  return (
    <section className="analytics-chart-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            POLICY PERFORMANCE
          </span>

          <h3>
            Rolling Win Rate
          </h3>
        </div>

        <span className="chart-window-badge">
          Window 10
        </span>
      </div>

      {data.length === 0 ? (
        <EmptyChart />
      ) : (
        <div className="chart-container">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <LineChart
              data={data}
              margin={{
                top: 8,
                right: 8,
                left: -18,
                bottom: 0,
              }}
            >
              <CartesianGrid
                stroke="rgba(148, 163, 184, 0.08)"
                vertical={false}
              />

              <XAxis
                dataKey="episode"
                stroke="#64748b"
                tick={{
                  fontSize: 9,
                }}
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                domain={[0, 1]}
                stroke="#64748b"
                tick={{
                  fontSize: 9,
                }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) =>
                  `${Math.round(value * 100)}%`
                }
              />

              <Tooltip
                contentStyle={{
                  background:
                    "rgba(8, 15, 30, 0.96)",
                  border:
                    "1px solid rgba(148, 163, 184, 0.16)",
                  borderRadius: "10px",
                  fontSize: "10px",
                }}
                formatter={(value) => [
                  `${(
                    Number(value ?? 0) * 100
                  ).toFixed(1)}%`,
                ]}
              />

              <Legend
                wrapperStyle={{
                  fontSize: "9px",
                }}
              />

              <Line
                type="monotone"
                dataKey="rolling_agent_win_rate"
                name="Agent O"
                stroke="#22d3ee"
                strokeWidth={2}
                dot={false}
                activeDot={{
                  r: 4,
                }}
              />

              <Line
                type="monotone"
                dataKey="rolling_human_win_rate"
                name="Human X"
                stroke="#f59e0b"
                strokeWidth={1.5}
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="rolling_draw_rate"
                name="Draw"
                stroke="#a78bfa"
                strokeWidth={1.5}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}


function EmptyChart() {
  return (
    <div className="empty-chart">
      Complete episodes to generate
      a learning curve.
    </div>
  );
}


export default LearningCurveChart;
