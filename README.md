---
title: AI Rubiks Cube Solver
emoji: 🧩
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# AI-Based Optimal Solver for the 3x3 Rubik's Cube

M.Sc. Thesis project by Edward Ogbei, Politechnika Czestochowa (PCZ), 2026.

The project trains a neural network to solve the 3x3 Rubik's Cube from scratch using
curriculum learning - starting with 1-move scrambles and working up to depth 8 as
the model earns each level. It then compares the AI solver against the classical
Kociemba algorithm across solve rate, solve time, and solution length.

---

## What this project does

- **Cube engine** - a full mathematical model of the 3x3 cube using cubie permutations
  and orientations (cp, co, ep, eo). Enforces all group-theory legality constraints.
- **AI solver** - a 184k-parameter MLP trained on Kociemba-generated expert moves.
  Two inference modes: greedy (fastest) and beam search (more thorough).
- **Curriculum learning** - the model advances to harder scrambles only when it clears
  an 80% solve-rate threshold on a fresh test set. If it can't clear the threshold,
  curriculum stops - this reveals the model's exact capacity ceiling.
- **3D web UI** - Three.js frontend with animated step-by-step solve, light theme,
  and a live benchmark comparison table.
- **Experiment suite** - ablation study across three model sizes (50k, 100k, 184k params)
  with full loss curves and solve-rate plots.

---

## Benchmark results (20 trials per depth, measured on CPU)

| Depth | Kociemba | AI Greedy | AI Beam (w=5) | Kociemba time | AI Greedy time |
|------:|:--------:|:---------:|:-------------:|:-------------:|:--------------:|
| 1     | 100%     | 100%      | 100%          | 0.20 ms       | 0.69 ms        |
| 2     | 100%     | 100%      | 100%          | 0.45 ms       | 1.18 ms        |
| 3     | 100%     | 100%      | 100%          | 2.28 ms       | 1.74 ms        |
| 4     | 100%     | 95%       | 100%          | 6.26 ms       | 3.65 ms        |
| 5     | 100%     | 55%       | 60%           | 26.0 ms       | 2.91 ms        |
| 6     | 100%     | 40%       | 50%           | 86.7 ms       | 3.73 ms        |
| 7     | 100%     | 10%       | 25%           | 379.8 ms      | 3.08 ms        |
| 8     | 100%     | 5%        | 10%           | 887.6 ms      | 2.45 ms        |
| 9     | 100%     | 5%        | 10%           | 4359 ms       | 5.26 ms        |
| 10    | 100%     | 0%        | 0%            | 10034 ms      | - ms           |

Key observation: the AI solver is significantly faster than Kociemba at every depth
(0.7 ms vs 380 ms at depth 7), but trades that speed for accuracy. Kociemba always
finds the optimal solution; the AI model is reliable up to depth 4-5 and degrades
beyond that - exactly what the curriculum learning analysis predicts.

Beam search (w=5) consistently outperforms greedy at depths 4-7 by keeping 5 candidate
paths alive simultaneously, catching cases where the single greedy pick leads to a dead end.

---

## Getting started

### Install dependencies
```bash
pip install -r requirements.txt
```

### Launch the interactive 3D viewer
```bash
python main.py visualize --web
```
Then open http://localhost:8080 in your browser.

### Validate the cube engine
```bash
python main.py validate
```

### Train the AI model
```bash
python main.py train --max-depth 8 --samples 30000 --epochs 50
```
The model trains progressively from depth 1 to 8, advancing only when the 80%
solve-rate threshold is cleared.

### Run the ablation experiments
```bash
python -m experiments.curriculum_experiments
```
Trains three model sizes (small/medium/large) and generates comparison plots in
`experiments/plots/`.

### Benchmark AI vs Kociemba
```bash
python main.py compare --num-tests 50 --max-depth 8
```

---

## Project structure

```
core/           Cube engine: CubieCube, moves, state encoder
data/           Dataset generator and statistics tools
solvers/        AI solver (MLP + beam search) and Kociemba (BFS)
experiments/    Ablation experiments and benchmark scripts
visualization/  Three.js web UI and HTTP server
utils/          Scramble utilities
tests/          Unit tests
docs/           Thesis, evaluation results, figures
```

---

## Model details

- Architecture: 324 inputs -> 256 -> 256 -> 128 -> 18 outputs (one per move)
- Parameters: 184,210
- Training: curriculum learning, depth 1 to 5 with default settings
- Dataset: expert moves from Kociemba BFS solver, one-hot encoded facelet states
- Advancement criterion: solve rate >= 80% on a fresh 100-sample test set
