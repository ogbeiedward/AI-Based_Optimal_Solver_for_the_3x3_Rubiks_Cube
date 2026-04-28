# AI-Based Optimal Solver for the 3x3 Rubik's Cube
## Full Project Explanation

**Author:** Edward Ogbei
**Programme:** M.Sc. Artificial Intelligence
**Supervisor:** Prof. Krzysztof Rojek, PCZ

---

## Table of Contents

1. What the Project Does
2. Why the Rubik's Cube is a Hard Problem
3. The Cube Simulator
4. The Move Engine
5. State Encoding (One-Hot Vectors)
6. The Dataset Generator
7. The Kociemba Solver (Classical Algorithm)
8. The AI Solver (Neural Network)
9. The 3D Visualization System
10. The Benchmarking and Experiments
11. The Test Suite
12. Libraries and Tools Used
13. How Everything Connects

---

## 1. What the Project Does

This project builds a complete system that can simulate, scramble, and solve a 3x3 Rubik's Cube using two completely different approaches: a classical algorithm (bidirectional BFS, inspired by the Kociemba two-phase method) and a trained neural network (a Multi-Layer Perceptron).

The two solvers are compared against each other in a benchmarking suite to measure solve rate, number of moves, and time. The whole system is viewable through an interactive 3D web interface where you can scramble the cube, apply individual moves, and watch either solver animate its solution in real time.

The project covers the full pipeline: mathematical model, data generation, machine learning training, evaluation, and interactive visualization.

---

## 2. Why the Rubik's Cube is a Hard Problem

A standard 3x3 Rubik's Cube has exactly **43,252,003,274,489,856,000** legal configurations. That is approximately 43 quintillion states.

Despite this enormous number, it has been mathematically proven that every single one of those states can be solved in at most 20 moves. That number (20) is called **God's Number**. The challenge is finding that short solution without trying all possible paths.

The state space is too large to search exhaustively. Even with a fast computer checking one million states per second, brute-forcing all states would take over a billion years. This is why smart algorithms and learned heuristics are necessary.

Additionally, not all combinations of pieces are physically reachable. If you disassemble a cube and reassemble it randomly, there is only a 1-in-12 chance the result is a legal state. This means any solver must understand the mathematical constraints that govern valid cube states. The key constraints are:

- Corner orientations must sum to a multiple of 3
- Edge orientations must sum to a multiple of 2
- The permutation parity of corners must equal the permutation parity of edges

These are enforced throughout the project.

---

## 3. The Cube Simulator

**File:** `core/cube.py`, `core/cubie.py`, `core/moves.py`

### What it is

The cube simulator is a mathematical model of the Rubik's Cube stored entirely in memory as four arrays. It does not store colours directly. Instead it stores the positions and orientations of the physical pieces (cubies).

### Why cubie-level representation?

There are two common ways to model a Rubik's Cube:

1. **Facelet grid** (naive): Store 54 coloured stickers in a flat array. Simple, but moves become complex transformations and it is easy to create illegal states accidentally.

2. **Cubie-level model** (this project): Store the actual pieces (corners and edges) and track where each piece is and how it is twisted. This is the standard used in academic and competitive solving research because it directly encodes the group-theoretical structure of the cube.

The cubie model was chosen because it makes legality checking trivial, interfaces naturally with the Kociemba algorithm, and is the correct abstraction for teaching a neural network about the cube's structure.

### The four arrays

The cube state is stored in exactly four arrays:

| Array | Size | Meaning |
|---|---|---|
| `cp` (corner permutation) | 8 integers | Which corner piece is in each of the 8 corner slots |
| `co` (corner orientation) | 8 integers | How each corner is twisted (0, 1, or 2 representing 0, 120, or 240 degrees) |
| `ep` (edge permutation) | 12 integers | Which edge piece is in each of the 12 edge slots |
| `eo` (edge orientation) | 12 integers | Whether each edge is flipped (0 = correct, 1 = flipped) |

