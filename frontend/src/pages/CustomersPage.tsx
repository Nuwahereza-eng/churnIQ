import { ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, CircleCheck, CircleX, Search, SlidersHorizontal, X } from "lucide-react";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { EmptyState, ErrorState } from "@/components/States";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Label, NativeSelect } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useApi } from "@/hooks/useApi";
import { useDebounce } from "@/hooks/useDebounce";
import { formatInt, formatMoney } from "@/lib/format";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";
import type { CustomerQuery, SortableColumn } from "@/types/api";

const CONTRACTS = ["Month-to-month", "One year", "Two year"];
const INTERNET = ["DSL", "Fiber optic", "No"];
const PAGE_SIZES = [10, 20, 50];

const COLUMNS: { key: SortableColumn; label: string; numeric?: boolean; className?: string }[] = [
  { key: "customerID", label: "Customer ID" },
  { key: "tenure", label: "Tenure (mo)", numeric: true },
  { key: "Contract", label: "Contract" },
  { key: "InternetService", label: "Internet" },
  { key: "PaymentMethod", label: "Payment method", className: "hidden md:table-cell" },
  { key: "TechSupport", label: "Tech support", className: "hidden 2xl:table-cell" },
  { key: "MonthlyCharges", label: "Monthly", numeric: true },
  { key: "TotalCharges", label: "Total", numeric: true, className: "hidden sm:table-cell" },
  { key: "Churn", label: "Churn" },
];

interface Filters {
  search: string;
  contract: string;
  internet: string;
  churn: "" | "Yes" | "No";
  tenureMin: string;
  tenureMax: string;
}

const EMPTY: Filters = { search: "", contract: "", internet: "", churn: "", tenureMin: "", tenureMax: "" };

function parseTenure(v: string): number | null {
  if (v.trim() === "") return null;
  const n = Number(v);
  return Number.isInteger(n) && n >= 0 && n <= 1200 ? n : NaN;
}

