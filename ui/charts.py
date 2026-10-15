"""Altair chart builders for the dashboard.

Colours follow a validated, colour-vision-deficiency-safe categorical order.
Each entity keeps its colour on every page (No churn = blue, Churn = orange;
Logistic Regression = blue, Decision Tree = orange, Random Forest = aqua).
"""

from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

CHURN_SCALE = alt.Scale(domain=["No", "Yes"], range=[BLUE, ORANGE])
MODEL_ORDER = ["Logistic Regression", "Decision Tree", "Random Forest"]
MODEL_SCALE = alt.Scale(domain=MODEL_ORDER, range=[BLUE, ORANGE, AQUA])
METRIC_SCALE = alt.Scale(domain=["Precision", "Recall", "F1"], range=[BLUE, ORANGE, AQUA])


def style(chart: alt.Chart, height: int = 320) -> alt.Chart:
    return (
        chart.properties(height=height, background=SURFACE)
        .configure_view(stroke=None)
        .configure_axis(
            gridColor=GRID, domainColor=BASELINE, tickColor=BASELINE,
            labelColor=INK_2, titleColor=INK_2, labelFontSize=12, titleFontSize=12,
            titleFontWeight="normal",
        )
        .configure_legend(labelColor=INK_2, titleColor=INK_2, orient="top", labelFontSize=12)
        .configure_title(color=INK, fontSize=14, anchor="start", fontWeight="normal")
    )


def _bar(**kw):
    return alt.Chart().mark_bar(cornerRadiusEnd=4, **kw)


# ---------------- Data exploration ----------------

def churn_distribution(df: pd.DataFrame) -> alt.Chart:
    counts = df["Churn"].value_counts().rename_axis("Churn").reset_index(name="customers")
    counts["share"] = counts["customers"] / counts["customers"].sum()
    base = alt.Chart(counts).encode(
        y=alt.Y("Churn:N", title=None, sort=["No", "Yes"]),
        x=alt.X("customers:Q", title="Customers", axis=alt.Axis(tickCount=6, format=",")),
    )
    bars = base.mark_bar(cornerRadiusEnd=4, height=36).encode(
        color=alt.Color("Churn:N", scale=CHURN_SCALE, legend=None),
        tooltip=["Churn", alt.Tooltip("customers:Q", format=","), alt.Tooltip("share:Q", format=".1%")],
    )
    labels = base.mark_text(align="left", dx=6, color=INK_2).encode(
        text=alt.Text("share:Q", format=".1%")
    )
    return style(bars + labels, height=140)


