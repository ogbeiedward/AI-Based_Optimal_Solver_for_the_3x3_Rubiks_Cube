"""
curriculum_experiments.py
--------------------------
Runs a series of training experiments at different model sizes and dataset sizes
to generate the plots required for the MSc thesis.

Experiments performed:
  1. Small model  (~50k params)  trained on 50,000 samples  up to depth 5
  2. Medium model (~100k params) trained on 100,000 samples up to depth 5
  3. Large model  (~184k params) trained on 150,000 samples up to depth 5

For each experiment the script records:
  - Training loss per epoch (loss curve)
  - Solve rate per curriculum depth (progression table)
  - Final solve rates at each scramble depth (bar chart)

All figures are saved to experiments/plots/.

Usage:
    python -m experiments.curriculum_experiments [--quick]

    --quick  Use very small sample sizes for a fast smoke-test run
             (not suitable for thesis-quality results).
"""

import argparse
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')           # Headless – works without a display
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from solvers.ai_solver import (
    RubiksMLP, train_model, evaluate_solve_rate,
)

# ---------------------------------------------------------------------------
# Experiment configurations
# ---------------------------------------------------------------------------

EXPERIMENTS = [
    {
        "label": "Small (50k samples, ~50k params)",
        "short": "small",
        "hidden": [128, 128],          # smaller hidden layers
        "samples_per_depth": 10_000,   # total ≈ 50k across 5 depths
        "epochs_per_depth": 30,
        "color": "#ff8080",
    },
    {
        "label": "Medium (100k samples, ~100k params)",
        "short": "medium",
        "hidden": [256, 128],
        "samples_per_depth": 20_000,
        "epochs_per_depth": 40,
        "color": "#80ccff",
    },
    {
        "label": "Large (150k samples, ~184k params)",
        "short": "large",
        "hidden": [256, 256, 128],     # default architecture
        "samples_per_depth": 30_000,
        "epochs_per_depth": 50,
        "color": "#80ff90",
    },
]

QUICK_OVERRIDE = {
    "samples_per_depth": 500,
    "epochs_per_depth": 5,
}

MAX_DEPTH = 5
LOSS_THRESHOLD = 0.8          # validation-loss proxy: if solve rate > 80 % advance
EVAL_TESTS = 50
SEED = 42

PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")


# ---------------------------------------------------------------------------
# Custom MLP that accepts arbitrary hidden sizes
# ---------------------------------------------------------------------------

