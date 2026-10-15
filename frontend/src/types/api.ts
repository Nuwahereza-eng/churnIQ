// TypeScript mirrors of the FastAPI/Pydantic schemas (backend/app/schemas).

export interface ApiErrorBody {
  error: { code: string; message: string; details: string[] };
}

export interface Health {
  status: "ok" | "degraded";
  dataset_available: boolean;
  model_available: boolean;
  results_available: boolean;
  model_name: string | null;
}

export interface GroupRate {
  group: string;
  customers: number;
  churned: number;
  churn_rate: number;
}

export interface HistogramBin {
  start: number;
  end: number;
  stayed: number;
  churned: number;
  stayed_share: number;
  churned_share: number;
}

export interface NumericSummary {
  churn: "Yes" | "No";
  count: number;
  mean: number;
  median: number;
  q1: number;
  q3: number;
  min: number;
  max: number;
}

export interface QualityCheck {
  check: string;
  result: string;
}

export interface Overview {
  total_customers: number;
  churned: number;
  stayed: number;
  churn_rate: number;
  churn_by_contract: GroupRate[];
  churn_by_tenure: GroupRate[];
  monthly_charges_summary: NumericSummary[];
  monthly_charges_histogram: HistogramBin[];
  dataset_summary: Record<string, string | number>;
  quality_checks: QualityCheck[];
}

export interface CustomerRow {
  customerID: string;
  tenure: number;
  Contract: string;
  InternetService: string;
  PaymentMethod: string;
  TechSupport: string;
  MonthlyCharges: number;
  TotalCharges: number;
  Churn: "Yes" | "No";
}

export type SortableColumn = keyof CustomerRow;

export interface CustomerPage {
  items: CustomerRow[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CustomerQuery {
  page: number;
  page_size: number;
  search?: string;
  contract?: string[];
  internet_service?: string[];
  churn?: "Yes" | "No" | "";
  tenure_min?: number | null;
  tenure_max?: number | null;
  sort_by: SortableColumn;
  sort_dir: "asc" | "desc";
}

export interface Association {
  feature: string;
  measure: string;
  strength: number;
  p_value: number;
}

export interface Importance {
  feature: string;
  mean: number;
  std: number;
}

export interface Coefficient {
  feature: string;
  value: number;
  kind: string;
}

export interface Insights {
  overall_churn_rate: number;
  churn_by_contract: GroupRate[];
  churn_by_tenure: GroupRate[];
  churn_by_internet_service: GroupRate[];
  churn_by_payment_method: GroupRate[];
  churn_by_monthly_charge_band: GroupRate[];
  monthly_charges_summary: NumericSummary[];
  associations: Association[];
  permutation_importance: Importance[] | null;
  importance_model: string | null;
  logistic_coefficients: Coefficient[] | null;
}

export interface Metrics {
  threshold: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc?: number | null;
  average_precision?: number | null;
  brier_score?: number | null;
  tp: number;
  fp: number;
  fn: number;
  tn: number;
  predicted_positive_rate: number;
}

export interface CurvePoint {
  x: number;
  y: number;
  threshold: number | null;
}

export interface CalibrationPoint {
  mean_predicted: number;
  fraction_positive: number;
}

export interface ClassReportRow {
  label: string;
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

export interface Evaluation {
  metrics: Metrics;
  confusion_matrix: number[][];
  classification_report: ClassReportRow[];
  roc_curve: CurvePoint[];
  pr_curve: CurvePoint[];
  calibration_curve: CalibrationPoint[];
  threshold_table: Metrics[];
}

export interface ModelResult {
  name: string;
  description: string;
  best_params: Record<string, string | number | null>;
  n_candidates: number;
  cv: Record<string, { mean: number; std: number }>;
  test: Evaluation;
}

export interface DeployedModel {
  base_model: string;
  calibration: string;
  decision_threshold: number;
  threshold_rule: string;
  brier_uncalibrated: number;
  brier_calibrated: number;
  mean_predicted_uncalibrated: number;
  mean_predicted_calibrated: number;
  observed_churn_rate_test: number;
  test: Evaluation;
}

export interface Methodology {
  n_train: number;
  n_test: number;
  test_size: number;
  cv_folds: number;
  random_state: number;
  train_churn_rate: number;
  test_churn_rate: number;
  selection_metric: string;
  trained_at: string;
  sklearn_version: string;
}

export interface ModelMetrics {
  selected_model: string;
  methodology: Methodology;
  models: ModelResult[];
  baseline: Metrics;
  deployed: DeployedModel;
}

export interface FeatureSpec {
  name: string;
  type: "categorical" | "binary" | "numeric";
  description: string;
  allowed_values?: (string | number)[] | null;
  min?: number | null;
  max?: number | null;
  training_min?: number | null;
  training_max?: number | null;
}

export interface ModelSchema {
  model_name: string;
  decision_threshold: number;
  features: FeatureSpec[];
  max_upload_bytes: number;
  max_batch_rows: number;
}

export interface CustomerFeatures {
  gender: string;
  SeniorCitizen: 0 | 1;
  Partner: string;
  Dependents: string;
  tenure: number;
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
  MonthlyCharges: number;
  TotalCharges: number | null;
}

export interface PredictionResult {
  churn_probability: number;
  predicted_churn: boolean;
  predicted_label: "Yes" | "No";
  risk_band: "Low" | "Medium" | "High";
  threshold: number;
  warnings: string[];
  model_name: string;
}

export interface BatchValidation {
  filename: string;
  n_rows: number;
  columns: string[];
  preview: Record<string, string>[];
  valid: boolean;
  errors: string[];
  warnings: string[];
  extra_columns: string[];
}

export interface BatchPrediction {
  filename: string;
  n_records: number;
  n_predicted_churn: number;
  mean_probability: number;
  threshold: number;
  columns: string[];
  rows: Record<string, string | number>[];
  warnings: string[];
  model_name: string;
}
