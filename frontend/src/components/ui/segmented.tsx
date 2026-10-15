import { cn } from "@/lib/utils";

interface SegmentedProps<T extends string> {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
  label: string;
  className?: string;
}

/** Compact single-choice control (radio group semantics). */
export function Segmented<T extends string>({ value, onChange, options, label, className }: SegmentedProps<T>) {
  return (
    <div role="radiogroup" aria-label={label} className={cn("inline-flex flex-wrap gap-0.5 rounded-lg border border-border bg-subtle p-1", className)}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="radio"
          aria-checked={value === o.value}
          onClick={() => onChange(o.value)}
          className={cn(
            "rounded-md px-3 py-1.5 text-[13px] font-medium text-muted-foreground transition-colors duration-150 cursor-pointer focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/35",
            value === o.value ? "bg-card text-accent-foreground shadow-sm" : "hover:bg-card/70 hover:text-foreground",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
