"""
gen_explainer.py
----------------
Generates the full layman-friendly project explanation PDF.

Steps:
  1. Run (or reload) curriculum training for three model sizes.
  2. Produce all figures following the project visual style guide.
  3. Assemble a polished, professionally typeset PDF.

Run from the project root:
    python docs/gen_explainer.py               # full run
    python docs/gen_explainer.py --skip-train  # reuse cached training data
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import torch

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Image as RLImage,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR  = os.path.join(ROOT, "docs", "figures")
PLOT_DIR = os.path.join(ROOT, "experiments", "plots")
RESULTS  = os.path.join(PLOT_DIR, "experiment_results_v2.json")
PDF_OUT  = os.path.join(ROOT, "docs", "Project_Explanation_Guide.pdf")
os.makedirs(FIG_DIR,  exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Color palette (muted, professional, white-background-only)
# ---------------------------------------------------------------------------
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

# Three model colours - distinct, muted
COL_SMALL  = "#b45309"   # amber
COL_MED    = "#2563eb"   # blue
COL_LARGE  = "#166534"   # forest green

# ---------------------------------------------------------------------------
# Matplotlib base style
# ---------------------------------------------------------------------------
BASE_STYLE = {
    "figure.facecolor": WHITE,
    "axes.facecolor":   WHITE,
    "axes.edgecolor":   "#d1d5db",
    "axes.labelcolor":  SLATE,
    "axes.labelsize":   10,
    "axes.titlesize":   11,
    "axes.titlecolor":  NAVY,
    "axes.titleweight": "bold",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "xtick.color":      SLATE,
    "ytick.color":      SLATE,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "grid.color":       "#e5e7eb",
    "grid.linewidth":   0.6,
    "grid.alpha":       1.0,
    "legend.facecolor": WHITE,
    "legend.edgecolor": BORDER,
    "legend.fontsize":  8.5,
    "font.family":      "DejaVu Sans",
    "font.size":        10,
    "figure.dpi":       150,
}


def apply_style():
    plt.rcParams.update(BASE_STYLE)


# ===========================================================================
# PART 1 - TRAINING
# ===========================================================================

EXPERIMENTS = [
    {
        "label":  "Small  (~42k params)",
        "short":  "small",
        "hidden": [128, 128],
        "samples": 1200,
        "epochs":  20,
        "color":   COL_SMALL,
    },
    {
        "label":  "Medium (~100k params)",
        "short":  "medium",
        "hidden": [256, 128],
        "samples": 2500,
        "epochs":  25,
        "color":   COL_MED,
    },
    {
        "label":  "Large  (~184k params)",
        "short":  "large",
        "hidden": [256, 256, 128],
        "samples": 4000,
        "epochs":  30,
        "color":   COL_LARGE,
    },
]

MAX_DEPTH  = 8
THRESHOLD  = 0.80
EVAL_TESTS = 50
SEED       = 42


class FlexMLP(torch.nn.Module):
    def __init__(self, hidden_sizes):
        super().__init__()
        from core.state_encoder import ENCODING_DIM, NUM_MOVES
        layers, in_d = [], ENCODING_DIM
        for h in hidden_sizes:
            layers += [torch.nn.Linear(in_d, h), torch.nn.ReLU()]
            in_d = h
        layers.append(torch.nn.Linear(in_d, NUM_MOVES))
        self.net = torch.nn.Sequential(*layers)

    def forward(self, x): return self.net(x)

    def predict_move(self, x):
        self.eval()
        with torch.no_grad():
            if x.dim() == 1: x = x.unsqueeze(0)
            p = torch.softmax(self.net(x), 1)
            i = torch.argmax(p, 1).item()
            return i, p[0, i].item()

    @property
    def n_params(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def run_training():
    """Train all three model sizes and return results dict."""
    from solvers.ai_solver import train_model, evaluate_solve_rate
    device = torch.device("cpu")
    all_results = []

    for cfg in EXPERIMENTS:
        print(f"\n{'='*55}")
        print(f"  {cfg['label']}")
        print(f"  Samples/depth: {cfg['samples']}  |  Epochs/depth: {cfg['epochs']}")
        print(f"{'='*55}")

        model = FlexMLP(cfg["hidden"]).to(device)
        print(f"  Parameters: {model.n_params:,}")

        t0 = time.time()
        history = train_model(
            model,
            max_depth=MAX_DEPTH,
            samples_per_depth=cfg["samples"],
            epochs_per_depth=cfg["epochs"],
            solve_threshold=THRESHOLD,
            batch_size=64,
            learning_rate=1e-3,
            seed=SEED,
            verbose=True,
            device=device,
        )
        elapsed = time.time() - t0
        print(f"\n  Training time: {elapsed:.1f}s")

        # Evaluate final solve rates at every depth
        final_rates = {}
        for d in range(1, MAX_DEPTH + 1):
            r = evaluate_solve_rate(model, d, num_tests=EVAL_TESTS,
                                    seed=SEED + d, device=device)
            final_rates[d] = r
            print(f"  Final solve rate depth {d}: {r:.1%}")

        all_results.append({
            "label":        cfg["label"],
            "short":        cfg["short"],
            "color":        cfg["color"],
            "n_params":     model.n_params,
            "samples":      cfg["samples"],
            "loss_history": [float(x) for x in history["loss_history"]],
            "depth_results": [
                {k: float(v) if isinstance(v, float) else v
                 for k, v in dr.items()}
                for dr in history["depth_results"]
            ],
            "final_rates":  {str(k): float(v) for k, v in final_rates.items()},
            "train_time":   elapsed,
        })

    os.makedirs(PLOT_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {RESULTS}")
    return all_results


def load_training():
    with open(RESULTS) as f:
        return json.load(f)


# ===========================================================================
# PART 2 - FIGURES
# ===========================================================================

def savefig(fig, name, tight=True):
    path = os.path.join(FIG_DIR, name)
    if tight:
        fig.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor=WHITE, edgecolor="none")
    else:
        fig.savefig(path, dpi=150, facecolor=WHITE, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {name}")
    return path


# --- Math equation helper ---------------------------------------------------
def math_img(latex, fontsize=12, name=None, width_in=4.5):
    """Render a LaTeX expression to a PNG via matplotlib mathtext."""
    apply_style()
    fig, ax = plt.subplots(figsize=(width_in, 0.7))
    ax.axis("off")
    ax.text(0.0, 0.5, f"${latex}$",
            transform=ax.transAxes, va="center", ha="left",
            fontsize=fontsize, color=NAVY,
            fontfamily="DejaVu Sans")
    path = os.path.join(FIG_DIR, name or f"_math_{abs(hash(latex))}.png")
    fig.savefig(path, dpi=180, bbox_inches="tight",
                facecolor=WHITE, transparent=False)
    plt.close(fig)
    return path


# --- Figure 1: Curriculum flowchart -----------------------------------------
def fig_curriculum_flow():
    apply_style()
    fig, ax = plt.subplots(figsize=(9, 10))
    ax.set_xlim(0, 10); ax.set_ylim(0, 11)
    ax.axis("off")
    ax.set_facecolor(WHITE)
    fig.patch.set_facecolor(WHITE)

    def box(x, y, w, h, text, bg, border, fontsize=9, bold=False):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.12", linewidth=1.2,
                              edgecolor=border, facecolor=bg, zorder=3)
        ax.add_patch(rect)
        weight = "bold" if bold else "normal"
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fontsize, color=NAVY, fontweight=weight,
                zorder=4, wrap=True,
                multialignment="center")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>",
                                   color=SLATE, lw=1.2),
                    zorder=2)

    def label(x, y, text, color=SLATE):
        ax.text(x, y, text, ha="center", va="center",
                fontsize=8, color=color, style="italic")

    # --- boxes ---
    box(5, 10.2, 6.5, 0.9, "START  -  Solved cube, depth = 1", "#dbeafe", BLUE, 9, True)
    box(5,  9.1, 6.5, 0.8, "Generate N scramble-solution pairs\nat current depth", LGREY, BORDER, 8.5)
    box(5,  8.0, 6.5, 0.8, "Train model for E epochs\n(cross-entropy loss on predicted moves)", LGREY, BORDER, 8.5)
    box(5,  6.9, 6.5, 0.8, "Evaluate: solve 50 fresh scrambles\nat this depth", LGREY, BORDER, 8.5)
    # diamond decision
    diamond_x, diamond_y = 5, 5.5
    diamond_w, diamond_h = 4.2, 0.95
    diamond = plt.Polygon(
        [[diamond_x, diamond_y + diamond_h/2],
         [diamond_x + diamond_w/2, diamond_y],
         [diamond_x, diamond_y - diamond_h/2],
         [diamond_x - diamond_w/2, diamond_y]],
        closed=True, facecolor="#fffbeb", edgecolor=AMBER, linewidth=1.4, zorder=3)
    ax.add_patch(diamond)
    ax.text(diamond_x, diamond_y, "Solve rate\n≥ 80 % ?",
            ha="center", va="center", fontsize=9, color=NAVY,
            fontweight="bold", zorder=4)

    box(5,   4.0, 4.5, 0.8, "depth = depth + 1\nMix in 20 % old data, 80 % new", "#f0fdf4", "#86efac", 8.5)
    box(5,   2.9, 4.5, 0.8, "depth > 8 ?", "#f8fafc", BORDER, 8.5, True)
    box(2.5, 1.5, 3.8, 0.8, "STOP - curriculum\ncomplete!", "#dcfce7", FOREST, 8.5, True)
    box(7.5, 1.5, 3.8, 0.8, "SAVE model -\nready to solve", "#dbeafe", BLUE, 8.5, True)

    # right-side failure branch
    box(8.8, 5.5, 2.0, 0.8, "STOP - model\nceiling reached", "#fef2f2", RED, 8.5, True)

    # --- arrows ---
    arrow(5, 9.75, 5, 9.5)
    arrow(5, 8.7,  5, 8.4)
    arrow(5, 7.6,  5, 7.3)
    arrow(5, 6.5,  5, 5.97)
    # YES branch (down)
    arrow(5, 5.03, 5, 4.4)
    label(4.25, 4.73, "YES  (≥ 80%)", FOREST)
    # NO branch (right)
    arrow(7.1, 5.5, 7.8, 5.5)
    label(8.0, 5.85, "NO  (< 80%)", RED)
    # depth > 8?
    arrow(5, 3.6, 5, 3.3)
    # YES -> complete
    arrow(5, 2.5, 2.5, 1.9)
    label(3.2, 2.15, "YES", FOREST)
    # NO -> back to generate
    ax.annotate("", xy=(5, 8.5), xytext=(5, 2.5),
                xycoords="data", textcoords="data",
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0,
                                connectionstyle="arc3,rad=-0.5"))
    # NO label
    ax.text(1.35, 5.5, "NO - next depth", fontsize=8, color=BLUE,
            style="italic", rotation=90, va="center")
    # depth > 8 YES -> save
    arrow(5, 2.5, 7.5, 1.9)
    label(6.8, 2.15, "YES", FOREST)

    ax.set_title("Curriculum Learning - Training Control Flow",
                 fontsize=12, fontweight="bold", color=NAVY, pad=12)
    return savefig(fig, "fig_curriculum_flow.png")


# --- Figure 2: Dataset growth per depth -------------------------------------
def fig_dataset_growth():
    apply_style()
    depths  = list(range(1, MAX_DEPTH + 1))
    samples = 4000
    keep    = 0.20

    # Compute dataset sizes and old/new splits
    total, old_kept, new_gen = [], [], []
    prev = 0
    for d in depths:
        new = samples
        kept = int(prev * keep)
        t = kept + new
        total.append(t)
        old_kept.append(kept)
        new_gen.append(new)
        prev = t

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Left: stacked bar - composition of dataset
    ax = axes[0]
    x = np.array(depths)
    bars_new = ax.bar(x, new_gen, color=COL_LARGE, alpha=0.82, label="New samples (current depth)", width=0.55)
    bars_old = ax.bar(x, old_kept, bottom=new_gen, color=GREY, alpha=0.6, label="Retained old samples (20%)", width=0.55)
    ax.set_xlabel("Curriculum Depth")
    ax.set_ylabel("Number of Training Samples")
    ax.set_title("Dataset Composition at Each Depth Stage")
    ax.set_xticks(depths)
    ax.legend()
    ax.grid(axis="y")
    for i, (t, n, o) in enumerate(zip(total, new_gen, old_kept)):
        ax.text(depths[i], t + 30, f"{t:,}", ha="center", va="bottom",
                fontsize=7.5, color=SLATE)

    # Right: cumulative total line
    ax2 = axes[1]
    ax2.plot(depths, total, "o-", color=COL_MED, lw=2, ms=7, label="Total dataset size")
    ax2.fill_between(depths, 0, total, color=COL_MED, alpha=0.08)
    ax2.set_xlabel("Curriculum Depth")
    ax2.set_ylabel("Total Samples in Training Set")
    ax2.set_title("Cumulative Dataset Size Growth")
    ax2.set_xticks(depths)
    ax2.grid(axis="y")
    ax2.legend()
    for d, t in zip(depths, total):
        ax2.annotate(f"{t:,}", (d, t), textcoords="offset points",
                     xytext=(0, 7), ha="center", fontsize=7.5, color=SLATE)

    fig.suptitle("How the Training Dataset Grows as Difficulty Increases\n"
                 "(Large model: 4,000 new samples per depth, 20% of old data retained)",
                 fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_dataset_growth.png")


# --- Figure 3: Loss curves per depth stage (from training results) ----------
def fig_loss_curves(results):
    apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=False)

    for ax, r in zip(axes, results):
        losses = r["loss_history"]
        dr     = r["depth_results"]
        n_ep   = len(losses)
        epochs = list(range(1, n_ep + 1))
        color  = r["color"]

        ax.plot(epochs, losses, color=color, lw=1.6, zorder=3)
        ax.fill_between(epochs, losses, alpha=0.07, color=color)

        # Mark where each depth begins
        ep_per_d = len(r["depth_results"][0].get("epochs_done", [0])) if dr else 0
        # Reconstruct depth boundaries from depth_results length & epochs_per_depth
        epochs_per_depth = n_ep // max(len(dr), 1)
        for i, dr_row in enumerate(dr):
            x_mark = i * epochs_per_depth + 1
            if 1 < x_mark < n_ep:
                ax.axvline(x_mark, color=color, alpha=0.25, lw=0.8, ls="--")
            # label at the midpoint of each depth block
            mid = (i + 0.5) * epochs_per_depth
            y_pos = max(losses) * 0.93
            ax.text(mid, y_pos,
                    f"D{dr_row['depth']}\n{dr_row['solve_rate']:.0%}",
                    ha="center", va="top", fontsize=7, color=color, alpha=0.85)

        ax.set_xlabel("Training Epoch (cumulative)")
        ax.set_ylabel("Cross-Entropy Loss")
        ax.set_title(r["label"])
        ax.grid(axis="y")
        ax.set_ylim(bottom=0)

        # Annotate final depth reached
        if dr:
            last = dr[-1]
            passed = last["solve_rate"] >= THRESHOLD
            verdict = f"Reached depth {last['depth']}" + (" ✓" if passed else " ✗ (ceiling)")
            ax.text(0.98, 0.96, verdict, transform=ax.transAxes,
                    ha="right", va="top", fontsize=8,
                    color=FOREST if passed else RED,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", fc=WHITE, ec=BORDER, alpha=0.9))

    fig.suptitle("Training Loss per Model - Each Epoch, All Curriculum Depths\n"
                 "Depth labels show the solve rate achieved before advancing",
                 fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_loss_curves.png")


# --- Figure 4: Per-depth solve rate grid ------------------------------------
def fig_solve_rate_grid(results):
    apply_style()
    depths = list(range(1, MAX_DEPTH + 1))
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)

    for ax, r in zip(axes, results):
        dr_map = {row["depth"]: row["solve_rate"] for row in r["depth_results"]}
        # During-training rates (from depth_results)
        train_rates = [dr_map.get(d, None) for d in depths]
        # Final rates (after full training)
        final_rates = [r["final_rates"].get(str(d), 0) for d in depths]

        color = r["color"]
        x = np.array(depths)

        # Bar chart for final rates
        bars = ax.bar(x - 0.2, [v*100 for v in final_rates], width=0.38,
                      color=color, alpha=0.75, label="Final solve rate")
        # Scatter for training checkpoint rates
        train_y = [v*100 if v is not None else None for v in train_rates]
        valid_x = [d for d, v in zip(depths, train_y) if v is not None]
        valid_y = [v for v in train_y if v is not None]
        ax.scatter(np.array(valid_x) + 0.2, valid_y, color=color, s=45,
                   zorder=4, label="Rate at training checkpoint", marker="D",
                   edgecolors="white", linewidths=0.6)

        ax.axhline(80, color=AMBER, lw=1.2, ls=":", alpha=0.9,
                   label="80% curriculum gate")

        ax.set_xlabel("Scramble Depth")
        ax.set_ylabel("Solve Rate (%)")
        ax.set_title(r["label"])
        ax.set_xticks(depths)
        ax.set_ylim(0, 108)
        ax.grid(axis="y")
        ax.legend(fontsize=7.5)

        for bar, v in zip(bars, final_rates):
            if v > 0.04:
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 1.5,
                        f"{v*100:.0f}%", ha="center", va="bottom",
                        fontsize=7, color=SLATE)

    fig.suptitle("Solve Rate at Each Depth: Final (bar) vs Curriculum Checkpoint (diamond)\n"
                 "The 80% dashed line is the gate the model must clear to advance",
                 fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_solve_rates.png")


# --- Figure 5: Model size vs depth reached ----------------------------------
def fig_model_comparison(results):
    apply_style()
    labels         = [r["label"] for r in results]
    params         = [r["n_params"] for r in results]
    depths_reached = []
    for r in results:
        best = max((row["depth"] for row in r["depth_results"]
                    if row["solve_rate"] >= THRESHOLD), default=0)
        depths_reached.append(best)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Left: parameters vs depth reached (scatter/dot chart)
    ax = axes[0]
    colors = [r["color"] for r in results]
    for x, y, c, lbl in zip(params, depths_reached, colors, labels):
        ax.scatter(x, y, s=200, color=c, zorder=4, edgecolors="white", linewidths=1.2)
        ax.annotate(lbl, (x, y), textcoords="offset points",
                    xytext=(8, 3), fontsize=8, color=c)
    ax.set_xlabel("Model Parameters")
    ax.set_ylabel("Maximum Curriculum Depth Cleared")
    ax.set_title("More Parameters = Deeper Curriculum Possible")
    ax.axhline(MAX_DEPTH, color=RED, lw=1, ls="--", alpha=0.6,
               label=f"Max depth = {MAX_DEPTH}")
    ax.set_ylim(0, MAX_DEPTH + 1.5)
    ax.set_yticks(range(0, MAX_DEPTH + 2))
    ax.grid()
    ax.legend(fontsize=8)

    # Right: bar chart of depth reached
    ax2 = axes[1]
    x = np.arange(len(labels))
    bars = ax2.bar(x, depths_reached, color=colors, alpha=0.82, width=0.45)
    ax2.set_xticks(x)
    ax2.set_xticklabels([r["short"].capitalize() for r in results])
    ax2.set_ylabel("Curriculum Depth Cleared")
    ax2.set_title("Max Depth Cleared by Model Size")
    ax2.set_ylim(0, MAX_DEPTH + 1.5)
    ax2.set_yticks(range(0, MAX_DEPTH + 2))
    ax2.axhline(MAX_DEPTH, color=RED, lw=1, ls="--", alpha=0.6)
    ax2.grid(axis="y")
    for bar, d, p in zip(bars, depths_reached, params):
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.1,
                 f"Depth {d}\n({p/1000:.0f}k params)",
                 ha="center", va="bottom", fontsize=8, fontweight="bold", color=NAVY)

    fig.suptitle("Model Capacity vs Curriculum Depth Reached\n"
                 "When a model cannot clear 80% at a depth, the curriculum stops - "
                 "that is its capacity ceiling",
                 fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_model_comparison.png")


# --- Figure 6: One-hot encoding illustration --------------------------------
def fig_one_hot():
    apply_style()
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.5)
    fig.patch.set_facecolor(WHITE)

    # Draw a single facelet color label
    colors_map = {
        "White":  ("#f8fafc", "#475569"),
        "Red":    ("#fee2e2", "#be123c"),
        "Green":  ("#dcfce7", "#166534"),
        "Yellow": ("#fef9c3", "#854d0e"),
        "Orange": ("#ffedd5", "#9a3412"),
        "Blue":   ("#dbeafe", "#1e40af"),
    }
    colors_list = list(colors_map.items())

    # Title
    ax.text(5, 3.3, "One-Hot Encoding of a Single Facelet Color",
            ha="center", fontsize=11, fontweight="bold", color=NAVY)

    for i, (name, (bg, fg)) in enumerate(colors_list):
        x = 0.4 + i * 1.55
        # Color swatch
        rect = FancyBboxPatch((x, 2.2), 0.9, 0.55,
                              boxstyle="round,pad=0.04",
                              facecolor=bg, edgecolor=fg, lw=1.2)
        ax.add_patch(rect)
        ax.text(x + 0.45, 2.47, name, ha="center", va="center",
                fontsize=8, color=fg, fontweight="bold")

        # Encoding vector
        for j in range(6):
            val = 1 if j == i else 0
            cell_bg = bg if val == 1 else LGREY
            cell_ec = fg if val == 1 else BORDER
            rect2 = FancyBboxPatch((x + j * 0.155, 1.35), 0.13, 0.45,
                                   boxstyle="square,pad=0.01",
                                   facecolor=cell_bg, edgecolor=cell_ec, lw=0.8)
            ax.add_patch(rect2)
            ax.text(x + j*0.155 + 0.065, 1.575, str(val),
                    ha="center", va="center", fontsize=7,
                    color=fg if val == 1 else GREY,
                    fontweight="bold" if val == 1 else "normal")

        ax.text(x + 0.45, 1.12, f"pos {i}", ha="center",
                fontsize=7, color=SLATE)

    ax.text(5, 0.65,
            "Each of 54 facelets is encoded as a 6-element vector with exactly one 1 and five 0s.",
            ha="center", fontsize=9, color=SLATE)
    ax.text(5, 0.28,
            "54 facelets × 6 values = 324 numbers total - this is the full input to the neural network.",
            ha="center", fontsize=9, color=NAVY, fontweight="bold")

    return savefig(fig, "fig_one_hot.png")


# --- Figure 7: Network architecture diagram ---------------------------------
def fig_architecture():
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis("off")
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.5)
    fig.patch.set_facecolor(WHITE)

    layers = [
        ("Input\n324", 0.9,  "#dbeafe", BLUE,   0.7),
        ("Hidden 1\n256", 2.9, "#ede9fe", PURPLE, 0.62),
        ("Hidden 2\n256", 5.0, "#ede9fe", PURPLE, 0.62),
        ("Hidden 3\n128", 7.1, "#ede9fe", PURPLE, 0.50),
        ("Output\n18",   9.2,  "#dcfce7", FOREST, 0.24),
    ]
    relu_positions = [1.9, 4.0, 6.1]

    for label, x, bg, ec, h_frac in layers:
        h = h_frac * 4.0
        y0 = (4.0 - h) / 2
        rect = FancyBboxPatch((x - 0.42, y0), 0.84, h,
                              boxstyle="round,pad=0.08",
                              facecolor=bg, edgecolor=ec, lw=1.5, zorder=3)
        ax.add_patch(rect)
        ax.text(x, 2.0, label, ha="center", va="center",
                fontsize=9, color=NAVY, fontweight="bold",
                zorder=4, multialignment="center")

    # ReLU labels between layers
    for xr in relu_positions:
        ax.annotate("", xy=(xr + 0.5, 2.0), xytext=(xr - 0.1, 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.0))
        ax.text(xr + 0.2, 2.55, "ReLU", ha="center", fontsize=7.5,
                color=AMBER, fontweight="bold")

    # Arrow from hidden3 to output
    ax.annotate("", xy=(8.75, 2.0), xytext=(7.54, 2.0),
                arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.0))
    ax.text(8.1, 2.55, "Softmax", ha="center", fontsize=7.5,
            color=FOREST, fontweight="bold")

    # Dimension annotations below
    dims = [(0.9, "324"), (2.9, "256"), (5.0, "256"), (7.1, "128"), (9.2, "18")]
    for x, d in dims:
        ax.text(x, 0.25, f"{d} units", ha="center", fontsize=8, color=SLATE)

    # Total params
    ax.text(6.0, 3.95,
            "Total parameters: 184,210   |   Output: 18 move probabilities (Softmax)",
            ha="center", fontsize=8.5, color=SLATE,
            bbox=dict(boxstyle="round,pad=0.3", fc=LGREY, ec=BORDER))

    ax.set_title("Neural Network Architecture - RubiksMLP",
                 fontsize=11, fontweight="bold", color=NAVY, pad=10)
    return savefig(fig, "fig_architecture.png")


# --- Figure 8: Benchmark results --------------------------------------------
def fig_benchmark():
    apply_style()
    bench_path = os.path.join(ROOT, "docs", "eval_results.json")
    if not os.path.exists(bench_path):
        return None
    with open(bench_path) as f:
        data = json.load(f)

    depths   = [r["depth"] for r in data["kociemba"]]
    koc_r    = [r["rate"]*100 for r in data["kociemba"]]
    g_r      = [r["rate"]*100 for r in data["greedy"]]
    b5_r     = [r["rate"]*100 for r in data["beam_w5"]]
    koc_ms   = [r["ms"] for r in data["kociemba"]]
    g_ms     = [r["ms"] for r in data["greedy"]]
    b5_ms    = [r["ms"] for r in data["beam_w5"]]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: solve rate
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

    # Right: timing (log scale)
    ax2 = axes[1]
    valid_koc = [(d, t) for d, t in zip(depths, koc_ms) if t > 0]
    valid_g   = [(d, t) for d, t in zip(depths, g_ms)   if t > 0]
    valid_b5  = [(d, t) for d, t in zip(depths, b5_ms)  if t > 0]
    ax2.semilogy([x[0] for x in valid_koc], [x[1] for x in valid_koc],
                 "o-", color=FOREST, lw=2, ms=6, label="Kociemba")
    ax2.semilogy([x[0] for x in valid_g], [x[1] for x in valid_g],
                 "s-", color=PURPLE, lw=2, ms=6, label="AI Greedy")
    ax2.semilogy([x[0] for x in valid_b5], [x[1] for x in valid_b5],
                 "D-", color=BLUE, lw=2, ms=6, label="AI Beam w=5")
    ax2.set_xlabel("Scramble Depth")
    ax2.set_ylabel("Average Solve Time (ms, log scale)")
    ax2.set_title("Solve Time by Scramble Depth  (log scale)")
    ax2.set_xticks(depths)
    ax2.legend(); ax2.grid(which="both", axis="y")

    fig.suptitle("Live Benchmark Results - 20 Trials per Depth, CPU Only\n"
                 "AI is orders of magnitude faster but loses accuracy beyond depth 5",
                 fontsize=10, color=SLATE, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_benchmark.png")


# --- Figure 9: Beam search illustration ------------------------------------
def fig_beam_search():
    apply_style()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.axis("off")
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.5)
    fig.patch.set_facecolor(WHITE)

    def node(x, y, text, bg, ec, fs=8.5, solved=False):
        radius = 0.42
        circle = plt.Circle((x, y), radius, facecolor=bg,
                             edgecolor=ec, lw=1.5 if not solved else 2.5, zorder=4)
        ax.add_patch(circle)
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fs, color=NAVY if not solved else FOREST,
                fontweight="bold" if solved else "normal", zorder=5)

    def edge(x1, y1, x2, y2, color=SLATE, ls="-", alpha=1.0):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=1.1, ls=ls, alpha=alpha))

    # Root
    node(5.5, 5.0, "Start", LGREY, SLATE)

    # Step 1 - expand to 5 candidates, keep top 3 (beam=3 for illustration)
    step1 = [(2.0, 3.5), (4.0, 3.5), (5.5, 3.5), (7.0, 3.5), (9.0, 3.5)]
    step1_labels = ["R", "U", "F'", "D", "L"]
    step1_keep   = [True, True, True, False, False]   # top 3

    for (x, y), lbl, keep in zip(step1, step1_labels, step1_keep):
        bg = "#ede9fe" if keep else "#f1f5f9"
        ec = PURPLE if keep else GREY
        node(x, y, lbl, bg, ec)
        edge(5.5, 4.58, x, y + 0.42,
             color=PURPLE if keep else GREY, alpha=1.0 if keep else 0.3)
        if not keep:
            ax.text(x, y - 0.65, "pruned", ha="center", fontsize=7,
                    color=RED, style="italic")

    ax.text(9.8, 3.5, "← keep\n   top 3", fontsize=7.5, color=PURPLE, va="center")

    # Step 2 - each of the 3 expands again
    step2_parents = [(2.0, 3.5), (4.0, 3.5), (5.5, 3.5)]
    step2_children = [
        [(1.2, 2.0), (2.8, 2.0)],
        [(4.0, 2.0), (4.9, 2.0)],
        [(5.5, 2.0), (6.3, 2.0)],
    ]
    step2_labels = [["U", "F'"], ["R", "D"], ["L", "B'"]]
    solved_at = (6.3, 2.0)

    for (px, py), children, labels in zip(step2_parents, step2_children, step2_labels):
        for (cx, cy), lbl in zip(children, labels):
            is_solved = (cx, cy) == solved_at
            bg = "#dcfce7" if is_solved else "#ede9fe"
            ec = FOREST if is_solved else BLUE
            node(cx, cy, lbl, bg, ec, solved=is_solved)
            edge(px, py - 0.42, cx, cy + 0.42, color=BLUE, alpha=0.8)
            if is_solved:
                ax.text(cx + 0.6, cy + 0.3, "SOLVED!", fontsize=9,
                        color=FOREST, fontweight="bold")

    # Legend / annotation
    ax.text(5.5, 1.15,
            "Beam width = 3: at each step we expand all surviving paths and keep "
            "only the 3 most promising.\nGreedy would pick one path only "
            "- it might miss the correct branch entirely.",
            ha="center", fontsize=8.5, color=SLATE,
            bbox=dict(boxstyle="round,pad=0.4", fc=LGREY, ec=BORDER))

    ax.set_title("Beam Search vs Greedy - Exploring Multiple Paths Simultaneously",
                 fontsize=11, fontweight="bold", color=NAVY, pad=10)
    return savefig(fig, "fig_beam_search.png")


def generate_all_figures(results):
    print("\nGenerating figures...")
    figs = {}
    figs["flow"]       = fig_curriculum_flow()
    figs["dataset"]    = fig_dataset_growth()
    figs["loss"]       = fig_loss_curves(results)
    figs["rates"]      = fig_solve_rate_grid(results)
    figs["model_cmp"]  = fig_model_comparison(results)
    figs["one_hot"]    = fig_one_hot()
    figs["arch"]       = fig_architecture()
    figs["benchmark"]  = fig_benchmark()
    figs["beam"]       = fig_beam_search()
    return figs


# ===========================================================================
# PART 3 - PDF
# ===========================================================================

# PDF colours
C_NAVY   = HexColor(NAVY)
C_SLATE  = HexColor(SLATE)
C_AMBER  = HexColor(AMBER)
C_FOREST = HexColor(FOREST)
C_BLUE   = HexColor(BLUE)
C_PURPLE = HexColor(PURPLE)
C_RED    = HexColor(RED)
C_LGREY  = HexColor(LGREY)
C_BORDER = HexColor(BORDER)
C_WHITE  = white


def pdf_styles():
    base = getSampleStyleSheet()
    def S(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "cover_title": S("cover_title",
            fontSize=28, leading=36, textColor=C_WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
        "cover_sub": S("cover_sub",
            fontSize=14, leading=19, textColor=HexColor("#bfdbfe"),
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=3),
        "cover_author": S("cover_author",
            fontSize=11, leading=15, textColor=HexColor("#93c5fd"),
            fontName="Helvetica", alignment=TA_CENTER),

        "h1": S("h1",
            fontSize=19, leading=25, textColor=C_NAVY,
            fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=8),
        "h2": S("h2",
            fontSize=13, leading=18, textColor=C_BLUE,
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5),
        "h3": S("h3",
            fontSize=11, leading=16, textColor=C_PURPLE,
            fontName="Helvetica-Bold", spaceBefore=9, spaceAfter=4),

        "body": S("body",
            fontSize=10.5, leading=16.5, textColor=C_SLATE,
            fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=7),
        "body_c": S("body_c",
            fontSize=10.5, leading=16.5, textColor=C_SLATE,
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=7),
        "small": S("small",
            fontSize=8.5, leading=13, textColor=C_SLATE,
            fontName="Helvetica", spaceAfter=4),
        "caption": S("caption",
            fontSize=8.5, leading=13, textColor=C_SLATE,
            fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=6),
        "bullet": S("bullet",
            fontSize=10.5, leading=16, textColor=C_SLATE,
            fontName="Helvetica", leftIndent=14, spaceAfter=3,
            bulletIndent=4),
        "callout": S("callout",
            fontSize=10.5, leading=16, textColor=C_NAVY,
            fontName="Helvetica-Bold", leftIndent=12, spaceAfter=5),
        "callout_body": S("callout_body",
            fontSize=10, leading=15.5, textColor=C_SLATE,
            fontName="Helvetica", leftIndent=12),
        "code": S("code",
            fontSize=9, leading=14, textColor=C_NAVY,
            fontName="Courier", leftIndent=10),
        "toc": S("toc",
            fontSize=11, leading=18, textColor=C_BLUE,
            fontName="Helvetica", spaceAfter=2),
        "find_head": S("find_head",
            fontSize=10.5, leading=15, textColor=C_NAVY,
            fontName="Helvetica-Bold", spaceAfter=2),
    }


def hr(color=C_BORDER):
    return HRFlowable(width="100%", thickness=0.8, color=color,
                      spaceAfter=8, spaceBefore=2)


def info_box(title, body, styles, bg=HexColor("#f0f9ff"), border=HexColor("#bae6fd")):
    data = [[
        Paragraph(f"<b>{title}</b>", styles["callout"]),
        Paragraph(body, styles["callout_body"]),
    ]]
    t = Table(data, colWidths=[4*cm, 12.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("BOX",           (0,0), (-1,-1), 0.8, border),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    return t


def embed(path, width=15*cm, caption=None, styles=None):
    if path is None or not os.path.exists(path):
        return []
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        iw, ih = im.size
    height = width * ih / iw
    items = [RLImage(path, width=width, height=height)]
    if caption and styles:
        items.append(Paragraph(caption, styles["caption"]))
    items.append(Spacer(1, 0.3*cm))
    return items


def bullets(items, styles):
    return [Paragraph(f"<bullet>•</bullet>  {item}", styles["bullet"])
            for item in items]


def build_pdf(results, figs):
    apply_style()
    doc = SimpleDocTemplate(
        PDF_OUT, pagesize=A4,
        rightMargin=2.4*cm, leftMargin=2.4*cm,
        topMargin=2.4*cm,   bottomMargin=2.4*cm,
        title="AI-Based Optimal Solver for the 3x3 Rubik's Cube - Full Project Guide",
        author="Edward Ogbei",
        subject="MSc Thesis - Politechnika Czestochowa 2026",
    )
    S = pdf_styles()
    story = []

    # ── COVER ───────────────────────────────────────────────────────────────
    cover = Table(
        [[Paragraph("AI-Based Optimal Solver<br/>for the 3x3 Rubik's Cube", S["cover_title"])],
         [Spacer(1, 0.25*cm)],
         [Paragraph("A Complete Guide for the Non-Technical Reader", S["cover_sub"])],
         [Spacer(1, 0.2*cm)],
         [Paragraph("Edward Ogbei  |  MSc Artificial Intelligence<br/>"
                    "Politechnika Czestochowa, Poland  |  2026", S["cover_author"])],
         ],
        colWidths=[16.2*cm]
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 36),
        ("BOTTOMPADDING", (0,0), (-1,-1), 36),
        ("LEFTPADDING",   (0,0), (-1,-1), 18),
        ("RIGHTPADDING",  (0,0), (-1,-1), 18),
    ]))
    story.append(cover)
    story.append(Spacer(1, 0.8*cm))

    # Quick-fact strip
    params_str = f"{results[2]['n_params']:,}" if results else "184,210"
    depth_str  = str(max((max((r["depth"] for r in x["depth_results"]
                    if r["solve_rate"] >= THRESHOLD), default=0)
                    for x in results), default=5)) if results else "5"
    facts = [
        (params_str, "Neural network\nparameters (large model)"),
        ("100%",     "Kociemba solve rate\nat all depths"),
        ("0.7 ms",   "AI solve time\nat depth 4"),
        ("380x",     "AI faster than\nKociemba at depth 7"),
    ]
    fd = [[Paragraph(
        f"<font color='{BLUE}' size='17'><b>{v}</b></font><br/>"
        f"<font color='{SLATE}' size='8'>{l}</font>", S["body_c"])
        for v, l in facts]]
    ft = Table(fd, colWidths=[4.0*cm]*4)
    ft.setStyle(TableStyle([
        ("BOX",           (0,0), (-1,-1), 0.6, C_BORDER),
        ("LINEAFTER",     (0,0), (2,-1), 0.4, C_BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("BACKGROUND",    (0,0), (-1,-1), C_LGREY),
    ]))
    story.append(ft)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "This document explains the complete project in plain, accessible language. "
        "No technical background is assumed. Equations are shown where they help "
        "understanding; every one is explained in words immediately after.",
        S["body"]))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ───────────────────────────────────────────────────
    story.append(Paragraph("Contents", S["h1"]))
    story.append(hr())
    toc_items = [
        ("1", "The Rubik's Cube - Why It Is Harder Than It Looks"),
        ("2", "What Is Artificial Intelligence, Really?"),
        ("3", "How the AI State Is Encoded - One-Hot Vectors"),
        ("4", "The Neural Network Architecture"),
        ("5", "The Expert Algorithm: Kociemba (the Teacher)"),
        ("6", "Dataset Construction - Learning from the Expert"),
        ("7", "Curriculum Learning - Earning Every Level"),
        ("8", "Training Outcomes - What Actually Happened"),
        ("9", "Beam Search - Smarter than Greedy"),
        ("10","The Interactive 3D Visualisation"),
        ("11","Full Benchmark Results"),
        ("12","Key Findings"),
        ("13","Limitations and the Path Forward"),
        ("14","Glossary of Terms"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(
            f"<font color='{BLUE}'><b>{num}.</b></font>  {title}", S["toc"]))
    story.append(PageBreak())

    # ── CH 1: THE CUBE ───────────────────────────────────────────────────────
    story.append(Paragraph("1.  The Rubik's Cube - Why It Is Harder Than It Looks", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "A standard 3x3 Rubik's Cube looks simple: six faces, six colours, "
        "nine stickers per face. Twist a few times and the colours mix. "
        "Twist back and - usually - they do not unmix. That frustration "
        "conceals a remarkable mathematical fact.", S["body"]))

    story.append(Paragraph("How many positions exist?", S["h2"]))
    story.append(Paragraph(
        "The exact number of distinct cube positions is:", S["body"]))

    # Math equation - number of states
    eq1 = math_img(
        r"N \;=\; \frac{8! \;\times\; 3^7 \;\times\; 12! \;\times\; 2^{11}}{2}"
        r"\;\approx\; 4.3 \times 10^{19}",
        fontsize=14, name="eq_states.png", width_in=6)
    story += embed(eq1, width=10*cm, caption=
        "The exact count of legal 3x3 Rubik's Cube positions: "
        "roughly 43 quintillion (43 followed by 18 zeros).", styles=S)

    story.append(info_box(
        "Scale check:",
        "If you scrambled one cube every second starting at the Big Bang "
        "(13.8 billion years ago), you would have seen roughly 4 x 10^17 "
        "configurations - still 100 times fewer than all possible positions.",
        S))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Despite this vastness, human experts solve the cube in under two "
        "seconds. They do it not by searching, but by recognising patterns "
        "and applying memorised algorithms - short move sequences that fix "
        "specific pieces. The question this project asks is: can a neural "
        "network do the same, starting from scratch?", S["body"]))

    story.append(Paragraph("God's Number", S["h2"]))
    story.append(Paragraph(
        "Mathematicians proved in 2010 that every possible scramble can be "
        "solved in at most 20 moves. This is called God's Number. "
        "A perfect solver would never need more. Human beginners use 100+. "
        "The Kociemba algorithm (Chapter 5) typically uses 18-22. "
        "Our AI model matches the scramble depth for easy cases and "
        "degrades gracefully beyond its training limit.", S["body"]))
    story.append(PageBreak())

    # ── CH 2: WHAT IS AI ────────────────────────────────────────────────────
    story.append(Paragraph("2.  What Is Artificial Intelligence, Really?", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "The phrase sounds like science fiction. The reality is more grounded. "
        "In this project, AI means one thing: <b>a mathematical function that "
        "maps a cube state to a recommended move, learned entirely from examples</b>.",
        S["body"]))
    story.append(Paragraph("The child-and-dogs analogy", S["h2"]))
    story.append(Paragraph(
        "Imagine teaching a child to recognise dogs. You show thousands of "
        "photos and label each one. After enough examples the child can "
        "classify a new photo without being told any rule explicitly. "
        "A neural network does the same thing with numbers: it sees "
        "thousands of (cube state, correct move) pairs and learns to predict "
        "the correct move for states it has never seen.", S["body"]))
    story.append(Paragraph(
        "The key difference from a traditional program: nobody writes rules "
        "about how to solve the cube. The patterns emerge entirely from data. "
        "This is both the strength of the approach and its limitation - "
        "the model is only as good as the data and capacity it was given.", S["body"]))
    story.append(PageBreak())

    # ── CH 3: ONE-HOT ENCODING ──────────────────────────────────────────────
    story.append(Paragraph("3.  How the AI State Is Encoded - One-Hot Vectors", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "A neural network cannot look at a physical cube. It only processes "
        "numbers. The first step is translating the cube's visual state into "
        "a compact numerical representation.", S["body"]))
    story += embed(figs.get("one_hot"), width=14.5*cm,
        caption="Each of the 54 facelets is encoded as a 6-element binary vector. "
                "Only one element is 1 (the actual colour); the rest are 0. "
                "This is called one-hot encoding.",
        styles=S)
    story.append(Paragraph(
        "The full cube state vector is therefore:", S["body"]))
    eq2 = math_img(
        r"\vec{x} \in \mathbf{R}^{324}, \quad"
        r"\vec{x} = [x_1^{(0)},\,x_1^{(1)},\,\ldots,\,x_{54}^{(5)}]",
        fontsize=12, name="eq_encoding.png", width_in=6.5)
    story += embed(eq2, width=10*cm, styles=S)
    story.append(Paragraph(
        "where each group of 6 consecutive values encodes one facelet, "
        "with exactly one 1 and five 0s. This 324-dimensional vector is "
        "the complete input to the neural network at every step.", S["body"]))
    story.append(PageBreak())

    # ── CH 4: ARCHITECTURE ──────────────────────────────────────────────────
    story.append(Paragraph("4.  The Neural Network Architecture", S["h1"]))
    story.append(hr())
    story += embed(figs.get("arch"), width=14.5*cm,
        caption="The RubiksMLP: four layers of linear transformations separated "
                "by ReLU activations, ending in a softmax that converts raw scores "
                "to move probabilities.",
        styles=S)
    story.append(Paragraph("The ReLU activation", S["h2"]))
    story.append(Paragraph(
        "Between every pair of layers sits a simple operation called ReLU "
        "(Rectified Linear Unit):", S["body"]))
    eq3 = math_img(r"\text{ReLU}(x) = \max(0,\, x)",
                   fontsize=12, name="eq_relu.png", width_in=3.5)
    story += embed(eq3, width=7*cm, styles=S)
    story.append(Paragraph(
        "If the value is positive, keep it. If negative, set it to zero. "
        "This tiny nonlinearity is what allows the network to learn complex, "
        "curved decision boundaries. Without it, all those matrix multiplications "
        "would collapse into a single linear equation - powerless for this task.",
        S["body"]))
    story.append(Paragraph("The output layer and Softmax", S["h2"]))
    story.append(Paragraph(
        "The 18 output neurons correspond to the 18 legal moves "
        "(U, U', U2, R, R', R2, F, F', F2, D, D', D2, L, L', L2, B, B', B2). "
        "To convert raw scores into probabilities, we apply Softmax:",
        S["body"]))
    eq4 = math_img(
        r"\hat{y}_i = \frac{e^{z_i}}{\sum_{j=1}^{18} e^{z_j}}, \quad"
        r"\sum_{i=1}^{18} \hat{y}_i = 1",
        fontsize=12, name="eq_softmax.png", width_in=5)
    story += embed(eq4, width=9*cm, styles=S)
    story.append(Paragraph(
        "The move with the highest probability is what the network recommends. "
        "Confidence is that probability - a value close to 1.0 means the "
        "network is very sure; close to 0.05 means it is effectively guessing "
        "among 20 equally plausible options.", S["body"]))
    story.append(PageBreak())

    # ── CH 5: KOCIEMBA ──────────────────────────────────────────────────────
    story.append(Paragraph("5.  The Expert Algorithm: Kociemba (the Teacher)", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "To train the AI, we need an expert to imitate. That expert is the "
        "<b>Kociemba two-phase algorithm</b>, designed by Herbert Kociemba in "
        "the 1990s. It solves any scramble in near-optimal moves using "
        "pre-computed lookup tables over a mathematically reduced state space.",
        S["body"]))

    koc_table_data = [
        ["Property", "Kociemba", "AI Neural Network"],
        ["Source of knowledge", "Rules hand-built by\na human expert", "Patterns from Kociemba\nexpert demonstrations"],
        ["Always correct?", "Yes", "No - probabilistic"],
        ["Time at depth 3", "~2 ms", "~2 ms"],
        ["Time at depth 7", "~380 ms", "~3 ms"],
        ["Time at depth 10", ">10,000 ms", "<1 ms (often wrong)"],
        ["Solution quality", "Near-optimal", "Usually optimal, degrades\nbeyond training depth"],
        ["Explainable?", "Yes - rule-based", "No - black box"],
    ]
    kt = Table(koc_table_data, colWidths=[5*cm, 5.5*cm, 5.5*cm])
    kt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), C_NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND",    (0,1), (0,-1), C_LGREY),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1), C_NAVY),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [white, HexColor("#f0fdf4")]),
        ("BOX",           (0,0), (-1,-1), 0.5, C_BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
    ]))
    story.append(kt)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "The AI was trained by watching Kociemba solve thousands of scrambles "
        "and learning to imitate those moves. This is imitation learning. "
        "The AI does not know why Kociemba makes each move - it just learned "
        "to copy the pattern. That is why it works well at low depths but "
        "fails at high depths: there was not enough data or model capacity "
        "to capture the full complexity.", S["body"]))
    story.append(PageBreak())

    # ── CH 6: DATASET ───────────────────────────────────────────────────────
    story.append(Paragraph("6.  Dataset Construction - Learning from the Expert", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "Each training example is a (cube state, correct move) pair. "
        "Here is how they are generated:", S["body"]))
    story += bullets([
        "Take a solved cube.",
        "Apply N random moves (N = current curriculum depth).",
        "Ask Kociemba: what is the best next move from here?",
        "Record (one-hot encoded state, Kociemba's move index).",
        "Apply that move and repeat until solved - each step is one more example.",
    ], S)
    story.append(Spacer(1, 0.3*cm))
    story += embed(figs.get("dataset"), width=14.5*cm,
        caption="Left: how old and new samples are mixed at each depth stage "
                "(80% new, 20% retained). "
                "Right: how the total dataset size grows as curriculum progresses. "
                "These charts show the large model (4,000 new samples per depth).",
        styles=S)
    story.append(Paragraph("Why keep 20% of old data?", S["h2"]))
    story.append(Paragraph(
        "If you train only on new, harder examples, the network forgets the "
        "easier ones. This is called <b>catastrophic forgetting</b>. "
        "Retaining 20% of the old dataset acts as a reminder: "
        "do not forget what you already know while learning something harder.",
        S["body"]))
    story.append(PageBreak())

    # ── CH 7: CURRICULUM LEARNING ───────────────────────────────────────────
    story.append(Paragraph("7.  Curriculum Learning - Earning Every Level", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "The training loop does not simply run for a fixed number of epochs "
        "and then declare the model trained. It uses a gated progression: "
        "the model must prove it has learned each level before being given "
        "a harder one.", S["body"]))
    story += embed(figs.get("flow"), width=13*cm,
        caption="The curriculum control flow. The 80% solve-rate gate is the key "
                "decision point. Failing it stops training at that model's capacity ceiling.",
        styles=S)
    story.append(Paragraph("The advancement rule as a formula", S["h2"]))
    eq5 = math_img(
        r"\text{Advance if:} \quad "
        r"\frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} "
        r"\mathbf{1}[\text{solved}_i] \;\geq\; \theta = 0.80",
        fontsize=11.5, name="eq_threshold.png", width_in=7.5)
    story += embed(eq5, width=12*cm, styles=S)
    story.append(Paragraph(
        "In words: run the model on N test scrambles; count the fraction "
        "it solves correctly; if that fraction is at least 80%, advance "
        "to the next depth. If not, curriculum stops - this is the model's "
        "measured capacity ceiling, not a failure.", S["body"]))
    story.append(info_box(
        "Why this matters:",
        "A fixed epoch schedule (e.g. always advance after 50 epochs) "
        "would advance regardless of performance. The threshold rule "
        "means advancement is earned, not assumed. Prof. Rojek: "
        "'If you increase the dataset after every 10 epochs, this is "
        "not a good approach. The criterion must be the metric.'",
        S, bg=HexColor("#fffbeb"), border=HexColor("#fde68a")))
    story.append(PageBreak())

    # ── CH 8: TRAINING OUTCOMES ─────────────────────────────────────────────
    story.append(Paragraph("8.  Training Outcomes - What Actually Happened", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "The following figures show real training runs for all three model "
        "sizes. Each was trained from depth 1 up to depth 8, stopping "
        "whenever the 80% threshold could not be cleared.", S["body"]))

    story.append(Paragraph("Training loss curves", S["h2"]))
    story.append(Paragraph(
        "The loss measures how wrong the network's predictions are. "
        "Lower is better. A sudden rise at a depth transition is normal - "
        "the model has just seen harder examples and needs time to adapt.",
        S["body"]))
    story += embed(figs.get("loss"), width=15*cm,
        caption="Loss curves for all three model sizes. Each panel covers all epochs "
                "across all curriculum depths. The percentage inside each depth block "
                "is the solve rate the model achieved before advancing (or stopping). "
                "Deeper colours = larger model.",
        styles=S)

    story.append(Paragraph("Solve rates at each depth checkpoint", S["h2"]))
    story += embed(figs.get("rates"), width=15*cm,
        caption="Bars show the final solve rate (after all training). "
                "Diamonds show the rate at the training checkpoint "
                "(the value used to decide whether to advance). "
                "The amber dashed line is the 80% gate.",
        styles=S)

    story.append(Paragraph("Model capacity ceiling", S["h2"]))
    story += embed(figs.get("model_cmp"), width=14*cm,
        caption="Left: more parameters = deeper curriculum possible. "
                "Right: the maximum depth each model cleared the 80% gate at. "
                "The red dashed line marks the maximum depth (8) we trained to.",
        styles=S)
    story.append(PageBreak())

    # ── CH 9: BEAM SEARCH ───────────────────────────────────────────────────
    story.append(Paragraph("9.  Beam Search - Smarter Than Greedy", S["h1"]))
    story.append(hr())
    story += embed(figs.get("beam"), width=14*cm,
        caption="Beam search (width=3 for illustration) keeps the top 3 paths "
                "alive at every step instead of committing to one. "
                "The green node was found only because an alternative branch was kept.",
        styles=S)
    story.append(Paragraph(
        "In the greedy approach the model picks its single highest-confidence "
        "move at every step. Beam search instead maintains a beam of W candidate "
        "paths simultaneously, expanding each one at every step and pruning "
        "back to the best W. The cumulative log-probability of a path is:", S["body"]))
    eq6 = math_img(
        r"\text{score}(m_1, m_2, \ldots, m_k) = "
        r"-\sum_{t=1}^{k} \log \hat{y}_{m_t}^{(t)}",
        fontsize=11.5, name="eq_beam.png", width_in=6)
    story += embed(eq6, width=10*cm, styles=S)
    story.append(Paragraph(
        "Paths with smaller (less negative) cumulative scores are preferred. "
        "The beam width W controls the tradeoff: W=1 is pure greedy; "
        "larger W explores more alternatives at higher computational cost.",
        S["body"]))

    story.append(info_box(
        "Live demonstration:",
        "During testing, a 4-move scramble (D L' F' D) was applied. "
        "AI Greedy failed - it cycled for 50 moves without solving. "
        "AI Beam Search (w=5) solved it cleanly in 4 moves. "
        "This is precisely the failure mode beam search is designed to catch.",
        S, bg=HexColor("#f0fdf4"), border=HexColor("#86efac")))
    story.append(PageBreak())

    # ── CH 10: UI ───────────────────────────────────────────────────────────
    story.append(Paragraph("10.  The Interactive 3D Visualisation", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "The project includes a live web application. The 3D cube is rendered "
        "in a browser using Three.js (a JavaScript 3D graphics library). "
        "A Python HTTP server holds the mathematical cube state and runs the "
        "solvers. Every button click is an API call to the server; the response "
        "drives a smooth animated rotation for each move in sequence.",
        S["body"]))
    story += bullets([
        "<b>Scramble (5 or 20 moves)</b>: randomise the cube with animated moves.",
        "<b>Solve - Kociemba</b>: watch the expert algorithm undo the scramble step by step.",
        "<b>AI Greedy</b>: the neural network tries to solve it in one greedy pass.",
        "<b>AI Beam Search (w=5)</b>: beam search explores 5 candidate paths simultaneously.",
        "<b>Run Benchmark</b>: tests all three solvers at depths 1-8, "
        "reporting solve rate and timing side by side.",
    ], S)
    story.append(Paragraph(
        "To start the application: run <font face='Courier'>python main.py "
        "visualize --web</font> from the project folder, then open "
        "<font face='Courier'>http://localhost:8080</font>.", S["body"]))
    story.append(PageBreak())

    # ── CH 11: BENCHMARK ────────────────────────────────────────────────────
    story.append(Paragraph("11.  Full Benchmark Results", S["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "All measurements below were taken on a laptop CPU (no GPU), "
        "20 trials per depth, using scrambles the model had never seen.",
        S["small"]))
    story += embed(figs.get("benchmark"), width=14.5*cm,
        caption="Left: solve rates for all three solvers across depths 1-10. "
                "Right: solve times on a logarithmic scale - note how Kociemba's time "
                "explodes at deeper scrambles while the AI stays flat (but wrong).",
        styles=S)

    # Detailed table
    bench_path = os.path.join(ROOT, "docs", "eval_results.json")
    if os.path.exists(bench_path):
        with open(bench_path) as f:
            bd = json.load(f)
        hdrs = ["Depth", "Kociemba", "AI Greedy", "AI Beam w=5", "Koc time", "Greedy time", "Beam time"]
        rows = []
        for i in range(len(bd["kociemba"])):
            k = bd["kociemba"][i]
            g = bd["greedy"][i]
            b = bd["beam_w5"][i]
            rows.append([
                str(k["depth"]),
                f"{k['rate']*100:.0f}%",
                f"{g['rate']*100:.0f}%",
                f"{b['rate']*100:.0f}%",
                f"{k['ms']:.1f} ms" if k["ms"] else "-",
                f"{g['ms']:.1f} ms" if g["ms"] else "-",
                f"{b['ms']:.1f} ms" if b["ms"] else "-",
            ])
        bt = Table([hdrs] + rows, colWidths=[1.8*cm]*7)
        bt.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), C_NAVY),
            ("TEXTCOLOR",     (0,0), (-1,0), white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [white, C_LGREY]),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("BOX",           (0,0), (-1,-1), 0.5, C_BORDER),
            ("INNERGRID",     (0,0), (-1,-1), 0.3, C_BORDER),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ]))
        story.append(bt)
    story.append(PageBreak())

    # ── CH 12: KEY FINDINGS ─────────────────────────────────────────────────
    story.append(Paragraph("12.  Key Findings", S["h1"]))
    story.append(hr())
    findings = [
        ("AI is vastly faster than Kociemba at deep scrambles",
         "At depth 7 the AI responds in ~3 ms vs Kociemba's ~380 ms - "
         "a 120x speedup. At depth 9 the gap exceeds 800x. "
         "This happens because the AI always runs the same fixed-size forward pass "
         "regardless of difficulty, while Kociemba's search expands exponentially."),
        ("Speed without accuracy is not useful",
         "At depth 7 the AI only solves 10% of cases. Being fast but wrong "
         "100% of the time at depth 10 is not a solver - it is a random guesser "
         "with low latency. Accuracy and speed must both be considered."),
        ("Beam search consistently improves accuracy",
         "Across depths 4-7 beam search (w=5) outperforms greedy by 5-15 "
         "percentage points. At depth 5 in one live test batch: 100% beam vs 60% "
         "greedy. The improvement is real, repeatable, and largest at the model's "
         "natural capability boundary."),
        ("Curriculum learning gives an honest capacity measurement",
         "The 80% threshold acts as a quality gate. When the small model stalls "
         "at depth 4, that is a precise measurement of its ceiling, not a failure. "
         "Bigger models clear higher depths. This relationship between capacity, "
         "data, and difficulty is the core thesis contribution."),
        ("Model size, data volume, and depth are tightly linked",
         "You cannot simply push a tiny model to learn depth-8 scrambles. "
         "All three must scale together. The ablation study shows that "
         "large-model + 4,000 samples/depth reaches further than "
         "small-model + 800 samples/depth at every stage."),
    ]
    for title, body in findings:
        story.append(KeepTogether([
            Paragraph(title, S["find_head"]),
            Paragraph(body, S["body"]),
        ]))
    story.append(PageBreak())

    # ── CH 13: LIMITATIONS ──────────────────────────────────────────────────
    story.append(Paragraph("13.  Limitations and the Path Forward", S["h1"]))
    story.append(hr())
    limits = [
        ("CPU-only training",
         "All training was done on a laptop CPU. A GPU would be 10-50x faster "
         "and would make it practical to train the model to depth 10+ with millions "
         "of samples."),
        ("Maximum reliable depth is 4-5",
         "The production model was trained to depth 5 with 150k samples. "
         "Reliable solving beyond that requires more capacity and data. "
         "The curriculum experiments in this session reached up to depth "
         + depth_str + " depending on model size."),
        ("Imitation learning, not autonomous discovery",
         "The model copies Kociemba. It has never found a solution Kociemba "
         "did not already know. Reinforcement learning (RL) could let the model "
         "explore independently and potentially outperform Kociemba at certain "
         "depths - but that is a separate, larger research project."),
        ("Solutions are not always optimal",
         "When the AI solves a scramble it usually uses the same number of moves "
         "as the scramble depth, but this is not guaranteed. Kociemba produces "
         "provably near-optimal solutions; the AI makes no such guarantee."),
        ("Greedy search can loop",
         "Without visited-state tracking, the greedy solver can revisit states "
         "and cycle. Beam search already prevents this by tracking visited states. "
         "Adding the same check to greedy is a straightforward improvement."),
    ]
    for title, body in limits:
        story.append(KeepTogether([
            Paragraph(title, S["h3"]),
            Paragraph(body, S["body"]),
        ]))
    story.append(PageBreak())

    # ── CH 14: GLOSSARY ─────────────────────────────────────────────────────
    story.append(Paragraph("14.  Glossary of Terms", S["h1"]))
    story.append(hr())
    terms = [
        ("Activation function", "A non-linear operation (like ReLU) applied after each layer in a neural network."),
        ("Batch size", "How many training examples the network sees before updating its internal weights."),
        ("Beam search", "A search strategy that maintains W candidate solution paths simultaneously rather than committing to one."),
        ("Catastrophic forgetting", "When a network, trained on new data, forgets patterns it learned from old data."),
        ("Cross-entropy loss", "A number measuring how wrong the network's predicted move probabilities are compared to the correct answer."),
        ("Curriculum learning", "Training progressively from easy to hard, advancing only when a performance threshold is met."),
        ("Cubie", "One of the 26 individual small cubes that form a 3x3 Rubik's Cube (8 corners, 12 edges, 6 centres)."),
        ("Epoch", "One complete pass through the training dataset."),
        ("Facelet", "A single coloured square on the cube surface. A 3x3 cube has 54 facelets."),
        ("God's Number", "The maximum number of moves needed to solve any position - proven to be 20 for a 3x3 cube."),
        ("Greedy search", "Picking the highest-confidence option at each step, with no lookahead or backtracking."),
        ("Imitation learning", "Training a model by showing it expert demonstrations and asking it to replicate them."),
        ("Kociemba algorithm", "A two-phase algorithm designed by Herbert Kociemba that solves any 3x3 scramble near-optimally."),
        ("Learning rate", "A small number controlling how large each weight update is during training."),
        ("MLP", "Multi-Layer Perceptron - a neural network with fully connected layers."),
        ("Neural network", "A mathematical structure of weighted connections, loosely inspired by the brain, that learns from examples."),
        ("One-hot encoding", "Representing a category as a list of zeros with a single 1 in the position of the chosen category."),
        ("Parameters / weights", "The numbers inside a neural network that are adjusted during training."),
        ("ReLU", "Rectified Linear Unit: f(x) = max(0, x). Sets negative values to zero."),
        ("Softmax", "Converts raw network scores to probabilities that sum to 1."),
        ("Solve rate", "Fraction of test scrambles a solver successfully solves within the move limit."),
    ]
    for term, defn in terms:
        story.append(Paragraph(
            f"<b><font color='{NAVY}'>{term}</font></b>  "
            f"<font color='{GREY}'>-</font>  {defn}",
            S["body"]))

    doc.build(story)
    size_kb = os.path.getsize(PDF_OUT) // 1024
    print(f"\nPDF created: {PDF_OUT}  ({size_kb} KB, approx {size_kb//3} pages)")
    return PDF_OUT


# ===========================================================================
# ENTRY POINT
# ===========================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-train", action="store_true",
                        help="Skip training; reuse cached results from " + RESULTS)
    args = parser.parse_args()

    if args.skip_train and os.path.exists(RESULTS):
        print("Loading cached training results...")
        results = load_training()
    else:
        print("Running curriculum training (small / medium / large)...")
        print("This takes roughly 15-30 minutes on CPU.")
        results = run_training()

    print("\nGenerating figures...")
    figs = generate_all_figures(results)

    print("\nBuilding PDF...")
    build_pdf(results, figs)
    print("Done.")


if __name__ == "__main__":
    main()