def churn_rate_bars(table: pd.DataFrame, overall_rate: float, title: str = "") -> alt.Chart:
    """Horizontal bars of churn rate per group, with the overall rate as a reference rule."""
    base = alt.Chart(table).encode(
        y=alt.Y("group:N", title=None, sort=None),
    )
    bars = base.mark_bar(cornerRadiusEnd=4, color=BLUE, height={"band": 0.6}).encode(
        x=alt.X("churn_rate:Q", title="Churn rate", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        tooltip=[
            alt.Tooltip("group:N", title="Group"),
            alt.Tooltip("customers:Q", format=","),
            alt.Tooltip("churned:Q", format=","),
            alt.Tooltip("churn_rate:Q", format=".1%", title="Churn rate"),
        ],
    )
    labels = base.mark_text(align="left", dx=6, color=INK_2).encode(
        x="churn_rate:Q", text=alt.Text("churn_rate:Q", format=".1%")
    )
    rule = alt.Chart(pd.DataFrame({"rate": [overall_rate]})).mark_rule(
        color=MUTED, strokeDash=[4, 4]
    ).encode(x="rate:Q", tooltip=[alt.Tooltip("rate:Q", format=".1%", title="Overall churn rate")])
    height = max(120, 44 * len(table))
    return style((bars + labels + rule).properties(title=title), height=height)


def numeric_distribution(df: pd.DataFrame, col: str, bins: int = 30) -> alt.Chart:
    """Histogram of a numeric column for each churn class, as % of that class.

    Binned in pandas so only the bin counts (not every customer) reach the browser.
    """
    values = df[col].astype(float)
    edges = np.histogram_bin_edges(values.dropna(), bins=bins)
    frames = []
    for label in ["No", "Yes"]:
        counts, _ = np.histogram(values[df["Churn"] == label].dropna(), bins=edges)
        frames.append(pd.DataFrame({
            "bin_start": edges[:-1], "bin_end": edges[1:], "count": counts,
            "share": counts / max(counts.sum(), 1), "Churn": label,
        }))
    chart = (
        alt.Chart(pd.concat(frames, ignore_index=True))
        .mark_bar()  # no corner radius: it hides ranged (x/x2) bars in Vega
        .encode(
            x=alt.X("bin_start:Q", title=col, bin="binned"),
            x2="bin_end:Q",
            y=alt.Y("share:Q", title="Share of customers in class", axis=alt.Axis(format="%")),
            color=alt.Color("Churn:N", scale=CHURN_SCALE, title="Churn"),
            row=alt.Row("Churn:N", title=None, sort=["No", "Yes"],
                        header=alt.Header(labelColor=INK_2, labelExpr="'Churn: ' + datum.value")),
            tooltip=[alt.Tooltip("bin_start:Q", title=f"{col} from", format=",.0f"),
                     alt.Tooltip("bin_end:Q", title="to", format=",.0f"),
                     "Churn:N", alt.Tooltip("count:Q", title="Customers"),
                     alt.Tooltip("share:Q", format=".1%", title="Share of class")],
        )
        .properties(height=150)
    )
    return (
        chart.properties(background=SURFACE)
        .configure_view(stroke=None)
        .configure_axis(gridColor=GRID, domainColor=BASELINE, tickColor=BASELINE,
                        labelColor=INK_2, titleColor=INK_2, titleFontWeight="normal")
        .configure_legend(orient="top", labelColor=INK_2, titleColor=INK_2)
    )


def association_bars(assoc: pd.DataFrame) -> alt.Chart:
    data = assoc.assign(abs_strength=assoc["strength"].abs())
    chart = alt.Chart(data).mark_bar(cornerRadiusEnd=4, color=BLUE, height={"band": 0.6}).encode(
        y=alt.Y("feature:N", sort="-x", title=None),
        x=alt.X("abs_strength:Q", title="Strength of association with churn (|value|)"),
        tooltip=["feature", "measure", alt.Tooltip("strength:Q", format=".3f"),
                 alt.Tooltip("p_value:Q", format=".2e", title="p-value")],
    )
    return style(chart, height=max(200, 24 * len(data)))


# ---------------- Model performance ----------------

def metric_comparison(table: pd.DataFrame) -> alt.Chart:
    """Grouped bars: metric (x) x model (colour)."""
    chart = alt.Chart(table).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("metric:N", title=None, sort=list(dict.fromkeys(table["metric"])),
                axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("model:N", sort=MODEL_ORDER),
        y=alt.Y("value:Q", title="Score (test set)", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("model:N", scale=MODEL_SCALE, title="Model"),
        tooltip=["model", "metric", alt.Tooltip("value:Q", format=".3f")],
    )
    return style(chart, height=320)


def _curve_frame(results: dict, key: str) -> pd.DataFrame:
    frames = []
    for name, res in results["models"].items():
        c = res["test"][key]
        frames.append(pd.DataFrame({"x": c["x"], "y": c["y"], "threshold": c.get("threshold"), "model": name}))
    return pd.concat(frames, ignore_index=True)


def roc_curves(results: dict) -> alt.Chart:
    data = _curve_frame(results, "roc_curve")
    auc = {n: r["test"]["metrics"]["roc_auc"] for n, r in results["models"].items()}
    data["label"] = data["model"].map(lambda n: f"{n} (AUC {auc[n]:.3f})")
    lines = alt.Chart(data).mark_line(strokeWidth=2).encode(
        x=alt.X("x:Q", title="False positive rate"),
        y=alt.Y("y:Q", title="True positive rate (recall)"),
        color=alt.Color("model:N", scale=MODEL_SCALE, title="Model"),
        tooltip=["label:N", alt.Tooltip("x:Q", format=".3f", title="FPR"),
                 alt.Tooltip("y:Q", format=".3f", title="TPR"),
                 alt.Tooltip("threshold:Q", format=".3f")],
    )
    diag = alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]})).mark_line(
        color=MUTED, strokeDash=[4, 4], strokeWidth=1
    ).encode(x="x:Q", y="y:Q")
    return style(diag + lines, height=360)


