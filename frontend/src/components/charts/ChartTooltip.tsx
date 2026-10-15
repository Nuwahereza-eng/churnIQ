import type { ReactNode } from "react";

import { COLORS } from "@/lib/colors";

export interface TooltipRow {
  label: string;
  value: ReactNode;
  color?: string;
}

/** Shared tooltip surface for all charts. */
export function TooltipBox({ title, rows }: { title?: ReactNode; rows: TooltipRow[] }) {
  return (
    <div className="min-w-40 rounded-lg border border-border bg-card px-3 py-2.5 text-xs shadow-md">
      {title !== undefined && <p className="mb-1.5 font-semibold text-foreground">{title}</p>}
      <ul className="space-y-1">
        {rows.map((r) => (
          <li key={r.label} className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-muted-foreground">
              {r.color && <span aria-hidden className="size-2 rounded-full" style={{ backgroundColor: r.color }} />}
              {r.label}
            </span>
            <span className="tabular-nums font-medium text-foreground">{r.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export const axisProps = {
  stroke: COLORS.axis,
  tick: { fill: COLORS.axisText, fontSize: 12 },
  tickLine: false,
} as const;

export const cursorFill = { fill: "rgba(26,115,232,0.06)" };
