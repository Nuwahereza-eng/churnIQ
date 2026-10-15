import { cn } from "@/lib/utils";

/** ChurnIQ mark: a retention curve that dips and recovers, inside a rounded tile. */
export function Logo({ collapsed = false, className }: { collapsed?: boolean; className?: string }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg viewBox="0 0 32 32" className="size-8 shrink-0" aria-hidden>
        <rect width="32" height="32" rx="9" fill="#1a73e8" />
        <path d="M7 12.5c3.2 0 4.2 8.5 8.4 8.5S21.6 10 25 10" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" />
        <circle cx="25" cy="10" r="2.4" fill="#fff" />
        <circle cx="25" cy="10" r="1.1" fill="#1a73e8" />
      </svg>
      {!collapsed && (
        <div className="leading-tight">
          <p className="text-[17px] font-semibold tracking-[-0.01em] text-foreground">
            Churn<span className="text-primary">IQ</span>
          </p>
          <p className="text-[11px] text-muted-foreground">Churn analytics · research</p>
        </div>
      )}
    </div>
  );
}
