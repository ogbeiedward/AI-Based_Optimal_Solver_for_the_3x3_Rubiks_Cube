"""
HUMAN-READABLE DESCRIPTION:
This script is used to benchmark and compare our custom AI solver against the mathematically perfect Kociemba algorithm to evaluate performance and efficiency.
"""

"""
ai_vs_kociemba.py
-----------------
Comparative evaluation of the AI solver vs the Kociemba two-phase solver.

Compares across scramble depths 1 to 5:
  - Solve rate
  - Average number of moves
  - Average solve time
  - Maximum depth solved

Also includes:
  - Failure analysis (which depths fail, why)
  - Confidence distribution of the AI solver
  - Statistical summary

Usage:
    python -m experiments.ai_vs_kociemba [--num-tests 50] [--max-depth 5] [--model-path model.pth]
"""

import argparse
import sys
import os
import time
import statistics
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from core.cube import CubieCube
from utils.scramble import generate_scramble_at_depth
from solvers.kociemba_solver import solve_with_kociemba
from solvers.ai_solver import RubiksMLP, solve_with_ai


def compare_solvers(model, num_tests=50, max_depth=5, seed=42, device=None):
    """
    Compare AI solver vs Kociemba across multiple scramble depths.

    Args:
        model: trained RubiksMLP instance.
        num_tests: number of test scrambles per depth.
        max_depth: maximum scramble depth to test.
        seed: RNG seed.
        device: torch device.

    Returns:
        dict with comparison results organized by depth.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    rng = random.Random(seed)
    results = {}

    for depth in range(1, max_depth + 1):
        ai_stats = {
            "solved": 0, "times": [], "moves": [],
            "confidences": [], "failures": [],
        }
        koc_stats = {
            "solved": 0, "times": [], "moves": [],
        }

        for t in range(num_tests):
            test_seed = rng.randint(0, 2**31 - 1)
            scramble = generate_scramble_at_depth(depth, seed=test_seed)

            # Create scrambled cube
            cube = CubieCube()
            cube.apply_sequence(scramble)

            # Solve with Kociemba
            koc_result = solve_with_kociemba(cube)
            if koc_result["error"] is None and koc_result["validated"]:
                koc_stats["solved"] += 1
                koc_stats["times"].append(koc_result["solve_time"])
                koc_stats["moves"].append(koc_result["num_moves"])

            # Solve with AI
            ai_result = solve_with_ai(cube, model, max_steps=50, device=device)
            if ai_result["solved"]:
                ai_stats["solved"] += 1
                ai_stats["times"].append(ai_result["solve_time"])
                ai_stats["moves"].append(ai_result["num_moves"])
            else:
                ai_stats["failures"].append({
                    "scramble": scramble,
                    "attempted_moves": ai_result["num_moves"],
                })

            if ai_result["confidences"]:
                ai_stats["confidences"].extend(ai_result["confidences"])

        results[depth] = {
            "num_tests": num_tests,
            "ai": ai_stats,
            "kociemba": koc_stats,
        }

    return results


def print_comparison(results):
    """Print a formatted comparison table."""
    print("\n" + "=" * 80)
    print("  AI vs KOCIEMBA COMPARISON")
    print("=" * 80)

    # Header
    print(f"{'Depth':>6} | {'AI Solve%':>10} {'AI Moves':>10} {'AI Time':>10} | "
          f"{'Koc Solve%':>10} {'Koc Moves':>10} {'Koc Time':>10}")
    print("-" * 80)

    ai_max_depth = 0

    for depth in sorted(results.keys()):
        r = results[depth]
        n = r["num_tests"]

        ai = r["ai"]
        koc = r["kociemba"]

        ai_rate = ai["solved"] / n * 100
        koc_rate = koc["solved"] / n * 100

        ai_avg_moves = statistics.mean(ai["moves"]) if ai["moves"] else 0
        koc_avg_moves = statistics.mean(koc["moves"]) if koc["moves"] else 0

        ai_avg_time = statistics.mean(ai["times"]) if ai["times"] else 0
        koc_avg_time = statistics.mean(koc["times"]) if koc["times"] else 0

        if ai["solved"] > 0:
            ai_max_depth = depth

        print(
            f"{depth:>6} | "
            f"{ai_rate:>9.1f}% {ai_avg_moves:>10.1f} {ai_avg_time:>9.4f}s | "
            f"{koc_rate:>9.1f}% {koc_avg_moves:>10.1f} {koc_avg_time:>9.4f}s"
        )

    print("-" * 80)
    print(f"  AI maximum depth solved: {ai_max_depth}")
    print()

    # Confidence distribution
    print("  AI Confidence Distribution:")
    all_confs = []
    for depth_data in results.values():
        all_confs.extend(depth_data["ai"]["confidences"])

    if all_confs:
        print(f"    Average confidence: {statistics.mean(all_confs):.3f}")
        print(f"    Median confidence:  {statistics.median(all_confs):.3f}")
        print(f"    Min confidence:     {min(all_confs):.3f}")
        print(f"    Max confidence:     {max(all_confs):.3f}")
    else:
        print("    No confidence data available.")

    # Failure analysis
    print("\n  Failure Analysis:")
    total_failures = 0
    for depth in sorted(results.keys()):
        failures = results[depth]["ai"]["failures"]
        total_failures += len(failures)
        if failures:
            print(f"    Depth {depth}: {len(failures)} failures out of {results[depth]['num_tests']}")

    if total_failures == 0:
        print("    No failures recorded.")

    print("=" * 80)


def run_comparison(num_tests=50, max_depth=5, model_path=None, seed=42):
    """
    Public entrypoint called by main.py's `compare` subcommand.

    Loads (or initialises) the AI model, runs compare_solvers(), and
    prints the formatted comparison table.

    Args:
        num_tests:   int, test cubes per depth.
        max_depth:   int, maximum scramble depth.
        model_path:  str or None, path to a saved .pt model file.
        seed:        int, RNG seed.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n  Device: {device}")

    model = RubiksMLP()
    if model_path and os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"  Loaded AI model from: {model_path}")
    else:
        if model_path:
            print(f"  WARNING: Model file '{model_path}' not found.")
        print("  Using UNTRAINED model (AI results will reflect random behaviour).")
    model = model.to(device)
    print(f"  AI model parameters: {model.get_parameter_count():,}")

    results = compare_solvers(
        model,
        num_tests=num_tests,
        max_depth=max_depth,
        seed=seed,
        device=device,
    )
    print_comparison(results)


def main():
    parser = argparse.ArgumentParser(
        description="Compare AI solver vs Kociemba two-phase solver"
    )
    parser.add_argument(
        "--num-tests", type=int, default=50,
        help="Number of test scrambles per depth (default: 50)"
    )
    parser.add_argument(
        "--max-depth", type=int, default=5,
        help="Maximum scramble depth to test (default: 5)"
    )
    parser.add_argument(
        "--model-path", type=str, default="rubiks_model.pth",
        help="Path to the trained model file (default: rubiks_model.pth)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)"
    )
    args = parser.parse_args()

    run_comparison(
        num_tests=args.num_tests,
        max_depth=args.max_depth,
        model_path=args.model_path,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()

