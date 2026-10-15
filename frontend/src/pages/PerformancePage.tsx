import { Activity, BookOpenCheck, CheckCheck, Crosshair, FlaskConical, Grid2x2, Scale, Search } from "lucide-react";
import { useState } from "react";

import { ChartCard } from "@/components/ChartCard";
import { ConfusionMatrix } from "@/components/charts/ConfusionMatrix";
import { CurveChart } from "@/components/charts/CurveChart";
import { MetricComparisonChart } from "@/components/charts/MetricComparisonChart";
import { MetricCard, TONES } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/States";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Segmented } from "@/components/ui/segmented";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useApi } from "@/hooks/useApi";
import { COLORS, METRIC_COLORS, MODEL_COLORS } from "@/lib/colors";
import { formatDate, formatInt, formatNum, formatPct } from "@/lib/format";
import { cn } from "@/lib/utils";
import { api } from "@/services/api";
import type { Evaluation, Metrics, ModelMetrics } from "@/types/api";

const NOTES: Record<string, { strengths: string; limitations: string }> = {
  "Logistic Regression": {
    strengths: "Transparent coefficients, fast and stable; probabilities are reasonably well ranked.",
    limitations: "Assumes additive, linear effects on the log-odds; interactions must be added by hand.",
  },
  "Decision Tree": {
    strengths: "Readable if/then rules that capture interactions automatically.",
    limitations: "High variance (small data changes can change the tree) and coarse probabilities.",
  },
  "Random Forest": {
    strengths: "Averages many trees, reducing variance and capturing non-linear effects.",
    limitations: "Less interpretable, larger and slower to train; gains over Logistic Regression are small here.",
  },
};

const DASH = "–";

// Plain-language definitions of the evaluation criteria (general definitions, not results).
const CRITERIA = [
  ["ROC-AUC", "How well the model ranks churners above non-churners across every threshold. 0.5 is random; 1.0 is perfect. Used to select the model."],
  ["Recall", "Of the customers who actually churned, the share the model flagged. Missed churners are lost retention opportunities."],
  ["Precision", "Of the customers the model flagged, the share who actually churned. Low precision means effort spent on customers who would stay."],
  ["F1-score", "The harmonic mean of precision and recall; it balances the two and was used to choose the decision threshold."],
  ["Brier score", "Mean squared error of the predicted probabilities (lower is better); it measures whether probabilities can be taken at face value."],
] as const;

function CardIcon({ icon: Icon, tone }: { icon: typeof Activity; tone: keyof typeof TONES }) {
  return (
    <span className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", TONES[tone])}>
      <Icon className="size-4" aria-hidden />
    </span>
  );
}
const fmt = (v: number | null | undefined, d = 3) => (v === null || v === undefined ? DASH : formatNum(v, d));

export function PerformancePage() {
  const metrics = useApi(api.modelMetrics);
  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Performance"
        description="Results of the experiments comparing Logistic Regression, Decision Tree and Random Forest on a held-out test set."
      />
      {metrics.loading && !metrics.data && <LoadingState label="Loading evaluation results" />}
      {metrics.error && !metrics.data && <ErrorState error={metrics.error} onRetry={metrics.reload} />}
      {metrics.data && <PerformanceContent data={metrics.data} />}
    </div>
  );
}

