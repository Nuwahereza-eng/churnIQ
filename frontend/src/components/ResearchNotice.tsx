import { FlaskConical } from "lucide-react";

import { cn } from "@/lib/utils";

/** Persistent reminder that figures come from a public sample dataset, not a live operator. */
export function ResearchNotice({ className, compact = false }: { className?: string; compact?: boolean }) {
  return (
    <div className={cn("flex items-start gap-2 text-xs text-muted-foreground", className)}>
      <FlaskConical className="mt-0.5 size-3.5 shrink-0" aria-hidden />
      <p>
        {compact
          ? "Research prototype · IBM Telco Customer Churn sample dataset (fictional provider)"
          : "Research prototype. All figures come from the public IBM Telco Customer Churn sample dataset, which describes a fictional telecom provider. They are not live statistics from any operator."}
      </p>
    </div>
  );
}
