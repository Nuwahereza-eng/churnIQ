import { CircleCheck, CircleX, Download, FileSpreadsheet, FileUp, Gauge, Percent, Play, RotateCcw, Upload, UserMinus } from "lucide-react";
import { useRef, useState, type DragEvent } from "react";

import { MetricCard } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { useToast } from "@/components/Toaster";
import { ErrorState, InlineLoading } from "@/components/States";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useApi } from "@/hooks/useApi";
import { downloadText, toCsv } from "@/lib/csv";
import { formatInt, formatPct } from "@/lib/format";
import { cn } from "@/lib/utils";
import { ApiError, api } from "@/services/api";
import type { BatchPrediction, BatchValidation } from "@/types/api";

const RESULT_PAGE = 25;

function StepTitle({ n, title, done }: { n: number; title: string; done?: boolean }) {
  return (
    <CardTitle className="flex items-center gap-2.5">
      <span
        aria-hidden
        className={cn(
          "flex size-7 items-center justify-center rounded-full text-[13px] font-semibold",
          done ? "bg-success-soft text-success" : "bg-accent text-primary",
        )}
      >
        {done ? <CircleCheck className="size-4" /> : n}
      </span>
      <span>
        <span className="sr-only">Step {n}: </span>
        {title}
      </span>
    </CardTitle>
  );
}

function asApiError(e: unknown) {
  return e instanceof ApiError ? e : new ApiError(0, "unknown", "The request failed.");
}

