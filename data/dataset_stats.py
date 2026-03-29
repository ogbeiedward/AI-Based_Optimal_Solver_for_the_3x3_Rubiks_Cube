"""
HUMAN-READABLE DESCRIPTION:
Loads a saved curriculum dataset and prints comprehensive statistics:
total samples, per-depth breakdown, move label distribution, and state uniqueness.
"""

"""
dataset_stats.py
----------------
Display statistics for a saved Rubik's Cube curriculum dataset.

Usage (from project root):
    python -m data.dataset_stats data/datasets/dataset_latest.npz
"""

import os
import sys
import numpy as np

from core.state_encoder import MOVE_LABELS


def print_dataset_stats(filepath=None, states=None, labels=None, depths=None):
    """
    Print comprehensive statistics for a curriculum dataset.

    Can be called with a file path (to load) or with pre-loaded arrays.

    Args:
        filepath: str, path to a .npz dataset file (optional).
        states:   np.ndarray (N, 324) float32 (optional, used if filepath=None).
        labels:   np.ndarray (N,)     int64   (optional, used if filepath=None).
        depths:   np.ndarray (N,)     int32   (optional, used if filepath=None).
    """
    if filepath is not None:
        if not os.path.exists(filepath):
            print(f"[ERROR] Dataset file not found: {filepath}")
            return
        data = np.load(filepath)
        states = data["states"]
        labels = data["labels"]
        depths = data["depths"]
        print(f"\n  Dataset file : {filepath}")
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  File size    : {size_mb:.2f} MB")

    N = len(labels)

    print("\n" + "=" * 62)
    print("  CURRICULUM DATASET STATISTICS")
    print("=" * 62)

    # --- Basic overview -------------------------------------------------------
    print(f"\n  Total samples      : {N:,}")
    print(f"  State vector dim   : {states.shape[1]}  (54 facelets x 6 colors)")
    print(f"  Move classes       : {len(MOVE_LABELS)}")

    # --- Depth distribution ---------------------------------------------------
    unique_depths = np.unique(depths)
    print(f"\n  Scramble depth range  : {depths.min()} – {depths.max()} moves")
    print(f"  Mean scramble depth   : {depths.mean():.2f}")
    print()
    print(f"  {'Depth':>6}  {'Samples':>9}  {'Fraction':>9}")
    print(f"  {'-----':>6}  {'---------':>9}  {'---------':>9}")
    for d in sorted(unique_depths):
        n_d = int((depths == d).sum())
        print(f"  {d:>6}  {n_d:>9,}  {n_d/N:>9.1%}")

    # --- Move label distribution -----------------------------------------------
    print()
    print(f"  {'Move':>5}  {'Index':>5}  {'Count':>8}  {'Fraction':>9}")
    print(f"  {'----':>5}  {'-----':>5}  {'-------':>8}  {'---------':>9}")
    for idx, move_name in enumerate(MOVE_LABELS):
        count = int((labels == idx).sum())
        print(f"  {move_name:>5}  {idx:>5}  {count:>8,}  {count/N:>9.1%}")

    # --- State uniqueness ------------------------------------------------------
    # Uniqueness approximation: compare states as byte hashes (fast)
    state_hashes = set()
    for row in states:
        state_hashes.add(row.tobytes())
    n_unique = len(state_hashes)
    print(f"\n  Unique states      : {n_unique:,}  ({n_unique/N:.1%} of total)")

    # --- Class balance ---------------------------------------------------------
    label_counts = np.bincount(labels, minlength=len(MOVE_LABELS))
    max_count = label_counts.max()
    min_count = label_counts.min()
    imbalance_ratio = max_count / max(min_count, 1)
    print(f"  Most common label  : {MOVE_LABELS[label_counts.argmax()]:>4}  "
          f"({max_count:,})")
    print(f"  Rarest label       : {MOVE_LABELS[label_counts.argmin()]:>4}  "
          f"({min_count:,})")
    print(f"  Imbalance ratio    : {imbalance_ratio:.2f}x")

    print("\n" + "=" * 62 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to latest dataset
        default_path = os.path.join(
            os.path.dirname(__file__), "datasets", "dataset_latest.npz"
        )
        print_dataset_stats(filepath=default_path)
    else:
        print_dataset_stats(filepath=sys.argv[1])
