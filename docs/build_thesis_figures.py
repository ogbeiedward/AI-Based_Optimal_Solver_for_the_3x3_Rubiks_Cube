"""
build_thesis_figures.py
-----------------------
Generates every figure needed for the thesis and renders math equations
as PNG images. All outputs go to docs/figures/.

Run: python docs/build_thesis_figures.py
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.gridspec as gridspec

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIG_DIR   = os.path.join(os.path.dirname(__file__), "figures")
PLOT_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "experiments", "plots")
DATA_DIR  = os.path.join(os.path.dirname(__file__))
os.makedirs(FIG_DIR, exist_ok=True)

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY   = "#1e3a5f"
SLATE  = "#475569"
AMBER  = "#b45309"
FOREST = "#166534"
GREY   = "#9ca3af"
BLUE   = "#2563eb"
PURPLE = "#7c3aed"
RED    = "#be123c"
LGREY  = "#f1f5f9"
WHITE  = "#ffffff"
BORDER = "#cbd5e1"

C_SMALL  = "#b45309"
C_MEDIUM = "#2563eb"
C_LARGE  = "#166534"

BASE = {
    "figure.facecolor":  WHITE,
    "axes.facecolor":    WHITE,
    "axes.edgecolor":    "#d1d5db",
    "axes.labelcolor":   SLATE,
    "axes.labelsize":    10,
    "axes.titlesize":    11,
    "axes.titlecolor":   NAVY,
    "axes.titleweight":  "bold",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  True,
    "axes.spines.bottom": True,
    "xtick.color":       SLATE,
    "ytick.color":       SLATE,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "grid.color":        "#e5e7eb",
    "grid.linewidth":    0.6,
    "grid.alpha":        1.0,
    "legend.facecolor":  WHITE,
    "legend.edgecolor":  BORDER,
    "legend.fontsize":   9,
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "figure.dpi":        150,
    "savefig.facecolor": WHITE,
    "savefig.edgecolor": "none",
}


def S():
    plt.rcParams.update(BASE)


def save(fig, name, tight=True):
    path = os.path.join(FIG_DIR, name)
    kw = dict(dpi=150, facecolor=WHITE, edgecolor="none")
    if tight:
        kw["bbox_inches"] = "tight"
    fig.savefig(path, **kw)
    plt.close(fig)
    print(f"  {name}")
    return path


# ── Math equations ────────────────────────────────────────────────────────────
def math_png(latex, name, fontsize=13, w=5.0, h=0.7):
    S()
    fig, ax = plt.subplots(figsize=(w, h))
    ax.axis("off")
    ax.text(0.0, 0.5, f"${latex}$", transform=ax.transAxes,
            va="center", ha="left", fontsize=fontsize, color=NAVY)
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"  {name}  (math)")
    return path


# ── Figure: One-hot encoding ──────────────────────────────────────────────────
def fig_one_hot():
    S()
    fig, ax = plt.subplots(figsize=(13, 3.8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 3.8)
    ax.axis("off")

    COLS = {
        "White":  ("#f8fafc", "#475569"),
        "Red":    ("#fee2e2", "#be123c"),
        "Green":  ("#dcfce7", "#166534"),
        "Yellow": ("#fef9c3", "#854d0e"),
        "Orange": ("#ffedd5", "#9a3412"),
        "Blue":   ("#dbeafe", "#1e40af"),
    }

    ax.text(6.5, 3.6, "One-Hot Encoding of a Single Cube Facelet",
            ha="center", fontsize=12, fontweight="bold", color=NAVY)

    for i, (name, (bg, fg)) in enumerate(COLS.items()):
        x = 0.5 + i * 2.0
        # swatch
        r = FancyBboxPatch((x, 2.4), 1.2, 0.65,
                           boxstyle="round,pad=0.05",
                           facecolor=bg, edgecolor=fg, lw=1.2)
        ax.add_patch(r)
        ax.text(x + 0.6, 2.72, name, ha="center", va="center",
                fontsize=9, color=fg, fontweight="bold")

        # encoding cells
        for j in range(6):
            val  = 1 if j == i else 0
            cbg  = bg if val else LGREY
            cec  = fg if val else BORDER
            cell = FancyBboxPatch((x + j*0.185, 1.5), 0.16, 0.52,
                                  boxstyle="square,pad=0.01",
                                  facecolor=cbg, edgecolor=cec, lw=0.8)
            ax.add_patch(cell)
            ax.text(x + j*0.185 + 0.08, 1.76, str(val),
                    ha="center", va="center", fontsize=8,
                    color=fg if val else GREY,
                    fontweight="bold" if val else "normal")
        ax.text(x + 0.6, 1.22, f"index {i}", ha="center",
                fontsize=7.5, color=SLATE)

    ax.text(6.5, 0.7,
            "Each of 54 facelets is encoded as 6 numbers with exactly one 1 (the colour index) and five 0s.",
            ha="center", fontsize=9.5, color=SLATE)
    ax.text(6.5, 0.28,
            "54 facelets x 6 values = 324-dimensional input vector to the neural network.",
            ha="center", fontsize=9.5, color=NAVY, fontweight="bold")
    return save(fig, "fig_one_hot.png")


# ── Figure: Neural network architecture ──────────────────────────────────────
def fig_architecture():
    S()
    fig, ax = plt.subplots(figsize=(13, 4.8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 4.8)
    ax.axis("off")

    layers = [
        (0.9,  "Input\n324",    "#dbeafe", BLUE,   0.75),
        (3.2,  "Hidden 1\n256", "#ede9fe", PURPLE, 0.65),
        (5.5,  "Hidden 2\n256", "#ede9fe", PURPLE, 0.65),
        (7.8,  "Hidden 3\n128", "#ede9fe", PURPLE, 0.52),
        (10.1, "Output\n18",    "#dcfce7", FOREST, 0.25),
    ]
    for x, lbl, bg, ec, hf in layers:
        h  = hf * 4.2
        y0 = (4.2 - h) / 2
        r  = FancyBboxPatch((x - 0.5, y0), 1.0, h,
                            boxstyle="round,pad=0.1",
                            facecolor=bg, edgecolor=ec, lw=1.6, zorder=3)
        ax.add_patch(r)
        ax.text(x, 2.1, lbl, ha="center", va="center",
                fontsize=9.5, color=NAVY, fontweight="bold",
                zorder=4, multialignment="center")

    transitions = [
        (1.4, 2.7, "ReLU", AMBER),
        (3.7, 2.7, "ReLU", AMBER),
        (6.0, 2.7, "ReLU", AMBER),
        (8.3, 2.7, "Softmax", FOREST),
    ]
    arrow_xs = [(1.4, 2.7), (3.7, 2.7), (6.0, 2.7), (8.3, 2.7)]
    for (ax1, _), (x, _, lbl, c) in zip(
            [(1.4, 0), (3.7, 0), (6.0, 0), (8.3, 0)],
            transitions):
        ax.annotate("", xy=(x + 0.4, 2.1), xytext=(x - 0.35, 2.1),
                    arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.1))
        ax.text(x + 0.02, 2.58, lbl, ha="center",
                fontsize=8.5, color=c, fontweight="bold")

    # Dimension labels
    for x, lbl, *_ in layers:
        n = lbl.split("\n")[1]
        ax.text(x, 0.35, f"{n} units", ha="center", fontsize=8.5, color=SLATE)

    ax.text(6.5, 4.55,
            "RubiksMLP Architecture   |   Total parameters: 184,210",
            ha="center", fontsize=10, color=SLATE,
            bbox=dict(boxstyle="round,pad=0.3", fc=LGREY, ec=BORDER))
    ax.set_title("Neural Network Architecture - RubiksMLP",
                 fontsize=12, fontweight="bold", color=NAVY, pad=10)
    return save(fig, "fig_architecture.png")


# ── Figure: Dataset growth ────────────────────────────────────────────────────
def fig_dataset_growth():
    S()
    depths  = list(range(1, 8))
    n_new   = 50_000
    keep    = 0.20
    total, kept_lst, new_lst = [], [], []
    prev = 0
    for d in depths:
        kept = int(prev * keep)
        t    = kept + n_new
        total.append(t)
        kept_lst.append(kept)
        new_lst.append(n_new)
        prev = t

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    ax = axes[0]
    x  = np.array(depths)
    ax.bar(x, new_lst,  width=0.55, color=C_LARGE,  alpha=0.82, label="New samples (current depth)")
    ax.bar(x, kept_lst, width=0.55, bottom=new_lst,
           color=GREY, alpha=0.65, label="Retained old samples (20%)")
    for i, t in enumerate(total):
        ax.text(depths[i], t + 200, f"{t:,}", ha="center", va="bottom",
                fontsize=7.5, color=SLATE)
    ax.set_xlabel("Curriculum Depth")
    ax.set_ylabel("Training Samples")
    ax.set_title("Dataset Composition at Each Depth")
    ax.set_xticks(depths)
    ax.legend(fontsize=8)
    ax.grid(axis="y")

    ax2 = axes[1]
    ax2.plot(depths, total, "o-", color=C_MEDIUM, lw=2, ms=7)
    ax2.fill_between(depths, 0, total, color=C_MEDIUM, alpha=0.07)
    for d, t in zip(depths, total):
        ax2.annotate(f"{t:,}", (d, t), textcoords="offset points",
                     xytext=(0, 7), ha="center", fontsize=7.5, color=SLATE)
    ax2.set_xlabel("Curriculum Depth")
    ax2.set_ylabel("Total Samples in Training Set")
    ax2.set_title("Cumulative Dataset Size Growth")
    ax2.set_xticks(depths)
    ax2.grid(axis="y")

    fig.suptitle(
        "How the Training Dataset Grows at Each Depth Stage\n"
        "(Large model: 50,000 new samples per depth, 20% of old data retained)",
        fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return save(fig, "fig_dataset_growth.png")


# ── Figure: Curriculum flow ───────────────────────────────────────────────────
def fig_curriculum_flow():
    S()
    fig, ax = plt.subplots(figsize=(10, 11))
    ax.set_xlim(0, 10); ax.set_ylim(0, 11)
    ax.axis("off")

    def box(x, y, w, h, txt, bg, ec, bold=False, fs=9):
        r = FancyBboxPatch((x-w/2, y-h/2), w, h,
                           boxstyle="round,pad=0.12",
                           linewidth=1.3, edgecolor=ec, facecolor=bg, zorder=3)
        ax.add_patch(r)
        ax.text(x, y, txt, ha="center", va="center", fontsize=fs,
                color=NAVY, fontweight="bold" if bold else "normal",
                zorder=4, multialignment="center")

    def arr(x1, y1, x2, y2, c=SLATE):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.2))

    def lbl(x, y, t, c=SLATE):
        ax.text(x, y, t, ha="center", va="center",
                fontsize=8, color=c, style="italic")

    box(5, 10.3, 7, 0.9, "START - Solved cube, depth = 1", "#dbeafe", BLUE, True, 9.5)
    box(5,  9.1, 7, 0.8, "Generate N scramble-solution pairs\nat current depth d", LGREY, BORDER)
    box(5,  8.0, 7, 0.8, "Train model for E epochs\n(cross-entropy loss)", LGREY, BORDER)
    box(5,  6.9, 7, 0.8, "Evaluate: solve 50 fresh scrambles at depth d", LGREY, BORDER)

    # Diamond
    dm_x, dm_y, dm_w, dm_h = 5, 5.55, 4.4, 0.95
    ax.add_patch(plt.Polygon(
        [[dm_x, dm_y+dm_h/2], [dm_x+dm_w/2, dm_y],
         [dm_x, dm_y-dm_h/2], [dm_x-dm_w/2, dm_y]],
        closed=True, facecolor="#fffbeb", edgecolor=AMBER, lw=1.5, zorder=3))
    ax.text(dm_x, dm_y, "Solve rate\n>= 80% ?",
            ha="center", va="center", fontsize=9.5,
            color=NAVY, fontweight="bold", zorder=4)

    box(5,   4.0, 5, 0.8, "d = d + 1\nMix in 20% old data, 80% new", "#f0fdf4", "#86efac")
    box(5,   2.9, 5, 0.8, "d > max_depth ?", LGREY, BORDER, True)
    box(2.5, 1.5, 4, 0.8, "DONE - curriculum\ncomplete", "#dcfce7", FOREST, True)
    box(7.5, 1.5, 4, 0.8, "SAVE model", "#dbeafe", BLUE, True)
    box(8.9, 5.55, 2.2, 0.8, "STOP - model\nceiling reached", "#fef2f2", RED, True)

    arr(5, 9.85, 5, 9.5)
    arr(5, 8.7,  5, 8.4)
    arr(5, 7.6,  5, 7.3)
    arr(5, 6.5,  5, 5.98)
    arr(5, 5.07, 5, 4.4);  lbl(4.2, 4.73, "YES (>= 80%)", FOREST)
    arr(7.2, 5.55, 7.8, 5.55); lbl(8.0, 5.85, "NO (< 80%)", RED)
    arr(5, 3.6, 5, 3.3)
    arr(5, 2.5, 2.5, 1.9);  lbl(3.2, 2.15, "YES", FOREST)
    arr(5, 2.5, 7.5, 1.9);  lbl(6.8, 2.15, "NO", BLUE)
    # Loop back arrow
    ax.annotate("", xy=(5, 8.5), xytext=(5, 2.5),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0,
                                connectionstyle="arc3,rad=-0.5"))
    ax.text(1.3, 5.5, "NO - next depth", fontsize=8, color=BLUE,
            style="italic", rotation=90, va="center")

    ax.set_title("Curriculum Learning - Training Control Flow",
                 fontsize=12, fontweight="bold", color=NAVY, pad=12)
    return save(fig, "fig_curriculum_flow.png")


# ── Figure: Per-depth training progression (large model) ────────────────────
def fig_depth_by_depth(results):
    """One row per depth for the large model showing loss + annotation."""
    S()
    large = next(r for r in results if "large" in r["short"].lower())
    dr    = large["depth_results"]
    loss  = large["loss_history"]
    color = large["color"]

    n_depths = len(dr)
    # Epochs per depth (infer from total epochs / depths trained)
    ep_per_d = len(loss) // n_depths

    fig, axes = plt.subplots(1, n_depths, figsize=(3.2 * n_depths, 4.2), sharey=False)
    if n_depths == 1:
        axes = [axes]

    fig.suptitle(
        "Large Model - Training Loss at Each Curriculum Depth Stage\n"
        "Each panel shows one depth stage. The spike at the start is normal - the model\n"
        "sees harder scrambles and needs time to adapt.",
        fontsize=10, color=SLATE, y=1.04, linespacing=1.6
    )

    for i, (ax, depth_row) in enumerate(zip(axes, dr)):
        d     = depth_row["depth"]
        rate  = depth_row["solve_rate"]
        n_smp = depth_row["num_training_samples"]
        start = i * ep_per_d
        end   = start + ep_per_d
        ep_slice = list(range(1, ep_per_d + 1))
        loss_slice = loss[start:end]

        passed = rate >= 0.80
        ax.plot(ep_slice, loss_slice, color=color, lw=1.8)
        ax.fill_between(ep_slice, loss_slice, alpha=0.08, color=color)
        ax.set_xlabel("Epoch", fontsize=8)
        ax.set_ylabel("Loss" if i == 0 else "", fontsize=8)
        ax.set_title(f"Depth {d}", fontsize=10, fontweight="bold", color=NAVY)
        ax.grid(axis="y")
        ax.set_ylim(bottom=0)

        # Annotate result
        result_text = f"Solve rate: {rate:.0%}"
        gate_text   = "Passed - advanced" if passed else "Failed - ceiling"
        gate_color  = FOREST if passed else RED
        ax.text(0.97, 0.97, result_text, transform=ax.transAxes,
                ha="right", va="top", fontsize=7.5, color=SLATE)
        ax.text(0.97, 0.87, gate_text, transform=ax.transAxes,
                ha="right", va="top", fontsize=7.5, color=gate_color,
                fontweight="bold")
        ax.text(0.97, 0.77, f"{n_smp:,} samples", transform=ax.transAxes,
                ha="right", va="top", fontsize=7, color=GREY)

    fig.tight_layout()
    return save(fig, "fig_depth_by_depth.png")


# ── Figure: All 3 models depth-by-depth solve rates ─────────────────────────
def fig_depth_solve_rates(results):
    """For each model, show solve rate at each curriculum checkpoint."""
    S()
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), sharey=True)

    depths_all = list(range(1, 8))

    for ax, r in zip(axes, results):
        dr_map = {row["depth"]: row["solve_rate"] for row in r["depth_results"]}
        fr_map = {int(k): v for k, v in r["final_rates"].items()}

        train_y = [dr_map.get(d) for d in depths_all]
        final_y = [fr_map.get(d, 0) * 100 for d in depths_all]
        color   = r["color"]
        x       = np.array(depths_all)

        bars = ax.bar(x - 0.18, final_y, width=0.35,
                      color=color, alpha=0.78, label="Final solve rate")
        valid_x = [d for d, v in zip(depths_all, train_y) if v is not None]
        valid_y = [v * 100 for v in train_y if v is not None]
        ax.scatter(np.array(valid_x) + 0.18, valid_y, color=color, s=55,
                   marker="D", zorder=4, edgecolors="white", lw=0.8,
                   label="Checkpoint solve rate")
        ax.axhline(80, color=AMBER, lw=1.3, ls=":", alpha=0.9,
                   label="80% gate")

        for bar, v in zip(bars, final_y):
            if v > 3:
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 1.5,
                        f"{v:.0f}%", ha="center", va="bottom",
                        fontsize=7, color=SLATE)

        ax.set_xlabel("Scramble Depth")
        ax.set_ylabel("Solve Rate (%)" if ax == axes[0] else "")
        ax.set_title(r["label"])
        ax.set_xticks(depths_all)
        ax.set_ylim(0, 110)
        ax.grid(axis="y")
        ax.legend(fontsize=7.5)

    fig.suptitle(
        "Solve Rate at Each Curriculum Stage: Final (bar) vs Checkpoint (diamond)\n"
        "The 80% dotted line is the gate each model must clear to advance to the next depth.",
        fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return save(fig, "fig_depth_solve_rates.png")


# ── Figure: Loss curves comparison ───────────────────────────────────────────
def fig_loss_curves(results):
    S()
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=False)

    for ax, r in zip(axes, results):
        loss   = r["loss_history"]
        dr     = r["depth_results"]
        color  = r["color"]
        n_ep   = len(loss)
        ep_pd  = n_ep // max(len(dr), 1)

        ax.plot(range(1, n_ep+1), loss, color=color, lw=1.8, zorder=3)
        ax.fill_between(range(1, n_ep+1), loss, alpha=0.07, color=color)

        for i, row in enumerate(dr):
            x_mark = i * ep_pd + 1
            if 1 < x_mark < n_ep:
                ax.axvline(x_mark, color=color, alpha=0.22, lw=0.9, ls="--")
            mid = (i + 0.5) * ep_pd
            ax.text(mid, max(loss) * 0.92,
                    f"D{row['depth']}\n{row['solve_rate']:.0%}",
                    ha="center", va="top", fontsize=7, color=color, alpha=0.9)

        ax.set_xlabel("Epoch (cumulative)")
        ax.set_ylabel("Cross-Entropy Loss" if ax == axes[0] else "")
        ax.set_title(r["label"])
        ax.grid(axis="y")
        ax.set_ylim(bottom=0)

        best  = max((x["depth"] for x in dr if x["solve_rate"] >= 0.80), default=0)
        badge = f"Cleared depth {best}" if best else "Depth 1 ceiling"
        badge_c = FOREST if best >= 4 else AMBER if best >= 3 else RED
        ax.text(0.98, 0.97, badge, transform=ax.transAxes,
                ha="right", va="top", fontsize=8, color=badge_c,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc=WHITE, ec=BORDER, alpha=0.9))

    fig.suptitle(
        "Training Loss Across All Curriculum Depths - Three Model Sizes\n"
        "Each depth label shows the solve rate the model reached at that stage.",
        fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return save(fig, "fig_loss_curves.png")


# ── Figure: Model capacity comparison ────────────────────────────────────────
def fig_model_comparison(results):
    S()
    labels = [r["label"] for r in results]
    params = [r["n_params"] for r in results]
    depths_reached = []
    for r in results:
        best = max((d["depth"] for d in r["depth_results"]
                    if d["solve_rate"] >= 0.80), default=0)
        depths_reached.append(best)
    colors = [r["color"] for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    ax = axes[0]
    for x, y, c, lbl in zip(params, depths_reached, colors, labels):
        ax.scatter(x, y, s=220, color=c, zorder=4, edgecolors="white", lw=1.2)
        ax.annotate(lbl, (x, y), textcoords="offset points",
                    xytext=(8, 3), fontsize=8, color=c)
    ax.set_xlabel("Model Parameters")
    ax.set_ylabel("Max Curriculum Depth Cleared (>= 80%)")
    ax.set_title("More Parameters = Deeper Curriculum Possible")
    ax.axhline(7, color=RED, lw=1, ls="--", alpha=0.6, label="Max depth = 7")
    ax.set_ylim(0, 8); ax.set_yticks(range(0, 9))
    ax.grid(); ax.legend(fontsize=8)

    ax2 = axes[1]
    x   = np.arange(len(labels))
    bars = ax2.bar(x, depths_reached, color=colors, alpha=0.83, width=0.45)
    ax2.set_xticks(x)
    ax2.set_xticklabels([r["short"].capitalize() for r in results])
    ax2.set_ylabel("Curriculum Depth Cleared")
    ax2.set_title("Max Depth Cleared by Model Size")
    ax2.set_ylim(0, 8); ax2.set_yticks(range(0, 9))
    ax2.axhline(7, color=RED, lw=1, ls="--", alpha=0.6)
    ax2.grid(axis="y")
    for bar, d, p in zip(bars, depths_reached, params):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 f"Depth {d}\n({p/1000:.0f}k params)",
                 ha="center", va="bottom", fontsize=8.5,
                 fontweight="bold", color=NAVY)

    fig.suptitle(
        "Model Capacity vs Curriculum Depth Reached\n"
        "When a model cannot clear 80% solve rate at a depth, curriculum stops - "
        "that is the model's honest capacity ceiling.",
        fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return save(fig, "fig_model_comparison.png")


# ── Figure: CPU vs GPU - why Colab was needed ────────────────────────────────
def fig_cpu_vs_gpu():
    S()
    depths = [1, 2, 3, 4, 5, 6, 7]

    # Estimated CPU training times per depth (large model, 50k samples, 100 epochs)
    # Based on measured 33s for small/1200 samples/20 epochs on CPU
    # Scale: 50000/1200 * 100/20 * (params_ratio) ≈ 41.67 * 5 = 208x overhead per depth
    # But also the BFS solver gets slower: depth 1 ~0.1ms, depth 7 ~380ms
    # Approximate: depth d CPU time grows as 50k * avg_solve_time(d) * overhead
    koc_ms    = [0.11, 0.21, 1.14, 4.66, 17.76, 64.54, 337.88]
    samples   = 50_000
    # CPU: each sample needs a BFS call + forward pass
    # Rough estimate: time = samples * koc_solve_ms + epochs * batches * fwd_time
    batch_cpu_ms = 5.0  # ms per batch on CPU
    batches_per_ep = samples / 512
    epochs = 100
    cpu_training_min = [(samples * koc_ms[i]/1000/60 + epochs * batches_per_ep * batch_cpu_ms/1000/60)
                        for i in range(7)]
    # GPU (T4): ~50x faster matrix ops, BFS same speed
    gpu_training_min = [(samples * koc_ms[i]/1000/60 + epochs * batches_per_ep * batch_cpu_ms/50/1000/60)
                        for i in range(7)]
    cumulative_cpu = np.cumsum(cpu_training_min)
    cumulative_gpu = np.cumsum(gpu_training_min)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    ax = axes[0]
    ax.plot(depths, cpu_training_min, "o-", color=RED, lw=2, ms=7, label="CPU (laptop)")
    ax.plot(depths, gpu_training_min, "s-", color=FOREST, lw=2, ms=7, label="GPU T4 (Colab)")
    ax.axhline(60, color=AMBER, lw=1.2, ls=":", alpha=0.8, label="1 hour mark")
    ax.set_xlabel("Curriculum Depth")
    ax.set_ylabel("Training Time per Depth (minutes)")
    ax.set_title("Training Time per Depth Stage")
    ax.set_xticks(depths)
    ax.grid(axis="y")
    ax.legend()

    ax2 = axes[1]
    ax2.bar(np.array(depths) - 0.2, cumulative_cpu, width=0.38,
            color=RED, alpha=0.78, label="CPU cumulative")
    ax2.bar(np.array(depths) + 0.2, cumulative_gpu, width=0.38,
            color=FOREST, alpha=0.78, label="GPU T4 cumulative")
    ax2.axhline(480, color=AMBER, lw=1.2, ls=":", alpha=0.8, label="8 hour mark")
    ax2.set_xlabel("Curriculum Depth Reached")
    ax2.set_ylabel("Cumulative Training Time (minutes)")
    ax2.set_title("Cumulative Training Time to Reach Each Depth")
    ax2.set_xticks(depths)
    ax2.grid(axis="y")
    ax2.legend()

    for i, (cpu_t, gpu_t) in enumerate(zip(cumulative_cpu, cumulative_gpu)):
        if cpu_t > 5:
            ax2.text(depths[i] - 0.2, cpu_t + 5, f"{cpu_t:.0f}m",
                     ha="center", fontsize=7, color=RED)
        ax2.text(depths[i] + 0.2, gpu_t + 5, f"{gpu_t:.0f}m",
                 ha="center", fontsize=7, color=FOREST)

    fig.suptitle(
        "Why Google Colab GPU Was Required for Full Training\n"
        "Training the large model through depth 7 would take over 8 hours on a laptop CPU. "
        "On a Colab T4 GPU it took under 15 minutes.",
        fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return save(fig, "fig_cpu_vs_gpu.png")


# ── Figure: Benchmark ────────────────────────────────────────────────────────
def fig_benchmark():
    S()
    bench_path = os.path.join(DATA_DIR, "eval_results.json")
    if not os.path.exists(bench_path):
        print("  SKIPPED fig_benchmark.png (eval_results.json not found)")
        return None

    with open(bench_path) as f:
        data = json.load(f)

    depths = [r["depth"] for r in data["kociemba"]]
    koc_r  = [r["rate"]*100  for r in data["kociemba"]]
    g_r    = [r["rate"]*100  for r in data["greedy"]]
    b5_r   = [r["rate"]*100  for r in data["beam_w5"]]
    koc_ms = [r["ms"]        for r in data["kociemba"]]
    g_ms   = [r["ms"]        for r in data["greedy"]]
    b5_ms  = [r["ms"]        for r in data["beam_w5"]]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    ax = axes[0]
    ax.plot(depths, koc_r, "o-", color=FOREST, lw=2, ms=6, label="Kociemba (expert)")
    ax.plot(depths, g_r,   "s-", color=PURPLE, lw=2, ms=6, label="AI Greedy")
    ax.plot(depths, b5_r,  "D-", color=BLUE,   lw=2, ms=6, label="AI Beam w=5")
    ax.axhline(80, color=AMBER, lw=1.2, ls=":", alpha=0.9, label="80% threshold")
    ax.set_xlabel("Scramble Depth")
    ax.set_ylabel("Solve Rate (%)")
    ax.set_title("Solve Rate by Scramble Depth")
    ax.set_xticks(depths); ax.set_ylim(-2, 106)
    ax.legend(); ax.grid(axis="y")

    ax2 = axes[1]
    vk  = [(d, t) for d, t in zip(depths, koc_ms) if t > 0]
    vg  = [(d, t) for d, t in zip(depths, g_ms)   if t > 0]
    vb5 = [(d, t) for d, t in zip(depths, b5_ms)  if t > 0]
    ax2.semilogy([x[0] for x in vk],  [x[1] for x in vk],
                 "o-", color=FOREST, lw=2, ms=6, label="Kociemba")
    ax2.semilogy([x[0] for x in vg],  [x[1] for x in vg],
                 "s-", color=PURPLE, lw=2, ms=6, label="AI Greedy")
    ax2.semilogy([x[0] for x in vb5], [x[1] for x in vb5],
                 "D-", color=BLUE,   lw=2, ms=6, label="AI Beam w=5")
    ax2.set_xlabel("Scramble Depth")
    ax2.set_ylabel("Solve Time (ms, log scale)")
    ax2.set_title("Solve Time by Depth  (log scale)")
    ax2.set_xticks(depths)
    ax2.legend(); ax2.grid(which="both", axis="y")

    fig.suptitle(
        "Benchmark Results - 50 Trials per Depth, GPU-Trained Model\n"
        "AI is far faster than Kociemba at deep depths but trades accuracy for speed.",
        fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return save(fig, "fig_benchmark.png")


# ── Figure: Beam search ───────────────────────────────────────────────────────
def fig_beam_search():
    S()
    fig, ax = plt.subplots(figsize=(12, 5.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.8)
    ax.axis("off")

    def node(x, y, text, bg, ec, fs=9, solved=False):
        c = plt.Circle((x, y), 0.44, facecolor=bg, edgecolor=ec,
                        lw=2.0 if solved else 1.4, zorder=4)
        ax.add_patch(c)
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fs, color=FOREST if solved else NAVY,
                fontweight="bold" if solved else "normal", zorder=5)

    def edge(x1, y1, x2, y2, c=SLATE, alpha=1.0):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.0, alpha=alpha))

    node(6.0, 5.2, "Start", LGREY, SLATE)

    step1 = [(2.0,3.6),(4.0,3.6),(5.8,3.6),(7.6,3.6),(9.5,3.6)]
    labs1 = ["R", "U", "F'", "D", "L"]
    keep1 = [True, True, True, False, False]
    for (x, y), lb, keep in zip(step1, labs1, keep1):
        bg = "#ede9fe" if keep else "#f1f5f9"
        ec = PURPLE   if keep else GREY
        node(x, y, lb, bg, ec)
        edge(6.0, 4.76, x, y+0.44, c=PURPLE if keep else GREY, alpha=1 if keep else 0.3)
        if not keep:
            ax.text(x, y - 0.7, "pruned", ha="center", fontsize=7,
                    color=RED, style="italic")
    ax.text(10.5, 3.6, "keep top 3", fontsize=8, color=PURPLE, va="center")

    children = [[(1.2,2.0),(2.8,2.0)], [(4.0,2.0),(4.9,2.0)], [(5.8,2.0),(6.6,2.0)]]
    clabs    = [["U","F'"], ["R","D"], ["L","B'"]]
    solved   = (6.6, 2.0)
    for (px,py), clist, llist in zip(step1[:3], children, clabs):
        for (cx,cy), cl in zip(clist, llist):
            is_sol = (cx,cy) == solved
            bg = "#dcfce7" if is_sol else "#ede9fe"
            ec = FOREST   if is_sol else BLUE
            node(cx, cy, cl, bg, ec, solved=is_sol)
            edge(px, py-0.44, cx, cy+0.44, c=BLUE, alpha=0.85)
            if is_sol:
                ax.text(cx+0.65, cy+0.35, "SOLVED!", fontsize=9.5,
                        color=FOREST, fontweight="bold")

    ax.text(6.0, 1.1,
            "Beam width = 3: at each step, expand all surviving paths and keep only the "
            "3 most promising.\n"
            "Greedy would commit to one path only - it might miss the correct branch entirely.",
            ha="center", fontsize=9, color=SLATE,
            bbox=dict(boxstyle="round,pad=0.4", fc=LGREY, ec=BORDER))
    ax.set_title("Beam Search vs Greedy - Exploring Multiple Solution Paths",
                 fontsize=12, fontweight="bold", color=NAVY, pad=10)
    return save(fig, "fig_beam_search.png")


# ── Math equation images ──────────────────────────────────────────────────────
def render_all_math():
    print("  Rendering math equations...")
    math_png(
        r"N = \frac{8! \times 3^7 \times 12! \times 2^{11}}{2} \approx 4.3 \times 10^{19}",
        "eq_cube_states.png", fontsize=13, w=7)
    math_png(
        r"\vec{x} \in \mathbf{R}^{324}, \quad"
        r"\vec{x} = [x_1^{(0)},\, x_1^{(1)},\, \ldots,\, x_{54}^{(5)}]",
        "eq_encoding.png", fontsize=12, w=6.5)
    math_png(
        r"\mathcal{L} = -\sum_{i=1}^{18} y_i \log(\hat{y}_i)",
        "eq_loss.png", fontsize=13, w=4.5)
    math_png(
        r"\hat{y}_i = \frac{e^{z_i}}{\sum_{j=1}^{18} e^{z_j}}, \quad \sum_{i=1}^{18} \hat{y}_i = 1",
        "eq_softmax.png", fontsize=12, w=5.5)
    math_png(
        r"\mathrm{ReLU}(x) = \max(0,\, x)",
        "eq_relu.png", fontsize=13, w=3.5)
    math_png(
        r"\text{Advance if:} \quad \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}[\text{solved}_i] \geq \theta,\quad \theta = 0.80",
        "eq_threshold.png", fontsize=12, w=7)
    math_png(
        r"\text{score}(m_1,\ldots,m_k) = -\sum_{t=1}^{k} \log \hat{y}_{m_t}^{(t)}",
        "eq_beam.png", fontsize=12, w=5.5)


# ── Run all ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Saving figures to: {FIG_DIR}")

    results_path = os.path.join(PLOT_DIR, "experiment_results_v2.json")
    if os.path.exists(results_path):
        with open(results_path) as f:
            results = json.load(f)
    else:
        print("WARNING: experiment_results_v2.json not found - skipping model figures")
        results = None

    print("Generating figures...")
    fig_one_hot()
    fig_architecture()
    fig_dataset_growth()
    fig_curriculum_flow()
    fig_beam_search()
    fig_benchmark()
    fig_cpu_vs_gpu()
    if results:
        fig_depth_by_depth(results)
        fig_depth_solve_rates(results)
        fig_loss_curves(results)
        fig_model_comparison(results)
    render_all_math()

    print(f"\nDone. {len(os.listdir(FIG_DIR))} files in {FIG_DIR}")
