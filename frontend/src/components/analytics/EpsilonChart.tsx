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
  EpsilonPoint,
} from "../../types/analytics";


interface EpsilonChartProps {
  data: EpsilonPoint[];
  currentEpsilon: number | null;
}


function EpsilonChart({
  data,
  currentEpsilon,
}: EpsilonChartProps) {
  return (
    <section className="analytics-chart-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            EXPLORATION POLICY
          </span>

          <h3>
            Epsilon Decay
          </h3>
        </div>

        <span className="epsilon-current">
          eps{" "}
          {currentEpsilon === null
            ? "--"
            : currentEpsilon.toFixed(4)}
        </span>
      </div>

      {data.length === 0 ? (
        <div className="empty-chart">
          Epsilon history will appear
          after training episodes complete.
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
                  id="epsilonGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#a78bfa"
                    stopOpacity={0.35}
                  />
                  <stop
                    offset="100%"
                    stopColor="#a78bfa"
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
                tick={{
                  fontSize: 9,
                }}
                tickLine={false}
                axisLine={false}
                stroke="#64748b"
              />

              <YAxis
                domain={[0, 1]}
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
                  Number(value ?? 0).toFixed(4),
                ]}
              />

              <Area
                type="monotone"
                dataKey="epsilon"
                name="epsilon"
                stroke="#a78bfa"
                strokeWidth={2}
                fill="url(#epsilonGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}


export default EpsilonChart;
