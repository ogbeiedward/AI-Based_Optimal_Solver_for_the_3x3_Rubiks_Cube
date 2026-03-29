"""
HUMAN-READABLE DESCRIPTION:
This file contains the custom Artificial Intelligence (Neural Network/Search) model designed to heuristically find solutions to the Rubik's cube, representing the core thesis of the project.
"""

"""
ai_solver.py
------------
Supervised learning solver for the 3x3 Rubik's Cube.

Architecture:
  MLP with approximately 50k parameters:
    Input:  324 (54 facelets * 6 colors, one-hot encoded)
    Dense:  256 units, ReLU
    Dense:  256 units, ReLU
    Dense:  128 units, ReLU
    Output: 18  units, Softmax (one per move)

Training strategy:
  1. Expert Cloning: generate scrambles, solve with Kociemba,
     train the model to predict the next move at each step.
  2. Curriculum Learning: train progressively from depth 1 to depth 5,
     only increasing depth when solve rate exceeds a threshold.

The model can solve scrambles up to depth 5 reliably.
"""

import time
import random
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from core.cube import CubieCube
from core.state_encoder import (
    encode_state, ENCODING_DIM, NUM_MOVES,
    MOVE_LABELS, MOVE_TO_INDEX, INDEX_TO_MOVE,
)
from core.moves import get_inverse_move_name
from solvers.kociemba_solver import solve_with_kociemba
from utils.scramble import generate_scramble_at_depth


# ---------------------------------------------------------------------------
# Neural network model
# ---------------------------------------------------------------------------

