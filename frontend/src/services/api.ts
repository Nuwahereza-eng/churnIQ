import type {
  ApiErrorBody,
  BatchPrediction,
  BatchValidation,
  CustomerFeatures,
  CustomerPage,
  CustomerQuery,
  Health,
  Insights,
  ModelMetrics,
  ModelSchema,
  Overview,
  PredictionResult,
} from "@/types/api";

// Same-origin by default (Vite proxies /api in development). Set VITE_API_BASE_URL
// when the API is hosted on a different origin.
const BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details: string[] = [],
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { ...init, headers: { Accept: "application/json", ...init?.headers } });
  } catch {
    throw new ApiError(0, "network_error", "Cannot reach the ChurnIQ API. Check that the backend is running.");
  }
  if (!res.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = (await res.json()) as ApiErrorBody;
    } catch {
      /* non-JSON error */
    }
    const err = body?.error;
    throw new ApiError(
      res.status,
      err?.code ?? "http_error",
      err?.message ?? `Request failed (HTTP ${res.status}).`,
      err?.details ?? [],
    );
  }
  return (await res.json()) as T;
}

function query(params: Record<string, unknown>): string {
  const sp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    if (Array.isArray(value)) value.forEach((v) => sp.append(key, String(v)));
    else sp.set(key, String(value));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

function upload<T>(path: string, file: File, params: Record<string, unknown> = {}): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  return request<T>(`${path}${query(params)}`, { method: "POST", body: form });
}

export const api = {
  health: () => request<Health>("/api/health"),
  schema: () => request<ModelSchema>("/api/schema"),
  templateUrl: () => `${BASE}/api/schema/template.csv`,
  overview: () => request<Overview>("/api/overview"),
  customers: (q: CustomerQuery) => request<CustomerPage>(`/api/customers${query({ ...q })}`),
  insights: () => request<Insights>("/api/insights"),
  modelMetrics: () => request<ModelMetrics>("/api/model/metrics"),
  predict: (customer: CustomerFeatures, threshold?: number) =>
    request<PredictionResult>("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer, threshold }),
    }),
  validateBatch: (file: File) => upload<BatchValidation>("/api/predict/batch/validate", file),
  predictBatch: (file: File, threshold?: number) =>
    upload<BatchPrediction>("/api/predict/batch", file, { threshold }),
};