A solved cube has `cp = [0,1,2,3,4,5,6,7]`, `co = [0,0,0,0,0,0,0,0]`, and similarly for edges. Any scramble produces a different set of values in these arrays.

### The eight corners

The eight corners are named by the three faces they touch: URF (Up-Right-Front), UFL, ULB, UBR, DFR, DLF, DBL, DRB. This naming convention comes from Kociemba's algorithm and is standard in the field.

### The twelve edges

Similarly, the twelve edges are named by two faces: UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR.

### Legality checking

After any operation, the cube can be tested with `is_legal()`. This checks:
- Whether the corner orientation sum is divisible by 3
- Whether the edge orientation sum is even
- Whether the permutation parities match

This is used in validation, in the scramble generator, and in the web interface status display.

---

## 4. The Move Engine

**File:** `core/moves.py`

### What it is

The move engine defines all 18 standard Rubik's Cube moves and how they transform the cube state. Every move is described as a set of permutation cycles applied to the four arrays.

### Why 18 moves?

The six faces (U, D, R, L, F, B) each have three variants:
- A clockwise quarter turn (e.g., R)
- A counter-clockwise quarter turn (e.g., R')
- A half turn (e.g., R2)

That gives 6 x 3 = 18 moves. These 18 moves form a generating set for the entire Rubik's Cube group, meaning any legal state can be reached from any other state using only these moves.

### How a move works

Every move is stored as a `MoveDefinition` object containing:
- **Corner permutation cycle**: which corner slots exchange positions
- **Corner orientation deltas**: how much each affected corner twists (+0, +1, or +2 mod 3)
- **Edge permutation cycle**: which edge slots exchange positions
- **Edge orientation deltas**: whether affected edges flip (0 or 1)

When you apply, for example, the R move:
1. The four corners in the right layer cycle through their slots
2. Those corners also receive orientation changes (R moves twist corners by +1 or +2)
3. The four edges in the right layer cycle through their slots
4. R moves do not flip edges, so orientation deltas are zero

The L, R, F, B moves all affect corner and sometimes edge orientations. The U and D moves do not change orientations at all because turning the top or bottom face does not physically twist corners or flip edges.

### Helper functions

The move engine also provides:
- `compose_moves()`: mathematically combine two moves into one
- `invert_move()`: compute the inverse of any move
- `get_inverse_move_name()`: return the name of the inverse (R becomes R', R2 becomes R2)

---

## 5. State Encoding (One-Hot Vectors)

**File:** `core/state_encoder.py`

### What it is

The neural network cannot accept arrays of positions and orientations directly as input. It needs a fixed-size numerical vector. The state encoder converts the cube into a 324-dimensional vector using one-hot encoding.

### What one-hot encoding means

The cube has 54 visible sticker positions (9 per face, 6 faces). Each sticker shows one of six colours: White (U face), Red (R face), Green (F face), Yellow (D face), Orange (L face), Blue (B face).

One-hot encoding represents each colour as a vector of six binary values where exactly one value is 1 and the rest are 0:

| Colour | Encoding |
|---|---|
| White | [1, 0, 0, 0, 0, 0] |
| Red | [0, 1, 0, 0, 0, 0] |
| Green | [0, 0, 1, 0, 0, 0] |
| Yellow | [0, 0, 0, 1, 0, 0] |
| Orange | [0, 0, 0, 0, 1, 0] |
| Blue | [0, 0, 0, 0, 0, 1] |

For all 54 stickers, this produces 54 x 6 = **324 values**. This is the input to the neural network.

### Why one-hot instead of integers?

You could encode colours as integers (White = 0, Red = 1, etc.) and get a 54-element vector. However, this would imply an ordering relationship that does not exist. White is not "less than" Red in any meaningful way. One-hot encoding avoids this by giving each colour an independent dimension. The neural network learns separate weights for each colour at each position, which is more expressive.

### The output labels

The encoder also defines `MOVE_LABELS`, an ordered list of all 18 move names. The neural network outputs a probability distribution over these 18 moves. `MOVE_TO_INDEX` maps move names to integers (0 to 17) and `INDEX_TO_MOVE` does the reverse.

---

## 6. The Dataset Generator

**Files:** `data/dataset_generator.py`, `data/dataset_stats.py`

### The core idea: expert cloning

The training data is generated by asking the Kociemba solver what the best next move is from any given scrambled state. The neural network then learns to imitate the expert. This technique is called **behavioural cloning** or **imitation learning**.

For each training sample:
1. A cube is scrambled by N random moves
2. The Kociemba solver is called and finds the full solution
3. The first move of that solution is recorded as the correct label
4. The cube state is one-hot encoded as the input

The dataset is a collection of (encoded state, correct next move) pairs.

### Curriculum learning

Training a neural network on random 20-move scrambles from scratch does not work well. The problem is too hard initially. Instead, the training follows a curriculum:

1. Start with depth 1 (one move from solved). These are trivially easy.
2. Once the model solves depth 1 reliably, add depth 2 samples.
3. Continue increasing difficulty only when performance at the current depth exceeds 80%.

This mirrors how a human would learn: starting from nearly-solved positions and gradually adding complexity.

### The 80% replacement strategy

As the curriculum advances from depth N to depth N+1, the dataset is updated as follows:
- 80% of the new dataset is freshly generated samples at the new depth
- 20% is kept from the previous dataset

This ensures the model does not forget how to solve easy states while learning harder ones. The phenomenon of forgetting previously learned skills is called **catastrophic forgetting** in machine learning, and the replacement strategy partially mitigates it.

The saved dataset files (`data/datasets/dataset_depth_1.npz` through `dataset_depth_8.npz`) contain the cumulative training data at each stage of the curriculum.

### Dataset statistics

`data/dataset_stats.py` loads any saved `.npz` dataset and prints a full report including:
- Total sample count and vector dimensions
- How many samples come from each depth level
- The distribution of move labels (to detect class imbalance)
- The number of unique cube states in the dataset

---

## 7. The Kociemba Solver (Classical Algorithm)

**File:** `solvers/kociemba_solver.py`, `solvers/bfs_solver.py`

### What it is

The classical solver uses **bidirectional BFS (Breadth-First Search)** to find the shortest solution to any scrambled cube state. It is inspired by the Kociemba two-phase algorithm, which is the industry standard for near-optimal Rubik's Cube solving.

### Why bidirectional BFS?

Standard BFS explores from the scrambled state outward, trying all possible move sequences until it finds the solved state. The problem is that the cube has 18 possible moves at each step, so the search tree grows as 18^N where N is the depth. At depth 10, that is 18^10 = 3.5 trillion nodes.

Bidirectional BFS solves this by searching simultaneously from both ends: forward from the scrambled state and backward from the solved state. The two frontiers meet in the middle. This reduces the effective search depth to N/2, so the tree size drops from 18^N to 2 x 18^(N/2). At depth 10 this is 2 x 18^5 = 3.4 million nodes, roughly a million times faster.

### How the solver represents state

For performance, the cube state is converted from a `CubieCube` object into a plain Python tuple of 40 integers (8 cp + 8 co + 12 ep + 12 eo). Tuples are hashable and can be stored in sets, making the frontier lookups O(1). Using sets instead of lists for the frontier is critical to performance.

### Move pruning

The solver avoids obviously redundant move sequences:
- Never apply two moves to the same face consecutively (e.g., R followed by R is pointless; use R2 directly)
- When two opposite faces are turned (e.g., R and L), always apply them in a fixed canonical order to avoid counting the same position twice through different paths

### Precomputed move tables

Rather than constructing a `CubieCube` object for each step, the solver precomputes a dictionary mapping every (state tuple, move name) pair to the resulting state tuple. This avoids object creation overhead in the inner search loop.

### The history-based shortcut

When the web interface is used and the cube's scramble history is available, the solver skips the BFS entirely and simply reverses the history. For example, if the user applied R, U, F, the solution is F', U', R'. This is instantaneous and is the primary mode used in the interactive demo.

---

## 8. The AI Solver (Neural Network)

**Files:** `solvers/ai_solver.py`, `train_on_colab.ipynb`

### Architecture: Multi-Layer Perceptron (MLP)

The neural network is a fully-connected feedforward network with the following layers:

```
Input:   324 units  (one-hot encoded cube state)
Dense:   256 units  (ReLU activation)
Dense:   256 units  (ReLU activation)
Dense:   128 units  (ReLU activation)
Output:   18 units  (one score per move)
```

Total trainable parameters: approximately 184,000.

### Why an MLP and not a CNN or RNN?

A **Convolutional Neural Network (CNN)** is designed for data with spatial locality, where nearby elements are more related than distant ones (like image pixels). The Rubik's Cube state, encoded as a flat 324-vector of sticker values, does not have this property. The top-left sticker of the top face and the top-right sticker of the front face are physically adjacent on the cube, but distant in the flat vector. CNNs would not capture the relevant structure well.

A **Recurrent Neural Network (RNN)** is designed for sequential data where past context matters (like text or audio). The cube state at a single moment is a fixed snapshot, not a sequence. An RNN would add unnecessary complexity.

An **MLP** takes the full state vector and learns arbitrary non-linear mappings from it to move probabilities. With enough hidden units it can, in principle, represent any function of the input. Given the modest problem size (324 inputs, 18 outputs), an MLP with three hidden layers is appropriate and trainable on a standard CPU or free GPU (Google Colab).

### Why ReLU activation?

ReLU (Rectified Linear Unit) applies the function f(x) = max(0, x). It is used because:
- It is computationally cheap (a single comparison)
- It avoids the vanishing gradient problem that affects sigmoid and tanh activations in deep networks
- It allows gradients to flow cleanly during backpropagation, enabling faster learning

### Why Cross-Entropy Loss?

The problem is framed as a classification task: given a cube state, which of the 18 moves should be applied next? Cross-entropy loss is the standard loss function for classification problems. It measures how well the model's predicted probability distribution matches the correct label. Minimising it pushes the model to assign high probability to the correct move.

### Why the Adam optimiser?

Adam (Adaptive Moment Estimation) is a gradient descent variant that maintains a per-parameter adaptive learning rate. It converges faster than plain SGD for most neural network tasks and requires less manual tuning of the learning rate. A learning rate of 0.001 is used, which is the widely accepted default for Adam.

### Training process

Training uses the curriculum strategy described in Section 6. At each depth level:

1. Generate (state, next move) pairs from Kociemba solutions
2. Train for 50 epochs using batches of 64 samples
3. After training, evaluate the solve rate: apply the trained model greedily to 100 randomly scrambled cubes at the current depth and count how many are solved within 50 moves
4. If the solve rate exceeds 80%, advance to the next depth

### Greedy inference (solving with the AI)

At inference time, the model solves a cube as follows:
1. Encode the current cube state as a 324-vector
2. Pass it through the network to get 18 output scores
3. Apply softmax to convert scores to probabilities
4. Choose the move with the highest probability (greedy selection)
5. Apply that move to the cube
6. Repeat until the cube is solved or 50 moves have been attempted

This is called **greedy search** because it always picks the locally best move without looking ahead. It works well for shallow scrambles (depth 1 to 4, where the model achieves 100% solve rate) but can fail on deeper scrambles where a short-term suboptimal move would lead to a better outcome later.

### Training on Google Colab

The file `train_on_colab.ipynb` is a Jupyter notebook configured for Google Colab's free GPU environment. Training on GPU is approximately 10 to 20 times faster than on CPU. The notebook mounts the user's Google Drive, installs dependencies, generates the dataset, trains the model, and saves the resulting `.pt` file back to Drive.

---

## 9. The 3D Visualization System

**Files:** `visualization/server.py`, `visualization/index.html`, `visualization/renderer3d.py`, `visualization/controls.py`

### Overview

The project has two independent visualizers:
1. A **web-based 3D viewer** using Three.js (WebGL), served from a Python HTTP backend
2. A **desktop viewer** using matplotlib and mpl_toolkits.mplot3d, launched as a standalone window

The web viewer is the primary demo interface. The desktop viewer was the original prototype used during early development.

### The Python HTTP backend (server.py)

The backend is a plain Python HTTP server (no external web framework like Flask or Django). It listens on port 8080 and exposes a small REST API:

| Endpoint | Method | What it does |
|---|---|---|
| `/` | GET | Serve the index.html file |
| `/state` | GET | Return current cube state as JSON |
| `/move` | POST | Apply one move (e.g., R) |
| `/scramble` | POST | Apply a random scramble |
| `/reset` | POST | Reset to solved state |
| `/solve` | POST | Solve using Kociemba, return solution |
| `/solve_ai` | POST | Solve using the neural network, return solution |

The server maintains two global variables: `_cube` (the current `CubieCube` object) and `_move_history` (the list of moves applied since the last reset or scramble). Every POST request updates these and returns the new state as JSON.

### Why plain HTTP and not Flask?

The API is small (seven endpoints, minimal logic) and adding Flask would introduce an extra dependency for no benefit. Python's built-in `http.server` module handles all the needed functionality.

### The Three.js web frontend (index.html)

Three.js is a JavaScript library for 3D graphics in the browser using WebGL. It was chosen because it runs in any modern browser without plugins, produces smooth 60 fps rendering, and has excellent built-in support for 3D objects, lighting, and camera controls.

The cube is built by creating 27 individual cubie objects (one for each of the 3x3x3 positions). Each cubie is a group of meshes:
- A dark grey internal box representing the physical plastic piece
- Coloured flat squares (called stickers) placed on each visible face

The frontend communicates with the backend via `fetch()` API calls. When the user clicks a button or the backend finishes solving, the frontend receives the new cube state and animates the transition.

### Animation system

The animation queue ensures moves play sequentially rather than all at once. When a solution of N moves is received, each move is added to the queue. The render loop processes one move at a time, smoothly rotating the affected layer by interpolating from 0 to 90 degrees. The speed is configurable.

### State synchronisation

The backend stores the cube as permutation and orientation arrays (`cp`, `co`, `ep`, `eo`). The frontend stores the cube as 27 physical 3D objects with positions and rotations in space. After each move, the frontend calls `syncState()` which uses the mathematical **rotation group of the cube (24 orientations)** to calculate the correct 3D rotation quaternion for each piece. This ensures the visual state always matches the mathematical state exactly.

### The desktop matplotlib viewer (controls.py, renderer3d.py)

The desktop viewer renders the cube using `Poly3DCollection` from `mpl_toolkits.mplot3d`. Each visible face of each cubie is drawn as a polygon with the appropriate colour. Keyboard bindings allow the user to apply moves (u/d/l/r/f/b keys), scramble (x key), and rotate the camera (arrow keys). This viewer was built first and served as the validation environment during development.

---

## 10. The Benchmarking and Experiments

**Files:** `experiments/ai_vs_kociemba.py`, `experiments/kociemba_benchmark.py`

### AI vs Kociemba comparison

`ai_vs_kociemba.py` runs both solvers on the same set of randomly scrambled cubes across depths 1 to 5 (configurable) and collects:

- Solve rate: what percentage of cubes each solver successfully solves
- Average number of moves in the solution
- Average wall-clock time per solve
- AI confidence distribution (how certain the model was about each move)
- Failure analysis: which depth levels caused failures

The results are printed as a side-by-side comparison table. This is the core empirical evidence for the thesis.

### Kociemba benchmark

`kociemba_benchmark.py` runs the Kociemba solver alone on a large batch of random scrambles (default 100) and produces statistical summaries: mean, median, min, max, and standard deviation for both time and solution length. This establishes the baseline performance of the classical solver independently.

### Results observed

The trained model achieves:
- 100% solve rate at scramble depths 1 through 4
- Approximately 71% solve rate at depth 5
- Average solve time under 10 milliseconds per cube

The Kociemba solver achieves close to 100% at all tested depths with solution lengths typically between 4 and 14 moves.

---

## 11. The Test Suite

**Files:** `tests/test_cube.py`, `tests/test_scramble.py`, `tests/test_encoder.py`, `tests/test_kociemba.py`

The test suite uses **pytest**, the standard Python testing framework. It covers:

**test_cube.py**: Verifies the cube model.
- A freshly created cube is solved and legal
- Applying a move followed by its inverse returns to solved
- Applying any move four times returns to solved
- All 18 moves preserve legality
- Orientation sums satisfy the mod-3 and mod-2 constraints after any sequence

**test_scramble.py**: Verifies the scramble generator.
- A scramble followed by its inverse always returns to solved
- WCA constraints are respected (no two consecutive moves on the same face)

**test_encoder.py**: Verifies the one-hot encoder.
- The encoder produces vectors of exactly 324 values
- Each group of 6 values sums to exactly 1 (exactly one hot bit per sticker)
- Encoding and decoding roundtrip correctly

**test_kociemba.py**: Verifies the solver.
- Solutions produced by the solver are valid (applying them returns to solved)
- Solutions are found within the expected number of moves

Tests are run with `pytest` from the project root.

---

## 12. Libraries and Tools Used

### Python 3.14

Python was chosen because it is the dominant language for machine learning and scientific computing. It has the richest ecosystem of relevant libraries and is well-suited for rapid prototyping.

### PyTorch (`torch`)

PyTorch is the deep learning framework used to define, train, and run the neural network. It was chosen over TensorFlow/Keras because:
- It uses dynamic computation graphs, making debugging easier
- Its API is more Pythonic and readable
- It is widely used in academic research
- It runs well on both CPU and CUDA GPU

The `nn.Module` class is used for the model, `DataLoader` for batching, `Adam` for optimisation, and `CrossEntropyLoss` for the training objective.

### NumPy (`numpy`)

NumPy is used throughout the project for:
- Storing and manipulating the training dataset as arrays
- Computing one-hot vectors efficiently using array indexing
- Statistical analysis in the benchmarking scripts

It is the foundational numerical library for Python and is used here because it provides fast array operations without the overhead of a full deep learning framework.

### Matplotlib (`matplotlib`)

Matplotlib is used for the desktop 3D viewer (`controls.py`, `renderer3d.py`). Specifically, `mpl_toolkits.mplot3d` enables 3D polygon rendering. It was chosen because it is part of the standard scientific Python stack, requires no additional installation beyond `pip install matplotlib`, and works well for the interactive keyboard-controlled prototype.

### Three.js (JavaScript, browser-side)

Three.js is a JavaScript WebGL library used for the production-quality 3D web interface. It provides the 3D scene, camera, lighting, and animation system. It was chosen over raw WebGL because raw WebGL requires hundreds of lines of shader code for basic shapes and lighting. Three.js abstracts all of this while remaining highly configurable.

### pytest

pytest is used to run the automated test suite. It is the de facto standard for Python testing because it requires minimal boilerplate (test functions just use `assert` statements), has excellent output formatting, and integrates with all major IDEs and CI systems.

### Docker

A `Dockerfile` is included to containerise the application for deployment. Docker packages the application together with all its dependencies so it runs identically on any machine or cloud host without setup. This was used for the Render.com deployment.

### Render.com

The application was deployed to Render.com using a Docker container. Render is a cloud hosting platform that can run Docker containers for free (with limitations). The deployed URL is used to demonstrate the project remotely.

### Google Colab (`train_on_colab.ipynb`)

Google Colab is a free cloud Jupyter notebook environment with access to GPUs. The training notebook was used to train the model on a GPU because the curriculum learning process (150,000 samples, 5 depth levels, 50 epochs each) takes significantly longer on a CPU.

---

## 13. How Everything Connects

The following describes the path data takes through the system during a typical demo session:

### Starting the application

Running `python main.py visualize --web` imports the `CubieCube` class, creates a fresh solved cube in memory, and starts the Python HTTP server on port 8080. The browser loads `index.html`, which builds 27 Three.js cubie objects in a solved configuration and calls `GET /state` to confirm the initial state.

### Scrambling

The user clicks Scramble. The browser sends `POST /scramble`. The server calls `generate_scramble()` (from `utils/scramble.py`) which produces a random sequence of 20 moves following WCA constraints. These moves are applied to the `CubieCube` object one by one, updating the `cp`, `co`, `ep`, `eo` arrays with each permutation. The server sends back the new state JSON. The browser reads the `cp`, `co`, `ep`, `eo` values and calls `syncState()`, which uses the 24-element rotation group to compute the correct 3D orientation quaternion for each cubie and snaps it into place.

### Solving with Kociemba

The user clicks Solve (Expert). The browser sends `POST /solve`. The server checks if a move history is available. If it is, the solution is instantly computed by reversing and inverting the history. If not, the bidirectional BFS is run: two frontiers expand from the scrambled state and the solved state until they meet. The solution move list is returned as JSON. The browser receives the list and enqueues each move as an animation, playing them one at a time at 8% progress per frame until the cube visually reaches the solved state.

### Solving with the AI

The user clicks Solve (AI). The browser sends `POST /solve_ai`. The server calls `encode_state()` to convert the `CubieCube` into a 324-element one-hot vector. This vector is fed into the trained `RubiksMLP`, which outputs 18 logit scores. Softmax converts these to probabilities. The highest-probability move is chosen, applied to the cube, and the process repeats until solved or 50 steps have been attempted. The full solution list is returned to the browser and animated in the same way as the Kociemba solution.

### The benchmarking comparison

Running `python main.py compare --max-depth 5` generates 50 random scrambles at each depth level, runs both solvers on each, and prints a table showing solve rate, average move count, and average time side by side. This is the primary evidence comparing the two approaches.

---

## Summary

| Component | File(s) | Role |
|---|---|---|
| Cube model | `core/cube.py`, `core/cubie.py` | Mathematical state representation |
| Move engine | `core/moves.py` | All 18 legal moves as permutation tables |
| State encoder | `core/state_encoder.py` | Convert cube to 324-dim one-hot vector |
| Scrambler | `utils/scramble.py` | Random WCA-style scramble generation |
| Dataset generator | `data/dataset_generator.py` | Expert cloning + curriculum datasets |
| Dataset stats | `data/dataset_stats.py` | Statistics and reporting on saved datasets |
| Kociemba solver | `solvers/kociemba_solver.py` | Bidirectional BFS classical solver |
| BFS solver | `solvers/bfs_solver.py` | Extended BFS with detailed statistics |
| AI solver | `solvers/ai_solver.py` | MLP neural network solver |
| Web server | `visualization/server.py` | REST API backend |
| Web frontend | `visualization/index.html` | Three.js interactive 3D viewer |
| Desktop viewer | `visualization/controls.py`, `renderer3d.py` | Matplotlib 3D prototype |
| Benchmarking | `experiments/ai_vs_kociemba.py` | AI vs Kociemba comparison |
| Performance test | `experiments/kociemba_benchmark.py` | Kociemba standalone benchmark |
| Tests | `tests/` | Automated validation suite |
| Entry point | `main.py` | CLI interface for all commands |
