import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  TDErrorPoint,
} from "../../types/analytics";


interface TDErrorChartProps {
  data: TDErrorPoint[];
}


function TDErrorChart({
  data,
}: TDErrorChartProps) {
  return (
    <section className="analytics-chart-card">
      <div className="chart-card-header">
        <div>
          <span className="chart-eyebrow">
            BELLMAN RESIDUAL
          </span>

          <h3>
            TD-Error Evolution
          </h3>
        </div>

        <span className="chart-window-badge">
          |d| mean
        </span>
      </div>

      {data.length === 0 ? (
        <div className="empty-chart">
          Learning updates will appear here.
        </div>
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
                  Number(value ?? 0).toFixed(4),
                ]}
              />

              <ReferenceLine
                y={0}
                stroke="rgba(148, 163, 184, 0.3)"
              />

              <Line
                type="monotone"
                dataKey="td_error"
                name="TD error d"
                stroke="#f59e0b"
                strokeWidth={1}
                dot={false}
                opacity={0.6}
              />

              <Line
                type="monotone"
                dataKey={
                  "rolling_mean_absolute_td_error"
                }
                name="Rolling mean |d|"
                stroke="#22d3ee"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}


export default TDErrorChart;
