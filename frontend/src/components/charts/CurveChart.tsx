import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Legend } from "@/components/ChartCard";
import { COLORS } from "@/lib/colors";
import { formatNum } from "@/lib/format";

import { TooltipBox, axisProps } from "./ChartTooltip";

export interface CurveSeries {
  name: string;
  color: string;
  points: { x: number; y: number; threshold?: number | null }[];
  dots?: boolean;
}

interface CurveChartProps {
  series: CurveSeries[];
  xLabel: string;
  yLabel: string;
  diagonal?: boolean; // y = x reference (ROC chance line, perfect calibration)
  hLine?: { y: number; label: string };
  vLine?: { x: number; label: string };
  height?: number;
  xDomain?: [number, number];
}

/** Multi-series line chart on a [0,1] x [0,1] plane (ROC, PR, calibration, threshold). */
export function CurveChart({ series, xLabel, yLabel, diagonal, hLine, vLine, height = 300, xDomain = [0, 1] }: CurveChartProps) {
  const legend: { label: string; color: string; dashed?: boolean }[] = series.map((s) => ({ label: s.name, color: s.color }));
  if (diagonal) legend.push({ label: "Reference (y = x)", color: COLORS.reference, dashed: true });
  if (hLine) legend.push({ label: hLine.label, color: COLORS.reference, dashed: true });
  if (vLine) legend.push({ label: vLine.label, color: COLORS.ink, dashed: true });

  return (
    <div>
      <Legend items={legend} />
      <ResponsiveContainer width="100%" height={height}>
        <LineChart margin={{ top: 4, right: 12, left: -4, bottom: 18 }}>
          <CartesianGrid stroke={COLORS.grid} />
          <XAxis
            type="number"
            dataKey="x"
            domain={xDomain}
            ticks={[0, 0.2, 0.4, 0.6, 0.8, 1]}
            {...axisProps}
            label={{ value: xLabel, position: "insideBottom", offset: -12, fill: COLORS.axisText, fontSize: 12 }}
          />
          <YAxis
            type="number"
            domain={[0, 1]}
            ticks={[0, 0.2, 0.4, 0.6, 0.8, 1]}
            {...axisProps}
            axisLine={false}
            width={44}
            label={{ value: yLabel, angle: -90, position: "insideLeft", offset: 14, fill: COLORS.axisText, fontSize: 12, style: { textAnchor: "middle" } }}
          />
          <Tooltip
            cursor={{ stroke: COLORS.reference, strokeDasharray: "3 3" }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              return (
                <TooltipBox
                  rows={payload.map((p) => {
                    const pt = p.payload as { x: number; y: number; threshold?: number | null };
                    const th = pt.threshold !== undefined && pt.threshold !== null ? ` · t=${pt.threshold.toFixed(2)}` : "";
                    return {
                      label: String(p.name),
                      value: `${xLabel.split(" ")[0]} ${formatNum(pt.x, 2)}, ${formatNum(pt.y, 3)}${th}`,
                      color: String(p.color),
                    };
                  })}
                />
              );
            }}
          />
          {diagonal && (
            <ReferenceLine
              segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]}
              stroke={COLORS.reference}
              strokeDasharray="4 4"
              ifOverflow="hidden"
            />
          )}
          {hLine && <ReferenceLine y={hLine.y} stroke={COLORS.reference} strokeDasharray="4 4" />}
          {vLine && <ReferenceLine x={vLine.x} stroke={COLORS.ink} strokeDasharray="4 4" />}
          {series.map((s) => (
            <Line
              key={s.name}
              data={s.points}
              dataKey="y"
              name={s.name}
              type="linear"
              stroke={s.color}
              strokeWidth={2}
              dot={s.dots ? { r: 4, fill: s.color, stroke: "#fff", strokeWidth: 1.5 } : false}
              activeDot={{ r: 4.5, stroke: "#fff", strokeWidth: 2 }}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
