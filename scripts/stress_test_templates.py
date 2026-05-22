"""
Legacy stress-test scaffold for the old function-based nature_plot_templates API.

The current workflow uses JSON figure specs rendered by:
skills/research-paper-figures/scripts/nature_plot_templates.py

Keep this file only as a historical note until it is rewritten against the
current JSON-spec renderer.
"""
raise SystemExit(
    "Legacy stress_test_templates.py is not compatible with the current JSON-spec "
    "renderer. Use skills/research-paper-figures/scripts/nature_plot_templates.py "
    "with examples/figure_specs/*.json instead."
)

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))

import traceback
import numpy as np
from nature_plot_templates import *

OUT = __import__('pathlib').Path("figures/stress_test")
OUT.mkdir(parents=True, exist_ok=True)

FAILED = []
PASSED = []

def t(name, fn):
    try:
        fn()
        PASSED.append(name)
        print(f"  PASS: {name}")
    except Exception as e:
        FAILED.append((name, str(e)))
        print(f"  FAIL: {name} — {e}")
        traceback.print_exc()


# ═══════════════════════════════════════════════
# 1. grouped_bar
# ═══════════════════════════════════════════════
print("\n=== grouped_bar ===")

def bar_long_labels():
    fig, ax = grouped_bar(
        ["Very Long Category Name A", "Even Longer Category Name B",
         "Extremely Long Unabbreviated Category C", "Short"],
        {"Series Alpha": [1, 2, 3, 4], "Series Beta": [2, 3, 1, 5]},
        xlabel="X axis label", ylabel="Y axis label")
    save_figure(fig, "bar_long_labels", output_dir=OUT)
t("bar_long_labels", bar_long_labels)

def bar_many_categories():
    fig, ax = grouped_bar(
        [f"Method_{i}" for i in range(15)],
        {f"Series_{j}": list(np.random.rand(15) * 10) for j in range(8)})
    save_figure(fig, "bar_many_categories", output_dir=OUT)
t("bar_many_categories", bar_many_categories)

def bar_extreme_values():
    fig, ax = grouped_bar(
        ["A", "B", "C"], {"S1": [1e-6, 1, 1e6]},
        errors={"S1": [1e-7, 0.5, 1e5]}, ylabel="Log-scale maybe?")
    save_figure(fig, "bar_extreme_values", output_dir=OUT)
t("bar_extreme_values", bar_extreme_values)

def bar_few_data():
    fig, ax = grouped_bar(["Only"], {"S1": [1.0]})
    save_figure(fig, "bar_few_data", output_dir=OUT)
t("bar_few_data", bar_few_data)

def bar_many_series():
    fig, ax = grouped_bar(
        ["A", "B"],
        {f"Series_{i}": [np.random.rand(), np.random.rand()] for i in range(20)})
    save_figure(fig, "bar_many_series", output_dir=OUT)
t("bar_many_series", bar_many_series)


# ═══════════════════════════════════════════════
# 2. line_trend
# ═══════════════════════════════════════════════
print("\n=== line_trend ===")

def line_long_labels():
    fig, ax = line_trend(
        np.linspace(0, 100, 30),
        {"Training Loss (cross-entropy with label smoothing)": np.random.rand(30),
         "Validation Loss (held-out test set)": np.random.rand(30)},
        xlabel="Training Epochs (logarithmically spaced)",
        ylabel="Cross-Entropy Loss Value (lower is better)")
    save_figure(fig, "line_long_labels", output_dir=OUT)
t("line_long_labels", line_long_labels)

def line_extreme_values():
    fig, ax = line_trend(
        np.linspace(0, 1, 50), {"A": np.logspace(-4, 4, 50)},
        log_scale=True, ylabel="Log-scale values")
    save_figure(fig, "line_extreme_values", output_dir=OUT)
t("line_extreme_values", line_extreme_values)

def line_few_points():
    fig, ax = line_trend([0, 1], {"S1": [0.5, 0.6]})
    save_figure(fig, "line_few_points", output_dir=OUT)
t("line_few_points", line_few_points)

