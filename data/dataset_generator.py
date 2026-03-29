"""
HUMAN-READABLE DESCRIPTION:
This module generates the curriculum training dataset for the Rubik's Cube AI solver.
Each sample is (one-hot encoded cube state, next Kociemba move label).
Datasets are generated at increasing difficulty levels and saved as .npz files.
The 80%-replacement strategy keeps the dataset balanced during curriculum scaling.
"""

"""
dataset_generator.py
--------------------
Curriculum dataset generator for the 3x3 Rubik's Cube AI solver.

Dataset format (per sample):
  - state:  numpy array of shape (324,) float32.
            One-hot encode of 54 facelets x 6 colors.
  - label:  int (0-17), index into MOVE_LABELS.
            The NEXT move that Kociemba recommends toward the solution.
  - depth:  int, how many moves away from solved this state was generated at.

Saved as .npz with arrays: 'states', 'labels', 'depths'

Curriculum scaling (80% replacement):
  - When growing from depth N to depth N+1:
    * Keep 20% of the old dataset (random sample)
    * Generate 80% new samples at depth N+1
    * Merge to form the new dataset
"""

import os
import random
import numpy as np

from core.cube import CubieCube
from core.state_encoder import encode_state, ENCODING_DIM, MOVE_TO_INDEX
from solvers.kociemba_solver import get_next_move
from utils.scramble import generate_scramble_at_depth


# Default save directory (relative to project root)
DEFAULT_DATASET_DIR = os.path.join(os.path.dirname(__file__), "datasets")


def generate_samples_at_depth(depth, num_samples, seed=None, bfs_timeout=5.0):
    """
    Generate training samples for exactly one scramble depth.

    For each sample:
      1. Apply `depth` random moves to a solved cube.
      2. Ask Kociemba for the next move toward the solution.
      3. One-hot encode the current state.
      4. Return (state_vec, move_label, depth).

    Args:
        depth:       int, number of scramble moves (= distance from solved).
        num_samples: int, how many samples to generate.
        seed:        optional int for reproducibility.
        bfs_timeout: float, max seconds the BFS solver is allowed per sample.
                     Samples that exceed this are skipped (counted as failed).

    Returns:
        states: np.ndarray  shape (N, 324) float32
        labels: np.ndarray  shape (N,)     int64
        depths: np.ndarray  shape (N,)     int32
        failed: int, how many samples were skipped (solver couldn't solve).
    """
    rng = random.Random(seed)
    states = []
    labels = []
    depths_list = []
    failed = 0

    for i in range(num_samples):
        sample_seed = rng.randint(0, 2**31 - 1)
        scramble = generate_scramble_at_depth(depth, seed=sample_seed)

        cube = CubieCube()
        cube.apply_sequence(scramble)

        # Skip already-solved (depth=0 only edge case)
        if cube.is_solved():
            continue

        # Get next move from Kociemba (with per-sample timeout)
        next_move = get_next_move(cube, timeout=bfs_timeout)
        if next_move is None:
            failed += 1
            continue

        move_idx = MOVE_TO_INDEX.get(next_move)
        if move_idx is None:
            failed += 1
            continue

        state_vec = encode_state(cube)
        states.append(state_vec)
        labels.append(move_idx)
        depths_list.append(depth)

    if len(states) == 0:
        return (
            np.zeros((0, ENCODING_DIM), dtype=np.float32),
            np.zeros(0, dtype=np.int64),
            np.zeros(0, dtype=np.int32),
            failed,
        )

    return (
        np.array(states, dtype=np.float32),
        np.array(labels, dtype=np.int64),
        np.array(depths_list, dtype=np.int32),
        failed,
    )


def merge_with_replacement(old_states, old_labels, old_depths,
                           new_states, new_labels, new_depths,
                           keep_fraction=0.20, seed=None):
    """
    Merge old and new datasets using the 80%-replacement strategy.

    Keeps `keep_fraction` of the old samples (randomly chosen)
    and combines them with all new samples.

    Args:
        old_*:         old dataset arrays (states, labels, depths).
        new_*:         new samples to incorporate.
        keep_fraction: fraction of OLD dataset to keep (default 0.20 = keep 20%).
        seed:          optional int for reproducibility.

    Returns:
        merged states, labels, depths  (all np.ndarray)
    """
    rng = np.random.default_rng(seed)

    n_old = len(old_labels)
    n_keep = max(1, int(n_old * keep_fraction))
    keep_indices = rng.choice(n_old, size=min(n_keep, n_old), replace=False)

    kept_states = old_states[keep_indices]
    kept_labels = old_labels[keep_indices]
    kept_depths = old_depths[keep_indices]

    merged_states = np.concatenate([kept_states, new_states], axis=0)
    merged_labels = np.concatenate([kept_labels, new_labels], axis=0)
    merged_depths = np.concatenate([kept_depths, new_depths], axis=0)

    return merged_states, merged_labels, merged_depths


