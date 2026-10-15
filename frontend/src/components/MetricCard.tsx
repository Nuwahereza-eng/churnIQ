import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export type Tone = "blue" | "red" | "green" | "amber" | "purple" | "teal" | "neutral";

/** Tinted icon backgrounds; the icon colour carries no data, the label does. */
export const TONES: Record<Tone, string> = {
  blue: "bg-accent text-primary",
  red: "bg-danger-soft text-danger",
  green: "bg-success-soft text-success",
  amber: "bg-warning-soft text-warning-foreground",
  purple: "bg-purple-soft text-purple",
  teal: "bg-teal-soft text-teal-foreground",
  neutral: "bg-muted text-muted-foreground",
};

interface MetricCardProps {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: LucideIcon;
  tone?: Tone;
  size?: "default" | "compact";
  className?: string;
}

/** Stat tile: icon, label, headline value, short supporting text. */
export function MetricCard({ label, value, hint, icon: Icon, tone = "blue", size = "default", className }: MetricCardProps) {
  const compact = size === "compact";
  return (
    <div
      className={cn(
        "min-w-0 rounded-xl border border-border bg-card shadow-xs transition-shadow duration-200 hover:shadow-sm",
        compact ? "px-4 py-3.5" : "px-5 py-4",
        className,
      )}
    >
      <div className="flex items-center gap-2.5">
        {Icon && (
          <span className={cn("flex shrink-0 items-center justify-center rounded-lg", compact ? "size-7" : "size-9", TONES[tone])}>
            <Icon className={compact ? "size-4" : "size-[18px]"} aria-hidden />
          </span>
        )}
        <p className="min-w-0 text-[13px] font-medium leading-tight text-muted-foreground">{label}</p>
      </div>
      <p
        className={cn(
          "font-semibold tracking-[-0.02em] text-foreground tabular-nums",
          compact ? "mt-2 text-2xl" : "mt-3 text-[30px] leading-9",
        )}
      >
        {value}
      </p>
      {hint && <p className="mt-1 text-xs leading-4 text-muted-foreground">{hint}</p>}
    </div>
  );
}