def line_many_series():
    fig, ax = line_trend(
        np.linspace(0, 10, 20),
        {f"Series_{i:02d}": np.cumsum(np.random.randn(20)) for i in range(15)})
    save_figure(fig, "line_many_series", output_dir=OUT)
t("line_many_series", line_many_series)

def line_error_bands():
    fig, ax = line_trend(
        np.linspace(0, 50, 40),
        {"Model A": np.sin(np.linspace(0, 4*np.pi, 40)) + 2,
         "Model B": np.cos(np.linspace(0, 4*np.pi, 40)) + 2},
        errors={"Model A": np.abs(np.random.randn(40)*0.3),
                "Model B": np.abs(np.random.randn(40)*0.2)})
    save_figure(fig, "line_error_bands", output_dir=OUT)
t("line_error_bands", line_error_bands)


# ═══════════════════════════════════════════════
# 3. heatmap
# ═══════════════════════════════════════════════
print("\n=== heatmap ===")

def heatmap_small():
    fig, ax = heatmap(np.array([[0.1, 0.9], [0.3, 0.7]]),
                      row_labels=["R1", "R2"], col_labels=["C1", "C2"])
    save_figure(fig, "heatmap_small", output_dir=OUT)
t("heatmap_small", heatmap_small)

def heatmap_large():
    fig, ax = heatmap(np.random.rand(50, 50), cmap="viridis", annotate=False)
    save_figure(fig, "heatmap_large", output_dir=OUT)
t("heatmap_large", heatmap_large)

def heatmap_jet_rejected():
    try:
        heatmap(np.eye(3), cmap="jet")
    except ValueError:
        return  # expected
    raise AssertionError("jet should have been rejected")
t("heatmap_jet_rejected", heatmap_jet_rejected)

def heatmap_extreme():
    fig, ax = heatmap(np.array([[1e6, -1e6], [0, 0.5]]), cmap="RdBu_r")
    save_figure(fig, "heatmap_extreme", output_dir=OUT)
t("heatmap_extreme", heatmap_extreme)

def heatmap_long_labels():
    fig, ax = heatmap(
        np.random.rand(8, 8),
        row_labels=[f"Very Long Row Label {i}" for i in range(8)],
        col_labels=[f"Very Long Col Label {i}" for i in range(8)])
    save_figure(fig, "heatmap_long_labels", output_dir=OUT)
t("heatmap_long_labels", heatmap_long_labels)


# ═══════════════════════════════════════════════
# 4. scatter
# ═══════════════════════════════════════════════
print("\n=== scatter ===")

def scatter_basic():
    fig, ax = scatter(
        {"A": np.random.randn(100), "B": np.random.randn(100) + 1},
        {"A": np.random.randn(100), "B": np.random.randn(100) + 1},
        xlabel="Dim 1", ylabel="Dim 2")
    save_figure(fig, "scatter_basic", output_dir=OUT)
t("scatter_basic", scatter_basic)

def scatter_many_groups():
    fig, ax = scatter(
        {f"G{i:02d}": np.random.randn(50) + i*0.5 for i in range(15)},
        {f"G{i:02d}": np.random.randn(50) + i*0.3 for i in range(15)})
    save_figure(fig, "scatter_many_groups", output_dir=OUT)
t("scatter_many_groups", scatter_many_groups)

def scatter_dense():
    fig, ax = scatter(
        {"A": np.random.randn(5000), "B": np.random.randn(5000)},
        {"A": np.random.randn(5000), "B": np.random.randn(5000)},
        alpha=0.3, s=4)
    save_figure(fig, "scatter_dense", output_dir=OUT)
t("scatter_dense", scatter_dense)

def scatter_extreme():
    fig, ax = scatter(
        {"A": [0, 1e6, -1e6], "B": [1e-6, 1, 0.5]},
        {"A": [0, 1e6, -1e6], "B": [1e-6, 1, 0.5]})
    save_figure(fig, "scatter_extreme", output_dir=OUT)
t("scatter_extreme", scatter_extreme)


# ═══════════════════════════════════════════════
# 5. radar
# ═══════════════════════════════════════════════
print("\n=== radar ===")

