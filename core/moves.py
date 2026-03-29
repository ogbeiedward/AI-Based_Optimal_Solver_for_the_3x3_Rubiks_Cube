"""
HUMAN-READABLE DESCRIPTION:
This file contains the extremely important mathematical maps for every Rubik's Cube rotation. When you perform a turn (like Right or Up), these arrays determine exactly how the pieces shuffle and flip.
"""

"""
moves.py
--------
Permutation and orientation tables for all six face moves of a 3x3 Rubik's Cube.

Each move is defined by:
  - A corner permutation (which corner slot goes where)
  - A corner orientation delta (how corner orientations change)
  - An edge permutation (which edge slot goes where)
  - An edge orientation delta (how edge orientations change)

Centers are NEVER moved by any face turn. They remain fixed.

Orientation conventions (Kociemba standard):
  Corner orientation:
    0 = reference (U/D) sticker is on U or D face
    1 = reference sticker is rotated 120 degrees clockwise
    2 = reference sticker is rotated 120 degrees counter-clockwise
    Orientation values are computed modulo 3.

  Edge orientation:
    0 = reference sticker is in its natural position
    1 = reference sticker is flipped
    Orientation values are computed modulo 2.

Move naming:
  U, D, L, R, F, B          = clockwise 90-degree face turns
  U', D', L', R', F', B'    = counter-clockwise 90-degree face turns (prime)
  U2, D2, L2, R2, F2, B2    = 180-degree face turns (double)
"""

from core.cubie import Corner, Edge

# ---------------------------------------------------------------------------
# Data structure for a single move definition
# ---------------------------------------------------------------------------

class MoveDefinition:
    """
    Stores the permutation and orientation deltas for one clockwise
    90-degree face turn, applied to corners and edges.

    corner_perm: tuple of 8 Corner values.
        corner_perm[i] = the corner that moves INTO slot i.
    corner_orient: tuple of 8 ints (each 0, 1, or 2).
        The orientation change added to the corner arriving at slot i.
    edge_perm: tuple of 12 Edge values.
        edge_perm[i] = the edge that moves INTO slot i.
    edge_orient: tuple of 12 ints (each 0 or 1).
        The orientation change added to the edge arriving at slot i.
    """

    def __init__(self, corner_perm, corner_orient, edge_perm, edge_orient):
        self.corner_perm = corner_perm
        self.corner_orient = corner_orient
        self.edge_perm = edge_perm
        self.edge_orient = edge_orient


# ---------------------------------------------------------------------------
# Identity (no-op) arrays for reference
# ---------------------------------------------------------------------------

_CORNER_IDENTITY = (
    Corner.URF, Corner.UFL, Corner.ULB, Corner.UBR,
    Corner.DFR, Corner.DLF, Corner.DBL, Corner.DRB,
)

_EDGE_IDENTITY = (
    Edge.UR, Edge.UF, Edge.UL, Edge.UB,
    Edge.DR, Edge.DF, Edge.DL, Edge.DB,
    Edge.FR, Edge.FL, Edge.BL, Edge.BR,
)

_ZERO_8 = (0, 0, 0, 0, 0, 0, 0, 0)
_ZERO_12 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


# ---------------------------------------------------------------------------
# U move (Up face, clockwise when looking at U)
# ---------------------------------------------------------------------------
# Corners: URF -> UBR -> ULB -> UFL -> URF  (4-cycle)
# Edges:   UR -> UB -> UL -> UF -> UR       (4-cycle)
# No orientation change for U-layer corners or edges.

_u_cp = list(_CORNER_IDENTITY)
_u_cp[Corner.URF] = Corner.UBR
_u_cp[Corner.UFL] = Corner.URF
_u_cp[Corner.ULB] = Corner.UFL
_u_cp[Corner.UBR] = Corner.ULB

_u_ep = list(_EDGE_IDENTITY)
_u_ep[Edge.UR] = Edge.UB
_u_ep[Edge.UF] = Edge.UR
_u_ep[Edge.UL] = Edge.UF
_u_ep[Edge.UB] = Edge.UL

MOVE_U = MoveDefinition(
    corner_perm=tuple(_u_cp),
    corner_orient=_ZERO_8,
    edge_perm=tuple(_u_ep),
    edge_orient=_ZERO_12,
)


# ---------------------------------------------------------------------------
# D move (Down face, clockwise when looking at D)
# ---------------------------------------------------------------------------
# Corners: DFR -> DLF -> DBL -> DRB -> DFR  (4-cycle)
# Edges:   DR -> DF -> DL -> DB -> DR       (4-cycle)
# No orientation change.

_d_cp = list(_CORNER_IDENTITY)
_d_cp[Corner.DFR] = Corner.DLF
_d_cp[Corner.DLF] = Corner.DBL
_d_cp[Corner.DBL] = Corner.DRB
_d_cp[Corner.DRB] = Corner.DFR

_d_ep = list(_EDGE_IDENTITY)
_d_ep[Edge.DR] = Edge.DF
_d_ep[Edge.DF] = Edge.DL
_d_ep[Edge.DL] = Edge.DB
_d_ep[Edge.DB] = Edge.DR