def save_dataset(states, labels, depths, filepath):
    """Save dataset arrays to a .npz file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    np.savez_compressed(filepath, states=states, labels=labels, depths=depths)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"  Saved: {filepath}  ({size_mb:.2f} MB, {len(labels):,} samples)")


def load_dataset(filepath):
    """
    Load a dataset from a .npz file.

    Returns:
        states: np.ndarray (N, 324) float32
        labels: np.ndarray (N,)     int64
        depths: np.ndarray (N,)     int32
    """
    data = np.load(filepath)
    return data["states"], data["labels"].astype(np.int64), data["depths"].astype(np.int32)


def generate_curriculum_dataset(
    max_depth=5,
    samples_per_depth=1000,
    keep_fraction=0.20,
    dataset_dir=None,
    seed=None,
    verbose=True,
    bfs_timeout=5.0,
):
    """
    Generate a curriculum dataset across depth levels 1 .. max_depth.

    Strategy:
      - Depth 1: generate `samples_per_depth` samples from scratch.
      - Depth N>1: generate `samples_per_depth` new samples, replace 80% of
                   the previous dataset (keep 20%), merge and save.

    Each depth level saves its own snapshot file AND an overwritten
    'latest' file for easy loading.

    Args:
        max_depth:        int, maximum scramble depth (default 5).
        samples_per_depth: int, samples generated at each new depth (default 1000).
        keep_fraction:    float, fraction of old dataset to keep (default 0.20).
        dataset_dir:      str, output directory (default data/datasets/).
        seed:             optional int for reproducibility.
        verbose:          bool, print progress.

    Returns:
        dict with keys:
          'states', 'labels', 'depths'  -> final merged dataset
          'depth_stats'                 -> list of dicts (one per depth)
    """
    if dataset_dir is None:
        dataset_dir = DEFAULT_DATASET_DIR

    os.makedirs(dataset_dir, exist_ok=True)

    rng = random.Random(seed)

    all_states = None
    all_labels = None
    all_depths = None

    depth_stats = []

    for depth in range(1, max_depth + 1):
        depth_seed = rng.randint(0, 2**31 - 1)

        if verbose:
            print(f"\n{'='*60}")
            print(f"  Generating depth {depth}/{max_depth} "
                  f"({samples_per_depth:,} new samples)...")
            print(f"{'='*60}")

        new_states, new_labels, new_depths, failed = generate_samples_at_depth(
            depth=depth,
            num_samples=samples_per_depth,
            seed=depth_seed,
            bfs_timeout=bfs_timeout,
        )

        n_generated = len(new_labels)
        if verbose:
            print(f"  Generated: {n_generated:,}  |  Failed/skipped: {failed:,}")

        if n_generated == 0:
            if verbose:
                print(f"  WARNING: no samples generated at depth {depth}, skipping.")
            continue

        # Merge with replacement
        if all_states is None:
            # First depth: start fresh
            all_states = new_states
            all_labels = new_labels
            all_depths = new_depths
        else:
            if verbose:
                print(f"  Merging: keeping {keep_fraction:.0%} of "
                      f"{len(all_labels):,} old samples + {n_generated:,} new ...")
            all_states, all_labels, all_depths = merge_with_replacement(
                all_states, all_labels, all_depths,
                new_states, new_labels, new_depths,
                keep_fraction=keep_fraction,
                seed=depth_seed,
            )

        if verbose:
            print(f"  Dataset total size: {len(all_labels):,} samples")

        # Save per-depth snapshot
        depth_file = os.path.join(dataset_dir, f"dataset_depth_{depth}.npz")
        save_dataset(all_states, all_labels, all_depths, depth_file)

        stat = {
            "depth": depth,
            "new_samples": n_generated,
            "failed": failed,
            "total_samples": len(all_labels),
        }
        depth_stats.append(stat)

    # Save 'latest' merged dataset
    latest_file = os.path.join(dataset_dir, "dataset_latest.npz")
    if all_states is not None:
        save_dataset(all_states, all_labels, all_depths, latest_file)

    return {
        "states": all_states,
        "labels": all_labels,
        "depths": all_depths,
        "depth_stats": depth_stats,
    }