function PerformanceContent({ data }: { data: ModelMetrics }) {
  const { methodology: m, deployed } = data;
  const deployedKey = `Deployed (calibrated ${data.selected_model})`;
  const [cmChoice, setCmChoice] = useState<string>(deployedKey);
  const cmEval: Evaluation =
    cmChoice === deployedKey ? deployed.test : (data.models.find((x) => x.name === cmChoice)?.test ?? deployed.test);
  const cmThreshold = cmChoice === deployedKey ? deployed.decision_threshold : 0.5;

  const ranked = [...data.models].sort((a, b) => b.cv.roc_auc.mean - a.cv.roc_auc.mean);
  const gap = ranked.length > 1 ? ranked[0].cv.roc_auc.mean - ranked[1].cv.roc_auc.mean : null;
  const thresholdRows = deployed.test.threshold_table.filter((r) => r.tp + r.fp > 0);

  return (
    <>
      <section aria-label="Deployed model" className="space-y-3">
        <p className="text-[13px] text-muted-foreground">
          <span className="font-medium text-foreground">Calibrated {data.selected_model}</span> · held-out test set of{" "}
          {formatInt(m.n_test)} customers · decision threshold {deployed.decision_threshold.toFixed(2)}
        </p>
        <div className="grid grid-cols-1 gap-4 min-[420px]:grid-cols-2 lg:grid-cols-5">
          <MetricCard icon={Activity} tone="blue" label="ROC-AUC" value={fmt(deployed.test.metrics.roc_auc)} hint="Ranking quality (0.5 = random)" />
          <MetricCard icon={Search} tone="teal" label="Recall" value={formatPct(deployed.test.metrics.recall)} hint="Churners identified" />
          <MetricCard icon={Crosshair} tone="purple" label="Precision" value={formatPct(deployed.test.metrics.precision)} hint="Flags that were correct" />
          <MetricCard icon={Scale} tone="amber" label="F1-score" value={fmt(deployed.test.metrics.f1)} hint="Balance of precision and recall" />
          <MetricCard icon={CheckCheck} tone="green" label="Accuracy" value={formatPct(deployed.test.metrics.accuracy)} hint="All predictions correct" />
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-5">
      <Card className="xl:col-span-3">
        <CardHeader className="flex-row items-start gap-3">
          <CardIcon icon={FlaskConical} tone="blue" />
          <div>
            <CardTitle>Dataset split and methodology</CardTitle>
            <CardDescription>How the models were trained, compared and deployed.</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-5 text-sm">
          <dl className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
            {[
              ["Training set", `${formatInt(m.n_train)} customers (${formatPct(m.train_churn_rate)} churn)`],
              ["Test set", `${formatInt(m.n_test)} customers (${formatPct(m.test_churn_rate)} churn)`],
              ["Split", `Stratified ${formatPct(1 - m.test_size, 0)} / ${formatPct(m.test_size, 0)}, seed ${m.random_state}`],
              ["Tuning", `Grid search, ${m.cv_folds}-fold stratified CV on training set`],
              ["Trained", formatDate(m.trained_at)],
              ["scikit-learn", m.sklearn_version],
            ].map(([k, v]) => (
              <div key={k} className="rounded-lg bg-subtle px-3 py-2.5">
                <dt className="text-xs text-muted-foreground">{k}</dt>
                <dd className="mt-0.5 font-medium">{v}</dd>
              </div>
            ))}
          </dl>
          <div className="space-y-3 leading-6 text-[#3c4043]">
            <p>
              <strong>Model selection.</strong> The final algorithm was chosen by {m.selection_metric}; the test set
              played no part in tuning, selection, calibration or threshold choice. <strong>{data.selected_model}</strong>{" "}
              was selected.
            </p>
            {gap !== null && gap < ranked[0].cv.roc_auc.std && (
              <p>
                Its cross-validated ROC-AUC exceeds {ranked[1].name} by only {formatNum(gap)}, less than one fold
                standard deviation ({formatNum(ranked[0].cv.roc_auc.std)}), so the two perform similarly.
              </p>
            )}
            <p>
              <strong>Deployment.</strong> {deployed.calibration}. Decision threshold {deployed.decision_threshold.toFixed(2)}:{" "}
              {deployed.threshold_rule}.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="xl:col-span-2">
        <CardHeader className="flex-row items-start gap-3">
          <CardIcon icon={BookOpenCheck} tone="teal" />
          <div>
            <CardTitle>How to read these metrics</CardTitle>
            <CardDescription>The evaluation criteria used on this page.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <dl className="divide-y divide-[#eceff1]">
            {CRITERIA.map(([term, def]) => (
              <div key={term} className="py-2.5 first:pt-0 last:pb-0">
                <dt className="text-[13px] font-semibold text-foreground">{term}</dt>
                <dd className="mt-0.5 text-[13px] leading-5 text-muted-foreground">{def}</dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>
      </div>

      <Card>
        <CardHeader className="flex-row items-start gap-3">
          <CardIcon icon={Scale} tone="purple" />
          <div>
            <CardTitle>Algorithm comparison</CardTitle>
            <CardDescription>Three algorithms and a majority-class baseline on the same held-out test set.</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="overflow-hidden rounded-lg border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Model</TableHead>
                  <TableHead className="text-right">CV ROC-AUC</TableHead>
                  <TableHead className="text-right">Accuracy</TableHead>
                  <TableHead className="text-right">Precision</TableHead>
                  <TableHead className="text-right">Recall</TableHead>
                  <TableHead className="text-right">F1</TableHead>
                  <TableHead className="text-right">ROC-AUC</TableHead>
                  <TableHead className="text-right">Avg. precision</TableHead>
                  <TableHead className="text-right">Brier</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.models.map((r) => (
                  <MetricsRow
                    key={r.name}
                    name={r.name}
                    color={MODEL_COLORS[r.name]}
                    cv={`${formatNum(r.cv.roc_auc.mean)} ± ${formatNum(r.cv.roc_auc.std)}`}
                    metrics={r.test.metrics}
                    selected={r.name === data.selected_model}
                  />
                ))}
                <MetricsRow name="Majority-class baseline" cv={DASH} metrics={data.baseline} muted />
              </TableBody>
            </Table>
          </div>
          <p className="text-xs text-muted-foreground">
            Test-set metrics at a 0.5 threshold for the uncalibrated, class-weighted models. The baseline always predicts
            "no churn": its accuracy shows why accuracy alone is misleading with imbalanced classes. Brier score: mean
            squared error of probabilities (lower is better).
          </p>
          <MetricComparisonChart models={data.models} />
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="ROC curves" description="True positive rate against false positive rate on the test set." footnote="Higher and further to the left is better.">
          <CurveChart
            series={data.models.map((r) => ({
              name: `${r.name} (AUC ${fmt(r.test.metrics.roc_auc)})`,
              color: MODEL_COLORS[r.name],
              points: r.test.roc_curve,
            }))}
            xLabel="False positive rate"
            yLabel="True positive rate"
            diagonal
          />
        </ChartCard>
        <ChartCard
          title="Precision–recall curves"
          description="More informative than ROC when the positive class is the minority."
          footnote="Dashed line: churn rate (precision of random guessing)."
        >
          <CurveChart
            series={data.models.map((r) => ({
              name: `${r.name} (AP ${fmt(r.test.metrics.average_precision)})`,
              color: MODEL_COLORS[r.name],
              points: r.test.pr_curve,
            }))}
            xLabel="Recall"
            yLabel="Precision"
            hLine={{ y: m.test_churn_rate, label: "No-skill baseline" }}
          />
        </ChartCard>
      </div>

      <Card>
        <CardHeader className="gap-3">
          <div className="flex items-start gap-3">
            <CardIcon icon={Grid2x2} tone="blue" />
            <div>
              <CardTitle>Confusion matrix</CardTitle>
              <CardDescription>Actual versus predicted classes on the test set.</CardDescription>
            </div>
          </div>
          <Segmented
            label="Model"
            value={cmChoice}
            onChange={setCmChoice}
            options={[...data.models.map((r) => ({ value: r.name, label: r.name })), { value: deployedKey, label: "Deployed (calibrated)" }]}
          />
        </CardHeader>
        <CardContent className="grid gap-6 lg:grid-cols-2 [&>*]:min-w-0">
          <div>
            <ConfusionMatrix matrix={cmEval.confusion_matrix} />
            <p className="mt-2 text-xs text-muted-foreground">Threshold {cmThreshold.toFixed(2)} · percentages are shares of all test customers.</p>
          </div>
          <div className="space-y-4">
            <div className="overflow-hidden rounded-lg border border-border">
              <Table aria-label="Classification report">
                <TableHeader>
                  <TableRow>
                    <TableHead>Class</TableHead>
                    <TableHead className="text-right">Precision</TableHead>
                    <TableHead className="text-right">Recall</TableHead>
                    <TableHead className="text-right">F1</TableHead>
                    <TableHead className="text-right">Support</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {cmEval.classification_report.map((r) => (
                    <TableRow key={r.label}>
                      <TableCell>{r.label}</TableCell>
                      <TableCell className="text-right tabular-nums">{fmt(r.precision)}</TableCell>
                      <TableCell className="text-right tabular-nums">{fmt(r.recall)}</TableCell>
                      <TableCell className="text-right tabular-nums">{fmt(r.f1)}</TableCell>
                      <TableCell className="text-right tabular-nums">{formatInt(r.support)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            <ul className="space-y-2 text-[13px] leading-5 text-[#3c4043]">
              <li>
                <strong>False positives ({formatInt(cmEval.metrics.fp)})</strong>: customers flagged as likely to churn
                who stayed. Cost: retention effort spent where it was not needed.
              </li>
              <li>
                <strong>False negatives ({formatInt(cmEval.metrics.fn)})</strong>: churners the model missed. Cost: lost
                customers who could have been approached.
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard
          title="Effect of the decision threshold"
          description="Deployed model on the test set."
          footnote="Lowering the threshold finds more churners (recall rises) but more flagged customers would have stayed (precision falls)."
        >
          <CurveChart
            series={(["precision", "recall", "f1"] as const).map((k) => ({
              name: k === "f1" ? "F1" : k[0].toUpperCase() + k.slice(1),
              color: METRIC_COLORS[k],
              points: thresholdRows.map((r) => ({ x: r.threshold, y: r[k], threshold: r.threshold })),
            }))}
            xLabel="Threshold"
            yLabel="Score"
            vLine={{ x: deployed.decision_threshold, label: `Deployed threshold (${deployed.decision_threshold.toFixed(2)})` }}
          />
        </ChartCard>
        <ChartCard
          title="Probability calibration"
          description={`Brier score ${formatNum(deployed.brier_uncalibrated)} → ${formatNum(deployed.brier_calibrated)} after calibration.`}
          footnote={`Points on the diagonal mean predicted probabilities match observed churn rates. Mean prediction: ${formatPct(deployed.mean_predicted_uncalibrated)} uncalibrated, ${formatPct(deployed.mean_predicted_calibrated)} calibrated, vs ${formatPct(deployed.observed_churn_rate_test)} observed.`}
        >
          <CurveChart
            series={[
              {
                name: `${data.selected_model} (uncalibrated)`,
                color: COLORS.churned,
                dots: true,
                points: (data.models.find((x) => x.name === data.selected_model)?.test.calibration_curve ?? []).map((p) => ({
                  x: p.mean_predicted,
                  y: p.fraction_positive,
                })),
              },
              {
                name: "Deployed (calibrated)",
                color: COLORS.stayed,
                dots: true,
                points: deployed.test.calibration_curve.map((p) => ({ x: p.mean_predicted, y: p.fraction_positive })),
              },
            ]}
            xLabel="Mean predicted probability"
            yLabel="Observed churn rate"
            diagonal
          />
        </ChartCard>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Strengths and limitations</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {data.models.map((r) => (
            <div key={r.name} className="rounded-xl border border-border bg-subtle/60 p-4 text-[13px]">
              <div className="flex items-center gap-2">
                <span aria-hidden className="size-2.5 rounded-full" style={{ backgroundColor: MODEL_COLORS[r.name] }} />
                <p className="font-semibold">{r.name}</p>
              </div>
              <p className="mt-2 leading-5 text-[#3c4043]">
                <strong>Strengths.</strong> {NOTES[r.name]?.strengths ?? r.description}
              </p>
              <p className="mt-1 leading-5 text-[#3c4043]">
                <strong>Limitations.</strong> {NOTES[r.name]?.limitations ?? DASH}
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                Best parameters:{" "}
                {Object.entries(r.best_params)
                  .map(([k, v]) => `${k}=${v ?? "None"}`)
                  .join(", ")}{" "}
                · {r.n_candidates} candidates
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Alert variant="info" title="Limitations of this evaluation">
        Results come from one stratified split of a fictional sample dataset; small differences between models are
        within sampling variability. There is no time dimension, so performance on future customers is untested, and the
        threshold was chosen by F1 rather than real retention costs.
      </Alert>
    </>
  );
}

function MetricsRow({
  name,
  cv,
  metrics,
  color,
  selected,
  muted,
}: {
  name: string;
  cv: string;
  metrics: Metrics;
  color?: string;
  selected?: boolean;
  muted?: boolean;
}) {
  return (
    <TableRow className={muted ? "text-muted-foreground" : undefined}>
      <TableCell>
        <span className="flex items-center gap-2 font-medium">
          {color && <span aria-hidden className="size-2.5 rounded-full" style={{ backgroundColor: color }} />}
          {name}
          {selected && <Badge variant="success">Selected</Badge>}
        </span>
      </TableCell>
      <TableCell className="text-right tabular-nums">{cv}</TableCell>
      {(["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision", "brier_score"] as const).map((k) => (
        <TableCell key={k} className="text-right tabular-nums">
          {fmt(metrics[k] as number | null | undefined)}
        </TableCell>
      ))}
    </TableRow>
  );
}
