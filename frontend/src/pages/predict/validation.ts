import type { CustomerFeatures, ModelSchema } from "@/types/api";

export interface FormValues {
  gender: string;
  SeniorCitizen: "0" | "1";
  Partner: string;
  Dependents: string;
  tenure: string;
  PhoneService: string;
  MultipleLines: string;
  InternetService: string;
  OnlineSecurity: string;
  OnlineBackup: string;
  DeviceProtection: string;
  TechSupport: string;
  StreamingTV: string;
  StreamingMovies: string;
  Contract: string;
  PaperlessBilling: string;
  PaymentMethod: string;
  MonthlyCharges: string;
  TotalCharges: string;
  autoTotal: boolean;
}

export const INTERNET_ADDONS = [
  "OnlineSecurity",
  "OnlineBackup",
  "DeviceProtection",
  "StreamingTV",
  "StreamingMovies",
] as const;

/** Neutral starting values for the form. They are illustrative, not a real customer. */
export const DEFAULT_VALUES: FormValues = {
  gender: "Female",
  SeniorCitizen: "0",
  Partner: "No",
  Dependents: "No",
  tenure: "12",
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "DSL",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: "65.00",
  TotalCharges: "",
  autoTotal: true,
};

export type FieldErrors = Partial<Record<keyof FormValues, string>>;

function num(v: string): number | null {
  if (v.trim() === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : NaN;
}

export function estimatedTotal(values: FormValues): number | null {
  const t = num(values.tenure);
  const m = num(values.MonthlyCharges);
  if (t === null || m === null || Number.isNaN(t) || Number.isNaN(m)) return null;
  return Math.round(t * m * 100) / 100;
}

/** Client-side validation mirroring the backend rules (the backend re-validates). */
export function validate(values: FormValues, schema: ModelSchema): { errors: FieldErrors; payload: CustomerFeatures | null } {
  const errors: FieldErrors = {};
  const spec = Object.fromEntries(schema.features.map((f) => [f.name, f]));

  for (const f of schema.features) {
    if (f.type !== "categorical") continue;
    const v = values[f.name as keyof FormValues];
    if (!f.allowed_values?.includes(v as string)) errors[f.name as keyof FormValues] = "Choose one of the listed options.";
  }

  const tenure = num(values.tenure);
  if (tenure === null) errors.tenure = "Enter the number of months.";
  else if (Number.isNaN(tenure) || !Number.isInteger(tenure)) errors.tenure = "Use a whole number of months.";
  else if (tenure < (spec.tenure.min ?? 0) || tenure > (spec.tenure.max ?? 1200))
    errors.tenure = `Must be between ${spec.tenure.min} and ${spec.tenure.max}.`;

  const monthly = num(values.MonthlyCharges);
  if (monthly === null) errors.MonthlyCharges = "Enter the monthly charge.";
  else if (Number.isNaN(monthly)) errors.MonthlyCharges = "Enter a number.";
  else if (monthly < (spec.MonthlyCharges.min ?? 0) || monthly > (spec.MonthlyCharges.max ?? 10000))
    errors.MonthlyCharges = `Must be between ${spec.MonthlyCharges.min} and ${spec.MonthlyCharges.max}.`;

  let total: number | null = values.autoTotal ? estimatedTotal(values) : num(values.TotalCharges);
  if (!values.autoTotal) {
    if (total === null && tenure !== 0) errors.TotalCharges = "Enter total charges (may be left blank only when tenure is 0).";
    else if (total !== null && Number.isNaN(total)) errors.TotalCharges = "Enter a number.";
    else if (total !== null && (total < 0 || total > (spec.TotalCharges.max ?? 1e6)))
      errors.TotalCharges = `Must be between 0 and ${spec.TotalCharges.max}.`;
  }
  if (total !== null && Number.isNaN(total)) total = null;

  if (Object.keys(errors).length > 0) return { errors, payload: null };

  return {
    errors,
    payload: {
      gender: values.gender,
      SeniorCitizen: values.SeniorCitizen === "1" ? 1 : 0,
      Partner: values.Partner,
      Dependents: values.Dependents,
      tenure: tenure as number,
      PhoneService: values.PhoneService,
      MultipleLines: values.MultipleLines,
      InternetService: values.InternetService,
      OnlineSecurity: values.OnlineSecurity,
      OnlineBackup: values.OnlineBackup,
      DeviceProtection: values.DeviceProtection,
      TechSupport: values.TechSupport,
      StreamingTV: values.StreamingTV,
      StreamingMovies: values.StreamingMovies,
      Contract: values.Contract,
      PaperlessBilling: values.PaperlessBilling,
      PaymentMethod: values.PaymentMethod,
      MonthlyCharges: monthly as number,
      TotalCharges: total,
    },
  };
}

/** Keep dependent service fields consistent with their parent service. */
export function applyDependencies(values: FormValues): FormValues {
  const next = { ...values };
  if (next.PhoneService === "No") next.MultipleLines = "No phone service";
  else if (next.MultipleLines === "No phone service") next.MultipleLines = "No";
  for (const k of [...INTERNET_ADDONS, "TechSupport"] as const) {
    if (next.InternetService === "No") next[k] = "No internet service";
    else if (next[k] === "No internet service") next[k] = "No";
  }
  return next;
}
