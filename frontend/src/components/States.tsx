import { AlertCircle, Inbox, RefreshCw, ServerOff } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { ApiError } from "@/services/api";

export function LoadingState({ label = "Loading", rows = 3 }: { label?: string; rows?: number }) {
  return (
    <div role="status" aria-live="polite" className="space-y-4">
      <span className="sr-only">{label}…</span>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-[120px] rounded-xl" />
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} className={i === 0 && rows % 2 === 1 ? "h-64 rounded-xl xl:col-span-2" : "h-64 rounded-xl"} />
        ))}
      </div>
    </div>
  );
}

export function InlineLoading({ label }: { label: string }) {
  return (
    <div role="status" aria-live="polite" className="flex items-center gap-2 text-sm text-muted-foreground [&>svg]:text-primary">
      <RefreshCw className="size-4 animate-spin" aria-hidden />
      {label}
    </div>
  );
}

export function ErrorState({ error, onRetry, title }: { error: ApiError; onRetry?: () => void; title?: string }) {
  const unavailable = error.status === 503 || error.status === 0;
  const Icon = unavailable ? ServerOff : AlertCircle;
  return (
    <div role="alert" className="flex flex-col items-center rounded-xl border border-border bg-card px-6 py-12 text-center shadow-xs">
      <span className="flex size-12 items-center justify-center rounded-full bg-danger-soft text-danger">
        <Icon className="size-5" aria-hidden />
      </span>
      <h2 className="mt-4 text-lg font-semibold">
        {title ?? (unavailable ? "Service unavailable" : "Something went wrong")}
      </h2>
      <p className="mt-1 max-w-md text-sm text-muted-foreground">{error.message}</p>
      {error.details.length > 0 && (
        <ul className="mt-3 max-w-md list-disc text-left text-xs text-muted-foreground">
          {error.details.slice(0, 5).map((d) => (
            <li key={d}>{d}</li>
          ))}
        </ul>
      )}
      {onRetry && (
        <Button variant="outline" size="sm" className="mt-5" onClick={onRetry}>
          <RefreshCw /> Try again
        </Button>
      )}
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center px-6 py-12 text-center">
      <span className="flex size-12 items-center justify-center rounded-full bg-accent text-primary">
        <Inbox className="size-5" aria-hidden />
      </span>
      <h3 className="mt-4 text-[15px] font-semibold">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
