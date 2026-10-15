import { cva, type VariantProps } from "class-variance-authority";
import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";

const alertVariants = cva("flex gap-3 rounded-xl border px-4 py-3 text-sm leading-relaxed [&>svg]:mt-0.5 [&>svg]:size-[18px] [&>svg]:shrink-0", {
  variants: {
    variant: {
      info: "border-[#d2e3fc] bg-accent/70 [&>svg]:text-primary",
      success: "border-[#ceead6] bg-success-soft [&>svg]:text-success",
      warning: "border-[#feefc3] bg-warning-soft [&>svg]:text-warning-foreground",
      danger: "border-[#fad2cf] bg-danger-soft [&>svg]:text-danger",
    },
  },
  defaultVariants: { variant: "info" },
});

const icons = { info: Info, success: CheckCircle2, warning: AlertTriangle, danger: XCircle };

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof alertVariants> {
  title?: string;
}

export function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  const Icon = icons[variant ?? "info"];
  return (
    <div role={variant === "danger" ? "alert" : "status"} className={cn(alertVariants({ variant }), className)} {...props}>
      <Icon aria-hidden />
      <div className="min-w-0 space-y-1">
        {title && <p className="font-medium text-foreground">{title}</p>}
        {children && <div className="text-[#3c4043]">{children}</div>}
      </div>
    </div>
  );
}
