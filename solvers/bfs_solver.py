"""
HUMAN-READABLE DESCRIPTION:
This script executes a Breadth-First Search (BFS). It brute-forces every possible move combination level-by-level to guarantee the absolute shortest possible path for very simple scrambles.
"""

"""
kociemba_solver.py
------------------
Pure Python Rubik's Cube solver using bidirectional BFS with
tuple-based state representation for fast hashing.

Instead of copying CubieCube objects, this solver represents each
state as a single tuple of 40 integers (8 cp + 8 co + 12 ep + 12 eo).
This eliminates object creation overhead and enables fast dict lookups.

Precomputed move transformation tables operate directly on these tuples,
avoiding method call overhead.

Centers are fixed and never moved by any operation.
"""

import time
from core.cube import CubieCube
from core.moves import MOVE_NAMES, ALL_MOVES, get_inverse_move_name


# ----------------------------------------------------------------
# Tuple-based state representation
# ----------------------------------------------------------------

def cube_to_tuple(cube):
    """Convert a CubieCube to a hashable tuple of 40 ints."""
    return (
        tuple(cube.cp) + tuple(cube.co) +
        tuple(cube.ep) + tuple(cube.eo)
    )


def solved_tuple():
    """Return the solved state as a tuple."""
    return (
        0, 1, 2, 3, 4, 5, 6, 7,     # cp
        0, 0, 0, 0, 0, 0, 0, 0,     # co
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,  # ep
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,    # eo
    )


# ----------------------------------------------------------------
# Precomputed move tables for tuple states
# ----------------------------------------------------------------

# Build transition tables: for each move, precompute how to transform
# a state tuple into a new state tuple.

class MoveTables:
    """Precomputed arrays for fast state transitions on tuples."""

    _tables = None  # dict[move_name -> (cp_perm, co_delta, ep_perm, eo_delta)]

    @classmethod
    def get(cls):
        if cls._tables is None:
            cls._build()
        return cls._tables

    @classmethod
    def _build(cls):
        cls._tables = {}
        for name in MOVE_NAMES:
            md = ALL_MOVES[name]
            cls._tables[name] = (
                tuple(md.corner_perm),
                tuple(md.corner_orient),
                tuple(md.edge_perm),
                tuple(md.edge_orient),
            )


def apply_move_to_tuple(state, move_name, tables):
    """
    Apply a move to a tuple state. Returns a new tuple.

    state layout: cp[0..7] co[8..15] ep[16..27] eo[28..39]
    """
    cp_perm, co_delta, ep_perm, eo_delta = tables[move_name]

    # Corner permutation and orientation
    new_cp = tuple(state[cp_perm[i]] for i in range(8))
    new_co = tuple(
        (state[8 + cp_perm[i]] + co_delta[i]) % 3 for i in range(8)
    )

    # Edge permutation and orientation
    new_ep = tuple(state[16 + ep_perm[i]] for i in range(12))
    new_eo = tuple(
        (state[28 + ep_perm[i]] + eo_delta[i]) % 2 for i in range(12)
    )

    return new_cp + new_co + new_ep + new_eo


# ----------------------------------------------------------------
# Move pruning
# ----------------------------------------------------------------

OPPOSITE_FACES = {
    'U': 'D', 'D': 'U',
    'R': 'L', 'L': 'R',
    'F': 'B', 'B': 'F',
}


def next_moves(last_move):
    """Return valid next moves after last_move, with redundancy pruning."""
    if last_move is None:
        return MOVE_NAMES

    last_face = last_move[0]
    result = []
    for m in MOVE_NAMES:
        mf = m[0]
        if mf == last_face:
            continue
        if OPPOSITE_FACES.get(mf) == last_face and mf > last_face:
            continue
        result.append(m)
    return result


# Precompute next_moves for each possible last move
_NEXT_MOVES_CACHE = {None: list(MOVE_NAMES)}
for _m in MOVE_NAMES:
    _NEXT_MOVES_CACHE[_m] = next_moves(_m)


# ----------------------------------------------------------------
# Bidirectional BFS with tuple states
# ----------------------------------------------------------------