MOVE_D = MoveDefinition(
    corner_perm=tuple(_d_cp),
    corner_orient=_ZERO_8,
    edge_perm=tuple(_d_ep),
    edge_orient=_ZERO_12,
)


# ---------------------------------------------------------------------------
# R move (Right face, clockwise when looking at R)
# ---------------------------------------------------------------------------
# Corners: URF -> DFR -> DRB -> UBR -> URF  (4-cycle)
# Corner orientations change: URF +1, DFR +2, DRB +1, UBR +2
# Edges:   UR -> FR -> DR -> BR -> UR       (4-cycle)
# No edge orientation change for R move.

_r_cp = list(_CORNER_IDENTITY)
_r_cp[Corner.URF] = Corner.DFR
_r_cp[Corner.DFR] = Corner.DRB
_r_cp[Corner.DRB] = Corner.UBR
_r_cp[Corner.UBR] = Corner.URF

_r_co = list(_ZERO_8)
_r_co[Corner.URF] = 2
_r_co[Corner.DFR] = 1
_r_co[Corner.DRB] = 2
_r_co[Corner.UBR] = 1

_r_ep = list(_EDGE_IDENTITY)
_r_ep[Edge.UR] = Edge.FR
_r_ep[Edge.FR] = Edge.DR
_r_ep[Edge.DR] = Edge.BR
_r_ep[Edge.BR] = Edge.UR

MOVE_R = MoveDefinition(
    corner_perm=tuple(_r_cp),
    corner_orient=tuple(_r_co),
    edge_perm=tuple(_r_ep),
    edge_orient=_ZERO_12,
)


# ---------------------------------------------------------------------------
# L move (Left face, clockwise when looking at L)
# ---------------------------------------------------------------------------
# Corners: UFL -> ULB -> DBL -> DLF -> UFL  (4-cycle)
# Corner orientations: UFL +1, ULB +2, DBL +1, DLF +2
# Edges:   UL -> BL -> DL -> FL -> UL       (4-cycle)
# No edge orientation change for L move.

_l_cp = list(_CORNER_IDENTITY)
_l_cp[Corner.UFL] = Corner.ULB
_l_cp[Corner.ULB] = Corner.DBL
_l_cp[Corner.DBL] = Corner.DLF
_l_cp[Corner.DLF] = Corner.UFL

_l_co = list(_ZERO_8)
_l_co[Corner.UFL] = 1
_l_co[Corner.ULB] = 2
_l_co[Corner.DBL] = 1
_l_co[Corner.DLF] = 2

_l_ep = list(_EDGE_IDENTITY)
_l_ep[Edge.UL] = Edge.BL
_l_ep[Edge.BL] = Edge.DL
_l_ep[Edge.DL] = Edge.FL
_l_ep[Edge.FL] = Edge.UL

MOVE_L = MoveDefinition(
    corner_perm=tuple(_l_cp),
    corner_orient=tuple(_l_co),
    edge_perm=tuple(_l_ep),
    edge_orient=_ZERO_12,
)


# ---------------------------------------------------------------------------
# F move (Front face, clockwise when looking at F)
# ---------------------------------------------------------------------------
# Corners: URF -> UFL -> DLF -> DFR -> URF  (4-cycle)
# Corner orientations: URF +1, UFL +2, DLF +1, DFR +2
# Edges:   UF -> FL -> DF -> FR -> UF       (4-cycle)
# Edge orientations: all four flipped (+1 mod 2)

_f_cp = list(_CORNER_IDENTITY)
_f_cp[Corner.URF] = Corner.UFL
_f_cp[Corner.UFL] = Corner.DLF
_f_cp[Corner.DLF] = Corner.DFR
_f_cp[Corner.DFR] = Corner.URF

_f_co = list(_ZERO_8)
_f_co[Corner.URF] = 1
_f_co[Corner.UFL] = 2
_f_co[Corner.DLF] = 1
_f_co[Corner.DFR] = 2

_f_ep = list(_EDGE_IDENTITY)
_f_ep[Edge.UF] = Edge.FL
_f_ep[Edge.FL] = Edge.DF
_f_ep[Edge.DF] = Edge.FR
_f_ep[Edge.FR] = Edge.UF

_f_eo = list(_ZERO_12)
_f_eo[Edge.UF] = 1
_f_eo[Edge.FL] = 1
_f_eo[Edge.DF] = 1
_f_eo[Edge.FR] = 1

MOVE_F = MoveDefinition(
    corner_perm=tuple(_f_cp),
    corner_orient=tuple(_f_co),
    edge_perm=tuple(_f_ep),
    edge_orient=tuple(_f_eo),
)


# ---------------------------------------------------------------------------
# B move (Back face, clockwise when looking at B)
# ---------------------------------------------------------------------------
# Corners: UBR -> ULB -> DBL -> DRB -> UBR  (4-cycle)
#   Wait, clockwise when looking at B means from the back:
#   UBR -> DRB -> DBL -> ULB -> UBR
# Corner orientations: UBR +1, DRB +2, DBL +1, ULB +2
# Edges:   UB -> BR -> DB -> BL -> UB       (4-cycle)
# Edge orientations: all four flipped (+1 mod 2)

