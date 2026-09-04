import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  RewardPoint,
} from "../../types/analytics";


interface RewardChartProps {
  data: RewardPoint[];
}


function RewardChart({
  data,
}: RewardChartProps) {
  return (
    <section className="analytics-chart-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            RETURN SIGNAL
          </span>

          <h3>
            Cumulative Reward
          </h3>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="empty-chart">
          Reward history is not available yet.
        </div>
      ) : (
        <div className="chart-container">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <AreaChart
              data={data}
              margin={{
                top: 8,
                right: 8,
                left: -18,
                bottom: 0,
              }}
            >
              <defs>
                <linearGradient
                  id="rewardGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#22d3ee"
                    stopOpacity={0.3}
                  />

                  <stop
                    offset="100%"
                    stopColor="#22d3ee"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>

              <CartesianGrid
                stroke="rgba(148, 163, 184, 0.08)"
                vertical={false}
              />

              <XAxis
                dataKey="update_id"
                tick={{
                  fontSize: 9,
                }}
                tickLine={false}
                axisLine={false}
                stroke="#64748b"
              />

              <YAxis
                tick={{
                  fontSize: 9,
                }}
                tickLine={false}
                axisLine={false}
                stroke="#64748b"
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
                  Number(value ?? 0).toFixed(3),
                ]}
              />

              <Area
                type="monotone"
                dataKey="cumulative_reward"
                name="Cumulative reward"
                stroke="#22d3ee"
                strokeWidth={2}
                fill="url(#rewardGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}


export default RewardChart;
