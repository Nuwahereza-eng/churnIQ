import { formatInt, formatPct } from "@/lib/format";
import { COLORS } from "@/lib/colors";
import type { GroupRate } from "@/types/api";

import { Legend } from "../ChartCard";

/**
 * 100% stacked bar per group: churned share and stayed share of that group's
 * customers, with the group size. Plain HTML so labels never collide.
 */
export function StackedShareChart({ data }: { data: GroupRate[] }) {
  return (
    <div>
      <Legend
        items={[
          { label: "Churned", color: COLORS.churned },
          { label: "Stayed", color: COLORS.stayed },
        ]}
      />
      <ul className="space-y-4" aria-label="Churned and stayed share by group">
        {data.map((d) => {
          const stayed = d.customers - d.churned;
          return (
            <li key={d.group}>
              <div className="mb-1.5 flex items-baseline justify-between gap-3 text-[13px]">
                <span className="font-medium text-foreground">{d.group}</span>
                <span className="text-muted-foreground tabular-nums">
                  <span className="font-semibold text-foreground">{formatPct(d.churn_rate)}</span> churned ·{" "}
                  {formatInt(d.customers)} customers
                </span>
              </div>
              <div
                className="flex h-3 w-full gap-0.5 overflow-hidden rounded-full"
                role="img"
                aria-label={`${d.group}: ${formatPct(d.churn_rate)} churned (${formatInt(d.churned)}), ${formatPct(1 - d.churn_rate)} stayed (${formatInt(stayed)})`}
              >
                <div
                  className="h-full rounded-l-full"
                  style={{ width: `${d.churn_rate * 100}%`, backgroundColor: COLORS.churned }}
                  title={`Churned: ${formatInt(d.churned)}`}
                />
                <div
                  className="h-full flex-1 rounded-r-full"
                  style={{ backgroundColor: COLORS.stayed, opacity: 0.85 }}
                  title={`Stayed: ${formatInt(stayed)}`}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
