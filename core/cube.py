"""
HUMAN-READABLE DESCRIPTION:
This is the core Rubik's Cube state engine. It mathematically tracks the permutation and orientation of every corner and edge piece (cp, co, ep, eo) and enforces the strict geometric rules that define a legal 3x3 cube.
"""

"""
cube.py
-------
CubieCube class: the main data structure for a 3x3 Rubik's Cube at cubie level.

The cube state is represented by four arrays:
  - corner_permutation:  8-element list, corner_permutation[slot] = which corner cubie is in that slot
  - corner_orientation:  8-element list, orientation of each corner in its slot (0, 1, or 2)
  - edge_permutation:   12-element list, edge_permutation[slot] = which edge cubie is in that slot
  - edge_orientation:   12-element list, orientation of each edge in its slot (0 or 1)

Centers are fixed and never stored in a permutation array.
They are always at their canonical positions.
"""

import copy
from core.cubie import (
    Color, Corner, Edge,
    CORNER_COLORS, EDGE_COLORS, CENTER_COLORS,
    COLOR_CHARS, CHAR_TO_COLOR,
)
from core.moves import ALL_MOVES, MOVE_NAMES, get_inverse_move_name


class CubieCube:
    """
    A cubie-level model of the 3x3 Rubik's Cube.

    Attributes:
        cp: list[int] of length 8, corner permutation
        co: list[int] of length 8, corner orientation (values in {0, 1, 2})
        ep: list[int] of length 12, edge permutation
        eo: list[int] of length 12, edge orientation (values in {0, 1})
    """

    def __init__(self):
        """Initialize to the solved state."""
        self.cp = list(range(8))   # Corner i is in slot i
        self.co = [0] * 8          # All orientations are 0
        self.ep = list(range(12))  # Edge i is in slot i
        self.eo = [0] * 12         # All orientations are 0

    def copy(self):
        """Return a deep copy of this cube state."""
        new = CubieCube()
        new.cp = self.cp[:]
        new.co = self.co[:]
        new.ep = self.ep[:]
        new.eo = self.eo[:]
        return new

    # ------------------------------------------------------------------
    # Move application
    # ------------------------------------------------------------------

    def apply_move(self, move_name):
        """
        Apply a single move to this cube (in place).

        Args:
            move_name: string, one of the 18 standard moves
                       (e.g. "U", "U'", "U2", "R", etc.)

        Raises:
            ValueError: if move_name is not recognized.
        """
        if move_name not in ALL_MOVES:
            raise ValueError(f"Unknown move: {move_name}")

        move_def = ALL_MOVES[move_name]

        # Apply corner permutation and orientation
        new_cp = [0] * 8
        new_co = [0] * 8
        for i in range(8):
            new_cp[i] = self.cp[move_def.corner_perm[i]]
            new_co[i] = (self.co[move_def.corner_perm[i]] + move_def.corner_orient[i]) % 3

        # Apply edge permutation and orientation
        new_ep = [0] * 12
        new_eo = [0] * 12
        for i in range(12):
            new_ep[i] = self.ep[move_def.edge_perm[i]]
            new_eo[i] = (self.eo[move_def.edge_perm[i]] + move_def.edge_orient[i]) % 2

        self.cp = new_cp
        self.co = new_co
        self.ep = new_ep
        self.eo = new_eo

    def apply_sequence(self, move_list):
        """
        Apply a sequence of moves to this cube (in place).

        Args:
            move_list: list of move name strings, or a single space-separated string.
        """
        if isinstance(move_list, str):
            move_list = move_list.split()
        for move_name in move_list:
            self.apply_move(move_name)

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_solved(self):
        """Return True if the cube is in the solved (identity) state."""
        for i in range(8):
            if self.cp[i] != i or self.co[i] != 0:
                return False
        for i in range(12):
            if self.ep[i] != i or self.eo[i] != 0:
                return False
        return True

    def is_legal(self):
        """
        Verify that this cube state satisfies all legality invariants:
          1. Corner permutation is a valid permutation of {0..7}
          2. Edge permutation is a valid permutation of {0..11}
          3. Sum of corner orientations is 0 mod 3
          4. Sum of edge orientations is 0 mod 2
          5. Corner and edge permutation parities are equal

        Returns:
            True if all invariants hold.
        """
        # Check permutation validity
        if sorted(self.cp) != list(range(8)):
            return False
        if sorted(self.ep) != list(range(12)):
            return False

        # Check orientation constraints
        if sum(self.co) % 3 != 0:
            return False
        if sum(self.eo) % 2 != 0:
            return False

        # Check parity constraint
        corner_parity = self._permutation_parity(self.cp)
        edge_parity = self._permutation_parity(self.ep)
        if corner_parity != edge_parity:
            return False

        return True

    @staticmethod
    def _permutation_parity(perm):
        """
        Compute the parity of a permutation (0 = even, 1 = odd).
        Uses cycle counting: parity = (n - number_of_cycles) mod 2.
        """
        n = len(perm)
        visited = [False] * n
        num_cycles = 0
        for i in range(n):
            if not visited[i]:
                num_cycles += 1
                j = i
                while not visited[j]:
                    visited[j] = True
                    j = perm[j]
        return (n - num_cycles) % 2

    # ------------------------------------------------------------------
    # Facelet string conversion (Kociemba format)
    # ------------------------------------------------------------------

    def to_kociemba_string(self):
        """
        Convert this cubie state to a 54-character facelet string.

        The string follows the standard Kociemba ordering:
            Positions  0.. 8: U face (U1..U9), row by row
            Positions  9..17: R face (R1..R9)
            Positions 18..26: F face (F1..F9)
            Positions 27..35: D face (D1..D9)
            Positions 36..44: L face (L1..L9)
            Positions 45..53: B face (B1..B9)

        Within each face the 9 facelets are numbered:
            0 1 2
            3 4 5
            6 7 8
        where facelet 4 is the (fixed) center.

        Centers are ALWAYS fixed at their canonical colors:
            U-center = U, R-center = R, F-center = F,
            D-center = D, L-center = L, B-center = B.
        """
        facelets = [''] * 54

        # Set fixed centers (position 4 of each face)
        facelets[4] = 'U'   # U center
        facelets[13] = 'R'  # R center
        facelets[22] = 'F'  # F center
        facelets[31] = 'D'  # D center
        facelets[40] = 'L'  # L center
        facelets[49] = 'B'  # B center

        # Standard Kociemba facelet numbering:
        #
        # U face:         R face:         F face:
        #  0  1  2         9 10 11        18 19 20
        #  3  4  5        12 13 14        21 22 23
        #  6  7  8        15 16 17        24 25 26
        #
        # D face:         L face:         B face:
        # 27 28 29        36 37 38        45 46 47
        # 30 31 32        39 40 41        48 49 50
        # 33 34 35        42 43 44        51 52 53
        #
        # Corner facelet positions (U/D sticker, clockwise sticker 1, clockwise sticker 2):
        #   URF: U9=8,  R1=9,  F3=20
        #   UFL: U7=6,  F1=18, L3=38
        #   ULB: U1=0,  L1=36, B3=47
        #   UBR: U3=2,  B1=45, R3=11
        #   DFR: D3=29, F9=26, R7=15
        #   DLF: D1=27, L9=44, F7=24
        #   DBL: D7=33, B9=53, L7=42
        #   DRB: D9=35, R9=17, B7=51

        corner_facelet_positions = {
            Corner.URF: (8, 9, 20),
            Corner.UFL: (6, 18, 38),
            Corner.ULB: (0, 36, 47),
            Corner.UBR: (2, 45, 11),
            Corner.DFR: (29, 26, 15),
            Corner.DLF: (27, 44, 24),
            Corner.DBL: (33, 53, 42),
            Corner.DRB: (35, 17, 51),
        }

        for slot in range(8):
            cubie = self.cp[slot]
            orient = self.co[slot]
            colors = CORNER_COLORS[Corner(cubie)]
            positions = corner_facelet_positions[Corner(slot)]
            for k in range(3):
                color_idx = (k - orient) % 3
                facelets[positions[k]] = COLOR_CHARS[colors[color_idx]]

        # Edge facelet positions (reference sticker, secondary sticker):
        #   UR: U6=5,  R2=10
        #   UF: U8=7,  F2=19
        #   UL: U4=3,  L2=37
        #   UB: U2=1,  B2=46
        #   DR: D6=32, R8=16
        #   DF: D2=28, F8=25
        #   DL: D4=30, L8=43
        #   DB: D8=34, B8=52
        #   FR: F6=23, R4=12
        #   FL: F4=21, L6=41
        #   BL: B6=48, L4=39
        #   BR: B4=50, R6=14

        edge_facelet_positions = {
            Edge.UR: (5, 10),
            Edge.UF: (7, 19),
            Edge.UL: (3, 37),
            Edge.UB: (1, 46),
            Edge.DR: (32, 16),
            Edge.DF: (28, 25),
            Edge.DL: (30, 43),
            Edge.DB: (34, 52),
            Edge.FR: (23, 12),
            Edge.FL: (21, 41),
            Edge.BL: (48, 39),
            Edge.BR: (50, 14),
        }

        for slot in range(12):
            cubie = self.ep[slot]
            orient = self.eo[slot]
            colors = EDGE_COLORS[Edge(cubie)]
            positions = edge_facelet_positions[Edge(slot)]
            for k in range(2):
                color_idx = (k + orient) % 2
                facelets[positions[k]] = COLOR_CHARS[colors[color_idx]]

        return ''.join(facelets)

    @classmethod
    def from_kociemba_string(cls, facelet_str):
        """
        Create a CubieCube from a 54-character Kociemba facelet string.

        Args:
            facelet_str: 54-character string using characters U, R, F, D, L, B.

        Returns:
            A new CubieCube instance.

        Raises:
            ValueError: if the string is malformed.
        """
        if len(facelet_str) != 54:
            raise ValueError(
                f"Facelet string must be exactly 54 characters, got {len(facelet_str)}"
            )

        cube = cls()

        corner_facelet_positions = {
            Corner.URF: (8, 9, 20),
            Corner.UFL: (6, 18, 38),
            Corner.ULB: (0, 36, 47),
            Corner.UBR: (2, 45, 11),
            Corner.DFR: (29, 26, 15),
            Corner.DLF: (27, 44, 24),
            Corner.DBL: (33, 53, 42),
            Corner.DRB: (35, 17, 51),
        }

        edge_facelet_positions = {
            Edge.UR: (5, 10),
            Edge.UF: (7, 19),
            Edge.UL: (3, 37),
            Edge.UB: (1, 46),
            Edge.DR: (32, 16),
            Edge.DF: (28, 25),
            Edge.DL: (30, 43),
            Edge.DB: (34, 52),
            Edge.FR: (23, 12),
            Edge.FL: (21, 41),
            Edge.BL: (48, 39),
            Edge.BR: (50, 14),
        }

        # Decode corners
        for slot in range(8):
            positions = corner_facelet_positions[Corner(slot)]
            observed = tuple(CHAR_TO_COLOR[facelet_str[p]] for p in positions)

            found = False
            for cubie_id in range(8):
                colors = CORNER_COLORS[Corner(cubie_id)]
                for orient in range(3):
                    rotated = tuple(colors[(k - orient) % 3] for k in range(3))
                    if rotated == observed:
                        cube.cp[slot] = cubie_id
                        cube.co[slot] = orient
                        found = True
                        break
                if found:
                    break
            if not found:
                raise ValueError(
                    f"Could not identify corner in slot {slot} "
                    f"with colors {observed}"
                )

        # Decode edges
        for slot in range(12):
            positions = edge_facelet_positions[Edge(slot)]
            observed = tuple(CHAR_TO_COLOR[facelet_str[p]] for p in positions)

            found = False
            for cubie_id in range(12):
                colors = EDGE_COLORS[Edge(cubie_id)]
                for orient in range(2):
                    rotated = tuple(colors[(k + orient) % 2] for k in range(2))
                    if rotated == observed:
                        cube.ep[slot] = cubie_id
                        cube.eo[slot] = orient
                        found = True
                        break
                if found:
                    break
            if not found:
                raise ValueError(
                    f"Could not identify edge in slot {slot} "
                    f"with colors {observed}"
                )

        return cube

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"CubieCube(\n"
            f"  cp={self.cp},\n"
            f"  co={self.co},\n"
            f"  ep={self.ep},\n"
            f"  eo={self.eo}\n"
            f")"
        )

    def __eq__(self, other):
        if not isinstance(other, CubieCube):
            return False
        return (
            self.cp == other.cp
            and self.co == other.co
            and self.ep == other.ep
            and self.eo == other.eo
        )

    def print_faces(self):
        """Print a 2D net of the cube faces for inspection."""
        s = self.to_kociemba_string()
        faces = {
            'U': s[0:9],
            'R': s[9:18],
            'F': s[18:27],
            'D': s[27:36],
            'L': s[36:45],
            'B': s[45:54],
        }

        def face_rows(face_str):
            return [face_str[0:3], face_str[3:6], face_str[6:9]]

        u = face_rows(faces['U'])
        l = face_rows(faces['L'])
        f = face_rows(faces['F'])
        r = face_rows(faces['R'])
        b = face_rows(faces['B'])
        d = face_rows(faces['D'])

        blank = "      "
        for row in u:
            print(blank + ' '.join(row))
        for i in range(3):
            print(
                ' '.join(l[i]) + " "
                + ' '.join(f[i]) + " "
                + ' '.join(r[i]) + " "
                + ' '.join(b[i])
            )
        for row in d:
            print(blank + ' '.join(row))