def radar_basic():
    fig, ax = radar(
        ["Speed", "Accuracy", "Memory", "Throughput", "Latency"],
        {"Model A": [0.8, 0.9, 0.6, 0.7, 0.5],
         "Model B": [0.6, 0.7, 0.9, 0.5, 0.8]})
    save_figure(fig, "radar_basic", output_dir=OUT)
t("radar_basic", radar_basic)

def radar_many_dims():
    fig, ax = radar(
        [f"Metric_{i}" for i in range(20)],
        {"A": list(np.random.rand(20)), "B": list(np.random.rand(20))})
    save_figure(fig, "radar_many_dims", output_dir=OUT)
t("radar_many_dims", radar_many_dims)

def radar_long_labels():
    fig, ax = radar(
        ["Very Long Metric Name A", "Very Long Metric Name B",
         "Very Long Metric Name C", "Very Long Metric Name D", "Short"],
        {"Method": [0.8, 0.6, 0.9, 0.4, 0.7]})
    save_figure(fig, "radar_long_labels", output_dir=OUT)
t("radar_long_labels", radar_long_labels)


# ═══════════════════════════════════════════════
# 6. distribution
# ═══════════════════════════════════════════════
print("\n=== distribution ===")

def dist_violin():
    fig, ax = distribution(
        {"A": np.random.randn(200), "B": np.random.randn(200)+1,
         "C": np.random.randn(150)-0.5}, kind="violin")
    save_figure(fig, "dist_violin", output_dir=OUT)
t("dist_violin", dist_violin)

def dist_box():
    fig, ax = distribution(
        {"A": np.random.randn(200), "B": np.random.randn(200)+1,
         "C": np.random.randn(150)-0.5}, kind="box")
    save_figure(fig, "dist_box", output_dir=OUT)
t("dist_box", dist_box)

def dist_hist():
    fig, ax = distribution(
        {"A": np.random.randn(500), "B": np.random.randn(500)+1.5}, kind="hist")
    save_figure(fig, "dist_hist", output_dir=OUT)
t("dist_hist", dist_hist)

def dist_many_groups():
    fig, ax = distribution(
        {f"Group_{i:02d}": np.random.randn(100)+i*0.5 for i in range(15)},
        kind="box")
    save_figure(fig, "dist_many_groups", output_dir=OUT)
t("dist_many_groups", dist_many_groups)

def dist_extreme_outliers():
    fig, ax = distribution(
        {"Normal": np.random.randn(100),
         "Outliers": np.concatenate([np.random.randn(95), [20, -15, 30, -25]])},
        kind="box")
    save_figure(fig, "dist_extreme_outliers", output_dir=OUT)
t("dist_extreme_outliers", dist_extreme_outliers)


# ═══════════════════════════════════════════════
# 7. forest
# ═══════════════════════════════════════════════
print("\n=== forest ===")

def forest_basic():
    fig, ax = forest(
        ["Treatment A", "Treatment B", "Treatment C", "Placebo", "Control"],
        [0.3, -0.1, 0.5, 0.05, 0.0],
        [0.1, -0.3, 0.3, -0.1, -0.05],
        [0.5, 0.1, 0.7, 0.2, 0.05])
    save_figure(fig, "forest_basic", output_dir=OUT)
t("forest_basic", forest_basic)

def forest_many_rows():
    fig, ax = forest(
        [f"Subgroup_{i}" for i in range(30)],
        list(np.random.randn(30) * 0.5),
        list(np.random.randn(30) * 0.5 - 1),
        list(np.random.randn(30) * 0.5 + 1))
    save_figure(fig, "forest_many_rows", output_dir=OUT)
t("forest_many_rows", forest_many_rows)


# ═══════════════════════════════════════════════
# 8. multi_panel
# ═══════════════════════════════════════════════
print("\n=== multi_panel ===")

def multi_panel_basic():
    fig, axes = multi_panel([
        {"type": "bar", "data": {"groups": ["A","B","C"],
         "values": {"S1":[1,2,3],"S2":[2,3,1]}}},
        {"type": "line", "data": {"x": [0,1,2,3],
         "series": {"L1":[0,1,2,3],"L2":[3,2,1,0]}}},
        {"type": "scatter", "data": {"x": {"G":np.random.randn(50)},
         "y": {"G":np.random.randn(50)}}},
        {"type": "hist", "data": {"data": {"D": np.random.randn(200)}}},
    ])
    save_figure(fig, "multi_panel_basic", output_dir=OUT)
