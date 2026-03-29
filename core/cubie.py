"""
HUMAN-READABLE DESCRIPTION:
This file stores all the foundational constants and definitions for the Rubik's Cube components. It defines the names, colors, and standard orderings for all the corner and edge pieces.
"""

"""
cubie.py
--------
Defines the fundamental data types for a cubie-level Rubik's Cube model.

Corner cubies have 3 color stickers and an orientation in {0, 1, 2}.
Edge cubies have 2 color stickers and an orientation in {0, 1}.
Centers are fixed and never moved by any face turn.

Color convention (Singmaster standard):
    U = White, R = Red, F = Green, D = Yellow, L = Orange, B = Blue
"""

from enum import IntEnum


# ---------------------------------------------------------------------------
# Color enumeration
# ---------------------------------------------------------------------------

class Color(IntEnum):
    """Six face colors of a standard Rubik's Cube."""
    U = 0  # White  (Up)
    R = 1  # Red    (Right)
    F = 2  # Green  (Front)
    D = 3  # Yellow (Down)
    L = 4  # Orange (Left)
    B = 5  # Blue   (Back)


# Human-readable color names for display
COLOR_NAMES = {
    Color.U: "White",
    Color.R: "Red",
    Color.F: "Green",
    Color.D: "Yellow",
    Color.L: "Orange",
    Color.B: "Blue",
}

# Single-character labels used in Kociemba facelet strings
COLOR_CHARS = {
    Color.U: "U",
    Color.R: "R",
    Color.F: "F",
    Color.D: "D",
    Color.L: "L",
    Color.B: "B",
}

CHAR_TO_COLOR = {v: k for k, v in COLOR_CHARS.items()}


# ---------------------------------------------------------------------------
# Corner cubie definitions
# ---------------------------------------------------------------------------

class Corner(IntEnum):
    """
    Eight corner positions on the cube.
    Named by the three faces they touch, listed in the order that defines
    orientation 0 (the U or D sticker is the reference facelet).

    Numbering follows the Kociemba convention:
        0: URF   1: UFL   2: ULB   3: UBR
        4: DFR   5: DLF   6: DBL   7: DRB
    """
    URF = 0
    UFL = 1
    ULB = 2
    UBR = 3
    DFR = 4
    DLF = 5
    DBL = 6
    DRB = 7


# The three face colors of each corner cubie in the solved state.
# Index 0 is the reference (U/D) sticker; indices 1 and 2 follow
# the clockwise twist direction.
CORNER_COLORS = {
    Corner.URF: (Color.U, Color.R, Color.F),
    Corner.UFL: (Color.U, Color.F, Color.L),
    Corner.ULB: (Color.U, Color.L, Color.B),
    Corner.UBR: (Color.U, Color.B, Color.R),
    Corner.DFR: (Color.D, Color.F, Color.R),
    Corner.DLF: (Color.D, Color.L, Color.F),
    Corner.DBL: (Color.D, Color.B, Color.L),
    Corner.DRB: (Color.D, Color.R, Color.B),
}


# ---------------------------------------------------------------------------
# Edge cubie definitions
# ---------------------------------------------------------------------------

class Edge(IntEnum):
    """
    Twelve edge positions on the cube.
    Named by the two faces they touch. The first face is the reference
    facelet that defines orientation 0.

    Numbering follows the Kociemba convention:
         0: UR   1: UF   2: UL   3: UB
         4: DR   5: DF   6: DL   7: DB
         8: FR   9: FL  10: BL  11: BR
    """
    UR = 0
    UF = 1
    UL = 2
    UB = 3
    DR = 4
    DF = 5
    DL = 6
    DB = 7
    FR = 8
    FL = 9
    BL = 10
    BR = 11


# The two face colors of each edge cubie in the solved state.
# Index 0 is the reference sticker; index 1 is the secondary sticker.
EDGE_COLORS = {
    Edge.UR: (Color.U, Color.R),
    Edge.UF: (Color.U, Color.F),
    Edge.UL: (Color.U, Color.L),
    Edge.UB: (Color.U, Color.B),
    Edge.DR: (Color.D, Color.R),
    Edge.DF: (Color.D, Color.F),
    Edge.DL: (Color.D, Color.L),
    Edge.DB: (Color.D, Color.B),
    Edge.FR: (Color.F, Color.R),
    Edge.FL: (Color.F, Color.L),
    Edge.BL: (Color.B, Color.L),
    Edge.BR: (Color.B, Color.R),
}


# ---------------------------------------------------------------------------
# Fixed center definitions
# ---------------------------------------------------------------------------

# Centers never move. Their face color is always equal to their face index.
# Provided here for completeness and for facelet-string generation.
CENTER_COLORS = {
    0: Color.U,  # Up center
    1: Color.R,  # Right center
    2: Color.F,  # Front center
    3: Color.D,  # Down center
    4: Color.L,  # Left center
    5: Color.B,  # Back center
}
