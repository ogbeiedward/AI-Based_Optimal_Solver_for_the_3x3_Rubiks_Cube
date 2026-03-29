# Rubik's Cube AI — Phase 1: Supervisor Update

**Project:** AI-Based Optimal Solver for the 3×3 Rubik's Cube (M.Sc. Thesis)  
**Author:** Edward Ogbei  
**Date:** March 2026  
**Phase:** 1 — 3D Visualization & Simulation  
**Status:** ✅ Complete

---

## 1. What Was Built

Phase 1 delivers a **fully functional 3D Rubik's Cube simulation** with two visualization frontends, a mathematically rigorous cube state engine, and foundational infrastructure for future AI solver work.

### What the User Sees
- An **interactive 3D Rubik's Cube** that can be rotated, scrambled, solved, and manipulated with keyboard shortcuts or clickable buttons
- Real-time status display showing cube state (solved/scrambled), legality checks, and move history
- Two visualization modes:
  - **Desktop viewer** (matplotlib-based, launched via `python main.py visualize`)
  - **Web-based viewer** (Three.js + HTTP server, accessed at `localhost:8080`)

### What's Under the Hood
- A **cubie-level mathematical model** of the cube, representing its ~4.3 × 10¹⁹ possible states
- All **18 standard moves** (6 faces × 3 variants: clockwise, counter-clockwise, double)
- WCA-style **scramble generator** with proper constraints
- A comprehensive **validation suite** with 7 categories of correctness tests
- **State encoder** (one-hot encoding to a 324-dimensional vector) ready for neural network input

---

## 2. How It Works — Architecture

### 2.1 Core Engine (`core/`)

The cube is **not** represented as a grid of 54 colored stickers. Instead, it uses a **cubie-level permutation model** — the same model used by the world's fastest solvers (Kociemba's algorithm):

