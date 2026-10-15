import * as React from "react";

import { cn } from "@/lib/utils";

export function Table({ className, ...props }: React.TableHTMLAttributes<HTMLTableElement>) {
  return (
    <div className="relative w-full overflow-x-auto">
      <table className={cn("w-full caption-bottom text-sm", className)} {...props} />
    </div>
  );
}

export const TableHeader = (p: React.HTMLAttributes<HTMLTableSectionElement>) => (
  <thead {...p} className={cn("[&_tr]:border-b [&_tr]:border-border bg-subtle", p.className)} />
);
export const TableBody = (p: React.HTMLAttributes<HTMLTableSectionElement>) => (
  <tbody {...p} className={cn("[&_tr:last-child]:border-0", p.className)} />
);
export const TableRow = (p: React.HTMLAttributes<HTMLTableRowElement>) => (
  <tr {...p} className={cn("border-b border-[#eceff1] transition-colors duration-150 hover:bg-[#f6f9fe]", p.className)} />
);
export const TableHead = (p: React.ThHTMLAttributes<HTMLTableCellElement>) => (
  <th
    {...p}
    className={cn("h-11 px-3 text-left align-middle text-xs font-medium whitespace-nowrap text-muted-foreground", p.className)}
  />
);
export const TableCell = (p: React.TdHTMLAttributes<HTMLTableCellElement>) => (
  <td {...p} className={cn("px-3 py-3 align-middle whitespace-nowrap text-foreground", p.className)} />
);
