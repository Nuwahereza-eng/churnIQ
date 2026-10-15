import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { TONES, type Tone } from "@/components/MetricCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  description?: string;
  footnote?: ReactNode;
  actions?: ReactNode;
  icon?: LucideIcon;
  tone?: Tone;
  children: ReactNode;
  className?: string;
}

export function ChartCard({ title, description, footnote, actions, icon: Icon, tone = "blue", children, className }: ChartCardProps) {
  return (
    <Card className={cn("flex min-w-0 flex-col", className)}>
      <CardHeader className="flex-row items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          {Icon && (
            <span className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", TONES[tone])}>
              <Icon className="size-4" aria-hidden />
            </span>
          )}
          <div className="min-w-0 space-y-0.5">
            <CardTitle>{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
        </div>
        {actions}
      </CardHeader>
      <CardContent className="flex-1">
        {children}
        {footnote && <p className="mt-4 border-t border-[#eceff1] pt-3 text-xs leading-5 text-muted-foreground">{footnote}</p>}
      </CardContent>
    </Card>
  );
}

/** Legend shown above a chart (always present for 2+ series). */
export function Legend({ items }: { items: { label: string; color: string; dashed?: boolean }[] }) {
  return (
    <ul className="mb-3 flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
      {items.map((i) => (
        <li key={i.label} className="flex items-center gap-1.5">
          {i.dashed ? (
            <span aria-hidden className="h-0 w-4 border-t-2 border-dashed" style={{ borderColor: i.color }} />
          ) : (
            <span aria-hidden className="size-2.5 rounded-full" style={{ backgroundColor: i.color }} />
          )}
          {i.label}
        </li>
      ))}
    </ul>
  );
}
