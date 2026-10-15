import { AlertTriangle, CalendarClock, CircleDollarSign, CreditCard, FileSignature, ListChecks, Sigma, Sparkles, TrendingUp, Wifi } from "lucide-react";

import { ChartCard } from "@/components/ChartCard";
import { ImportanceChart } from "@/components/charts/ImportanceChart";
import { RateBarChart } from "@/components/charts/RateBarChart";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/States";
import { Alert } from "@/components/ui/alert";
import { TONES } from "@/components/MetricCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useApi } from "@/hooks/useApi";
import { formatMoney, formatNum, formatPct } from "@/lib/format";
import { api } from "@/services/api";
import type { GroupRate, Insights } from "@/types/api";

function top(rates: GroupRate[]) {
  return [...rates].sort((a, b) => b.churn_rate - a.churn_rate)[0];
}
function bottom(rates: GroupRate[]) {
  return [...rates].sort((a, b) => a.churn_rate - b.churn_rate)[0];
}

export function InsightsPage() {
  const insights = useApi(api.insights);
  return (
    <div className="space-y-6">
      <PageHeader
        title="Insights"
        description="Patterns in the data and what the model relies on. These are statistical associations, not causes."
      />
      <Alert variant="warning" title="Association is not causation">
        These results describe which customers churned in a historical, fictional dataset and which inputs the model uses.
        They do not show that changing a characteristic (for example moving a customer to a longer contract) would cause
        them to stay. That would require controlled experiments.
      </Alert>
      {insights.loading && !insights.data && <LoadingState label="Loading insights" />}
      {insights.error && !insights.data && <ErrorState error={insights.error} onRetry={insights.reload} />}
      {insights.data && <InsightsContent data={insights.data} />}
    </div>
  );
}