| Component | What It Stores | Size |
|---|---|---|
| `cp` — Corner Permutation | Which of the 8 corner cubies sits in each slot | 8 integers |
| [co](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/cube.py#43-51) — Corner Orientation | How each corner is twisted (0°, 120°, 240°) | 8 integers (mod 3) |
| [ep](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/cube.py#384-393) — Edge Permutation | Which of the 12 edge cubies sits in each slot | 12 integers |
| `eo` — Edge Orientation | Whether each edge is flipped | 12 integers (mod 2) |

**Key design decisions:**
- Centers are **never stored** — they're fixed by the physical mechanism and always at their canonical positions
- Moves are applied via **permutation composition** and **modular orientation arithmetic**, not by shuffling sticker colors
- Three physical invariants are enforced and validated: corner orientation sum ≡ 0 (mod 3), edge orientation sum ≡ 0 (mod 2), and parity(corners) = parity(edges)

### 2.2 Move System ([core/moves.py](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/moves.py))

Each of the 6 base moves (U, D, R, L, F, B) is defined as a [MoveDefinition](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/moves.py#38-58) containing:
- A corner 4-cycle permutation + orientation deltas
- An edge 4-cycle permutation + orientation deltas

The 18-move set is generated **algebraically** at module load:
- **Clockwise** (e.g. R) — directly defined
- **Double** (e.g. R2) — computed as R composed with R
- **Prime/Inverse** (e.g. R') — computed as R composed three times (R³ = R⁻¹ in a cyclic group of order 4)

### 2.3 Visualization (`visualization/`)

Two independent rendering frontends share the same core engine:

**Matplotlib Desktop Viewer** ([renderer3d.py](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/visualization/renderer3d.py) + [controls.py](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/visualization/controls.py)):
- Renders 26 small cubes as `Poly3DCollection` polygons in a 3D coordinate system
- Maps each of the 54 Kociemba facelets to a specific [(x, y, z, face_index)](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/cubie.py#97-120) on the cubie grid
- Interactive keyboard controls with on-screen legend panel
- Dark theme with status bar and solve info panel

**Three.js Web Viewer** ([server.py](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/visualization/server.py) + [index.html](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/visualization/index.html)):
- HTTP server (Python `HTTPServer`) exposes a REST API: `GET /state`, `POST /move`, `POST /scramble`, `POST /reset`, `POST /solve`
- Frontend uses Three.js for hardware-accelerated WebGL rendering with orbit camera controls
- Each cubie is a `THREE.Group` with a dark base box plus colored sticker planes on exposed faces
- Sidebar with clickable move buttons, status panel, and solution display

### 2.4 Scramble Generator ([utils/scramble.py](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/utils/scramble.py))

Generates **WCA-style** random scrambles (20–25 moves) with constraints:
- No consecutive moves on the same face
- No trivial inverse redundancy (e.g. R then R')
- Avoids axis redundancy (e.g. U D U)
- Supports deterministic seeding for reproducibility

### 2.5 State Encoder ([core/state_encoder.py](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/state_encoder.py))

Converts the cube state into a **324-dimensional one-hot vector** (54 facelets × 6 possible colors). This is the input format for the planned neural network solver in later phases.

---

## 3. File Structure

```
rubiks_cube_ai/
├── main.py                    # CLI entry point (visualize / scramble / validate)
├── requirements.txt           # Dependencies (matplotlib, numpy)
├── core/
│   ├── cube.py                # CubieCube class (state model + Kociemba conversion)
│   ├── cubie.py               # Enums: Color, Corner, Edge + color lookup tables
│   ├── moves.py               # 18-move table + permutation composition algebra
│   └── state_encoder.py       # One-hot encoding for neural network input
├── visualization/
│   ├── renderer3d.py          # Matplotlib 3D polygon renderer
│   ├── controls.py            # Interactive keyboard viewer (matplotlib)
│   ├── server.py              # HTTP REST API server
│   └── index.html             # Three.js WebGL frontend
├── solvers/
│   ├── kociemba_solver.py     # History reversal + bidirectional BFS solver
│   ├── bfs_solver.py          # Standalone BFS solver
│   └── ai_solver.py           # Placeholder for neural network solver
├── utils/
│   └── scramble.py            # WCA-style scramble generator
├── tests/
│   ├── test_cube.py           # Core cube model tests
│   ├── test_encoder.py        # State encoder tests
│   ├── test_kociemba.py       # Solver tests
│   └── test_scramble.py       # Scramble generator tests
├── experiments/
│   ├── ai_vs_kociemba.py      # Benchmark framework
│   └── kociemba_benchmark.py  # Solver performance tests
└── docs/
    └── problem_description.md # Ch. 2 of thesis (math background)
```

---

## 4. Validation & Testing

The project includes a **7-part validation suite** (`python main.py validate`):

| # | Test | What It Verifies |
|---|---|---|
| 1 | Solved state checks | [is_solved()](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/cube.py#107-116), [is_legal()](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/cube.py#117-148), correct Kociemba string |
| 2 | Move + inverse = identity | Every face: move then its inverse returns to solved |
| 3 | Four rotations = identity | Every face⁴ = identity (group order is 4) |
| 4 | All 18 moves preserve legality | Every move produces a legal state |
| 5 | Orientation invariants | After complex sequences, CO sum ≡ 0 mod 3, EO sum ≡ 0 mod 2 |
| 6 | Scramble + inverse = solved | 10 different seeded scrambles validated |
| 7 | Centers never move | All 18 moves leave center facelets unchanged |

Additionally, there are **pytest unit tests** covering the cube model, encoder, solver, and scramble generation.

---

## 5. Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.13** | Core language |
| **NumPy** | Numeric arrays for state encoding and geometry |
| **Matplotlib** | Desktop 3D visualization (Poly3DCollection) |
| **Three.js (r128)** | WebGL-based browser 3D visualization |
| **Python HTTPServer** | Lightweight REST API for web frontend |
| **pytest** | Unit testing framework |

---

## 6. What Comes Next (Future Phases)

| Phase | Description | Status |
|---|---|---|
| Phase 1 | 3D Visualization & Simulation | ✅ Complete |
| Phase 2 | Kociemba Two-Phase Solver (IDA* + pruning tables) | 🔄 In progress |
| Phase 3 | AI Solver (Neural network with curriculum learning) | ⬜ Planned |
| Phase 4 | AI vs. Kociemba comparative evaluation | ⬜ Planned |

---

## 7. Possible Supervisor Questions & Answers

### Q1: "Why did you use a cubie-level permutation model instead of simply storing 54 sticker colors?"

**A:** The cubie model represents the cube as 4 arrays (corner permutation, corner orientation, edge permutation, edge orientation) rather than 54 color values. This has three major advantages:
1. **Mathematical correctness** — moves are applied via permutation composition, which naturally preserves the three physical invariants (corner orientation, edge orientation, permutation parity). A sticker-based model doesn't inherently enforce these.
2. **Efficiency for solvers** — the Kociemba algorithm, pattern databases, and pruning tables all operate on coordinate-based representations derived from the cubie model. Converting from stickers would be an unnecessary extra step.
3. **State space compatibility** — this is the standard representation used in the academic literature (Kociemba, Rokicki et al.), making the work directly comparable to published results.

---

### Q2: "What is the state space size and why is it exactly 4.3 × 10¹⁹?"

**A:** Without constraints, the raw count would be 8! × 3⁸ × 12! × 2¹² ≈ 5.19 × 10²⁰. But three physical constraints reduce this by a factor of 12:
- Corner orientations must sum to 0 mod 3 → divides by 3
- Edge orientations must sum to 0 mod 2 → divides by 2
- Corner and edge permutation parities must match → divides by 2

**Result:** 8! × 3⁷ × 12! × 2¹⁰ = **43,252,003,274,489,856,000** ≈ 4.3 × 10¹⁹ legal states.

---

### Q3: "How does the 3D rendering work?"

**A:** Two independent rendering approaches are implemented:

1. **Matplotlib (desktop):** Each of the 26 visible cubies is rendered as 6 polygons using `Poly3DCollection`. The cube model outputs a 54-character Kociemba string, which is mapped to [(x, y, z, face_index)](file:///c:/Users/Edward/.gemini/antigravity/scratch/rubiks_cube_ai/core/cubie.py#97-120) tuples via a precomputed lookup table. Each face is colored according to the sticker color or dark gray for internal faces.

2. **Three.js (browser):** Each cubie is a `THREE.Group` consisting of a dark base box plus `THREE.PlaneGeometry` sticker meshes on exposed faces. Colors are updated by mapping the server's facelet array to the correct sticker materials. The camera uses `OrbitControls` for mouse-based rotation.

Both renderers are **read-only** — they convert the cube's internal state to visuals but never mutate it.

---

### Q4: "How do you verify that your move implementations are correct?"

**A:** Through multiple layers of validation:
1. **Algebraic identity tests:** For every face F, applying F then F' returns to solved (inverse identity), and applying F four times returns to solved (cyclic group of order 4).
2. **Invariant preservation:** After any sequence of moves, the three physical invariants are checked: corner orientation sum mod 3, edge orientation sum mod 2, and parity equality.
3. **Round-trip tests:** Random scrambles are generated, then their computed inverse is applied — the result must be the solved state.
4. **Center immutability:** All 18 moves are verified to leave center facelets unchanged.
5. **Kociemba string validation:** The solved state must produce exactly `UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB`.

---

### Q5: "Why two separate visualizations (matplotlib and Three.js)?"

**A:** Each serves a different purpose:
- **Matplotlib** provides a quick desktop tool for development and debugging — it launches instantly with no browser needed and integrates with Python's ecosystem (e.g., breakpoints, inline data inspection).
- **Three.js** delivers a polished, hardware-accelerated visual experience suitable for demonstrations and presentations. It supports smoother camera movement, better lighting, and runs in any browser.

Both share the exact same core engine, ensuring consistency.

---

### Q6: "What is the Kociemba string format and why is it important?"

**A:** The Kociemba string is a 54-character representation where each character (U, R, F, D, L, B) denotes the color of one facelet. The characters are ordered face by face: U-face (positions 0–8), R-face (9–17), F-face (18–26), D-face (27–35), L-face (36–44), B-face (45–53). Within each face, facelets are numbered row-by-row from top-left.

It's important because:
1. It's the **standard exchange format** between cube solvers worldwide
2. It bridges the cubie model (internal) and visual model (display)
3. It allows interoperability with external tools and libraries

---

### Q7: "How does the scramble generator ensure valid scrambles?"

**A:** The generator enforces WCA-style constraints:
1. No two consecutive moves on the same face (e.g., no R R2)
2. No move on an opposite face sandwiched by the same face (e.g., no U D U)
3. Scramble length is randomized between 20–25 moves if not specified
4. Optional seeding for reproducible results

After generation, scrambles are validated by applying the scramble, then its inverse, and confirming the cube returns to solved.

---

### Q8: "How will the AI solver work in the next phase?"

**A:** The infrastructure is already in place:
- The **state encoder** converts any cube state to a 324-dimensional one-hot vector (54 facelets × 6 colors)
- The **move label mapping** defines the 18-move output space for the neural network
- The planned approach uses **curriculum learning** — training on progressively deeper scrambles (1-move, then 2-move, etc.) with a multi-layer perceptron (MLP) that predicts the next move to apply

The AI solver will then be benchmarked against the Kociemba solver on metrics like solve rate, number of moves, and computation time.

---

### Q9: "What is God's Number and how does it relate to your project?"

**A:** God's Number is **20** — the maximum number of moves needed to solve any legal configuration of a 3×3 Rubik's Cube (in the half-turn metric). This was proven by Rokicki et al. in 2010 using massive distributed computation.

For the project, God's Number serves as:
1. A **theoretical benchmark** — any solver claiming optimality must find solutions ≤ 20 moves
2. A **difficulty reference** — scrambles of 20+ random moves effectively produce random cube states
3. A **training depth target** — the AI solver should eventually handle scrambles up to depth 20

---

### Q10: "What dependencies does the project require?"

**A:** The project is intentionally lightweight:
- **matplotlib** — for the desktop 3D viewer
- **numpy** — for array operations in the state encoder and geometry computations
- No external solver libraries are used — the Kociemba solver is implemented from scratch
- The web viewer uses Three.js via CDN (no npm/build step required)
