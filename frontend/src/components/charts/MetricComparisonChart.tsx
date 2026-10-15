import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Legend } from "@/components/ChartCard";
import { COLORS, MODEL_COLORS } from "@/lib/colors";
import { formatNum } from "@/lib/format";
import type { ModelResult } from "@/types/api";

import { TooltipBox, axisProps, cursorFill } from "./ChartTooltip";

const METRICS = [
  ["accuracy", "Accuracy"],
  ["precision", "Precision"],
  ["recall", "Recall"],
  ["f1", "F1"],
  ["roc_auc", "ROC-AUC"],
] as const;

export function MetricComparisonChart({ models }: { models: ModelResult[] }) {
  const rows = METRICS.map(([key, label]) => {
    const row: Record<string, string | number> = { metric: label };
    for (const m of models) row[m.name] = (m.test.metrics[key] as number | null) ?? 0;
    return row;
  });
  return (
    <div>
      <Legend items={models.map((m) => ({ label: m.name, color: MODEL_COLORS[m.name] ?? COLORS.axis }))} />
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={rows} margin={{ top: 4, right: 8, left: -8, bottom: 0 }} barGap={3} barCategoryGap="22%">
          <CartesianGrid vertical={false} stroke={COLORS.grid} />
          <XAxis dataKey="metric" {...axisProps} />
          <YAxis domain={[0, 1]} {...axisProps} axisLine={false} width={44} />
          <Tooltip
            cursor={cursorFill}
            content={({ active, payload, label }) =>
              active && payload?.length ? (
                <TooltipBox
                  title={String(label)}
                  rows={payload.map((p) => ({ label: String(p.name), value: formatNum(Number(p.value)), color: String(p.color) }))}
                />
              ) : null
            }
          />
          {models.map((m) => (
            <Bar
              key={m.name}
              dataKey={m.name}
              fill={MODEL_COLORS[m.name] ?? COLORS.axis}
              radius={[3, 3, 0, 0]}
              maxBarSize={24}
              isAnimationActive={false}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
