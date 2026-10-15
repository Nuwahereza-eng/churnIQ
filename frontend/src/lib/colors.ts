// Chart colours. Each entity keeps its colour everywhere. The categorical sets below
// pass the colour-vision-deficiency checks (adjacent and all-pairs) against white.
export const COLORS = {
  stayed: "#1a73e8",
  churned: "#d93025",
  grid: "#eceff1",
  axis: "#dadce0",
  axisText: "#5f6368",
  reference: "#80868b",
  ink: "#202124",
} as const;

export const MODEL_COLORS: Record<string, string> = {
  "Logistic Regression": "#1a73e8",
  "Decision Tree": "#e37400",
  "Random Forest": "#0f9d8a",
};

export const METRIC_COLORS = {
  precision: "#1a73e8",
  recall: "#e37400",
  f1: "#0f9d8a",
} as const;

// Sequential blue ramp for magnitude (confusion matrix cells), light to dark
export const SEQ_BLUE = ["#e8f0fe", "#d2e3fc", "#aecbfa", "#8ab4f8", "#669df6", "#4285f4", "#1a73e8", "#1967d2", "#185abc"];

export function seqBlue(fraction: number) {
  const i = Math.min(SEQ_BLUE.length - 1, Math.max(0, Math.round(fraction * (SEQ_BLUE.length - 1))));
  return SEQ_BLUE[i];
}
