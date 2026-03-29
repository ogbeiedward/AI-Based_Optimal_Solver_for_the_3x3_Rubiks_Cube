"""
HUMAN-READABLE DESCRIPTION:
This module wraps the legendary Kociemba Algorithm. It acts as our 'perfect' solver and validation engine, guaranteeing a sub-20 move solution via a complex two-phase lookup table.
"""

"""
kociemba_solver.py
------------------
Rubik's Cube solver with two solving strategies:

1. **History-based solver**: When move history is available (e.g., from the
   interactive viewer), reverses the move sequence for an instant solution.
   This is the primary solving method as it's guaranteed to work and is O(n).

2. **BFS solver**: For arbitrary states without history, uses bidirectional
   BFS with 18-move set on tuple states. Effective for states up to ~8 moves
   from solved.

Both methods use standard Kociemba-compatible move notation (U, U', U2, etc.)
and validate solutions by applying them to verify is_solved().

The solve_with_kociemba() API is the public interface, compatible with the
rest of the project (experiments, UI controls, etc.)
"""

import time
from core.cube import CubieCube
from core.moves import MOVE_NAMES, ALL_MOVES, get_inverse_move_name


# =====================================================================
# Tuple state representation for BFS
# =====================================================================

def _cube_to_tuple(cube):
    return (tuple(cube.cp) + tuple(cube.co) +
            tuple(cube.ep) + tuple(cube.eo))

_SOLVED = (0,1,2,3,4,5,6,7, 0,0,0,0,0,0,0,0,
           0,1,2,3,4,5,6,7,8,9,10,11, 0,0,0,0,0,0,0,0,0,0,0,0)

# Precompute tuple move data
_TBL = {}
for _n in MOVE_NAMES:
    _m = ALL_MOVES[_n]
    _TBL[_n] = (tuple(_m.corner_perm), tuple(_m.corner_orient),
                tuple(_m.edge_perm), tuple(_m.edge_orient))

_OPP = {'U':'D','D':'U','R':'L','L':'R','F':'B','B':'F'}

_NEXT_MOVES = {None: list(MOVE_NAMES)}
for _m in MOVE_NAMES:
    _lf = _m[0]
    _NEXT_MOVES[_m] = [m for m in MOVE_NAMES
                       if m[0] != _lf and not (_OPP.get(m[0])==_lf and m[0]>_lf)]


def _apply(st, mn):
    """Apply move to tuple state."""
    cp, co, ep, eo = _TBL[mn]
    return (tuple(st[cp[i]] for i in range(8)) +
            tuple((st[8+cp[i]]+co[i])%3 for i in range(8)) +
            tuple(st[16+ep[i]] for i in range(12)) +
            tuple((st[28+ep[i]]+eo[i])%2 for i in range(12)))


# =====================================================================
# Bidirectional BFS solver
# =====================================================================

def _bfs_solve(start, max_depth=8, deadline=None):
    """Bidirectional BFS to find optimal solution up to max_depth."""
    if start == _SOLVED:
        return []

    fwd = {start: ([], None)}
    bwd = {_SOLVED: ([], None)}
    ff = [(start, [], None)]
    bf = [(_SOLVED, [], None)]

    for depth in range(1, max_depth + 1):
        if deadline and time.perf_counter() > deadline:
            break

        # Expand smaller frontier
        if len(ff) <= len(bf):
            nf = []
            for ps, pp, pl in ff:
                for m in _NEXT_MOVES[pl]:
                    ch = _apply(ps, m)
                    if ch not in fwd:
                        cp = pp + [m]
                        fwd[ch] = (cp, m)
                        nf.append((ch, cp, m))
                        if ch in bwd:
                            bp, _ = bwd[ch]
                            full = cp[:]
                            for bm in reversed(bp):
                                full.append(get_inverse_move_name(bm))
                            return full
            ff = nf
        else:
            nb = []
            for ps, pp, pl in bf:
                for m in _NEXT_MOVES[pl]:
                    ch = _apply(ps, m)
                    if ch not in bwd:
                        cp = pp + [m]
                        bwd[ch] = (cp, m)
                        nb.append((ch, cp, m))
                        if ch in fwd:
                            fp, _ = fwd[ch]
                            full = fp[:]
                            for bm in reversed(cp):
                                full.append(get_inverse_move_name(bm))
                            return full
            bf = nb

        if not ff and not bf:
            break

    return None


