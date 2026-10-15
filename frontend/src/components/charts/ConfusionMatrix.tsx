import { seqBlue } from "@/lib/colors";
import { formatInt, formatPct } from "@/lib/format";

const CELL_NAMES = [
  ["True negative", "False positive"],
  ["False negative", "True positive"],
];
const LABELS = ["No churn", "Churn"];

/** 2x2 confusion matrix (rows = actual, columns = predicted). */
export function ConfusionMatrix({ matrix }: { matrix: number[][] }) {
  const total = matrix.flat().reduce((a, b) => a + b, 0);
  const max = Math.max(...matrix.flat());
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[300px] border-separate border-spacing-1 text-sm" aria-label="Confusion matrix">
        <thead>
          <tr>
            <th className="w-24" />
            <th colSpan={2} className="pb-1 text-center text-xs font-medium text-muted-foreground">
              Predicted
            </th>
          </tr>
          <tr>
            <th className="text-left text-xs font-medium text-muted-foreground">Actual</th>
            {LABELS.map((l) => (
              <th key={l} scope="col" className="text-center text-xs font-medium text-muted-foreground">
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={LABELS[i]}>
              <th scope="row" className="text-left text-xs font-medium text-muted-foreground">
                {LABELS[i]}
              </th>
              {row.map((v, j) => {
                const frac = v / max;
                const dark = frac > 0.55;
                return (
                  <td
                    key={j}
                    className="h-24 rounded-lg text-center align-middle transition-transform duration-150"
                    style={{ backgroundColor: seqBlue(0.15 + frac * 0.75), color: dark ? "#fff" : "#202124" }}
                    title={`${CELL_NAMES[i][j]}: ${formatInt(v)}`}
                  >
                    <div className="text-xl font-semibold tabular-nums">{formatInt(v)}</div>
                    <div className={dark ? "text-[11px] text-white/90" : "text-[11px] text-[#3c4043]"}>
                      {CELL_NAMES[i][j]} · {formatPct(v / total, 0)}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
