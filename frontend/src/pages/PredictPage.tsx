import { CreditCard, FileSignature, RotateCcw, Sparkles, User, Wifi, type LucideIcon } from "lucide-react";
import { useState, type FormEvent, type ReactNode } from "react";

import { FormField } from "@/components/FormField";
import { PageHeader } from "@/components/PageHeader";
import { EmptyState, ErrorState, InlineLoading, LoadingState } from "@/components/States";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, NativeSelect } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/useApi";
import { ApiError, api } from "@/services/api";
import type { FeatureSpec, ModelSchema, PredictionResult } from "@/types/api";

import { PredictionResultCard } from "./predict/PredictionResultCard";
import {
  applyDependencies,
  DEFAULT_VALUES,
  estimatedTotal,
  validate,
  type FieldErrors,
  type FormValues,
} from "./predict/validation";

const LABELS: Record<string, string> = {
  OnlineSecurity: "Online security",
  OnlineBackup: "Online backup",
  DeviceProtection: "Device protection",
  StreamingTV: "Streaming TV",
  StreamingMovies: "Streaming movies",
  TechSupport: "Technical support",
  PhoneService: "Phone service",
  MultipleLines: "Multiple lines",
  InternetService: "Internet service",
  PaperlessBilling: "Paperless billing",
  PaymentMethod: "Payment method",
  Contract: "Contract type",
  Partner: "Has a partner",
  Dependents: "Has dependents",
  gender: "Gender",
};

function Section({
  icon: Icon,
  step,
  title,
  description,
  children,
}: {
  icon: LucideIcon;
  step: number;
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <fieldset className="space-y-4 border-b border-[#eceff1] pb-7 last-of-type:border-0 last-of-type:pb-0">
      <div className="flex items-start gap-3">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-accent text-primary">
          <Icon className="size-4" aria-hidden />
        </span>
        <div>
          <legend className="text-base font-semibold text-foreground">
            <span className="sr-only">Step {step}: </span>
            {title}
          </legend>
          {description && <p className="mt-0.5 text-[13px] leading-5 text-muted-foreground">{description}</p>}
        </div>
      </div>
      <div className="grid gap-x-4 gap-y-5 sm:grid-cols-2 lg:grid-cols-3">{children}</div>
    </fieldset>
  );
}

export function PredictPage() {
  const schema = useApi(api.schema);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Predict Churn"
        description="Enter a customer's account and service details to estimate their probability of churning with the trained model."
      />
      {schema.loading && !schema.data && <LoadingState label="Loading model schema" rows={1} />}
      {schema.error && !schema.data && <ErrorState error={schema.error} onRetry={schema.reload} title="The model is not available" />}
      {schema.data && <PredictForm schema={schema.data} />}
    </div>
  );
}