class FlexMLP(torch.nn.Module):
    """MLP with configurable hidden layer sizes for ablation experiments."""

    def __init__(self, hidden_sizes):
        super().__init__()
        from core.state_encoder import ENCODING_DIM, NUM_MOVES
        layers = []
        in_dim = ENCODING_DIM
        for h in hidden_sizes:
            layers += [torch.nn.Linear(in_dim, h), torch.nn.ReLU()]
            in_dim = h
        layers.append(torch.nn.Linear(in_dim, NUM_MOVES))
        self.network = torch.nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

    def predict_move(self, x):
        self.eval()
        with torch.no_grad():
            if x.dim() == 1:
                x = x.unsqueeze(0)
            logits = self.forward(x)
            probs = torch.softmax(logits, dim=1)
            idx = torch.argmax(probs, dim=1).item()
            conf = probs[0, idx].item()
        return idx, conf

    def get_parameter_count(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------
# Run one experiment
# ---------------------------------------------------------------------------

def run_experiment(cfg, quick=False, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    samples = QUICK_OVERRIDE["samples_per_depth"] if quick else cfg["samples_per_depth"]
    epochs  = QUICK_OVERRIDE["epochs_per_depth"]  if quick else cfg["epochs_per_depth"]

    model = FlexMLP(cfg["hidden"]).to(device)
    n_params = model.get_parameter_count()
    print(f"\n{'='*60}")
    print(f"Experiment: {cfg['label']}")
    print(f"Parameters: {n_params:,}")
    print(f"Samples/depth: {samples:,}  |  Epochs/depth: {epochs}")
    print(f"{'='*60}")

    history = train_model(
        model,
        max_depth=MAX_DEPTH,
        samples_per_depth=samples,
        epochs_per_depth=epochs,
        solve_threshold=LOSS_THRESHOLD,
        batch_size=64,
        learning_rate=1e-3,
        seed=SEED,
        verbose=True,
        device=device,
    )

    # Evaluate final solve rates per depth
    final_solve_rates = {}
    for depth in range(1, MAX_DEPTH + 1):
        rate = evaluate_solve_rate(model, depth, num_tests=EVAL_TESTS, seed=SEED + depth, device=device)
        final_solve_rates[depth] = rate
        print(f"  Final solve rate @ depth {depth}: {rate:.1%}")

    return {
        "label": cfg["label"],
        "short": cfg["short"],
        "color": cfg["color"],
        "n_params": n_params,
        "samples_per_depth": samples,
        "loss_history": history["loss_history"],
        "depth_results": history["depth_results"],
        "final_solve_rates": final_solve_rates,
    }


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def make_plots(results):
    os.makedirs(PLOT_DIR, exist_ok=True)

    _style()

    # 1. Loss curves per model
    _plot_loss_curves(results)

    # 2. Solve-rate bars per depth, grouped by model
    _plot_solve_rate_bars(results)

    # 3. Curriculum progression (depth reached vs model)
    _plot_curriculum_progression(results)

    # 4. Combined overview figure (for thesis)
    _plot_combined(results)

    print(f"\nAll plots saved to: {PLOT_DIR}")


def _style():
    plt.rcParams.update({
        'figure.facecolor': '#0d0d1a',
        'axes.facecolor':   '#13132a',
        'axes.edgecolor':   '#404060',
        'axes.labelcolor':  '#c0c0e0',
        'xtick.color':      '#a0a0c0',
        'ytick.color':      '#a0a0c0',
        'text.color':       '#e0e0ff',
        'grid.color':       '#252540',
        'grid.linestyle':   '--',
        'grid.alpha':       0.6,
        'legend.facecolor': '#1a1a30',
        'legend.edgecolor': '#404060',
        'font.family':      'DejaVu Sans',
        'font.size':        10,
    })


def _plot_loss_curves(results):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Training Loss Curves — Model Size Comparison", fontsize=13, pad=12)
    ax.set_xlabel("Training Epoch (cumulative across curriculum depths)")
    ax.set_ylabel("Cross-Entropy Loss")
    ax.grid(True)

    for r in results:
        losses = r["loss_history"]
        epochs = list(range(1, len(losses) + 1))
        ax.plot(epochs, losses, label=r["label"], color=r["color"], linewidth=1.8)

        # Mark depth transitions
        epochs_per_d = len(losses) // MAX_DEPTH
        for d in range(1, MAX_DEPTH):
            x = d * epochs_per_d
            if x < len(losses):
                ax.axvline(x=x, color=r["color"], alpha=0.25, linestyle=':')

    # Depth boundary annotations
    if results:
        l = results[0]["loss_history"]
        epochs_per_d = len(l) // MAX_DEPTH
        for d in range(1, MAX_DEPTH):
            x = d * epochs_per_d
            if x < len(l):
                ax.text(x + 0.5, ax.get_ylim()[1] * 0.95,
                        f"Depth {d+1}", fontsize=7, color='#888899', rotation=90, va='top')

    ax.legend(loc='upper right')
    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "loss_curves.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _plot_solve_rate_bars(results):
    depths = list(range(1, MAX_DEPTH + 1))
    n_models = len(results)
    width = 0.25
    offsets = np.linspace(-(n_models - 1) * width / 2, (n_models - 1) * width / 2, n_models)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Final Solve Rate by Scramble Depth and Model Size", fontsize=13, pad=12)
    ax.set_xlabel("Scramble Depth")
    ax.set_ylabel("Solve Rate (%)")
    ax.set_xticks(depths)
    ax.set_ylim(0, 105)
    ax.grid(True, axis='y')

    for i, r in enumerate(results):
        rates = [r["final_solve_rates"].get(d, 0) * 100 for d in depths]
        bars = ax.bar(
            [d + offsets[i] for d in depths],
            rates,
            width=width,
            color=r["color"],
            alpha=0.85,
            label=r["label"],
        )
        for bar, rate in zip(bars, rates):
            if rate > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                        f"{rate:.0f}%", ha='center', va='bottom', fontsize=7)

    ax.axhline(y=80, color='#ffcc44', linestyle='--', linewidth=1, alpha=0.7, label='80% threshold')
    ax.legend(loc='upper right', fontsize=8)
    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "solve_rate_bars.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _plot_curriculum_progression(results):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Curriculum Learning: Depth Reached per Model\n(stops when model cannot pass 80% solve rate threshold)", fontsize=12, pad=12)
    ax.set_xlabel("Model Configuration")
    ax.set_ylabel("Maximum Curriculum Depth Reached")
    ax.set_ylim(0, MAX_DEPTH + 1)
    ax.set_yticks(range(1, MAX_DEPTH + 2))
    ax.grid(True, axis='y')

    labels = [r["short"].capitalize() for r in results]
    depths_reached = []
    for r in results:
        d = max((dr["depth"] for dr in r["depth_results"] if dr["solve_rate"] >= LOSS_THRESHOLD), default=0)
        depths_reached.append(d)

    bars = ax.bar(labels, depths_reached, color=[r["color"] for r in results], alpha=0.85, width=0.4)
    for bar, d in zip(bars, depths_reached):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"Depth {d}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.axhline(y=MAX_DEPTH, color='#ff6060', linestyle='--', linewidth=1, alpha=0.7, label=f'Max depth = {MAX_DEPTH}')
    ax.legend()
    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "curriculum_progression.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _plot_combined(results):
    """Single combined figure for the thesis (loss + solve rates side by side)."""
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle(
        "Curriculum Learning Ablation: Effect of Model Size and Dataset Size\n"
        "MSc Thesis — AI-Based Optimal Solver for the 3×3 Rubik's Cube — Edward Ogbei",
        fontsize=12, y=1.01,
    )

    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)

    # Left: loss curves
    ax_loss = fig.add_subplot(gs[0, 0])
    ax_loss.set_title("Training Loss Curves", fontsize=11)
    ax_loss.set_xlabel("Cumulative Training Epoch")
    ax_loss.set_ylabel("Cross-Entropy Loss")
    ax_loss.grid(True)
    for r in results:
        ax_loss.plot(r["loss_history"], label=r["label"], color=r["color"], linewidth=1.6)
    ax_loss.legend(fontsize=7, loc='upper right')

    # Right: solve-rate bars
    ax_bars = fig.add_subplot(gs[0, 1])
    ax_bars.set_title("Final Solve Rate per Scramble Depth", fontsize=11)
    ax_bars.set_xlabel("Scramble Depth")
    ax_bars.set_ylabel("Solve Rate (%)")
    ax_bars.set_ylim(0, 110)
    ax_bars.grid(True, axis='y')

    depths = list(range(1, MAX_DEPTH + 1))
    n = len(results)
    width = 0.25
    offsets = np.linspace(-(n - 1) * width / 2, (n - 1) * width / 2, n)
    for i, r in enumerate(results):
        rates = [r["final_solve_rates"].get(d, 0) * 100 for d in depths]
        ax_bars.bar([d + offsets[i] for d in depths], rates, width=width,
                    color=r["color"], alpha=0.85, label=r["label"])
    ax_bars.axhline(y=80, color='#ffcc44', linestyle='--', linewidth=1, alpha=0.7, label='80% threshold')
    ax_bars.set_xticks(depths)
    ax_bars.legend(fontsize=7, loc='upper right')

    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "thesis_combined.png")
    fig.savefig(path, dpi=180, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Save raw results to JSON (for reproducibility / thesis appendix)
# ---------------------------------------------------------------------------

def save_results_json(results):
    os.makedirs(PLOT_DIR, exist_ok=True)
    serialisable = []
    for r in results:
        serialisable.append({
            "label": r["label"],
            "short": r["short"],
            "n_params": r["n_params"],
            "samples_per_depth": r["samples_per_depth"],
            "loss_history": [float(x) for x in r["loss_history"]],
            "depth_results": [
                {k: (float(v) if isinstance(v, float) else v) for k, v in dr.items()}
                for dr in r["depth_results"]
            ],
            "final_solve_rates": {str(k): float(v) for k, v in r["final_solve_rates"].items()},
        })
    path = os.path.join(PLOT_DIR, "experiment_results.json")
    with open(path, "w") as f:
        json.dump(serialisable, f, indent=2)
    print(f"  Results saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Curriculum learning ablation experiments")
    parser.add_argument("--quick", action="store_true",
                        help="Use tiny samples/epochs for a fast smoke-test")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if str(device) == "cpu":
        print("Note: running on CPU. Full experiments may take 30-90 minutes.")
        print("      Use --quick for a 2-minute smoke test.")

    all_results = []
    for cfg in EXPERIMENTS:
        result = run_experiment(cfg, quick=args.quick, device=device)
        all_results.append(result)

    print("\nGenerating plots...")
    make_plots(all_results)
    save_results_json(all_results)

    print("\nSummary:")
    print(f"{'Model':<45} {'Params':>8} {'Samples/D':>10} {'Depth Reached':>14}")
    print("-" * 80)
    for r in all_results:
        dr = r["depth_results"]
        reached = max((d["depth"] for d in dr if d["solve_rate"] >= LOSS_THRESHOLD), default=0)
        print(f"{r['label']:<45} {r['n_params']:>8,} {r['samples_per_depth']:>10,} {reached:>14}")


if __name__ == "__main__":
    main()
