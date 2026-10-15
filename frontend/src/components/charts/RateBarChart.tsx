import { Bar, BarChart, CartesianGrid, LabelList, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { COLORS } from "@/lib/colors";
import { formatInt, formatPct } from "@/lib/format";
import type { GroupRate } from "@/types/api";

import { TooltipBox, axisProps, cursorFill } from "./ChartTooltip";

interface RateBarChartProps {
  data: GroupRate[];
  overallRate?: number;
  layout?: "horizontal" | "vertical"; // vertical = bars grow upward
  labelWidth?: number;
  height?: number;
  color?: string;
}

/** Churn rate per group, with the overall churn rate as a dashed reference line. */
export function RateBarChart({ data, overallRate, layout = "horizontal", labelWidth = 150, height, color = COLORS.stayed }: RateBarChartProps) {
  const rows = data.map((d) => ({ ...d, label: d.group }));
  // Round the top of the rate axis up to the next 10% so short bars are not dwarfed by an empty 100% scale.
  const niceMax = Math.min(1, Math.ceil((Math.max(...data.map((d) => d.churn_rate), overallRate ?? 0) + 0.05) * 10) / 10);
  const tooltip = (
    <Tooltip
      cursor={cursorFill}
      content={({ active, payload }) => {
        if (!active || !payload?.length) return null;
        const d = payload[0].payload as GroupRate;
        return (
          <TooltipBox
            title={d.group}
            rows={[
              { label: "Churn rate", value: formatPct(d.churn_rate) },
              { label: "Customers", value: formatInt(d.customers) },
              { label: "Churned", value: formatInt(d.churned) },
            ]}
          />
        );
      }}
    />
  );

  if (layout === "vertical") {
    return (
      <ResponsiveContainer width="100%" height={height ?? 260}>
        <BarChart data={rows} margin={{ top: 20, right: 8, left: -8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={COLORS.grid} />
          <XAxis dataKey="label" {...axisProps} interval={0} />
          <YAxis {...axisProps} axisLine={false} domain={[0, niceMax]} tickFormatter={(v) => formatPct(v, 0)} width={48} />
          {tooltip}
          {overallRate !== undefined && (
            <ReferenceLine y={overallRate} stroke={COLORS.reference} strokeDasharray="4 4" />
          )}
          <Bar dataKey="churn_rate" fill={color} radius={[4, 4, 0, 0]} maxBarSize={40} isAnimationActive={false}>
            <LabelList dataKey="churn_rate" position="top" formatter={(v: unknown) => formatPct(Number(v))} fill={COLORS.ink} fontSize={12} fontWeight={500} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height ?? Math.max(140, rows.length * 42 + 30)}>
      <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 48, left: 0, bottom: 0 }}>
        <CartesianGrid horizontal={false} stroke={COLORS.grid} />
        <XAxis type="number" {...axisProps} domain={[0, niceMax]} tickFormatter={(v) => formatPct(v, 0)} />
        <YAxis type="category" dataKey="label" {...axisProps} axisLine={false} width={labelWidth} />
        {tooltip}
        {overallRate !== undefined && (
          <ReferenceLine x={overallRate} stroke={COLORS.reference} strokeDasharray="4 4" />
        )}
        <Bar dataKey="churn_rate" fill={color} radius={[0, 4, 4, 0]} maxBarSize={18} isAnimationActive={false}>
          <LabelList dataKey="churn_rate" position="right" formatter={(v: unknown) => formatPct(Number(v))} fill={COLORS.ink} fontSize={12} fontWeight={500} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
