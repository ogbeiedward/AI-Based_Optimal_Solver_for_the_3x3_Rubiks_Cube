"""
HUMAN-READABLE DESCRIPTION:
This script runs massive batches of scrambles through the Kociemba solver to gather statistical data on solve speeds and average move counts.
"""

"""
kociemba_benchmark.py
---------------------
Benchmark the Kociemba two-phase algorithm on random scrambles.

Collects statistics on:
  - Solve time (average, min, max, std)
  - Solution length in moves (average, min, max, std)
  - Validation success rate

Usage:
    python -m experiments.kociemba_benchmark [--num-scrambles 100] [--seed 42]
"""

import argparse
import sys
import time
import statistics

# Add parent directory to path for imports
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cube import CubieCube
from utils.scramble import generate_scramble
from solvers.kociemba_solver import solve_with_kociemba


def run_benchmark(num_scrambles=100, seed=42, verbose=True):
    """
    Benchmark Kociemba solver on random scrambles.

    Args:
        num_scrambles: number of random scrambles to solve.
        seed: RNG seed for deterministic scramble generation.
        verbose: print progress and results.

    Returns:
        dict with benchmark statistics.
    """
    solve_times = []
    solution_lengths = []
    validated_count = 0
    error_count = 0

    for i in range(num_scrambles):
        scramble = generate_scramble(seed=seed + i)
        cube = CubieCube()
        cube.apply_sequence(scramble)

        result = solve_with_kociemba(cube)

        if result["error"] is not None:
            error_count += 1
            if verbose:
                print(f"  Scramble {i + 1}: ERROR: {result['error']}")
            continue

        solve_times.append(result["solve_time"])
        solution_lengths.append(result["num_moves"])

        if result["validated"]:
            validated_count += 1

        if verbose and (i + 1) % 20 == 0:
            print(f"  Completed {i + 1}/{num_scrambles} scrambles...")

    # Compute statistics
    stats = {
        "num_scrambles": num_scrambles,
        "num_solved": len(solve_times),
        "num_errors": error_count,
        "num_validated": validated_count,
        "validation_rate": validated_count / max(len(solve_times), 1),
    }

    if solve_times:
        stats["time_avg"] = statistics.mean(solve_times)
        stats["time_min"] = min(solve_times)
        stats["time_max"] = max(solve_times)
        stats["time_std"] = statistics.stdev(solve_times) if len(solve_times) > 1 else 0.0
        stats["time_median"] = statistics.median(solve_times)

    if solution_lengths:
        stats["length_avg"] = statistics.mean(solution_lengths)
        stats["length_min"] = min(solution_lengths)
        stats["length_max"] = max(solution_lengths)
        stats["length_std"] = statistics.stdev(solution_lengths) if len(solution_lengths) > 1 else 0.0
        stats["length_median"] = statistics.median(solution_lengths)

    return stats


def print_results(stats):
    """Print benchmark results in a formatted table."""
    print("\n" + "=" * 60)
    print("  KOCIEMBA BENCHMARK RESULTS")
    print("=" * 60)
    print(f"  Total scrambles:     {stats['num_scrambles']}")
    print(f"  Successfully solved: {stats['num_solved']}")
    print(f"  Errors:              {stats['num_errors']}")
    print(f"  Validated:           {stats['num_validated']}")
    print(f"  Validation rate:     {stats['validation_rate']:.1%}")
    print()

    if "time_avg" in stats:
        print("  Solve Time (seconds):")
        print(f"    Average:  {stats['time_avg']:.6f}")
        print(f"    Median:   {stats['time_median']:.6f}")
        print(f"    Min:      {stats['time_min']:.6f}")
        print(f"    Max:      {stats['time_max']:.6f}")
        print(f"    Std Dev:  {stats['time_std']:.6f}")
        print()

    if "length_avg" in stats:
        print("  Solution Length (moves):")
        print(f"    Average:  {stats['length_avg']:.1f}")
        print(f"    Median:   {stats['length_median']:.1f}")
        print(f"    Min:      {stats['length_min']}")
        print(f"    Max:      {stats['length_max']}")
        print(f"    Std Dev:  {stats['length_std']:.1f}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark the Kociemba two-phase solver"
    )
    parser.add_argument(
        "--num-scrambles", type=int, default=100,
        help="Number of random scrambles to solve (default: 100)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for deterministic scrambles (default: 42)"
    )
    args = parser.parse_args()

    print(f"Running Kociemba benchmark with {args.num_scrambles} scrambles...")
    stats = run_benchmark(
        num_scrambles=args.num_scrambles,
        seed=args.seed,
    )
    print_results(stats)


if __name__ == "__main__":
    main()
