import {
  ArrowRight,
  CalendarClock,
  CircleDollarSign,
  Database,
  FileSignature,
  Percent,
  PieChart as PieIcon,
  ShieldCheck,
  Sparkles,
  UserCheck,
  UserMinus,
  Users,
  type LucideIcon,
} from "lucide-react";
import { Link } from "react-router-dom";

import { ChartCard } from "@/components/ChartCard";
import { DistributionChart } from "@/components/charts/DistributionChart";
import { HistogramChart } from "@/components/charts/HistogramChart";
import { RateBarChart } from "@/components/charts/RateBarChart";
import { StackedShareChart } from "@/components/charts/StackedShareChart";
import { MetricCard, TONES, type Tone } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/States";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useApi } from "@/hooks/useApi";
import { formatDate, formatInt, formatMoney, formatPct } from "@/lib/format";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";
import type { GroupRate, ModelMetrics, Overview } from "@/types/api";

const byRate = (rates: GroupRate[]) => [...rates].sort((a, b) => b.churn_rate - a.churn_rate);

export function OverviewPage() {
  const overview = useApi(api.overview);
  const metrics = useApi(api.modelMetrics);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customer churn overview"
        description="Explore customer retention patterns and model insights from the research dataset."
        actions={
          <>
            <Button asChild variant="secondary">
              <Link to="/customers">
                <Users /> Explore customers
              </Link>
            </Button>
            <Button asChild>
              <Link to="/predict">
                Predict churn <ArrowRight />
              </Link>
            </Button>
          </>
        }
      />

      {overview.loading && !overview.data && <LoadingState label="Loading overview" />}
      {overview.error && !overview.data && <ErrorState error={overview.error} onRetry={overview.reload} />}
      {overview.data && <OverviewContent data={overview.data} metrics={metrics} />}
    </div>
  );
}

