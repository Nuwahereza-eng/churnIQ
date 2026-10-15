import { useId, type ReactElement, cloneElement } from "react";

import { Label } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface FormFieldProps {
  label: string;
  help?: string;
  error?: string;
  className?: string;
  children: ReactElement<Record<string, unknown>>;
}

/** Label + control + help/error text, wired up with ids and aria attributes. */
export function FormField({ label, help, error, className, children }: FormFieldProps) {
  const id = useId();
  const helpId = `${id}-help`;
  const errorId = `${id}-error`;
  const describedBy = [help && helpId, error && errorId].filter(Boolean).join(" ") || undefined;
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <Label htmlFor={id}>{label}</Label>
      {cloneElement(children, {
        id,
        "aria-describedby": describedBy,
        "aria-invalid": error ? true : undefined,
      })}
      {error ? (
        <p id={errorId} className="flex items-center gap-1 text-xs font-medium text-danger">
          {error}
        </p>
      ) : help ? (
        <p id={helpId} className="text-xs text-muted-foreground">
          {help}
        </p>
      ) : null}
    </div>
  );
}
