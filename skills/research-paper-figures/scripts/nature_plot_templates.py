"""Local Nature-style plotting templates for thesis figures.

This script is a controlled port of useful nature-figure ideas into the local
research workflow. It renders common research plots from a JSON figure spec and
keeps outputs traceable to claims, source data, and figure-plan records.
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import image as mpimg


PALETTE = {
    "hero": "#245B8F",
    "hero_light": "#8FB5D6",
    "baseline": "#5C6378",
    "baseline_light": "#B9C0D4",
    "support": "#6EA878",
    "support_light": "#CFE5D3",
    "contrast": "#B85C58",
    "contrast_light": "#E7B4B0",
    "neutral": "#777777",
    "neutral_light": "#D7D7D7",
    "ink": "#222222",
    "delta_up": "#2E9E44",
    "delta_down": "#D33F3F",
    "teal": "#3C929A",
    "violet": "#8F6CB3",
}

DEFAULT_COLORS = [
    PALETTE["hero"],
    PALETTE["baseline"],
    PALETTE["support"],
    PALETTE["contrast"],
    PALETTE["teal"],
    PALETTE["violet"],
]

FAMILY_COLORS = [
    "#484878",
    "#7884B4",
    "#B4C0E4",
    "#E8E6F0",
    "#E4CCD8",
    "#F0C0CC",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_style(font_size: float = 9, axes_linewidth: float = 1.0) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": font_size,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": axes_linewidth,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def choose_colors(spec: dict[str, Any], n: int) -> list[str]:
    style = spec.get("style", {})
    if style.get("colors"):
        colors = list(style["colors"])
    elif style.get("palette") == "family":
        colors = FAMILY_COLORS
    else:
        colors = DEFAULT_COLORS
    if not colors:
        colors = DEFAULT_COLORS
    return [colors[i % len(colors)] for i in range(n)]


def add_panel_label(ax, label: str, x: float = -0.08, y: float = 1.04) -> None:
    ax.text(x, y, label, transform=ax.transAxes, fontsize=10, fontweight="bold", ha="left", va="bottom")


def luminance(hex_color: str) -> float:
    c = hex_color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def tighten_ylim(ax, values: np.ndarray, lower_zero: bool = False, margin_frac: float = 0.12) -> None:
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return
    lo, hi = float(vals.min()), float(vals.max())
    if lower_zero:
        lo = min(0.0, lo)
    span = max(hi - lo, abs(hi) * 0.04, 1e-6)
    ax.set_ylim(lo - span * margin_frac, hi + span * margin_frac)


def validate_spec(spec: dict[str, Any], template_name: str) -> list[str]:
    warnings: list[str] = []
    for field in ("figure_id", "template", "claim", "caption", "data"):
        if field not in spec:
            warnings.append(f"missing required field: {field}")
    if spec.get("template") != template_name:
        warnings.append(f"template mismatch: expected {template_name}, got {spec.get('template')}")
    if not spec.get("audit", {}).get("source_data") and not spec.get("data", {}).get("source"):
        warnings.append("source data is not recorded")
    return warnings


def annotate_bars(ax, bars, fmt: str = "{:.3g}", placement: str = "outside", orientation: str = "vertical") -> None:
    for bar in bars:
        value = bar.get_width() if orientation == "horizontal" else bar.get_height()
        if placement == "inside":
            face = mpl.colors.to_hex(bar.get_facecolor())
            text_color = "white" if luminance(face) < 128 else "black"
            if orientation == "horizontal":
                ax.text(bar.get_width() * 0.98, bar.get_y() + bar.get_height() / 2, fmt.format(value), ha="right", va="center", fontsize=7, color=text_color)
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 0.98, fmt.format(value), ha="center", va="top", fontsize=7, color=text_color)
        else:
            if orientation == "horizontal":
                ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, " " + fmt.format(value), ha="left", va="center", fontsize=7)
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), fmt.format(value), ha="center", va="bottom", fontsize=7)


def apply_hatches(containers, hatches: list[str] | None = None) -> None:
    hatches = hatches or ["/", "\\", ".", "x", "o", "+"]
    for container, hatch in zip(containers, hatches):
        for patch in container:
            patch.set_hatch(hatch)
            patch.set_edgecolor(PALETTE["ink"])
            patch.set_linewidth(0.8)


def format_log_axis(ax, axis: str = "y") -> None:
    if axis == "x":
        ax.set_xscale("log")
        ax.xaxis.set_minor_locator(mpl.ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
    else:
        ax.set_yscale("log")
        ax.yaxis.set_minor_locator(mpl.ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
    ax.grid(False)


def add_reference_line(ax, value: float, label: str = "", axis: str = "y") -> None:
    if axis == "x":
        ax.axvline(value, color=PALETTE["neutral"], lw=0.9, ls="--", alpha=0.75)
        if label:
            ax.text(value, 0.98, label, transform=ax.get_xaxis_transform(), rotation=90, ha="right", va="top", fontsize=7, color=PALETTE["neutral"])
    else:
        ax.axhline(value, color=PALETTE["neutral"], lw=0.9, ls="--", alpha=0.75)
        if label:
            ax.text(0.99, value, label, transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=7, color=PALETTE["neutral"])


def add_event_annotations(ax, events: list[dict[str, Any]]) -> None:
    if not events:
        return
    y0, y1 = ax.get_ylim()
    dy = (y1 - y0) * 0.08
    for event in events:
        x = event["x"]
        y = event.get("y", y1 - dy)
        label = event.get("label", "")
        ax.annotate(
            label,
            xy=(x, y),
            xytext=(x, min(y + dy, y1)),
            ha="center",
            va="bottom",
            fontsize=7,
            arrowprops={"arrowstyle": "-|>", "lw": 0.8, "color": PALETTE["ink"], "mutation_scale": 8},
        )


def make_shared_legend(fig, axes, loc: str = "upper center", ncol: int | None = None) -> None:
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l):
            if label and label not in labels:
                handles.append(handle)
                labels.append(label)
    if handles:
        fig.legend(handles, labels, loc=loc, ncol=ncol or max(1, len(labels)), frameon=False)
        for ax in axes:
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()


def finalize_figure(fig, out: Path, formats: list[str], dpi: int = 300) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if any(getattr(ax, "name", "") == "polar" for ax in fig.axes):
        fig.subplots_adjust(top=0.90, bottom=0.10, left=0.08, right=0.90)
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="This figure includes Axes that are not compatible with tight_layout.*")
            fig.tight_layout(pad=1.6)
    for fmt in formats:
        fig.savefig(out.with_suffix(f".{fmt}"), dpi=dpi, bbox_inches="tight")


def render_grouped_bar(spec: dict[str, Any]):
    data = spec["data"]
    categories = data["categories"]
    series = [np.asarray(s["values"], dtype=float) for s in data["series"]]
    labels = [s["name"] for s in data["series"]]
    errors = [np.asarray(s.get("errors", np.zeros_like(series[i])), dtype=float) for i, s in enumerate(data["series"])]
    colors = choose_colors(spec, len(series))
    style = spec.get("style", {})

    fig, ax = plt.subplots(figsize=style.get("figsize", [7.2, 4.2]))
    x = np.arange(len(categories))
    width = float(style.get("group_width", 0.78)) / max(len(series), 1)

    containers = []
    for i, (vals, err, label, color) in enumerate(zip(series, errors, labels, colors)):
        offset = (i - (len(series) - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            vals,
            width=width,
            yerr=err if np.any(err) else None,
            capsize=style.get("capsize", 3),
            label=label,
            color=color,
            edgecolor=PALETTE["ink"],
            linewidth=0.8,
        )
        containers.append(bars)
        if style.get("annotate"):
            annotate_bars(ax, bars, fmt=style.get("fmt", "{:.3g}"), placement=style.get("annotation_placement", "outside"), orientation="vertical")
    if style.get("hatch"):
        apply_hatches(containers)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=style.get("x_rotation", 0), ha="center")
    ax.set_ylabel(style.get("ylabel", data.get("ylabel", "Value")))
    if style.get("xlabel"):
        ax.set_xlabel(style["xlabel"])
    if style.get("tight_y", True):
        tighten_ylim(ax, np.concatenate(series), lower_zero=bool(style.get("lower_zero", False)))
    ax.legend(loc=style.get("legend_loc", "best"))
    return fig, [ax]


def render_line_trend(spec: dict[str, Any]):
    data = spec["data"]
    x = np.asarray(data["x"], dtype=float)
    lines = data["series"]
    colors = choose_colors(spec, len(lines))
    style = spec.get("style", {})
    fig, ax = plt.subplots(figsize=style.get("figsize", [7.2, 4.0]))
    all_y = []
    for line, color in zip(lines, colors):
        y = np.asarray(line["values"], dtype=float)
        all_y.append(y.reshape(-1))
        if y.ndim == 2:
            mean = y.mean(axis=0)
            std = y.std(axis=0)
            ax.plot(x, mean, color=color, lw=style.get("linewidth", 1.8), marker=style.get("marker", "o"), ms=style.get("markersize", 4), label=line["name"])
            ax.fill_between(x, mean - std, mean + std, color=color, alpha=style.get("shadow_alpha", 0.16))
        else:
            ax.plot(x, y, color=color, lw=style.get("linewidth", 1.8), marker=style.get("marker", "o"), ms=style.get("markersize", 4), label=line["name"])
    ax.set_xlabel(style.get("xlabel", data.get("xlabel", "x")))
    ax.set_ylabel(style.get("ylabel", data.get("ylabel", "Value")))
    if style.get("tight_y", True):
        tighten_ylim(ax, np.concatenate(all_y), lower_zero=False)
    for ref in style.get("reference_lines", []):
        add_reference_line(ax, ref["value"], ref.get("label", ""), ref.get("axis", "y"))
    add_event_annotations(ax, style.get("events", []))
    ax.legend(loc=style.get("legend_loc", "best"))
    return fig, [ax]


def render_threshold_curve(spec: dict[str, Any]):
    fig, axes = render_line_trend(spec)
    ax = axes[0]
    style = spec.get("style", {})
    best = spec.get("data", {}).get("best")
    if best:
        ax.scatter([best["x"]], [best["y"]], s=56, color=PALETTE["delta_up"], edgecolors="white", linewidths=0.7, zorder=5)
        ax.annotate(best.get("label", "selected"), xy=(best["x"], best["y"]), xytext=(best["x"], best["y"] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.08), ha="center", fontsize=7, arrowprops={"arrowstyle": "-|>", "lw": 0.8})
    ax.set_xlabel(style.get("xlabel", spec.get("data", {}).get("xlabel", "Threshold")))
    return fig, axes


def render_heatmap(spec: dict[str, Any]):
    data = spec["data"]
    matrix = np.asarray(data["matrix"], dtype=float)
    style = spec.get("style", {})
    fig, ax = plt.subplots(figsize=style.get("figsize", [6.2, 4.8]))
    cmap = plt.get_cmap(style.get("cmap", "RdBu_r" if style.get("diverging") else "magma"))
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=style.get("vmin"), vmax=style.get("vmax"))
    ax.set_xticks(np.arange(matrix.shape[1]))
    ax.set_xticklabels(data.get("x_labels", [str(i) for i in range(matrix.shape[1])]), rotation=style.get("x_rotation", 30), ha="right")
    ax.set_yticks(np.arange(matrix.shape[0]))
    ax.set_yticklabels(data.get("y_labels", [str(i) for i in range(matrix.shape[0])]))
    if style.get("annotate", True):
        norm = mpl.colors.Normalize(vmin=np.nanmin(matrix), vmax=np.nanmax(matrix))
        for (i, j), val in np.ndenumerate(matrix):
            if not np.isfinite(val):
                continue
            r, g, b, _ = cmap(norm(val))
            txt = "white" if (0.299 * r + 0.587 * g + 0.114 * b) < 0.5 else "black"
            ax.text(j, i, style.get("fmt", "{:.2f}").format(val), ha="center", va="center", fontsize=style.get("annotation_size", 7), color=txt)
    if style.get("colorbar", True):
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if style.get("cbar_label"):
            cbar.set_label(style["cbar_label"])
    ax.tick_params(axis="both", length=0)
    ax.set_frame_on(False)
    return fig, [ax]


def render_confusion_heatmap(spec: dict[str, Any]):
    data = spec["data"]
    matrix = np.asarray(data["matrix"], dtype=float)
    style = spec.get("style", {})
    if style.get("normalize") == "row":
        denom = matrix.sum(axis=1, keepdims=True)
        matrix = np.divide(matrix, denom, out=np.zeros_like(matrix), where=denom != 0)
    elif style.get("normalize") == "all":
        total = matrix.sum()
        if total:
            matrix = matrix / total
    local = {
        **spec,
        "data": {
            "matrix": matrix.tolist(),
            "x_labels": data.get("labels", data.get("x_labels")),
            "y_labels": data.get("labels", data.get("y_labels")),
        },
        "style": {
            **style,
            "cmap": style.get("cmap", "Blues"),
            "fmt": style.get("fmt", "{:.2f}" if style.get("normalize") else "{:.0f}"),
            "cbar_label": style.get("cbar_label", "Proportion" if style.get("normalize") else "Count"),
        },
    }
    fig, axes = render_heatmap(local)
    axes[0].set_xlabel(style.get("xlabel", "Predicted label"))
    axes[0].set_ylabel(style.get("ylabel", "True label"))
    return fig, axes


def render_scatter(spec: dict[str, Any]):
    data = spec["data"]
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    style = spec.get("style", {})
    color_values = data.get("color")
    size_values = np.asarray(data.get("size", np.full_like(x, style.get("size", 40))), dtype=float)
    fig, ax = plt.subplots(figsize=style.get("figsize", [5.5, 4.8]))
    sc = ax.scatter(x, y, c=color_values if color_values is not None else choose_colors(spec, 1)[0], s=size_values, alpha=style.get("alpha", 0.82), edgecolors="white", linewidths=0.6)
    if style.get("median_guides"):
        ax.axvline(np.median(x), color=PALETTE["neutral"], lw=0.8, ls="--", alpha=0.7)
        ax.axhline(np.median(y), color=PALETTE["neutral"], lw=0.8, ls="--", alpha=0.7)
    if color_values is not None and style.get("colorbar", True):
        cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        if style.get("cbar_label"):
            cbar.set_label(style["cbar_label"])
    ax.set_xlabel(style.get("xlabel", data.get("xlabel", "x")))
    ax.set_ylabel(style.get("ylabel", data.get("ylabel", "y")))
    return fig, [ax]


def render_distribution(spec: dict[str, Any]):
    data = spec["data"]
    groups = data["groups"]
    labels = [g["name"] for g in groups]
    values = [np.asarray(g["values"], dtype=float) for g in groups]
    colors = choose_colors(spec, len(groups))
    style = spec.get("style", {})
    fig, ax = plt.subplots(figsize=style.get("figsize", [6.2, 4.2]))
    parts = ax.violinplot(values, showmeans=False, showmedians=True, widths=0.72)
    for body, color in zip(parts["bodies"], colors):
        body.set_facecolor(color)
        body.set_edgecolor(PALETTE["ink"])
        body.set_alpha(0.55)
    ax.boxplot(values, widths=0.16, patch_artist=True, showfliers=False, boxprops={"facecolor": "white", "edgecolor": PALETTE["ink"], "linewidth": 0.8}, medianprops={"color": PALETTE["ink"]})
    if style.get("strip", True):
        rng = np.random.default_rng(int(style.get("jitter_seed", 7)))
        for i, (vals, color) in enumerate(zip(values, colors), start=1):
            jitter = rng.normal(0, 0.035, size=len(vals))
            ax.scatter(np.full_like(vals, i, dtype=float) + jitter, vals, s=style.get("strip_size", 14), color=color, alpha=0.55, edgecolors="white", linewidths=0.35, zorder=3)
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=style.get("x_rotation", 0))
    ax.set_ylabel(style.get("ylabel", data.get("ylabel", "Value")))
    return fig, [ax]


def render_forest(spec: dict[str, Any]):
    data = spec["data"]
    labels = list(data["labels"])
    estimates = np.asarray(data["estimates"], dtype=float)
    lows = np.asarray(data["ci_low"], dtype=float)
    highs = np.asarray(data["ci_high"], dtype=float)
    if spec.get("style", {}).get("sort"):
        order = np.argsort(estimates)
        if spec["style"].get("sort") == "desc":
            order = order[::-1]
        labels = [labels[i] for i in order]
        estimates, lows, highs = estimates[order], lows[order], highs[order]
    colors = choose_colors(spec, len(labels))
    style = spec.get("style", {})
    fig, ax = plt.subplots(figsize=style.get("figsize", [5.8, 4.5]))
    y = np.arange(len(labels))[::-1]
    for band in style.get("bands", []):
        start = len(labels) - 1 - int(band["start"])
        end = len(labels) - 1 - int(band["end"])
        ax.axhspan(end - 0.5, start + 0.5, color=band.get("color", PALETTE["neutral_light"]), alpha=band.get("alpha", 0.22), zorder=0)
    for yi, est, lo, hi, color in zip(y, estimates, lows, highs, colors):
        ax.plot([lo, hi], [yi, yi], color=color, lw=1.8)
        ax.plot(est, yi, marker="o", ms=4.5, color=color)
    add_reference_line(ax, style.get("reference", 0.0), style.get("reference_label", "reference"), axis="x")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(style.get("xlabel", data.get("xlabel", "Estimate")))
    return fig, [ax]


def render_radar(spec: dict[str, Any]):
    data = spec["data"]
    labels = data["labels"]
    series = data["series"]
    colors = choose_colors(spec, len(series))
    style = spec.get("style", {})
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles_closed = np.r_[angles, angles[0]]
    fig = plt.figure(figsize=style.get("figsize", [6.2, 5.6]))
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    bounds = data.get("bounds")
    for item, color in zip(series, colors):
        vals = np.asarray(item["values"], dtype=float)
        if bounds:
            lo = np.asarray([b[0] for b in bounds], dtype=float)
            hi = np.asarray([b[1] for b in bounds], dtype=float)
            vals = np.divide(vals - lo, hi - lo, out=np.zeros_like(vals), where=(hi - lo) != 0)
        vals_closed = np.r_[vals, vals[0]]
        ax.plot(angles_closed, vals_closed, color=color, lw=1.8, label=item["name"])
        ax.fill(angles_closed, vals_closed, color=color, alpha=0.07)
        ax.scatter(angles, vals, color=color, s=18, zorder=4)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels)
    ax.set_ylim(style.get("rmin", 0), style.get("rmax", 1))
    if bounds:
        ax.text(0.5, -0.12, "Values normalized per axis; inspect bounds before comparing area.", transform=ax.transAxes, ha="center", va="top", fontsize=7, color=PALETTE["neutral"])
    ax.grid(color=PALETTE["neutral_light"], lw=0.6)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.08))
    return fig, [ax]


def render_log_bar(spec: dict[str, Any]):
    data = spec["data"]
    categories = data["categories"]
    values = np.asarray(data["values"], dtype=float)
    errors = np.asarray(data.get("errors", np.zeros_like(values)), dtype=float)
    style = spec.get("style", {})
    colors = choose_colors(spec, len(categories))
    fig, ax = plt.subplots(figsize=style.get("figsize", [6.8, 4.2]))
    bars = ax.bar(np.arange(len(categories)), values, yerr=errors if np.any(errors) else None, color=colors, edgecolor=PALETTE["ink"], linewidth=0.8, capsize=style.get("capsize", 3))
    format_log_axis(ax, style.get("axis", "y"))
    if style.get("annotate", True):
        annotate_bars(ax, bars, fmt=style.get("fmt", "{:.3g}"), placement="outside", orientation="vertical")
    ax.set_xticks(np.arange(len(categories)))
    ax.set_xticklabels(categories, rotation=style.get("x_rotation", 25), ha="right")
    ax.set_ylabel(style.get("ylabel", data.get("ylabel", "Value")))
    return fig, [ax]


def render_ablation_barh(spec: dict[str, Any]):
    data = spec["data"]
    labels = data["labels"]
    values = np.asarray(data["values"], dtype=float)
    errors = np.asarray(data.get("errors", np.zeros_like(values)), dtype=float)
    style = spec.get("style", {})
    base = mpl.colors.to_rgb(style.get("color", PALETTE["hero"]))
    alphas = np.linspace(style.get("alpha_min", 0.28), style.get("alpha_max", 0.95), len(values))
    colors = [(base[0], base[1], base[2], a) for a in alphas]
    fig, ax = plt.subplots(figsize=style.get("figsize", [6.8, 4.2]))
    y = np.arange(len(labels))
    bars = ax.barh(y, values, xerr=errors if np.any(errors) else None, color=colors, edgecolor=PALETTE["ink"], linewidth=0.8, capsize=style.get("capsize", 3))
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(style.get("xlabel", data.get("xlabel", "Score")))
    if style.get("annotate", True):
        annotate_bars(ax, bars, fmt=style.get("fmt", "{:.3g}"), placement="outside", orientation="horizontal")
    tighten_ylim(ax, y, lower_zero=True, margin_frac=0.08)
    ax.invert_yaxis() if style.get("top_is_full", True) else None
    return fig, [ax]


def render_image_plate(spec: dict[str, Any]):
    data = spec["data"]
    rows = int(data.get("rows", 2))
    cols = int(data.get("cols", 3))
    style = spec.get("style", {})
    fig, axes = plt.subplots(rows, cols, figsize=style.get("figsize", [7.2, 4.8]), squeeze=False)
    paths = data.get("paths", [])
    labels = data.get("labels", [])
    rng = np.random.default_rng(int(style.get("seed", 12)))
    for idx, ax in enumerate(axes.ravel()):
        ax.set_facecolor("black")
        if idx < len(paths):
            img = mpimg.imread(paths[idx])
        else:
            x = np.linspace(-1, 1, 120)
            y = np.linspace(-1, 1, 90)
            xx, yy = np.meshgrid(x, y)
            cx, cy = rng.uniform(-0.35, 0.35, size=2)
            img = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) * rng.uniform(3.0, 8.0))
            img += 0.18 * rng.random(img.shape)
        ax.imshow(img, cmap=style.get("cmap", "magma"))
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        if idx < len(labels):
            ax.text(0.03, 0.92, labels[idx], transform=ax.transAxes, color="white", fontsize=7, fontweight="bold", ha="left", va="top")
        if style.get("scale_bar", True):
            ax.plot([0.68, 0.92], [0.88, 0.88], transform=ax.transAxes, color="white", lw=2.0)
            ax.text(0.80, 0.82, style.get("scale_label", "demo"), transform=ax.transAxes, color="white", fontsize=6, ha="center", va="top")
    return fig, list(axes.ravel())


def render_asymmetric_hero(spec: dict[str, Any]):
    style = spec.get("style", {})
    panels = spec["panels"]
    fig = plt.figure(figsize=style.get("figsize", [7.2, 5.6]))
    gs = fig.add_gridspec(3, 4, hspace=0.34, wspace=0.34)
    slots = [
        gs[:2, :2],
        gs[0, 2:],
        gs[1, 2:],
        gs[2, :2],
        gs[2, 2:],
    ]
    axes = []
    for idx, panel in enumerate(panels[: len(slots)]):
        ax = fig.add_subplot(slots[idx])
        draw_on_existing(ax, {**panel, "style": {**style, **panel.get("style", {})}}, panel["template"])
        ax.set_title(panel.get("title", ""), fontsize=9, loc="left")
        add_panel_label(ax, chr(ord("a") + idx))
        axes.append(ax)
    if style.get("shared_legend"):
        make_shared_legend(fig, axes, loc=style.get("legend_loc", "upper center"))
    return fig, axes


def render_multi_panel(spec: dict[str, Any]):
    style = spec.get("style", {})
    panels = spec["panels"]
    if style.get("layout") == "asymmetric":
        return render_asymmetric_hero(spec)
    fig = plt.figure(figsize=style.get("figsize", [7.2, 5.2]))
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.32)
    axes = []
    for idx, panel in enumerate(panels[:4]):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        mini = {**panel, "style": {**spec.get("style", {}), **panel.get("style", {}), "figsize": [3, 2]}}
        if panel["template"] == "grouped_bar":
            draw_on_existing(ax, mini, "grouped_bar")
        elif panel["template"] == "line_trend":
            draw_on_existing(ax, mini, "line_trend")
        elif panel["template"] == "heatmap":
            draw_on_existing(ax, mini, "heatmap")
        elif panel["template"] == "scatter":
            draw_on_existing(ax, mini, "scatter")
        ax.set_title(panel.get("title", ""), fontsize=9)
        add_panel_label(ax, chr(ord("a") + idx))
        axes.append(ax)
    return fig, axes


def draw_on_existing(ax, spec: dict[str, Any], kind: str) -> None:
    data = spec["data"]
    colors = choose_colors(spec, 8)
    if kind == "grouped_bar":
        categories = data["categories"]
        values = np.asarray(data["series"][0]["values"], dtype=float)
        ax.bar(np.arange(len(categories)), values, color=colors[: len(categories)], edgecolor=PALETTE["ink"], linewidth=0.6)
        ax.set_xticks(np.arange(len(categories)))
        ax.set_xticklabels(categories, rotation=30, ha="right", fontsize=7)
        ax.set_ylabel(data.get("ylabel", "Value"), fontsize=7)
        tighten_ylim(ax, values)
    elif kind == "line_trend":
        x = np.asarray(data["x"], dtype=float)
        for item, color in zip(data["series"], colors):
            ax.plot(x, item["values"], color=color, lw=1.2, marker="o", ms=2.5, label=item["name"])
        ax.legend(fontsize=6)
    elif kind == "heatmap":
        matrix = np.asarray(data["matrix"], dtype=float)
        ax.imshow(matrix, aspect="auto", cmap=spec.get("style", {}).get("cmap", "magma"))
        ax.set_xticks([])
        ax.set_yticks([])
    elif kind == "scatter":
        ax.scatter(data["x"], data["y"], color=colors[0], s=25, alpha=0.8, edgecolors="white", linewidths=0.5)
        ax.set_xlabel(data.get("xlabel", "x"), fontsize=7)
        ax.set_ylabel(data.get("ylabel", "y"), fontsize=7)
    elif kind == "log_bar":
        categories = data["categories"]
        values = np.asarray(data["values"], dtype=float)
        ax.bar(np.arange(len(categories)), values, color=colors[: len(categories)], edgecolor=PALETTE["ink"], linewidth=0.6)
        ax.set_yscale("log")
        ax.set_xticks(np.arange(len(categories)))
        ax.set_xticklabels(categories, rotation=30, ha="right", fontsize=7)
        ax.set_ylabel(data.get("ylabel", "Value"), fontsize=7)
    elif kind == "ablation_barh":
        labels = data["labels"]
        values = np.asarray(data["values"], dtype=float)
        ax.barh(np.arange(len(labels)), values, color=colors[0], alpha=0.65, edgecolor=PALETTE["ink"], linewidth=0.6)
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel(data.get("xlabel", "Score"), fontsize=7)
        ax.invert_yaxis()
    elif kind == "threshold_curve":
        draw_on_existing(ax, spec, "line_trend")
    elif kind == "confusion_heatmap":
        draw_on_existing(ax, spec, "heatmap")
    elif kind == "distribution":
        groups = data["groups"]
        values = [np.asarray(g["values"], dtype=float) for g in groups]
        ax.boxplot(values, patch_artist=True, showfliers=False)
        ax.set_xticklabels([g["name"] for g in groups], rotation=30, ha="right", fontsize=7)
        ax.set_ylabel(data.get("ylabel", "Value"), fontsize=7)
    elif kind == "forest":
        labels = data["labels"]
        estimates = np.asarray(data["estimates"], dtype=float)
        lows = np.asarray(data["ci_low"], dtype=float)
        highs = np.asarray(data["ci_high"], dtype=float)
        y = np.arange(len(labels))[::-1]
        ax.hlines(y, lows, highs, color=colors[0], lw=1.3)
        ax.scatter(estimates, y, color=colors[0], s=18)
        ax.axvline(spec.get("style", {}).get("reference", 0.0), color=PALETTE["neutral"], ls="--", lw=0.7)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=7)
    elif kind == "image_plate":
        ax.set_facecolor("black")
        x = np.linspace(-1, 1, 100)
        y = np.linspace(-1, 1, 75)
        xx, yy = np.meshgrid(x, y)
        img = np.exp(-(xx**2 + yy**2) * 5)
        ax.imshow(img, cmap=spec.get("style", {}).get("cmap", "magma"))
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)


RENDERERS = {
    "grouped_bar": render_grouped_bar,
    "line_trend": render_line_trend,
    "heatmap": render_heatmap,
    "scatter": render_scatter,
    "radar": render_radar,
    "distribution": render_distribution,
    "forest": render_forest,
    "multi_panel": render_multi_panel,
    "log_bar": render_log_bar,
    "ablation_barh": render_ablation_barh,
    "threshold_curve": render_threshold_curve,
    "confusion_heatmap": render_confusion_heatmap,
    "asymmetric_hero": render_asymmetric_hero,
    "image_plate": render_image_plate,
}


def write_qa(spec: dict[str, Any], out_base: Path, formats: list[str]) -> None:
    audit = spec.get("audit", {})
    template = spec.get("template", "unknown")
    warnings = validate_spec(spec, template if template in RENDERERS else str(template))
    if template == "radar":
        warnings.append("radar charts can overstate area; confirm axis scaling and caption wording")
    if "demo inline data" in str(audit.get("source_data", "")):
        warnings.append("demo data is not manuscript evidence")
    checks = [
        ("figure_id_recorded", bool(spec.get("figure_id"))),
        ("claim_recorded", bool(spec.get("claim"))),
        ("caption_recorded", bool(spec.get("caption"))),
        ("source_data_recorded", bool(audit.get("source_data") or spec.get("data", {}).get("source"))),
        ("script_or_notebook_recorded", bool(audit.get("script_or_notebook"))),
        ("svg_export_requested", "svg" in formats),
        ("template_validation_clean", not warnings),
        *[(f"output_{fmt}_exists", out_base.with_suffix(f".{fmt}").exists()) for fmt in formats],
    ]
    lines = [
        "# Nature-Style Figure QA",
        "",
        f"- Figure ID: {spec.get('figure_id', 'unknown')}",
        f"- Template: {spec.get('template', 'unknown')}",
        f"- Claim: {spec.get('claim', 'not recorded')}",
        f"- Source data: {audit.get('source_data') or spec.get('data', {}).get('source', 'not recorded')}",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for name, ok in checks:
        lines.append(f"| {name} | {'pass' if ok else 'review'} |")
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(["", "## Caption", "", spec.get("caption", "Caption not provided.")])
    out_base.with_suffix(".qa.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_spec(spec: dict[str, Any], out: Path, formats: list[str], qa_report: bool) -> None:
    style = spec.get("style", {})
    apply_style(font_size=float(style.get("font_size", 9)), axes_linewidth=float(style.get("axes_linewidth", 1.0)))
    template = spec["template"]
    if template not in RENDERERS:
        raise SystemExit(f"Unknown template {template!r}; available: {', '.join(RENDERERS)}")
    fig, axes = RENDERERS[template](spec)
    if spec.get("title") and not style.get("hide_title", False):
        fig.suptitle(spec["title"], fontsize=float(style.get("title_size", 11)), y=0.995)
    for ax in axes:
        ax.tick_params(labelsize=float(style.get("tick_size", 8)))
    finalize_figure(fig, out, formats, dpi=int(style.get("dpi", 300)))
    plt.close(fig)
    if qa_report:
        write_qa(spec, out, formats)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Nature-style thesis figure templates from JSON specs.")
    parser.add_argument("--spec", required=True, type=Path, help="Path to a figure spec JSON file.")
    parser.add_argument("--out", required=True, type=Path, help="Output base path without extension.")
    parser.add_argument("--formats", default="svg,pdf,png", help="Comma-separated formats: svg,pdf,png.")
    parser.add_argument("--qa-report", action="store_true", help="Write a Markdown QA report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec = load_json(args.spec)
    formats = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
    render_spec(spec, args.out.with_suffix(""), formats, args.qa_report)


if __name__ == "__main__":
    main()