_b_cp = list(_CORNER_IDENTITY)
_b_cp[Corner.UBR] = Corner.DRB
_b_cp[Corner.DRB] = Corner.DBL
_b_cp[Corner.DBL] = Corner.ULB
_b_cp[Corner.ULB] = Corner.UBR

_b_co = list(_ZERO_8)
_b_co[Corner.UBR] = 2
_b_co[Corner.DRB] = 1
_b_co[Corner.DBL] = 2
_b_co[Corner.ULB] = 1

_b_ep = list(_EDGE_IDENTITY)
_b_ep[Edge.UB] = Edge.BR
_b_ep[Edge.BR] = Edge.DB
_b_ep[Edge.DB] = Edge.BL
_b_ep[Edge.BL] = Edge.UB

_b_eo = list(_ZERO_12)
_b_eo[Edge.UB] = 1
_b_eo[Edge.BR] = 1
_b_eo[Edge.DB] = 1
_b_eo[Edge.BL] = 1

MOVE_B = MoveDefinition(
    corner_perm=tuple(_b_cp),
    corner_orient=tuple(_b_co),
    edge_perm=tuple(_b_ep),
    edge_orient=tuple(_b_eo),
)


# ---------------------------------------------------------------------------
# Move table: maps base move name to its MoveDefinition
# ---------------------------------------------------------------------------

BASE_MOVES = {
    "U": MOVE_U,
    "D": MOVE_D,
    "R": MOVE_R,
    "L": MOVE_L,
    "F": MOVE_F,
    "B": MOVE_B,
}


# ---------------------------------------------------------------------------
# Composition helpers
# ---------------------------------------------------------------------------

def compose_corner_perm(perm_a, perm_b):
    """
    Compose two corner permutations: result[i] = perm_a[perm_b[i]].
    This applies perm_b first, then perm_a.
    """
    return tuple(perm_a[perm_b[i]] for i in range(8))


def compose_corner_orient(orient_a, perm_a, orient_b, perm_b):
    """
    Compose corner orientations for the composition of two moves.
    result[i] = (orient_a[perm_b[i]] + orient_b[i]) mod 3
    """
    return tuple((orient_a[perm_b[i]] + orient_b[i]) % 3 for i in range(8))


def compose_edge_perm(perm_a, perm_b):
    """
    Compose two edge permutations: result[i] = perm_a[perm_b[i]].
    """
    return tuple(perm_a[perm_b[i]] for i in range(12))


def compose_edge_orient(orient_a, perm_a, orient_b, perm_b):
    """
    Compose edge orientations for the composition of two moves.
    result[i] = (orient_a[perm_b[i]] + orient_b[i]) mod 2
    """
    return tuple((orient_a[perm_b[i]] + orient_b[i]) % 2 for i in range(12))


def compose_moves(move_a, move_b):
    """
    Compose two MoveDefinitions: apply move_b first, then move_a.
    Returns a new MoveDefinition.
    """
    cp = compose_corner_perm(move_a.corner_perm, move_b.corner_perm)
    co = compose_corner_orient(
        move_a.corner_orient, move_a.corner_perm,
        move_b.corner_orient, move_b.corner_perm,
    )
    ep = compose_edge_perm(move_a.edge_perm, move_b.edge_perm)
    eo = compose_edge_orient(
        move_a.edge_orient, move_a.edge_perm,
        move_b.edge_orient, move_b.edge_perm,
    )
    return MoveDefinition(cp, co, ep, eo)


def invert_move(move_def):
    """
    Compute the inverse of a MoveDefinition (apply it three times for a
    90-degree move, which is equivalent to the prime move).
    """
    double = compose_moves(move_def, move_def)
    return compose_moves(double, move_def)


# ---------------------------------------------------------------------------
# Build the full move table (18 moves)
# ---------------------------------------------------------------------------

ALL_MOVES = {}

for name, base in BASE_MOVES.items():
    # Clockwise (e.g. "U")
    ALL_MOVES[name] = base
    # Double (e.g. "U2")
    ALL_MOVES[name + "2"] = compose_moves(base, base)
    # Prime / inverse (e.g. "U'")
    ALL_MOVES[name + "'"] = invert_move(base)


# Ordered list of all 18 move names for indexing
MOVE_NAMES = [
    "U", "U'", "U2",
    "R", "R'", "R2",
    "F", "F'", "F2",
    "D", "D'", "D2",
    "L", "L'", "L2",
    "B", "B'", "B2",
]

MOVE_INDEX = {name: idx for idx, name in enumerate(MOVE_NAMES)}


def get_inverse_move_name(move_name):
    """Return the name of the inverse of the given move."""
    if move_name.endswith("'"):
        return move_name[0]  # R' -> R
    elif move_name.endswith("2"):
        return move_name  # R2 -> R2 (self-inverse)
    else:
        return move_name + "'"  # R -> R'