export function CustomersPage() {
  const [filters, setFilters] = useState<Filters>(EMPTY);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [sortBy, setSortBy] = useState<SortableColumn>("customerID");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const search = useDebounce(filters.search, 300);

  const tMin = parseTenure(filters.tenureMin);
  const tMax = parseTenure(filters.tenureMax);
  const tenureError =
    Number.isNaN(tMin) || Number.isNaN(tMax)
      ? "Tenure must be a whole number of months."
      : tMin !== null && tMax !== null && tMin > tMax
        ? "Minimum tenure cannot exceed maximum tenure."
        : null;

  const query: CustomerQuery = {
    page,
    page_size: pageSize,
    search: search || undefined,
    contract: filters.contract ? [filters.contract] : [],
    internet_service: filters.internet ? [filters.internet] : [],
    churn: filters.churn,
    tenure_min: tenureError ? null : tMin,
    tenure_max: tenureError ? null : tMax,
    sort_by: sortBy,
    sort_dir: sortDir,
  };
  const key = JSON.stringify(query);
  const result = useApi(() => api.customers(query), [key]);

  // Return to page 1 whenever filters change
  useEffect(() => setPage(1), [search, filters.contract, filters.internet, filters.churn, filters.tenureMin, filters.tenureMax, pageSize]);

  const set = <K extends keyof Filters>(k: K, v: Filters[K]) => setFilters((f) => ({ ...f, [k]: v }));
  const activeCount = (Object.keys(EMPTY) as (keyof Filters)[]).filter((k) => filters[k] !== EMPTY[k]).length;
  const activeFilters = activeCount > 0;

  const toggleSort = (col: SortableColumn) => {
    if (col === sortBy) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortBy(col);
      setSortDir("asc");
    }
  };

  const data = result.data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customer Explorer"
        description="Browse, search and filter customer records from the public IBM Telco sample dataset. Demographic fields are not shown."
      />

      <Card className="p-5 sm:p-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <span className="flex size-8 items-center justify-center rounded-lg bg-accent text-primary">
              <SlidersHorizontal className="size-4" aria-hidden />
            </span>
            <h2 className="text-[17px] font-semibold">Filter customers</h2>
            {activeFilters && <Badge>{activeCount} active</Badge>}
          </div>
          {activeFilters && (
            <Button variant="ghost" size="sm" onClick={() => setFilters(EMPTY)}>
              <X /> Clear filters
            </Button>
          )}
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-[minmax(200px,1.4fr)_repeat(3,minmax(140px,1fr))_minmax(190px,1fr)]">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="search">Search customer ID</Label>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
              <Input
                id="search"
                value={filters.search}
                onChange={(e) => set("search", e.target.value)}
                placeholder="e.g. 7590-VHVEG"
                maxLength={40}
                className="pl-9"
              />
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="contract">Contract</Label>
            <NativeSelect id="contract" value={filters.contract} onChange={(e) => set("contract", e.target.value)}>
              <option value="">All contracts</option>
              {CONTRACTS.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </NativeSelect>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="internet">Internet service</Label>
            <NativeSelect id="internet" value={filters.internet} onChange={(e) => set("internet", e.target.value)}>
              <option value="">All services</option>
              {INTERNET.map((c) => (
                <option key={c} value={c}>
                  {c === "No" ? "No internet" : c}
                </option>
              ))}
            </NativeSelect>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="churn">Churn status</Label>
            <NativeSelect id="churn" value={filters.churn} onChange={(e) => set("churn", e.target.value as Filters["churn"])}>
              <option value="">All customers</option>
              <option value="Yes">Churned</option>
              <option value="No">Stayed</option>
            </NativeSelect>
          </div>
          <fieldset className="flex flex-col gap-1.5">
            <legend className="mb-1.5 text-[13px] font-medium leading-none">Tenure (months)</legend>
            <div className="flex items-center gap-2">
              <Input
                aria-label="Minimum tenure"
                inputMode="numeric"
                placeholder="Min"
                value={filters.tenureMin}
                onChange={(e) => set("tenureMin", e.target.value)}
                aria-invalid={tenureError ? true : undefined}
              />
              <span className="text-muted-foreground">–</span>
              <Input
                aria-label="Maximum tenure"
                inputMode="numeric"
                placeholder="Max"
                value={filters.tenureMax}
                onChange={(e) => set("tenureMax", e.target.value)}
                aria-invalid={tenureError ? true : undefined}
              />
            </div>
          </fieldset>
        </div>
        {tenureError && <p className="mt-2 text-xs font-medium text-danger">{tenureError}</p>}
      </Card>

      <div className="flex flex-wrap items-center justify-between gap-2 px-1 text-[13px] text-muted-foreground">
        <span aria-live="polite">
          {data ? (
            <>
              <span className="font-semibold text-foreground tabular-nums">{formatInt(data.total)}</span> matching customer
              {data.total === 1 ? "" : "s"}
              {activeFilters ? " for the current filters" : " in the dataset"}
            </>
          ) : (
            " "
          )}
        </span>
        {result.loading && data && <span className="text-primary">Updating…</span>}
      </div>

      {result.error ? (
        <ErrorState error={result.error} onRetry={result.reload} />
      ) : (
        <Card className="relative overflow-hidden">
          <div aria-hidden className={cn("absolute inset-x-0 top-0 z-10 h-0.5 overflow-hidden", !(result.loading && data) && "invisible")}>
            <div className="h-full w-1/3 animate-progress bg-primary" />
          </div>
          <Table aria-busy={result.loading} aria-label="Customer records">
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                {COLUMNS.map((c) => {
                  const active = sortBy === c.key;
                  const Icon = !active ? ArrowUpDown : sortDir === "asc" ? ArrowUp : ArrowDown;
                  return (
                    <TableHead
                      key={c.key}
                      className={cn(c.numeric && "text-right", c.className)}
                      aria-sort={active ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
                    >
                      <button
                        type="button"
                        onClick={() => toggleSort(c.key)}
                        className={cn(
                          "inline-flex items-center gap-1 rounded-md px-1 py-0.5 transition-colors hover:text-foreground cursor-pointer",
                          active && "text-primary",
                          c.numeric && "flex-row-reverse",
                        )}
                      >
                        {c.label}
                        <Icon className={cn("size-3.5", !active && "opacity-50")} aria-hidden />
                      </button>
                    </TableHead>
                  );
                })}
              </TableRow>
            </TableHeader>
            <TableBody>
              {result.loading && !data
                ? Array.from({ length: 8 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell colSpan={COLUMNS.length}>
                        <Skeleton className="h-5" />
                      </TableCell>
                    </TableRow>
                  ))
                : data?.items.map((r) => (
                    <TableRow key={r.customerID} className={cn("transition-opacity", result.loading && "opacity-60")}>
                      <TableCell className="font-mono text-[13px] text-[#3c4043]">{r.customerID}</TableCell>
                      <TableCell className="text-right tabular-nums">{r.tenure}</TableCell>
                      <TableCell>{r.Contract}</TableCell>
                      <TableCell>{r.InternetService === "No" ? "None" : r.InternetService}</TableCell>
                      <TableCell className="hidden md:table-cell">{r.PaymentMethod}</TableCell>
                      <TableCell className="hidden 2xl:table-cell">{r.TechSupport}</TableCell>
                      <TableCell className="text-right tabular-nums">{formatMoney(r.MonthlyCharges)}</TableCell>
                      <TableCell className="hidden text-right tabular-nums sm:table-cell">{formatMoney(r.TotalCharges)}</TableCell>
                      <TableCell>
                        {r.Churn === "Yes" ? (
                          <Badge variant="danger">
                            <CircleX aria-hidden /> Churned
                          </Badge>
                        ) : (
                          <Badge variant="success">
                            <CircleCheck aria-hidden /> Stayed
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
            </TableBody>
          </Table>
          {data && data.items.length === 0 && (
            <EmptyState
              title="No customers match these filters"
              description="Try widening the tenure range or clearing a filter."
              action={
                <Button variant="outline" size="sm" onClick={() => setFilters(EMPTY)}>
                  Clear filters
                </Button>
              }
            />
          )}
          {data && data.total > 0 && (
            <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border bg-subtle px-4 py-3 text-[13px]">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Label htmlFor="page-size" className="font-normal text-muted-foreground">
                  Rows per page
                </Label>
                <NativeSelect id="page-size" className="h-8 w-[76px] bg-card" value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
                  {PAGE_SIZES.map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </NativeSelect>
              </div>
              <div className="flex items-center gap-3">
                <span className="tabular-nums text-muted-foreground">
                  Page {data.page} of {data.total_pages}
                </span>
                <div className="flex gap-1">
                  <Button variant="secondary" size="icon" className="size-8 bg-card" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} aria-label="Previous page">
                    <ChevronLeft />
                  </Button>
                  <Button
                    variant="secondary"
                    size="icon"
                    className="size-8 bg-card"
                    disabled={page >= data.total_pages}
                    onClick={() => setPage((p) => p + 1)}
                    aria-label="Next page"
                  >
                    <ChevronRight />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}
      <Alert variant="info">
        Records originate from the public IBM Telco Customer Churn sample, which describes a fictional provider. Gender,
        age and household fields are omitted from this view because they are not needed for exploration.
      </Alert>
    </div>
  );
}