def pr_curves(results: dict, base_rate: float) -> alt.Chart:
    data = _curve_frame(results, "pr_curve")
    lines = alt.Chart(data).mark_line(strokeWidth=2).encode(
        x=alt.X("x:Q", title="Recall", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("y:Q", title="Precision", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("model:N", scale=MODEL_SCALE, title="Model"),
        tooltip=["model:N", alt.Tooltip("x:Q", format=".3f", title="Recall"),
                 alt.Tooltip("y:Q", format=".3f", title="Precision"),
                 alt.Tooltip("threshold:Q", format=".3f")],
    )
    rule = alt.Chart(pd.DataFrame({"y": [base_rate]})).mark_rule(
        color=MUTED, strokeDash=[4, 4]
    ).encode(y="y:Q", tooltip=[alt.Tooltip("y:Q", format=".1%", title="Churn rate (no-skill precision)")])
    return style(rule + lines, height=360)


def confusion_matrix_chart(cm: list[list[int]]) -> alt.Chart:
    labels = ["No churn", "Churn"]
    names = [["True negative", "False positive"], ["False negative", "True positive"]]
    rows = [
        {"actual": labels[i], "predicted": labels[j], "count": cm[i][j], "cell": names[i][j]}
        for i in range(2) for j in range(2)
    ]
    data = pd.DataFrame(rows)
    total = data["count"].sum()
    data["share"] = data["count"] / total
    data["text"] = data.apply(lambda r: f"{r['count']:,} ({r['share']:.0%})", axis=1)
    base = alt.Chart(data).encode(
        x=alt.X("predicted:N", title="Predicted", sort=labels, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("actual:N", title="Actual", sort=labels),
    )
    rect = base.mark_rect(cornerRadius=4, stroke=SURFACE, strokeWidth=2).encode(
        color=alt.Color("count:Q", scale=alt.Scale(range=SEQ_BLUE[:5]), legend=None),
        tooltip=["cell", "actual", "predicted", alt.Tooltip("count:Q", format=","),
                 alt.Tooltip("share:Q", format=".1%")],
    )
    text = base.mark_text(fontSize=14).encode(
        text="text:N",
        color=alt.condition(alt.datum.share > 0.3, alt.value("#ffffff"), alt.value(INK)),
    )
    return style(rect + text, height=260)


def threshold_chart(table: list[dict], current: float) -> alt.Chart:
    df = pd.DataFrame(table)
    # precision is undefined when nothing is flagged; leave those thresholds out
    df = df[(df["tp"] + df["fp"]) > 0]
    long = df.melt(id_vars=["threshold"], value_vars=["precision", "recall", "f1"],
                   var_name="metric", value_name="value")
    long["metric"] = long["metric"].map({"precision": "Precision", "recall": "Recall", "f1": "F1"})
    hover = alt.selection_point(fields=["threshold"], nearest=True, on="pointerover", empty=False)
    base = alt.Chart(long).encode(
        x=alt.X("threshold:Q", title="Decision threshold", scale=alt.Scale(domain=[0, 1])),
    )
    lines = base.mark_line(strokeWidth=2).encode(
        y=alt.Y("value:Q", title="Score", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("metric:N", scale=METRIC_SCALE, title=None),
    )
    points = base.mark_point(size=60, filled=True).encode(
        y="value:Q", color=alt.Color("metric:N", scale=METRIC_SCALE, legend=None),
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
    )
    wide = df.rename(columns={"f1": "F1", "precision": "Precision", "recall": "Recall"})
    crosshair = alt.Chart(wide).mark_rule(color=MUTED).encode(
        x="threshold:Q",
        opacity=alt.condition(hover, alt.value(0.6), alt.value(0)),
        tooltip=[alt.Tooltip("threshold:Q", format=".2f"),
                 alt.Tooltip("Precision:Q", format=".3f"), alt.Tooltip("Recall:Q", format=".3f"),
                 alt.Tooltip("F1:Q", format=".3f"),
                 alt.Tooltip("predicted_positive_rate:Q", format=".1%", title="Flagged as churn")],
    ).add_params(hover)
    marker = alt.Chart(pd.DataFrame({"t": [current]})).mark_rule(color=INK, strokeDash=[4, 4]).encode(x="t:Q")
    return style(lines + points + crosshair + marker, height=320)


def calibration_chart(points: dict[str, dict]) -> alt.Chart:
    """Reliability diagram. ``points`` maps a label to {mean_predicted, fraction_positive}."""
    frames = [
        pd.DataFrame({"predicted": p["mean_predicted"], "observed": p["fraction_positive"], "model": label})
        for label, p in points.items()
    ]
    data = pd.concat(frames, ignore_index=True)
    domain = list(points)
    scale = alt.Scale(domain=domain, range=[ORANGE, BLUE, AQUA][: len(domain)])
    base = alt.Chart(data).encode(
        x=alt.X("predicted:Q", title="Mean predicted probability", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("observed:Q", title="Observed churn rate", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("model:N", scale=scale, title=None),
        tooltip=["model", alt.Tooltip("predicted:Q", format=".3f"), alt.Tooltip("observed:Q", format=".3f")],
    )
    diag = alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]})).mark_line(
        color=MUTED, strokeDash=[4, 4], strokeWidth=1
    ).encode(x="x:Q", y="y:Q")
    return style(diag + base.mark_line(strokeWidth=2) + base.mark_point(size=60, filled=True), height=340)


# ---------------- Insights / predictions ----------------

def importance_bars(rows: list[dict], value: str, title: str, error: str | None = None,
                    signed: bool = False) -> alt.Chart:
    data = pd.DataFrame(rows)
    if signed:
        data["direction"] = data[value].map(lambda v: "Higher churn odds" if v > 0 else "Lower churn odds")
        color = alt.Color("direction:N", title=None,
                          scale=alt.Scale(domain=["Higher churn odds", "Lower churn odds"], range=[ORANGE, BLUE]))
    else:
        color = alt.value(BLUE)
    tooltip = ["feature", alt.Tooltip(f"{value}:Q", format=".4f")]
    if error:
        tooltip.append(alt.Tooltip(f"{error}:Q", format=".4f", title="Std. dev."))
    bars = alt.Chart(data).mark_bar(cornerRadiusEnd=4, height={"band": 0.6}).encode(
        y=alt.Y("feature:N", sort=alt.EncodingSortField(field=value, op="max", order="descending")
                if not signed else alt.EncodingSortField(field="abs", order="descending"), title=None),
        x=alt.X(f"{value}:Q", title=title),
        color=color,
        tooltip=tooltip,
    )
    if signed:
        bars = bars.transform_calculate(abs=f"abs(datum['{value}'])")
    return style(bars, height=max(200, 26 * len(data)))


def probability_histogram(probs: pd.Series, threshold: float) -> alt.Chart:
    edges = np.linspace(0, 1, 21)
    counts, _ = np.histogram(np.clip(probs.to_numpy(dtype=float), 0, 1), bins=edges)
    data = pd.DataFrame({"start": edges[:-1], "end": edges[1:], "customers": counts})
    bars = alt.Chart(data).mark_bar(color=BLUE).encode(
        x=alt.X("start:Q", bin="binned", title="Predicted churn probability",
                scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%")),
        x2="end:Q",
        y=alt.Y("customers:Q", title="Customers"),
        tooltip=[alt.Tooltip("start:Q", format=".0%", title="From"), alt.Tooltip("end:Q", format=".0%", title="To"),
                 alt.Tooltip("customers:Q", format=",")],
    )
    rule = alt.Chart(pd.DataFrame({"t": [threshold]})).mark_rule(color=INK, strokeDash=[4, 4]).encode(
        x="t:Q", tooltip=[alt.Tooltip("t:Q", title="Decision threshold", format=".2f")]
    )
    return style(bars + rule, height=260)


def scenario_bars(data: pd.DataFrame, threshold: float) -> alt.Chart:
    base = alt.Chart(data).encode(y=alt.Y("scenario:N", title=None, sort=None))
    bars = base.mark_bar(cornerRadiusEnd=4, height={"band": 0.6}).encode(
        x=alt.X("probability:Q", title="Predicted churn probability", scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format="%")),
        color=alt.condition(alt.datum.current, alt.value(ORANGE), alt.value(BLUE)),
        tooltip=["scenario", alt.Tooltip("probability:Q", format=".1%")],
    )
    labels = base.mark_text(align="left", dx=6, color=INK_2).encode(
        x="probability:Q", text=alt.Text("probability:Q", format=".1%")
    )
    rule = alt.Chart(pd.DataFrame({"t": [threshold]})).mark_rule(color=MUTED, strokeDash=[4, 4]).encode(x="t:Q")
    return style(bars + labels + rule, height=max(120, 44 * len(data)))