function InsightsContent({ data }: { data: Insights }) {
  const overall = data.overall_churn_rate;
  const findings = [
    { label: "Contract", hi: top(data.churn_by_contract), lo: bottom(data.churn_by_contract) },
    { label: "Tenure (months)", hi: top(data.churn_by_tenure), lo: bottom(data.churn_by_tenure) },
    { label: "Internet service", hi: top(data.churn_by_internet_service), lo: bottom(data.churn_by_internet_service) },
    { label: "Payment method", hi: top(data.churn_by_payment_method), lo: bottom(data.churn_by_payment_method) },
  ];
  const [stayed, churned] = ["No", "Yes"].map((c) => data.monthly_charges_summary.find((s) => s.churn === c)!);

  return (
    <>
      <Card>
        <CardHeader className="flex-row items-start gap-3">
          <span className={`mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg ${TONES.blue}`}>
            <ListChecks className="size-4" aria-hidden />
          </span>
          <div>
            <CardTitle>Key findings</CardTitle>
            <CardDescription>Highest and lowest churn group for each characteristic, computed from the dataset.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-hidden rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Characteristic</TableHead>
                  <TableHead>Highest churn group</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                  <TableHead>Lowest churn group</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {findings.map((f) => (
                  <TableRow key={f.label}>
                    <TableCell className="font-medium">{f.label}</TableCell>
                    <TableCell>{f.hi.group}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatPct(f.hi.churn_rate)}</TableCell>
                    <TableCell>{f.lo.group}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatPct(f.lo.churn_rate)}</TableCell>
                  </TableRow>
                ))}
                <TableRow>
                  <TableCell className="font-medium">Monthly charges (median)</TableCell>
                  <TableCell>Churned</TableCell>
                  <TableCell className="text-right tabular-nums">{formatMoney(churned.median)}</TableCell>
                  <TableCell>Stayed</TableCell>
                  <TableCell className="text-right tabular-nums">{formatMoney(stayed.median)}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Overall churn rate {formatPct(overall)}. Many of these groups overlap: for example, new customers are mostly
            on month-to-month contracts, and fibre-optic customers pay higher monthly charges.
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard icon={FileSignature} title="Churn by contract type" description="Dashed line: overall churn rate.">
          <RateBarChart data={data.churn_by_contract} overallRate={overall} labelWidth={120} />
        </ChartCard>
        <ChartCard icon={CalendarClock} tone="teal" title="Churn by tenure group" description="Months with the provider. Dashed line: overall churn rate.">
          <RateBarChart data={data.churn_by_tenure} overallRate={overall} layout="vertical" height={230} />
        </ChartCard>
        <ChartCard icon={Wifi} tone="purple" title="Churn by service type" description="Internet service subscribed. Dashed line: overall churn rate.">
          <RateBarChart
            data={data.churn_by_internet_service.map((g) => ({ ...g, group: g.group === "No" ? "No internet" : g.group }))}
            overallRate={overall}
            labelWidth={100}
          />
        </ChartCard>
        <ChartCard icon={CreditCard} tone="amber" title="Churn by payment method" description="Dashed line: overall churn rate.">
          <RateBarChart data={data.churn_by_payment_method} overallRate={overall} labelWidth={170} />
        </ChartCard>
        <ChartCard
          icon={CircleDollarSign}
          tone="green"
          title="Churn by monthly charge band"
          description="Customers grouped by monthly charge."
          footnote="Very low charges are mostly phone-only customers without internet service."
          className="xl:col-span-2"
        >
          <RateBarChart data={data.churn_by_monthly_charge_band} overallRate={overall} layout="vertical" height={230} />
        </ChartCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard
          icon={Sparkles}
          title="What the model relies on"
          description={`Permutation importance: drop in ROC-AUC when one column is shuffled (${data.importance_model ?? "deployed model"}, test set).`}
          footnote="Correlated columns (tenure, TotalCharges, Contract) share information, so each one's importance can be understated. A near-zero value means the model can do as well without that column, not that it is unrelated to churn."
        >
          {data.permutation_importance ? (
            <ImportanceChart
              data={data.permutation_importance.map((p) => ({ feature: p.feature, value: p.mean, error: p.std }))}
              valueLabel="Mean drop in ROC-AUC"
              labelWidth={130}
            />
          ) : (
            <p className="text-sm text-muted-foreground">Importance results are not available. Train the model to compute them.</p>
          )}
        </ChartCard>
        <ChartCard
          icon={TrendingUp}
          tone="purple"
          title="Logistic Regression coefficients"
          description="Largest standardised coefficients (change in log-odds of churn)."
          footnote="Category coefficients are relative to the other categories of the same feature. Correlated features (charges, tenure, internet type) can take offsetting signs, so read them together."
        >
          {data.logistic_coefficients ? (
            <ImportanceChart
              data={data.logistic_coefficients.slice(0, 12).map((c) => ({ feature: c.feature, value: c.value }))}
              valueLabel="Coefficient"
              signed
              labelWidth={190}
            />
          ) : (
            <p className="text-sm text-muted-foreground">Coefficients are not available.</p>
          )}
        </ChartCard>
      </div>

      <Card>
        <CardHeader className="flex-row items-start gap-3">
          <span className={`mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg ${TONES.teal}`}>
            <Sigma className="size-4" aria-hidden />
          </span>
          <div>
            <CardTitle>Strength of association with churn</CardTitle>
            <CardDescription>One variable at a time, strongest first.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <div className="max-h-96 overflow-auto rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Feature</TableHead>
                  <TableHead>Measure</TableHead>
                  <TableHead className="text-right">Strength</TableHead>
                  <TableHead className="text-right">p-value</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.associations.map((a) => (
                  <TableRow key={a.feature}>
                    <TableCell className="font-medium">{a.feature}</TableCell>
                    <TableCell className="text-muted-foreground">{a.measure}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatNum(a.strength)}</TableCell>
                    <TableCell className="text-right tabular-nums">{a.p_value < 1e-4 ? "< 0.0001" : formatNum(a.p_value, 4)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <p className="mt-3 flex gap-2 text-xs text-muted-foreground">
            <AlertTriangle className="size-3.5 shrink-0" aria-hidden />
            One-variable-at-a-time measures (Cramér's V for categorical features, point-biserial correlation for numeric
            ones). They do not control for other variables. With about 7,000 customers even weak associations are
            statistically significant, so effect size matters more than the p-value.
          </p>
        </CardContent>
      </Card>
    </>
  );
}