function OverviewContent({
  data,
  metrics,
}: {
  data: Overview;
  metrics: { data: ModelMetrics | null; error: { message: string } | null; loading: boolean };
}) {
  return (
    <>
      <section aria-label="Key figures" className="grid grid-cols-1 gap-4 min-[420px]:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Users} tone="blue" label="Total customers" value={formatInt(data.total_customers)} hint="Records in the sample dataset" />
        <MetricCard icon={UserMinus} tone="red" label="Customers churned" value={formatInt(data.churned)} hint="Left within the last month" />
        <MetricCard icon={UserCheck} tone="green" label="Customers retained" value={formatInt(data.stayed)} hint="Still customers at the snapshot" />
        <MetricCard icon={Percent} tone="purple" label="Overall churn rate" value={formatPct(data.churn_rate)} hint="Churned ÷ total customers" />
      </section>

      <div className="grid gap-4 xl:grid-cols-5">
        <ChartCard
          className="xl:col-span-2"
          icon={PieIcon}
          title="Churn distribution"
          description="Customers who stayed versus customers who churned."
          footnote="The classes are imbalanced, so accuracy alone is a poor guide to model quality."
        >
          <DistributionChart stayed={data.stayed} churned={data.churned} />
        </ChartCard>
        <ChartCard
          icon={FileSignature}
          className="xl:col-span-3"
          title="Churn by contract type"
          description="Share of each contract's customers who churned or stayed."
          footnote={`Overall churn rate: ${formatPct(data.churn_rate)}.`}
        >
          <StackedShareChart data={data.churn_by_contract} />
        </ChartCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard icon={CalendarClock} title="Churn rate by tenure" description="Months with the provider, grouped. Dashed line: overall churn rate.">
          <RateBarChart data={data.churn_by_tenure} overallRate={data.churn_rate} layout="vertical" height={280} />
        </ChartCard>
        <ChartCard
          icon={CircleDollarSign}
          title="Monthly charges by churn status"
          description="How monthly charges are spread within each group."
        >
          <HistogramChart data={data.monthly_charges_histogram} height={220} />
          <div className="mt-4 grid grid-cols-2 gap-3 text-[13px]">
            {[...data.monthly_charges_summary]
              .sort((a, b) => Number(a.churn === "Yes") - Number(b.churn === "Yes"))
              .map((s) => (
                <div key={s.churn} className="rounded-lg bg-subtle px-3 py-2.5">
                  <p className="text-muted-foreground">{s.churn === "Yes" ? "Churned" : "Stayed"} · median</p>
                  <p className="mt-0.5 text-[15px] font-semibold tabular-nums">
                    {formatMoney(s.median)}{" "}
                    <span className="text-xs font-normal text-muted-foreground">
                      IQR {formatMoney(s.q1)}–{formatMoney(s.q3)}
                    </span>
                  </p>
                </div>
              ))}
          </div>
        </ChartCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <KeyObservations data={data} className="xl:col-span-2" />
        <DeployedModelCard metrics={metrics} />
      </div>

      <Card>
        <CardHeader className="flex-row items-start gap-3">
          <span className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", TONES.teal)}>
            <Database className="size-4" aria-hidden />
          </span>
          <div>
            <CardTitle>Dataset and data quality</CardTitle>
            <CardDescription>What the figures above are computed from, and the checks run when it is loaded.</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
          <dl className="grid content-start gap-x-6 gap-y-4 text-sm sm:grid-cols-2">
            {[
              ["Dataset", data.dataset_summary.name],
              ["Provider", data.dataset_summary.provider],
              ["Rows × columns", `${formatInt(Number(data.dataset_summary.rows))} × ${data.dataset_summary.columns}`],
              ["Model features", `${data.dataset_summary.model_features} (customerID excluded)`],
              ["Tenure range", `${data.dataset_summary.tenure_range_months} months`],
              ["Monthly charges range", String(data.dataset_summary.monthly_charges_range)],
            ].map(([k, v]) => (
              <div key={String(k)} className="min-w-0">
                <dt className="text-xs text-muted-foreground">{k}</dt>
                <dd className="mt-0.5 font-medium">{v}</dd>
              </div>
            ))}
          </dl>
          <div className="overflow-hidden rounded-lg border border-border">
            <Table aria-label="Data quality checks">
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Data quality check</TableHead>
                  <TableHead>Result</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.quality_checks.map((q) => (
                  <TableRow key={q.check}>
                    <TableCell className="text-muted-foreground">{q.check}</TableCell>
                    <TableCell className="whitespace-normal">{q.result}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </>
  );
}

interface Observation {
  icon: LucideIcon;
  tone: Tone;
  title: string;
  text: string;
}

/** Short findings derived from the API response; nothing here is typed in by hand. */
function KeyObservations({ data, className }: { data: Overview; className?: string }) {
  const contract = byRate(data.churn_by_contract);
  const tenure = byRate(data.churn_by_tenure);
  const median = (c: "Yes" | "No") => data.monthly_charges_summary.find((s) => s.churn === c)?.median;
  const churnedMedian = median("Yes");
  const stayedMedian = median("No");

  const items: Observation[] = [];
  if (contract.length > 1) {
    const hi = contract[0];
    const lo = contract[contract.length - 1];
    items.push({
      icon: FileSignature,
      tone: "blue",
      title: "Contract length",
      text: `${hi.group} customers churned at ${formatPct(hi.churn_rate)}, compared with ${formatPct(lo.churn_rate)} on ${lo.group.toLowerCase()} contracts.`,
    });
  }
  if (tenure.length > 1) {
    const hi = tenure[0];
    const lo = tenure[tenure.length - 1];
    items.push({
      icon: CalendarClock,
      tone: "teal",
      title: "Tenure",
      text: `Churn was highest at ${hi.group} months (${formatPct(hi.churn_rate)}) and lowest at ${lo.group} months (${formatPct(lo.churn_rate)}).`,
    });
  }
  if (churnedMedian !== undefined && stayedMedian !== undefined) {
    items.push({
      icon: CircleDollarSign,
      tone: "amber",
      title: "Monthly charges",
      text: `Customers who churned had a median monthly charge of ${formatMoney(churnedMedian)}, versus ${formatMoney(stayedMedian)} for those who stayed.`,
    });
  }
  items.push({
    icon: Percent,
    tone: "purple",
    title: "Class balance",
    text: `${formatPct(data.churn_rate)} of customers churned, so a model that always predicts "stays" would be ${formatPct(1 - data.churn_rate)} accurate while finding no churners.`,
  });

  return (
    <Card className={className}>
      <CardHeader className="flex-row items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", TONES.blue)}>
            <Sparkles className="size-4" aria-hidden />
          </span>
          <div>
            <CardTitle>Key observations</CardTitle>
            <CardDescription>Computed from the dataset. These are associations, not causes.</CardDescription>
          </div>
        </div>
        <Button asChild variant="ghost" size="sm" className="text-primary hover:text-primary-hover">
          <Link to="/insights">
            All insights <ArrowRight />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        <ul className="grid gap-3 sm:grid-cols-2">
          {items.map((o) => (
            <li key={o.title} className="flex gap-3 rounded-lg border border-[#eceff1] p-3.5">
              <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-lg", TONES[o.tone])}>
                <o.icon className="size-4" aria-hidden />
              </span>
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-foreground">{o.title}</p>
                <p className="mt-0.5 text-[13px] leading-5 text-[#3c4043]">{o.text}</p>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

function DeployedModelCard({
  metrics,
}: {
  metrics: { data: ModelMetrics | null; error: { message: string } | null; loading: boolean };
}) {
  const m = metrics.data;
  return (
    <Card className="flex flex-col">
      <CardHeader className="flex-row items-start gap-3">
        <span className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", TONES.green)}>
          <ShieldCheck className="size-4" aria-hidden />
        </span>
        <div>
          <CardTitle>Deployed model</CardTitle>
          <CardDescription>Scores on the held-out test set.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4 text-sm">
        {metrics.loading && !m && <p className="text-muted-foreground">Loading model results…</p>}
        {metrics.error && !m && <p className="text-muted-foreground">{metrics.error.message}</p>}
        {m && (
          <>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold">Calibrated {m.selected_model}</span>
              <Badge variant="success">Deployed</Badge>
            </div>
            <dl className="grid grid-cols-2 gap-3">
              {[
                ["ROC-AUC", m.deployed.test.metrics.roc_auc?.toFixed(3) ?? "Not available"],
                ["Recall", formatPct(m.deployed.test.metrics.recall)],
                ["Precision", formatPct(m.deployed.test.metrics.precision)],
                ["Threshold", m.deployed.decision_threshold.toFixed(2)],
              ].map(([k, v]) => (
                <div key={k} className="rounded-lg bg-subtle px-3 py-2.5">
                  <dt className="text-xs text-muted-foreground">{k}</dt>
                  <dd className="mt-0.5 text-lg font-semibold tabular-nums">{v}</dd>
                </div>
              ))}
            </dl>
            <p className="text-xs text-muted-foreground">
              {formatInt(m.methodology.n_test)} test customers · trained {formatDate(m.methodology.trained_at)}
            </p>
            <Button asChild variant="outline" className="mt-auto w-full">
              <Link to="/performance">
                View model performance <ArrowRight />
              </Link>
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
