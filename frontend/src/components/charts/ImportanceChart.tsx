import { Bar, BarChart, CartesianGrid, Cell, ErrorBar, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Legend } from "@/components/ChartCard";
import { COLORS } from "@/lib/colors";

import { TooltipBox, axisProps, cursorFill } from "./ChartTooltip";

interface ImportanceChartProps {
  data: { feature: string; value: number; error?: number }[];
  valueLabel: string;
  signed?: boolean; // diverging: positive = higher churn odds
  labelWidth?: number;
}

export function ImportanceChart({ data, valueLabel, signed = false, labelWidth = 170 }: ImportanceChartProps) {
  const height = Math.max(160, data.length * 26 + 40);
  return (
    <div>
      {signed && (
        <Legend
          items={[
            { label: "Associated with higher churn odds", color: COLORS.churned },
            { label: "Associated with lower churn odds", color: COLORS.stayed },
          ]}
        />
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
          <CartesianGrid horizontal={false} stroke={COLORS.grid} />
          <XAxis type="number" {...axisProps} tickFormatter={(v) => Number(v).toFixed(signed ? 1 : 3)} />
          <YAxis type="category" dataKey="feature" {...axisProps} axisLine={false} width={labelWidth} interval={0} />
          {signed && <ReferenceLine x={0} stroke={COLORS.reference} />}
          <Tooltip
            cursor={cursorFill}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload as { feature: string; value: number; error?: number };
              const rows = [{ label: valueLabel, value: d.value.toFixed(4) }];
              if (d.error !== undefined) rows.push({ label: "Std. deviation", value: d.error.toFixed(4) });
              return <TooltipBox title={d.feature} rows={rows} />;
            }}
          />
          <Bar dataKey="value" radius={4} maxBarSize={14} isAnimationActive={false} fill={COLORS.stayed}>
            {signed && data.map((d) => <Cell key={d.feature} fill={d.value >= 0 ? COLORS.churned : COLORS.stayed} />)}
            {!signed && data.some((d) => d.error !== undefined) && (
              <ErrorBar dataKey="error" width={4} stroke={COLORS.axisText} direction="x" />
            )}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