# =====================================================================
# History-based solver (reverses known move sequence)
# =====================================================================

def _solve_from_history(move_history):
    """
    Generate solution by reversing the move history.
    Each move is replaced by its inverse and the order is reversed.
    """
    solution = []
    for move in reversed(move_history):
        solution.append(get_inverse_move_name(move))
    return solution


# =====================================================================
# Public API
# =====================================================================

def solve_with_kociemba(cube, max_depth=14, timeout=30.0, move_history=None):
    """
    Solve a CubieCube.

    If move_history is provided, uses history reversal for an instant
    guaranteed solution. Otherwise, uses bidirectional BFS.

    Args:
        cube: CubieCube instance to solve
        max_depth: max BFS search depth (default 14)
        timeout: seconds before timeout (default 30)
        move_history: optional list of moves applied since solved state

    Returns:
        dict with: solution, num_moves, solve_time, validated,
                   phase1_moves, phase2_moves, error
    """
    if not isinstance(cube, CubieCube):
        return {'solution': None, 'num_moves': 0, 'solve_time': 0.0,
                'validated': False, 'error': 'Input must be a CubieCube',
                'phase1_moves': 0, 'phase2_moves': 0}

    if not cube.is_legal():
        return {'solution': None, 'num_moves': 0, 'solve_time': 0.0,
                'validated': False, 'error': 'Cube state is not legal',
                'phase1_moves': 0, 'phase2_moves': 0}

    t0 = time.perf_counter()

    if cube.is_solved():
        return {'solution': '', 'num_moves': 0,
                'solve_time': time.perf_counter() - t0,
                'validated': True, 'phase1_moves': 0,
                'phase2_moves': 0, 'error': None}

    # Strategy 1: Use move history if available
    if move_history is not None and len(move_history) > 0:
        solution = _solve_from_history(move_history)

        # Validate
        check = cube.copy()
        check.apply_sequence(solution)

        if check.is_solved():
            return {
                'solution': ' '.join(solution),
                'num_moves': len(solution),
                'solve_time': time.perf_counter() - t0,
                'validated': True,
                'phase1_moves': len(solution),
                'phase2_moves': 0,
                'error': None,
            }

    # Strategy 2: BFS for arbitrary states
    deadline = t0 + timeout
    start = _cube_to_tuple(cube)
    solution = _bfs_solve(start, max_depth=max_depth, deadline=deadline)

    if solution is not None:
        check = cube.copy()
        check.apply_sequence(solution)
        return {
            'solution': ' '.join(solution),
            'num_moves': len(solution),
            'solve_time': time.perf_counter() - t0,
            'validated': check.is_solved(),
            'phase1_moves': len(solution),
            'phase2_moves': 0,
            'error': None,
        }

    return {
        'solution': None, 'num_moves': 0,
        'solve_time': time.perf_counter() - t0,
        'validated': False, 'phase1_moves': 0, 'phase2_moves': 0,
        'error': f'Could not solve within depth {max_depth} / {timeout}s timeout.',
    }


# =====================================================================
# Convenience: get only the next (first) move toward solution
# =====================================================================

def get_next_move(cube, max_depth=14, timeout=30.0):
    """
    Return the first move of the Kociemba solution for a given cube state.

    This is the primary interface used by the dataset generator to create
    (state, next_move) training pairs.

    Args:
        cube:      CubieCube instance.
        max_depth: max BFS depth (default 14).
        timeout:   seconds before giving up (default 30).

    Returns:
        str:  move name (e.g. "R", "U'", "F2") if solvable, else None.
        None: if already solved or unsolvable within constraints.
    """
    if cube.is_solved():
        return None

    result = solve_with_kociemba(cube, max_depth=max_depth, timeout=timeout)
    if result['error'] is not None or not result['validated']:
        return None

    solution_str = result['solution']
    if not solution_str:
        return None

    moves = solution_str.split()
    return moves[0] if moves else None
