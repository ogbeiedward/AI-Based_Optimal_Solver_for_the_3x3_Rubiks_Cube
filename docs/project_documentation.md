# Project Architecture: AI-Based Optimal Solver for the 3x3 Rubik's Cube

This document serves as the primary context repository for the project. It details the mechanical modeling, the visualization engine, and the mathematical constraints discovered and enforced during development.

## 1. Project Overview
The objective of this project is to provide a complete software stack for simulating, scrambling, and optimally solving a 3x3 Rubik's Cube. 
The system is divided into two major operational realms:
- **The Mathematical Backend:** Written in Python, modeling the cube algebraically using explicit permutation matrices.
- **The 3D Visualization Frontend:** A local HTTP web server serving a Three.js interface that rigidly obeys the backend's combinatorial state.

## 2. Core Backend (`core/`)
The backend completely ignores 3D geometry and tracks abstract combinatorial states.

### [cubie.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cubie.py)
Defines Kociemba standard enums and naming conventions:
- **6 Fixed Centers:** Used as reference frames.
- **8 Corners:** 3-color pieces (e.g., URF, DBL) assigned integer IDs 0-7.
- **12 Edges:** 2-color pieces (e.g., UR, DF) assigned integer IDs 0-11.

### [cube.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py)
The [CubieCube](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#25-438) class is the absolute source of truth for the puzzle's state. It tracks four fundamental integer arrays:
- **`cp` (Corner Permutation):** An array of length 8 indicating which original corner piece currently occupies which physical slot.
- **[co](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#43-51) (Corner Orientation):** An array of length 8 indicating the twist of each corner (`0`, `1`, `2`) relative to the U/D axis.
- **[ep](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#384-393) (Edge Permutation):** An array of length 12 mapping edge pieces to edge slots.
- **`eo` (Edge Orientation):** An array of length 12 tracking edge flips (`0`, `1`).
This file also contains the extremely strict [is_legal()](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#117-148) constraint checker, which validates parity equality between corners and edges, and verifies that the modulo sums across `eo` and [co](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#43-51) equal zero.

### [moves.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/moves.py) (Crucial Constraints)
Calculates permutations for the 18 Half-Turn Metric moves (U, D, R, L, F, B and their inverses/doubles).
> [!IMPORTANT]
> **Historical Bug and Fix:** Previously, the `B` face move applied a mathematically counter-clockwise corner rotation alongside a clockwise edge rotation. Simultaneously, the `L` move applied a counter-clockwise edge rotation alongside a clockwise corner rotation. These invisible internal paradoxes caused the visualization layers to visually shear and "jump" out of sync. They have since been rewritten and strictly align with clockwise cyclic permutations.

## 3. Visualization Engine (`visualization/`)
The visualizer ([server.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/visualization/server.py) and [index.html](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/visualization/index.html)) operates by explicitly interpreting the `[cp, co, ep, eo]` backend state arrays, mapping them dynamically into physical rendering space.

### [server.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/visualization/server.py)
A lightweight `/state` endpoint host. It listens for `/move`, `/scramble`, and `/solve` HTTP requests, evaluates them against [CubieCube](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#25-438), and outputs JSON containing the exact `cp, co, ep, eo` lists alongside history arrays.

### [index.html](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/visualization/index.html) (Three.js WebGL)
The 3D frontend does not utilize "sticker swapping." It utilizes strict, fully simulated **Rigid Layer Mechanics**:
- **Piece Identity:** Automatically instantiates 26 independent `THREE.Group` solid bodies tracking 6 static center components.
- **Queue-Based Kinematics:** Animations (like Scrambling or Solving) queue inside an `animQueue`. Specific logical layer targets (e.g., `Math.round(cubie.position.y) === 1`) are bounded to an `AnimationPivot` and explicitly rotated exactly $\pm90^\circ$ or $180^\circ$.
- **Combinatorial Locking ([syncState()](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/visualization/index.html#386-406)):** After a physical float-based interpolation concludes, the visualizer mathematically evaluates the 24 permutations of the cubic rigid symmetry group (`Q24`). It guarantees visually perfect drift-free alignment by enforcing exact normal vector matching against the backend's supplied logical slot configurations, completely destroying floating point precision decay.

## 4. Solvers (`solvers/`)
The logic paths generating movement sequences natively support multiple heuristic approaches:
1. **[kociemba_solver.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/solvers/kociemba_solver.py):** Generates verified, theoretically-bound low-move solutions optimally using a two-phase Kociemba lookup table mapping.
2. **[bfs_solver.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/solvers/bfs_solver.py):** A fundamental breadth-first search implementation likely used for resolving states near completion or exploring explicit shallow tree branches perfectly.
3. **[ai_solver.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/solvers/ai_solver.py):** Provides advanced, likely heuristic/neural-network driven optimizations forming the namesake of this repository.

## Future Context Reminders
When working within this repository:
- **Never implement arbitrary rotational Euler angles:** All 3D movement inside the browser must translate from explicit combinations of `[cp, co]` mapped through the pre-computed `Q24` array grid. Standard continuous float updates will shear coordinates.
- **Modifying [moves.py](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/moves.py) requires rigorous geometric testing:** Validation methods ([is_legal()](file:///d:/GitHub/PCZ-2025-Courses/Project/AI-Based_Optimal_Solver_for_the_3x3_Rubiks_Cube/core/cube.py#117-148)) verify group-theory closure, but do *not* verify physically correct rotation geometries. If modifying move arrays, verify via the browser visualizer perfectly matching corner slices against internal core edges.