function PredictForm({ schema }: { schema: ModelSchema }) {
  const [values, setValues] = useState<FormValues>(DEFAULT_VALUES);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [threshold, setThreshold] = useState(schema.decision_threshold);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [submitError, setSubmitError] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [stale, setStale] = useState(false);

  const spec = Object.fromEntries(schema.features.map((f) => [f.name, f])) as Record<string, FeatureSpec>;
  const options = (name: string) => (spec[name]?.allowed_values ?? []).map(String);

  const update = (patch: Partial<FormValues>) => {
    setValues((v) => applyDependencies({ ...v, ...patch }));
    setErrors((e) => {
      const next = { ...e };
      for (const k of Object.keys(patch)) delete next[k as keyof FormValues];
      return next;
    });
    if (result) setStale(true);
  };

  const select = (name: keyof FormValues, help?: string, disabled = false) => (
    <FormField label={LABELS[name] ?? name} help={help} error={errors[name]}>
      <NativeSelect value={String(values[name])} disabled={disabled} onChange={(e) => update({ [name]: e.target.value } as Partial<FormValues>)}>
        {options(name).map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </NativeSelect>
    </FormField>
  );

  const rangeHelp = (name: string, unit = "") => {
    const f = spec[name];
    return f?.training_min !== undefined && f?.training_min !== null
      ? `Training data range: ${f.training_min}–${f.training_max}${unit}. Values outside it are less reliable.`
      : undefined;
  };

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const { errors: errs, payload } = validate(values, schema);
    setErrors(errs);
    if (!payload) {
      setSubmitError(null);
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      setResult(await api.predict(payload, threshold));
      setStale(false);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err : new ApiError(0, "unknown", "The prediction request failed."));
    } finally {
      setSubmitting(false);
    }
  }

  const noInternet = values.InternetService === "No";
  const total = estimatedTotal(values);
  const errorCount = Object.keys(errors).length;

  return (
    <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
      <Card>
        <CardHeader>
          <CardTitle>Customer details</CardTitle>
          <CardDescription>
            The form starts with illustrative values that do not describe a real customer. All 19 fields used by the
            model are required.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} noValidate className="space-y-7" aria-label="Customer details">
            {errorCount > 0 && (
              <Alert variant="danger" title={`Please correct ${errorCount} field${errorCount === 1 ? "" : "s"}`}>
                The highlighted fields need attention before a prediction can be made.
              </Alert>
            )}

            <Section icon={User} step={1} title="Customer information" description="Tenure and the profile fields in the model's input schema. Demographic fields carry little weight in the deployed model.">
              <FormField label="Tenure (months)" help={rangeHelp("tenure", " months")} error={errors.tenure}>
                <Input type="number" inputMode="numeric" min={0} step={1} value={values.tenure} onChange={(e) => update({ tenure: e.target.value })} />
              </FormField>
              {select("gender")}
              <FormField label="Senior citizen (65+)" error={errors.SeniorCitizen}>
                <NativeSelect value={values.SeniorCitizen} onChange={(e) => update({ SeniorCitizen: e.target.value as "0" | "1" })}>
                  <option value="0">No</option>
                  <option value="1">Yes</option>
                </NativeSelect>
              </FormField>
              {select("Partner")}
              {select("Dependents")}
            </Section>

            <Section icon={FileSignature} step={2} title="Contract and billing" description="Contract term and what the customer is charged.">
              {select("Contract", "Longer contracts are associated with lower churn in the data.")}
              {select("PaperlessBilling")}
              <FormField label="Monthly charges" help={rangeHelp("MonthlyCharges")} error={errors.MonthlyCharges}>
                <Input type="number" inputMode="decimal" min={0} step="0.01" value={values.MonthlyCharges} onChange={(e) => update({ MonthlyCharges: e.target.value })} />
              </FormField>
              <FormField
                label="Total charges"
                help={values.autoTotal ? "Estimated as tenure × monthly charges." : "Total billed to date. May be blank only when tenure is 0."}
                error={errors.TotalCharges}
              >
                <Input
                  type="number"
                  inputMode="decimal"
                  min={0}
                  step="0.01"
                  disabled={values.autoTotal}
                  value={values.autoTotal ? (total ?? "").toString() : values.TotalCharges}
                  onChange={(e) => update({ TotalCharges: e.target.value })}
                />
              </FormField>
              <div className="flex items-center gap-2.5 sm:col-span-2 lg:col-span-1 lg:pt-6">
                <input
                  id="auto-total"
                  type="checkbox"
                  className="size-4 cursor-pointer accent-primary"
                  checked={values.autoTotal}
                  onChange={(e) => update({ autoTotal: e.target.checked, TotalCharges: e.target.checked ? "" : String(total ?? "") })}
                />
                <Label htmlFor="auto-total" className="cursor-pointer font-normal">
                  Estimate total from tenure
                </Label>
              </div>
            </Section>

            <Section icon={Wifi} step={3} title="Services and support" description="Add-ons are set automatically when the parent service is absent.">
              {select("PhoneService")}
              {select("MultipleLines", values.PhoneService === "No" ? "Not applicable without phone service." : undefined, values.PhoneService === "No")}
              {select("InternetService")}
              {select("OnlineSecurity", undefined, noInternet)}
              {select("OnlineBackup", undefined, noInternet)}
              {select("DeviceProtection", undefined, noInternet)}
              {select("StreamingTV", undefined, noInternet)}
              {select("StreamingMovies", undefined, noInternet)}
              {select("TechSupport", noInternet ? "Not applicable without internet service." : undefined, noInternet)}
            </Section>

            <Section icon={CreditCard} step={4} title="Payment details" description="How the customer pays their bill.">
              {select("PaymentMethod")}
            </Section>

            <details className="rounded-lg border border-border bg-subtle px-4 py-3">
              <summary className="cursor-pointer text-sm font-medium text-foreground marker:text-muted-foreground">Decision threshold (advanced)</summary>
              <div className="mt-3 space-y-2">
                <div className="flex items-center justify-between text-[13px]">
                  <Label htmlFor="threshold">Predict churn when probability ≥</Label>
                  <span className="font-semibold tabular-nums">{threshold.toFixed(2)}</span>
                </div>
                <input
                  id="threshold"
                  type="range"
                  min={0.05}
                  max={0.95}
                  step={0.01}
                  value={threshold}
                  onChange={(e) => {
                    setThreshold(Number(e.target.value));
                    if (result) setStale(true);
                  }}
                  className="w-full accent-primary"
                />
                <p className="text-xs text-muted-foreground">
                  Model default: {schema.decision_threshold.toFixed(2)} (chosen on training data to maximise F1). Lower
                  values flag more customers; higher values flag fewer.
                </p>
              </div>
            </details>

            <div className="flex flex-wrap items-center gap-3 border-t border-border pt-5">
              <Button type="submit" size="lg" disabled={submitting}>
                <Sparkles /> {submitting ? "Predicting…" : "Predict churn"}
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => {
                  setValues(DEFAULT_VALUES);
                  setErrors({});
                  setResult(null);
                  setSubmitError(null);
                  setThreshold(schema.decision_threshold);
                }}
              >
                <RotateCcw /> Reset
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4 xl:sticky xl:top-24">
        {submitting && (
          <Card className="space-y-4 p-6">
            <InlineLoading label="Scoring customer…" />
            <Skeleton className="h-24" />
            <Skeleton className="h-4 w-2/3" />
          </Card>
        )}
        {submitError && <ErrorState error={submitError} title="Prediction failed" />}
        {result && !submitting && (
          <>
            {stale && (
              <Alert variant="info">Inputs have changed since this prediction. Submit again to update it.</Alert>
            )}
            <PredictionResultCard result={result} />
          </>
        )}
        {!result && !submitting && !submitError && (
          <Card>
            <EmptyState title="No prediction yet" description="Complete the form and select Predict churn to estimate this customer’s churn probability." />
          </Card>
        )}
      </div>
    </div>
  );
}
