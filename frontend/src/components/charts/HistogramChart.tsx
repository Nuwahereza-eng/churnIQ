import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Legend } from "@/components/ChartCard";
import { COLORS } from "@/lib/colors";
import { formatInt, formatPct } from "@/lib/format";
import type { HistogramBin } from "@/types/api";

import { TooltipBox, axisProps } from "./ChartTooltip";

/**
 * Distribution of monthly charges within each class, as a share of that class
 * (comparable despite the class imbalance). Bins are contiguous, so an area
 * outline of the histogram is a faithful shape.
 */
export function HistogramChart({ data, height = 260 }: { data: HistogramBin[]; height?: number }) {
  const rows = data.map((b) => ({ ...b, label: `${b.start.toFixed(0)}–${b.end.toFixed(0)}` }));
  return (
    <div>
      <Legend
        items={[
          { label: "Stayed (share of stayers)", color: COLORS.stayed },
          { label: "Churned (share of churners)", color: COLORS.churned },
        ]}
      />
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={rows} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          <defs>
            <linearGradient id="fill-stayed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={COLORS.stayed} stopOpacity={0.22} />
              <stop offset="100%" stopColor={COLORS.stayed} stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="fill-churned" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={COLORS.churned} stopOpacity={0.2} />
              <stop offset="100%" stopColor={COLORS.churned} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} stroke={COLORS.grid} />
          <XAxis dataKey="label" {...axisProps} interval="preserveStartEnd" minTickGap={12} />
          <YAxis {...axisProps} axisLine={false} tickFormatter={(v) => formatPct(v, 0)} width={48} />
          <Tooltip
            cursor={{ stroke: COLORS.reference, strokeDasharray: "3 3" }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload as HistogramBin & { label: string };
              return (
                <TooltipBox
                  title={`Monthly charges ${d.label}`}
                  rows={[
                    { label: "Stayed", value: `${formatPct(d.stayed_share)} (${formatInt(d.stayed)})`, color: COLORS.stayed },
                    { label: "Churned", value: `${formatPct(d.churned_share)} (${formatInt(d.churned)})`, color: COLORS.churned },
                  ]}
                />
              );
            }}
          />
          <Area
            type="monotone"
            dataKey="stayed_share"
            name="Stayed"
            stroke={COLORS.stayed}
            strokeWidth={2}
            fill="url(#fill-stayed)"
            activeDot={{ r: 4, stroke: "#fff", strokeWidth: 2 }}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="churned_share"
            name="Churned"
            stroke={COLORS.churned}
            strokeWidth={2}
            fill="url(#fill-churned)"
            activeDot={{ r: 4, stroke: "#fff", strokeWidth: 2 }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
