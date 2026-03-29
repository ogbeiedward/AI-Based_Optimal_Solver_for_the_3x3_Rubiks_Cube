# AI-Based Optimal Solver for the 3x3 Rubik's Cube

This repository contains the implementation of my M.Sc. Thesis project, which focuses on developing an optimal solver for the 3x3 Rubik's Cube using a hybrid approach of classical computational algorithms and neural network heuristics.

## Project Overview

The system provides a comprehensive framework for Rubik's Cube simulation and solving:

- **Cube Engine:** A robust mathematical model that manages cubie permutations and orientations, enforcing all group-theoretical invariants and legality constraints.
- **AI Solver:** A Multi-Layer Perceptron (MLP) trained via curriculum learning to predict optimal move sequences.
- **3D Visualization:** An interactive web-based interface built with Three.js and a Python backend for real-time state visualization.
- **Experimental Suite:** Tools for benchmarking the AI solver against the mathematically optimal Kociemba algorithm.

## Getting Started

### 1. Installation
Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Interactive Visualization
Launch the visualization server to interact with the 3D cube:
```bash
python main.py visualize --web
```
Access the interface at `http://localhost:8080`.

### 3. Core Engine Validation
Verify the mathematical integrity of the cube engine:
```bash
python main.py validate
```

### 4. Performance Comparison
Execute the benchmarking script to evaluate the AI solver's efficiency across various scramble depths:
```bash
python main.py compare --num-tests 50 --max-depth 5
```

For detailed architectural information, please refer to the `docs/` directory.