def bidirectional_solve(cube, max_depth=14, timeout=30.0):
    """
    Solve using bidirectional BFS on tuple-based state representation.

    Forward search from scrambled state, backward search from solved state.
    When frontiers meet, the solution is assembled.

    Args:
        cube: CubieCube to solve
        max_depth: maximum solution depth
        timeout: time limit in seconds

    Returns:
        dict with solution info
    """
    start_time = time.perf_counter()
    deadline = start_time + timeout
    tables = MoveTables.get()

    start_state = cube_to_tuple(cube)
    goal_state = solved_tuple()

    if start_state == goal_state:
        return {
            'solution': '',
            'num_moves': 0,
            'solve_time': time.perf_counter() - start_time,
            'nodes_explored': 0,
            'validated': True,
            'error': None,
        }

    # Forward: state -> (path_list, last_move)
    # Backward: state -> (path_list, last_move)
    forward = {start_state: ([], None)}
    backward = {goal_state: ([], None)}

    forward_frontier = [(start_state, [], None)]
    backward_frontier = [(goal_state, [], None)]

    nodes_explored = 0

    for depth in range(1, max_depth + 1):
        if time.perf_counter() > deadline:
            break

        # Expand the smaller frontier
        if len(forward_frontier) <= len(backward_frontier):
            # Expand forward
            new_frontier = []
            for parent_state, parent_path, parent_last in forward_frontier:
                for move_name in _NEXT_MOVES_CACHE[parent_last]:
                    nodes_explored += 1
                    child_state = apply_move_to_tuple(
                        parent_state, move_name, tables
                    )

                    if child_state not in forward:
                        child_path = parent_path + [move_name]
                        forward[child_state] = (child_path, move_name)
                        new_frontier.append(
                            (child_state, child_path, move_name)
                        )

                        if child_state in backward:
                            back_path, _ = backward[child_state]
                            full = child_path[:]
                            for bm in reversed(back_path):
                                full.append(get_inverse_move_name(bm))

                            elapsed = time.perf_counter() - start_time
                            check = cube.copy()
                            check.apply_sequence(full)

                            return {
                                'solution': ' '.join(full),
                                'num_moves': len(full),
                                'solve_time': elapsed,
                                'nodes_explored': nodes_explored,
                                'validated': check.is_solved(),
                                'error': None,
                            }

                # Periodic time check
                if nodes_explored % 100000 == 0 and time.perf_counter() > deadline:
                    break

            forward_frontier = new_frontier
        else:
            # Expand backward
            new_frontier = []
            for parent_state, parent_path, parent_last in backward_frontier:
                for move_name in _NEXT_MOVES_CACHE[parent_last]:
                    nodes_explored += 1
                    child_state = apply_move_to_tuple(
                        parent_state, move_name, tables
                    )

                    if child_state not in backward:
                        child_path = parent_path + [move_name]
                        backward[child_state] = (child_path, move_name)
                        new_frontier.append(
                            (child_state, child_path, move_name)
                        )

                        if child_state in forward:
                            fwd_path, _ = forward[child_state]
                            full = fwd_path[:]
                            for bm in reversed(child_path):
                                full.append(get_inverse_move_name(bm))

                            elapsed = time.perf_counter() - start_time
                            check = cube.copy()
                            check.apply_sequence(full)

                            return {
                                'solution': ' '.join(full),
                                'num_moves': len(full),
                                'solve_time': elapsed,
                                'nodes_explored': nodes_explored,
                                'validated': check.is_solved(),
                                'error': None,
                            }

                if nodes_explored % 100000 == 0 and time.perf_counter() > deadline:
                    break

            backward_frontier = new_frontier

    elapsed = time.perf_counter() - start_time
    return {
        'solution': None,
        'num_moves': 0,
        'solve_time': elapsed,
        'nodes_explored': nodes_explored,
        'validated': False,
        'error': (
            f'Search exhausted after {elapsed:.1f}s '
            f'({nodes_explored} nodes explored, max_depth={max_depth}). '
            f'Try increasing timeout or max_depth.'
        ),
    }


# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

def solve_with_kociemba(cube, max_depth=14, timeout=30.0):
    """
    Solve a CubieCube using bidirectional BFS.

    Args:
        cube: CubieCube instance to solve
        max_depth: maximum moves (default 14)
        timeout: seconds before timeout (default 30)

    Returns:
        dict with: solution, num_moves, solve_time, validated, error
    """
    if not isinstance(cube, CubieCube):
        return {
            'solution': None,
            'num_moves': 0,
            'solve_time': 0.0,
            'nodes_explored': 0,
            'validated': False,
            'error': 'Input must be a CubieCube instance',
        }

    if not cube.is_legal():
        return {
            'solution': None,
            'num_moves': 0,
            'solve_time': 0.0,
            'nodes_explored': 0,
            'validated': False,
            'error': 'Cube state is not legal',
        }

    return bidirectional_solve(cube, max_depth=max_depth, timeout=timeout)