t("multi_panel_basic", multi_panel_basic)

def multi_panel_single():
    fig, axes = multi_panel([
        {"type": "bar", "data": {"groups": ["A","B"],
         "values": {"S1":[1,2]}}},
    ])
    save_figure(fig, "multi_panel_single", output_dir=OUT)
t("multi_panel_single", multi_panel_single)

def _make_panel_data(i):
    return {"type": "bar", "data": {
        "groups": [f"G{g}" for g in range(3)],
        "values": {f"S{j}": list(np.random.rand(3)) for j in range(2)}}}

def multi_panel_many():
    fig, axes = multi_panel([_make_panel_data(i) for i in range(9)])
    save_figure(fig, "multi_panel_many", output_dir=OUT)
t("multi_panel_many", multi_panel_many)


# ═══════════════════════════════════════════════
# 9. log_bar
# ═══════════════════════════════════════════════
print("\n=== log_bar ===")

def log_bar_basic():
    fig, ax = log_bar(["A","B","C","D","E"], [1e0, 1e1, 1e2, 1e3, 1e4])
    save_figure(fig, "log_bar_basic", output_dir=OUT)
t("log_bar_basic", log_bar_basic)

def log_bar_horizontal():
    fig, ax = log_bar(["Alpha","Beta","Gamma","Delta"],
                      [1e-2, 1, 1e2, 1e4], horizontal=True)
    save_figure(fig, "log_bar_horizontal", output_dir=OUT)
t("log_bar_horizontal", log_bar_horizontal)

def log_bar_many():
    fig, ax = log_bar([f"Item_{i}" for i in range(30)],
                      np.logspace(-3, 3, 30))
    save_figure(fig, "log_bar_many", output_dir=OUT)
t("log_bar_many", log_bar_many)

def log_bar_single():
    fig, ax = log_bar(["Only"], [1.0])
    save_figure(fig, "log_bar_single", output_dir=OUT)
t("log_bar_single", log_bar_single)


# ═══════════════════════════════════════════════
# 10. ablation_barh
# ═══════════════════════════════════════════════
print("\n=== ablation_barh ===")

def ablation_basic():
    fig, ax = ablation_barh(
        ["Full model", "- Component A", "- Component B", "- Component C", "- All"],
        0.70, [0.85, 0.78, 0.82, 0.72, 0.60])
    save_figure(fig, "ablation_basic", output_dir=OUT)
t("ablation_basic", ablation_basic)

def ablation_many():
    fig, ax = ablation_barh(
        [f"Ablation {i}" for i in range(20)],
        0.50, list(np.random.rand(20) * 0.6 + 0.2))
    save_figure(fig, "ablation_many", output_dir=OUT)
t("ablation_many", ablation_many)

def ablation_close_values():
    fig, ax = ablation_barh(
        ["A", "B", "C", "D"],
        0.800, [0.801, 0.799, 0.802, 0.798])
    save_figure(fig, "ablation_close_values", output_dir=OUT)
t("ablation_close_values", ablation_close_values)


# ═══════════════════════════════════════════════
# 11. threshold_curve
# ═══════════════════════════════════════════════
print("\n=== threshold_curve ===")

def threshold_basic():
    t = np.linspace(0, 1, 100)
    prec = t ** 0.5
    rec = 1 - t ** 2
    f1 = 2 * prec * rec / (prec + rec + 1e-12)
    fig, ax = threshold_curve(
        t, {"Precision": prec, "Recall": rec, "F1": f1},
        optimal_threshold=0.35)
    save_figure(fig, "threshold_basic", output_dir=OUT)
t("threshold_basic", threshold_basic)

def threshold_many_curves():
    fig, ax = threshold_curve(
        np.linspace(0, 1, 50),
        {f"Metric_{i}": np.random.rand(50) for i in range(12)})
    save_figure(fig, "threshold_many_curves", output_dir=OUT)
