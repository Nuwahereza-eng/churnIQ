import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { COLORS } from "@/lib/colors";
import { formatInt, formatPct } from "@/lib/format";

import { TooltipBox } from "./ChartTooltip";

/** Donut of stayed vs churned customers, with the churn rate in the centre and a labelled legend. */
export function DistributionChart({ stayed, churned }: { stayed: number; churned: number }) {
  const total = stayed + churned;
  const parts = [
    { label: "Stayed", value: stayed, color: COLORS.stayed },
    { label: "Churned", value: churned, color: COLORS.churned },
  ];
  return (
    <figure
      aria-label={`Stayed ${formatInt(stayed)} (${formatPct(stayed / total)}), churned ${formatInt(churned)} (${formatPct(churned / total)})`}
      className="flex flex-col items-center gap-6 sm:flex-row"
    >
      <div className="relative size-[180px] shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={parts}
              dataKey="value"
              nameKey="label"
              innerRadius={62}
              outerRadius={88}
              startAngle={90}
              endAngle={-270}
              stroke="#ffffff"
              strokeWidth={2}
              cornerRadius={4}
              paddingAngle={1}
              isAnimationActive={false}
            >
              {parts.map((p) => (
                <Cell key={p.label} fill={p.color} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0].payload as (typeof parts)[number];
                return <TooltipBox title={d.label} rows={[{ label: "Customers", value: `${formatInt(d.value)} (${formatPct(d.value / total)})`, color: d.color }]} />;
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold tracking-[-0.02em] tabular-nums">{formatPct(churned / total)}</span>
          <span className="text-xs text-muted-foreground">churn rate</span>
        </div>
      </div>
      <figcaption className="grid w-full gap-3">
        {parts.map((p) => (
          <div key={p.label} className="flex items-center justify-between gap-3 rounded-lg bg-subtle px-3 py-2.5">
            <span className="flex items-center gap-2 text-[13px] text-muted-foreground">
              <span aria-hidden className="size-2.5 rounded-full" style={{ backgroundColor: p.color }} />
              {p.label}
            </span>
            <span className="text-right">
              <span className="block text-[15px] font-semibold tabular-nums">{formatInt(p.value)}</span>
              <span className="block text-xs text-muted-foreground tabular-nums">{formatPct(p.value / total)}</span>
            </span>
          </div>
        ))}
      </figcaption>
    </figure>
  );
}