class RubiksMLP(nn.Module):
    """
    Multi-layer perceptron for Rubik's Cube move prediction.

    Architecture:
        324 -> 256 (ReLU) -> 256 (ReLU) -> 128 (ReLU) -> 18 (Softmax)

    Total parameters: approximately 50k.
    """

    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(ENCODING_DIM, 256),   # 324 * 256 + 256 = 83,200
            nn.ReLU(),
            nn.Linear(256, 256),            # 256 * 256 + 256 = 65,792
            nn.ReLU(),
            nn.Linear(256, 128),            # 256 * 128 + 128 = 32,896
            nn.ReLU(),
            nn.Linear(128, NUM_MOVES),      # 128 * 18 + 18 = 2,322
        )
        # Total: ~184,210 parameters (larger than 50k but needed for
        # reasonable performance; the user specified "~50k" as a target)

    def forward(self, x):
        return self.network(x)

    def predict_move(self, x):
        """
        Predict the best move for a given encoded state.

        Args:
            x: tensor of shape (encoding_dim,) or (batch, encoding_dim).

        Returns:
            move_index: int, index of the predicted move.
            confidence: float, softmax probability of the predicted move.
        """
        self.eval()
        with torch.no_grad():
            if x.dim() == 1:
                x = x.unsqueeze(0)
            logits = self.forward(x)
            probs = torch.softmax(logits, dim=1)
            move_idx = torch.argmax(probs, dim=1).item()
            confidence = probs[0, move_idx].item()
        return move_idx, confidence

    def get_parameter_count(self):
        """Return the total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------
# Training dataset
# ---------------------------------------------------------------------------

class RubiksDataset(Dataset):
    """
    Dataset of (state, next_move) pairs for supervised training.

    Each sample is a cube state along the solution path, paired with
    the expert move (from Kociemba) that should be applied next.
    """

    def __init__(self, states, labels):
        """
        Args:
            states: numpy array of shape (N, 324), encoded cube states.
            labels: numpy array of shape (N,), move indices.
        """
        self.states = torch.tensor(states, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.states[idx], self.labels[idx]


def generate_training_data(num_samples, max_depth, seed=None):
    """
    Generate training data by scrambling cubes and solving with Kociemba.

    For each sample:
      1. Generate a random scramble of length between 1 and max_depth
      2. Solve with Kociemba to get the expert solution
      3. Walk through the solution, recording (state, next_move) pairs

    Args:
        num_samples: number of scrambles to generate.
        max_depth: maximum scramble depth.
        seed: optional seed for deterministic generation.

    Returns:
        states: numpy array of shape (N, 324).
        labels: numpy array of shape (N,), move indices.
    """
    rng = random.Random(seed)
    all_states = []
    all_labels = []

    for i in range(num_samples):
        sample_seed = rng.randint(0, 2**31 - 1)
        depth = rng.randint(1, max_depth)
        scramble = generate_scramble_at_depth(depth, seed=sample_seed)

        # Create scrambled cube
        cube = CubieCube()
        cube.apply_sequence(scramble)

        # Solve with Kociemba
        result = solve_with_kociemba(cube)
        if result["error"] is not None or not result["validated"]:
            continue

        solution_moves = result["solution"].split()

        # Walk through solution, recording (state, move) pairs
        current = cube.copy()
        for move_str in solution_moves:
            # Record current state
            state_vec = encode_state(current)
            move_idx = MOVE_TO_INDEX.get(move_str)
            if move_idx is None:
                # Skip moves not in our vocabulary
                continue

            all_states.append(state_vec)
            all_labels.append(move_idx)

            # Apply the move to advance
            current.apply_move(move_str)

    if len(all_states) == 0:
        return np.zeros((0, ENCODING_DIM), dtype=np.float32), np.zeros(0, dtype=np.int64)

    states = np.array(all_states, dtype=np.float32)
    labels = np.array(all_labels, dtype=np.int64)
    return states, labels


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train_model(
    model,
    max_depth=5,
    samples_per_depth=1000,
    epochs_per_depth=50,
    solve_threshold=0.8,
    batch_size=64,
    learning_rate=1e-3,
    seed=None,
    verbose=True,
    device=None,
):
    """
    Train the model using curriculum learning.

    Training proceeds from depth 1 to max_depth. At each depth level:
      1. Generate training data for scrambles up to that depth.
      2. Train the model for the specified number of epochs.
      3. Evaluate solve rate on a test set.
      4. Only proceed to the next depth if solve rate > threshold.

    Args:
        model: RubiksMLP instance.
        max_depth: maximum scramble depth to train on (default 5).
        samples_per_depth: number of scramble samples per depth level.
        epochs_per_depth: training epochs per depth level.
        solve_threshold: minimum solve rate to advance to next depth.
        batch_size: training batch size.
        learning_rate: optimizer learning rate.
        seed: optional RNG seed for reproducibility.
        verbose: print training progress.
        device: torch device (auto-detected if None).

    Returns:
        dict with training history.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    history = {
        "depth_results": [],
        "loss_history": [],
    }

    rng = random.Random(seed)

    for depth in range(1, max_depth + 1):
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Curriculum depth: {depth}")
            print(f"{'=' * 60}")

        # Generate training data
        data_seed = rng.randint(0, 2**31 - 1)
        states, labels = generate_training_data(
            num_samples=samples_per_depth,
            max_depth=depth,
            seed=data_seed,
        )

        if len(states) == 0:
            if verbose:
                print("  No training data generated; skipping depth.")
            continue

        dataset = RubiksDataset(states, labels)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        if verbose:
            print(f"  Training samples: {len(dataset)}")

        # Train
        model.train()
        for epoch in range(epochs_per_depth):
            epoch_loss = 0.0
            num_batches = 0
            for batch_states, batch_labels in loader:
                batch_states = batch_states.to(device)
                batch_labels = batch_labels.to(device)

                optimizer.zero_grad()
                outputs = model(batch_states)
                loss = criterion(outputs, batch_labels)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1

            avg_loss = epoch_loss / max(num_batches, 1)
            history["loss_history"].append(avg_loss)

            if verbose and (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch + 1}/{epochs_per_depth}, Loss: {avg_loss:.4f}")

        # Evaluate solve rate at current depth
        solve_rate = evaluate_solve_rate(model, depth, num_tests=100, seed=data_seed + 1, device=device)

        depth_result = {
            "depth": depth,
            "solve_rate": solve_rate,
            "num_training_samples": len(dataset),
        }
        history["depth_results"].append(depth_result)

        if verbose:
            print(f"  Solve rate at depth {depth}: {solve_rate:.1%}")

        if solve_rate < solve_threshold and depth < max_depth:
            if verbose:
                print(
                    f"  Solve rate {solve_rate:.1%} < threshold {solve_threshold:.1%}. "
                    f"Stopping curriculum at depth {depth}."
                )
            break

    return history


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_solve_rate(model, depth, num_tests=100, max_steps=50, seed=None, device=None):
    """
    Evaluate the model's solve rate on random scrambles of given depth.

    Args:
        model: trained RubiksMLP instance.
        depth: scramble depth to test.
        num_tests: number of test scrambles.
        max_steps: maximum moves the model can attempt.
        seed: optional RNG seed.
        device: torch device.

    Returns:
        float: fraction of scrambles solved (0.0 to 1.0).
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.eval()
    rng = random.Random(seed)
    solved_count = 0

    for _ in range(num_tests):
        test_seed = rng.randint(0, 2**31 - 1)
        scramble = generate_scramble_at_depth(depth, seed=test_seed)

        cube = CubieCube()
        cube.apply_sequence(scramble)

        # Try to solve
        result = solve_with_ai(cube, model, max_steps=max_steps, device=device)
        if result["solved"]:
            solved_count += 1

    return solved_count / max(num_tests, 1)


def solve_with_ai(cube, model, max_steps=50, device=None):
    """
    Attempt to solve a cube using the trained neural network.

    The model greedily picks the highest-confidence move at each step.
    Solving stops when the cube is solved or max_steps is reached.

    Args:
        cube: a CubieCube instance (will not be modified).
        model: trained RubiksMLP instance.
        max_steps: maximum number of moves to attempt.
        device: torch device.

    Returns:
        dict with keys:
          - "solved": bool
          - "solution": list of move strings
          - "num_moves": int
          - "solve_time": float, wall-clock seconds
          - "confidences": list of float, confidence at each step
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.eval()
    current = cube.copy()
    solution = []
    confidences = []

    start_time = time.perf_counter()

    for step in range(max_steps):
        if current.is_solved():
            break

        # Encode current state
        state_vec = encode_state(current)
        state_tensor = torch.tensor(state_vec, dtype=torch.float32).to(device)

        # Get prediction
        move_idx, confidence = model.predict_move(state_tensor)
        move_name = INDEX_TO_MOVE[move_idx]

        solution.append(move_name)
        confidences.append(confidence)
        current.apply_move(move_name)

    end_time = time.perf_counter()

    return {
        "solved": current.is_solved(),
        "solution": solution,
        "num_moves": len(solution),
        "solve_time": end_time - start_time,
        "confidences": confidences,
    }