t("threshold_many_curves", threshold_many_curves)


# ═══════════════════════════════════════════════
# 12. confusion_heatmap
# ═══════════════════════════════════════════════
print("\n=== confusion_heatmap ===")

def confusion_basic():
    fig, ax = confusion_heatmap(
        np.array([[45, 2, 1], [3, 38, 4], [2, 5, 41]]),
        class_names=["Cat", "Dog", "Bird"])
    save_figure(fig, "confusion_basic", output_dir=OUT)
t("confusion_basic", confusion_basic)

def confusion_many_classes():
    cm = np.zeros((20, 20), dtype=int)
    for i in range(20):
        cm[i, i] = np.random.randint(20, 100)
        for j in range(3):
            k = (i + j + 1) % 20
            cm[i, k] = np.random.randint(0, 10)
    fig, ax = confusion_heatmap(
        cm, class_names=[f"Class_{i:02d}" for i in range(20)],
        normalize=False)
    save_figure(fig, "confusion_many_classes", output_dir=OUT)
t("confusion_many_classes", confusion_many_classes)

def confusion_imbalanced():
    fig, ax = confusion_heatmap(
        np.array([[100, 0, 0], [50, 5, 0], [30, 10, 2]]),
        class_names=["Majority", "Minority", "Rare"])
    save_figure(fig, "confusion_imbalanced", output_dir=OUT)
t("confusion_imbalanced", confusion_imbalanced)


# ═══════════════════════════════════════════════
# 13. asymmetric_hero
# ═══════════════════════════════════════════════
print("\n=== asymmetric_hero ===")

def hero_basic():
    fig, (ax_main, ax_side) = asymmetric_hero(
        main_data={"groups": ["A","B","C","D"],
                   "values": {"Ours":[0.85,0.78,0.92,0.65],
                              "BL":[0.72,0.70,0.81,0.65]}},
        side_data={"groups": ["A","B"],
                   "values": {"S1":[1,2], "S2":[2,1]}},
        main_type="bar", side_type="bar")
    save_figure(fig, "hero_basic", output_dir=OUT)
t("hero_basic", hero_basic)

def hero_line_main():
    x = np.linspace(0, 50, 30)
    fig, axes = asymmetric_hero(
        main_data={"x": x,
                   "series": {"Train": np.exp(-x/20)+np.random.randn(30)*0.05,
                              "Val": np.exp(-x/25)+0.1+np.random.randn(30)*0.05}},
        side_data={"data": {"A": np.random.randn(100),
                            "B": np.random.randn(100)+1}},
        main_type="line", side_type="hist")
    save_figure(fig, "hero_line_main", output_dir=OUT)
t("hero_line_main", hero_line_main)


# ═══════════════════════════════════════════════
# 14. image_plate
# ═══════════════════════════════════════════════
print("\n=== image_plate ===")

def image_plate_basic():
    fig, axes = image_plate(
        [np.random.rand(32, 32) for _ in range(8)],
        ncols=4, labels=[f"Sample {i}" for i in range(8)])
    save_figure(fig, "image_plate_basic", output_dir=OUT)
t("image_plate_basic", image_plate_basic)

def image_plate_many():
    fig, axes = image_plate(
        [np.random.rand(28, 28) for _ in range(50)], ncols=10)
    save_figure(fig, "image_plate_many", output_dir=OUT)
t("image_plate_many", image_plate_many)

def image_plate_single():
    fig, axes = image_plate(
        [np.random.rand(64, 64)], ncols=1, labels=["Single"])
    save_figure(fig, "image_plate_single", output_dir=OUT)
t("image_plate_single", image_plate_single)


# ═══════════════════════════════════════════════
# Results
# ═══════════════════════════════════════════════
print(f"\n{'='*60}")
total = len(PASSED) + len(FAILED)
print(f"RESULTS: {len(PASSED)} passed, {len(FAILED)} failed out of {total}")
if FAILED:
    print("\nFAILURES:")
    for name, err in FAILED:
        print(f"  {name}: {err[:120]}")
else:
    print("ALL TESTS PASSED")
print(f"{'='*60}")