export function BatchPage() {
  const schema = useApi(api.schema);
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);
  const [validation, setValidation] = useState<BatchValidation | null>(null);
  const [result, setResult] = useState<BatchPrediction | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState<"validating" | "predicting" | null>(null);
  const [dragging, setDragging] = useState(false);
  const [shown, setShown] = useState(RESULT_PAGE);
  const notify = useToast();

  const maxBytes = schema.data?.max_upload_bytes ?? 5 * 1024 * 1024;

  function reset() {
    setFile(null);
    setValidation(null);
    setResult(null);
    setError(null);
    setClientError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  async function handleFile(f: File | undefined) {
    reset();
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".csv")) return setClientError("Please choose a .csv file.");
    if (f.size === 0) return setClientError("The selected file is empty.");
    if (f.size > maxBytes) return setClientError(`The file is larger than ${(maxBytes / 1024 / 1024).toFixed(0)} MB.`);
    setFile(f);
    setBusy("validating");
    try {
      setValidation(await api.validateBatch(f));
    } catch (e) {
      setError(asApiError(e));
    } finally {
      setBusy(null);
    }
  }

  async function runPredictions() {
    if (!file) return;
    setBusy("predicting");
    setError(null);
    try {
      const r = await api.predictBatch(file);
      setResult(r);
      setShown(RESULT_PAGE);
      notify({
        variant: "success",
        title: `Scored ${formatInt(r.n_records)} records`,
        description: `${formatInt(r.n_predicted_churn)} predicted to churn. Results are ready to download.`,
      });
    } catch (e) {
      const err = asApiError(e);
      setError(err);
      notify({ variant: "error", title: "Batch prediction failed", description: err.message });
    } finally {
      setBusy(null);
    }
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    void handleFile(e.dataTransfer.files?.[0]);
  }

  function downloadResults() {
    if (!result) return;
    const base = result.filename.replace(/\.csv$/i, "");
    const name = `${base}_churn_predictions.csv`;
    downloadText(name, toCsv(result.columns, result.rows));
    notify({ variant: "success", title: "Download started", description: name });
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Batch Predictions"
        description="Upload a CSV of customers to score them all at once. Original columns are preserved and prediction columns are appended."
        actions={
          <Button asChild variant="outline">
            <a href={api.templateUrl()} download="churniq_template.csv">
              <Download /> CSV template
            </a>
          </Button>
        }
      />

      {schema.error && !schema.data && <ErrorState error={schema.error} onRetry={schema.reload} title="The model is not available" />}

      {!schema.error && (
        <Card>
          <CardHeader>
            <StepTitle n={1} title="Upload a file" done={Boolean(validation?.valid)} />
            <CardDescription>
              The CSV must contain the {schema.data?.features.length ?? 19} model columns named exactly as in the template
              (extra columns such as customerID are kept but ignored by the model). Maximum{" "}
              {(maxBytes / 1024 / 1024).toFixed(0)} MB and {formatInt(schema.data?.max_batch_rows ?? 10000)} rows.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className={cn(
                "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors duration-150",
                dragging ? "border-primary bg-accent" : "border-border-strong bg-subtle hover:border-[#8ab4f8]",
              )}
            >
              <span className="flex size-12 items-center justify-center rounded-full bg-accent text-primary">
                <FileUp className="size-6" aria-hidden />
              </span>
              <div>
                <p className="text-sm font-medium">{file ? file.name : "Drag a CSV file here"}</p>
                <p className="text-xs text-muted-foreground">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : "or choose one from your computer"}
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => inputRef.current?.click()}>
                  <Upload /> Choose file
                </Button>
                {file && (
                  <Button variant="ghost" size="sm" onClick={reset}>
                    <RotateCcw /> Clear
                  </Button>
                )}
              </div>
              <input
                ref={inputRef}
                type="file"
                accept=".csv,text/csv"
                className="sr-only"
                aria-label="Customer CSV file"
                onChange={(e) => void handleFile(e.target.files?.[0])}
              />
            </div>
            {clientError && <Alert variant="danger" title="File not accepted">{clientError}</Alert>}
            {busy === "validating" && <InlineLoading label="Checking file…" />}
          </CardContent>
        </Card>
      )}

      {error && (
        <Alert variant="danger" title={error.message}>
          {error.details.length > 0 && (
            <ul className="mt-1 max-h-60 list-disc overflow-y-auto pl-4">
              {error.details.map((d) => (
                <li key={d}>{d}</li>
              ))}
            </ul>
          )}
        </Alert>
      )}

      {validation && !result && (
        <Card>
          <CardHeader className="flex-row items-start justify-between gap-3">
            <div>
              <StepTitle n={2} title="Review and validate" done={Boolean(result)} />
              <CardDescription>
                {formatInt(validation.n_rows)} record{validation.n_rows === 1 ? "" : "s"} · {validation.columns.length} columns
                {validation.extra_columns.length > 0 && ` · kept but not used: ${validation.extra_columns.join(", ")}`}
              </CardDescription>
            </div>
            <Badge variant={validation.valid ? "success" : "danger"}>{validation.valid ? "Valid" : "Invalid"}</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            {!validation.valid && (
              <Alert variant="danger" title="The file cannot be scored. Fix these problems and upload it again.">
                <ul className="mt-1 max-h-60 list-disc overflow-y-auto pl-4">
                  {validation.errors.map((e) => (
                    <li key={e}>{e}</li>
                  ))}
                </ul>
              </Alert>
            )}
            {validation.valid && validation.warnings.length > 0 && (
              <Alert variant="warning" title={`${validation.warnings.length} warning(s): predictions can still be made`}>
                <ul className="mt-1 max-h-40 list-disc overflow-y-auto pl-4">
                  {validation.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              </Alert>
            )}
            <div>
              <p className="mb-2 text-[13px] font-medium">Preview (first {validation.preview.length} rows)</p>
              <div className="max-h-80 overflow-auto rounded-lg border border-border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      {validation.columns.map((c) => (
                        <TableHead key={c}>{c}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {validation.preview.map((row, i) => (
                      <TableRow key={i}>
                        {validation.columns.map((c) => (
                          <TableCell key={c} className="text-[13px]">
                            {row[c]}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
            <Button onClick={runPredictions} disabled={!validation.valid || busy !== null}>
              <Play /> {busy === "predicting" ? "Scoring…" : `Run predictions for ${formatInt(validation.n_rows)} records`}
            </Button>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card>
          <CardHeader className="flex-row flex-wrap items-start justify-between gap-3">
            <div>
              <StepTitle n={3} title="Results" />
              <CardDescription>
                {result.filename} · {result.model_name} · threshold {result.threshold.toFixed(2)}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={reset}>
                <RotateCcw /> New file
              </Button>
              <Button onClick={downloadResults}>
                <Download /> Download CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <MetricCard size="compact" icon={FileSpreadsheet} tone="blue" label="Records processed" value={formatInt(result.n_records)} />
              <MetricCard size="compact" icon={UserMinus} tone="red" label="Predicted to churn" value={formatInt(result.n_predicted_churn)} />
              <MetricCard size="compact" icon={Percent} tone="purple" label="Share flagged" value={formatPct(result.n_predicted_churn / result.n_records)} />
              <MetricCard size="compact" icon={Gauge} tone="teal" label="Mean churn probability" value={formatPct(result.mean_probability)} />
            </div>
            {result.warnings.length > 0 && (
              <Alert variant="warning" title={`${result.warnings.length} warning(s)`}>
                <ul className="mt-1 max-h-40 list-disc overflow-y-auto pl-4">
                  {result.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              </Alert>
            )}
            <div className="max-h-[480px] overflow-auto rounded-lg border border-border">
              <Table aria-label="Prediction results">
                <TableHeader>
                  <TableRow>
                    {result.columns.includes("customerID") && <TableHead>customerID</TableHead>}
                    <TableHead className="text-right">Churn probability</TableHead>
                    <TableHead>Prediction</TableHead>
                    <TableHead>Risk band</TableHead>
                    <TableHead>Contract</TableHead>
                    <TableHead className="text-right">Tenure</TableHead>
                    <TableHead className="text-right">Monthly</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {result.rows.slice(0, shown).map((r, i) => (
                    <TableRow key={i}>
                      {result.columns.includes("customerID") && <TableCell className="font-mono text-[13px]">{r.customerID}</TableCell>}
                      <TableCell className="text-right tabular-nums">{formatPct(Number(r.churn_probability))}</TableCell>
                      <TableCell>
                        {r.predicted_churn === "Yes" ? (
                          <Badge variant="danger">
                            <CircleX aria-hidden /> Likely to churn
                          </Badge>
                        ) : (
                          <Badge variant="success">
                            <CircleCheck aria-hidden /> Likely to stay
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant={r.risk_band === "High" ? "danger" : r.risk_band === "Medium" ? "warning" : "neutral"}>{String(r.risk_band)}</Badge>
                      </TableCell>
                      <TableCell>{r.Contract}</TableCell>
                      <TableCell className="text-right tabular-nums">{r.tenure}</TableCell>
                      <TableCell className="text-right tabular-nums">{r.MonthlyCharges}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 text-[13px] text-muted-foreground">
              <span>
                Showing {formatInt(Math.min(shown, result.rows.length))} of {formatInt(result.rows.length)} rows in the
                original order. The download contains every original column plus churn_probability, predicted_churn and
                risk_band.
              </span>
              {shown < result.rows.length && (
                <Button variant="outline" size="sm" onClick={() => setShown((s) => s + RESULT_PAGE * 4)}>
                  Show more
                </Button>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Probabilities are model estimates, not certainties. Use them to prioritise outreach, never to penalise customers.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
