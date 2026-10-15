import { Info, ShieldAlert, ShieldCheck } from "lucide-react";

import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPct } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PredictionResult } from "@/types/api";

const OUTCOME = {
  churn: { label: "Likely to churn", icon: ShieldAlert, box: "bg-danger-soft", text: "text-[#b3261e]", arc: "#d93025" },
  stay: { label: "Likely to stay", icon: ShieldCheck, box: "bg-success-soft", text: "text-success", arc: "#188038" },
};

/** Half-circle gauge: probability as an arc, decision threshold as a tick. */
function ProbabilityGauge({ value, threshold, color }: { value: number; threshold: number; color: string }) {
  const r = 80;
  const cx = 100;
  const cy = 96;
  const point = (t: number, radius = r) => {
    const angle = Math.PI * (1 - t);
    return [cx + radius * Math.cos(angle), cy - radius * Math.sin(angle)];
  };
  const arc = (t: number) => {
    const [x, y] = point(Math.max(0.001, Math.min(0.999, t)));
    return `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${x.toFixed(2)} ${y.toFixed(2)}`;
  };
  const [tx1, ty1] = point(threshold, r - 16);
  const [tx2, ty2] = point(threshold, r + 14);
  return (
    <svg viewBox="0 0 200 122" className="mx-auto w-full max-w-[260px]" aria-hidden>
      <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke="#eceff1" strokeWidth="16" strokeLinecap="round" />
      <path d={arc(value)} fill="none" stroke={color} strokeWidth="16" strokeLinecap="round" />
      <line x1={tx1} y1={ty1} x2={tx2} y2={ty2} stroke="#202124" strokeWidth="2.5" strokeLinecap="round" />
      <text x={cx - r} y={cy + 24} textAnchor="middle" fontSize="10" fill="#5f6368">
        0%
      </text>
      <text x={cx + r} y={cy + 24} textAnchor="middle" fontSize="10" fill="#5f6368">
        100%
      </text>
    </svg>
  );
}

export function PredictionResultCard({ result }: { result: PredictionResult }) {
  const o = result.predicted_churn ? OUTCOME.churn : OUTCOME.stay;
  const p = result.churn_probability;
  return (
    <Card aria-live="polite" data-testid="prediction-result" className="overflow-hidden">
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle>Prediction result</CardTitle>
        <Badge variant={result.risk_band === "High" ? "danger" : result.risk_band === "Medium" ? "warning" : "success"}>
          {result.risk_band} risk
        </Badge>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className={cn("flex items-center gap-3 rounded-xl p-4", o.box)}>
          <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-card">
            <o.icon className={cn("size-5", o.text)} aria-hidden />
          </span>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Predicted outcome</p>
            <p className={cn("text-lg font-semibold leading-tight", o.text)}>{o.label}</p>
          </div>
        </div>

        <div className="text-center">
          <p className="text-[13px] font-medium text-muted-foreground">Estimated churn probability</p>
          <div className="relative mt-2">
            <ProbabilityGauge value={p} threshold={result.threshold} color={o.arc} />
            <p className="absolute inset-x-0 bottom-7 text-[34px] font-semibold leading-none tracking-[-0.02em] tabular-nums">
              {formatPct(p)}
            </p>
          </div>
          <p className="mt-2 flex items-center justify-center gap-1.5 text-xs text-muted-foreground">
            <span aria-hidden className="inline-block h-3 w-0.5 rounded-full bg-foreground" />
            Decision threshold {formatPct(result.threshold, 0)}
          </p>
        </div>

        <p className="text-[13px] leading-5 text-[#3c4043]">
          Among historical customers with a similar profile, about <strong>{formatPct(p, 0)}</strong> churned. Because
          this is {result.predicted_churn ? "at or above" : "below"} the decision threshold of {result.threshold.toFixed(2)}, the
          model classifies the customer as <strong>{o.label.toLowerCase()}</strong>.
        </p>

        {result.warnings.length > 0 && (
          <Alert variant="warning" title="Check these inputs">
            <ul className="list-disc pl-4">
              {result.warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          </Alert>
        )}

        <div className="flex gap-2.5 rounded-lg bg-subtle p-3 text-xs leading-5 text-muted-foreground">
          <Info className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
          <p>
            <span className="font-medium text-foreground">Model estimate, not a guaranteed outcome.</span> Produced by{" "}
            {result.model_name}, trained on fictional sample data. Use it as decision support alongside human
            judgement, never to penalise a customer.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
