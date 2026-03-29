"""
HUMAN-READABLE DESCRIPTION:
This script handles drawing the Python-based matplotlib 3D visualizer, calculating coordinates and colors for a very basic rigid geometric rendering.
"""

"""
renderer3d.py
-------------
Matplotlib-based 3D renderer for the Rubik's Cube using Poly3DCollection.

Renders the cube as 26 visible small cubes (cubies) with gaps between them.
The logical cube state is read from a CubieCube instance via the Kociemba
facelet string; rendering is purely visual and never mutates cube state.

Color convention (Singmaster standard):
    U = White, R = Red, F = Green, D = Yellow, L = Orange, B = Blue
    Internal (hidden) faces = Dark Gray (#1a1a1a)
"""

import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# ---------------------------------------------------------------------------
# Color mapping
# ---------------------------------------------------------------------------

# Facelet character -> RGB hex color for rendering
FACE_COLORS = {
    'U': '#FFFFFF',   # White
    'R': '#C41E3A',   # Red
    'F': '#009E60',   # Green
    'D': '#FFD500',   # Yellow
    'L': '#FF5800',   # Orange
    'B': '#0051BA',   # Blue
}

INTERNAL_COLOR = '#1a1a1a'   # Near-black for hidden faces
EDGE_COLOR = '#000000'       # Black edge lines
CUBIE_SIZE = 0.92            # < 1.0 creates gaps between cubies


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _cube_faces(x, y, z, size=CUBIE_SIZE):
    """
    Return the 6 faces (each a list of 4 corners) of a unit cubie
    centered at (x, y, z) with the given edge length.

    Face ordering: -X, +X, -Y, +Y, -Z, +Z
    which corresponds to: L, R, D, U, B, F
    in the standard cube coordinate system where:
        +X = R,  -X = L
        +Y = U,  -Y = D
        +Z = F,  -Z = B
    """
    s = size / 2.0
    # 8 corners of the small cube
    corners = np.array([
        [x - s, y - s, z - s],  # 0
        [x + s, y - s, z - s],  # 1
        [x + s, y + s, z - s],  # 2
        [x - s, y + s, z - s],  # 3
        [x - s, y - s, z + s],  # 4
        [x + s, y - s, z + s],  # 5
        [x + s, y + s, z + s],  # 6
        [x - s, y + s, z + s],  # 7
    ])

    faces = [
        [corners[0], corners[3], corners[7], corners[4]],  # -X face (L)
        [corners[1], corners[2], corners[6], corners[5]],  # +X face (R)
        [corners[0], corners[1], corners[5], corners[4]],  # -Y face (D)
        [corners[2], corners[3], corners[7], corners[6]],  # +Y face (U)
        [corners[0], corners[1], corners[2], corners[3]],  # -Z face (B)
        [corners[4], corners[5], corners[6], corners[7]],  # +Z face (F)
    ]
    return faces


def _get_facelet_grid():
    """
    Build a mapping from the 54 Kociemba facelet positions to
    (cubie_x, cubie_y, cubie_z, face_index) tuples.

    The cube is centered at origin. Cubie coordinates are in {-1, 0, 1}.
    Face_index follows _cube_faces ordering: 0=-X(L), 1=+X(R), 2=-Y(D), 3=+Y(U), 4=-Z(B), 5=+Z(F)
    """
    mapping = {}

    # Kociemba facelet numbering within each face:
    #   0 1 2
    #   3 4 5
    #   6 7 8

    # U face (facelets 0-8): Y = +1, face_index = 3 (+Y)
    # Looking down at U face: row goes -Z to +Z (back to front),
    # column goes -X to +X (left to right)
    for idx in range(9):
        row, col = divmod(idx, 3)
        x = col - 1       # -1, 0, 1
        z = -(row - 1)     # 1, 0, -1  (row 0 = back = +Z? No, standard: row 0 = back)
        # Kociemba U face: row 0 is the back edge of U
        # U0 U1 U2 are at z=1 (back side when B is -Z... wait)
        # Let me be precise about the coordinate system:
        #   Standard: F face is at z=+1, B face at z=-1
        #   U face at y=+1, D face at y=-1
        #   R face at x=+1, L face at x=-1
        #
        # Kociemba U face layout (viewed from above):
        #   U0(ULB corner) U1(UB edge) U2(UBR corner)   <- back row (z=-1)
        #   U3(UL edge)    U4(center)  U5(UR edge)      <- middle
        #   U6(UFL corner) U7(UF edge) U8(URF corner)   <- front row (z=+1)
        x = col - 1
        z = 1 - row   # row 0 -> z=1... no, row 0 is back (z=-1)
        z = -(row - 1)  # row 0 -> z=1, row 1 -> z=0, row 2 -> z=-1
        # But ULB is at position (x=-1, y=1, z=-1), so U0 should map to x=-1, z=-1
        # U0 = row 0, col 0 -> x=-1, z = -(0-1) = 1. That's wrong.
        # Correction: For U face, looking DOWN onto it:
        #   U0 = back-left (x=-1, z=-1)
        #   U2 = back-right (x=1, z=-1)
        #   U6 = front-left (x=-1, z=1)
        #   U8 = front-right (x=1, z=1)
        z = row - 1    # row 0 -> z=-1, row 2 -> z=1
        z = -(row - 1)  # Hmm, let me just hardcode the correct mapping
        pass

    # It's cleaner to build this mapping explicitly.
    # I'll map each of the 54 facelets to the cubie grid coordinate + face.

    # Helper: given face, row (0-2), col (0-2), return (x, y, z, face_idx)
    def u_face(row, col):
        # U face: y=1, face_idx=3 (+Y)
        # Kociemba layout (looking down at U):
        #   row 0 = back edge (z=-1), row 2 = front edge (z=+1)
        #   col 0 = left (x=-1),      col 2 = right (x=+1)
        return (col - 1, 1, row - 1, 3)

    def d_face(row, col):
        # D face: y=-1, face_idx=2 (-Y)
        # Kociemba layout (looking up at D from below):
        #   row 0 = front edge (z=+1), row 2 = back edge (z=-1)
        #   col 0 = left (x=-1),       col 2 = right (x=+1)
        return (col - 1, -1, 1 - row, 2)

    def f_face(row, col):
        # F face: z=1, face_idx=5 (+Z)
        # Looking at front: row 0 = top (y=+1), row 2 = bottom (y=-1)
        # col 0 = left (x=-1), col 2 = right (x=+1)
        return (col - 1, 1 - row, 1, 5)

    def b_face(row, col):
        # B face: z=-1, face_idx=4 (-Z)
        # Looking at back (from behind): row 0 = top (y=+1), row 2 = bottom (y=-1)
        # col 0 = left-when-looking-at-back = RIGHT in world (x=+1)
        # col 2 = right-when-looking-at-back = LEFT in world (x=-1)
        return (1 - col, 1 - row, -1, 4)

    def r_face(row, col):
        # R face: x=1, face_idx=1 (+X)
        # Looking at right face: row 0 = top (y=+1), row 2 = bottom (y=-1)
        # col 0 = front (z=+1)... actually in Kociemba:
        # R face col 0 = the edge touching F face, so z=+1 -> no...
        # Standard Kociemba R face orientation (looking at it from the right):
        # col 0 is at the back (z=-1), col 2 is at the front... no.
        # Let me check: R1=facelet 9, which is the URF corner's R sticker.
        # URF is at (1, 1, 1), so R face facelet 9 (row=0, col=0) -> z=1
        # R3=facelet 11, which is UBR corner's R sticker.
        # UBR is at (1, 1, -1), so R face facelet 11 (row=0, col=2) -> z=-1
        # So col 0 -> z=+1, col 2 -> z=-1 (front to back)
        return (1, 1 - row, 1 - col, 1)

    def l_face(row, col):
        # L face: x=-1, face_idx=0 (-X)
        # Looking at left face (from the left):
        # L1=facelet 36, ULB corner's L sticker. ULB at (-1, 1, -1).
        # facelet 36 is row=0, col=0 -> z=-1... no wait.
        # Kociemba L face: L1(36), L2(37), L3(38)
        # L1 = ULB corner L sticker -> position (-1, 1, -1) -> row=0, col=0
        # L3 = UFL corner L sticker -> position (-1, 1, 1) -> row=0, col=2
        # So col 0 -> z=-1, col 2 -> z=+1
        return (-1, 1 - row, col - 1, 0)
    
    face_funcs = [
        (0, u_face),    # facelets 0..8
        (9, r_face),    # facelets 9..17
        (18, f_face),   # facelets 18..26
        (27, d_face),   # facelets 27..35
        (36, l_face),   # facelets 36..44
        (45, b_face),   # facelets 45..53
    ]

    for base, func in face_funcs:
        for i in range(9):
            row, col = divmod(i, 3)
            mapping[base + i] = func(row, col)

    return mapping


# Pre-compute the facelet mapping at module load
_FACELET_MAP = _get_facelet_grid()


# ---------------------------------------------------------------------------
# Main rendering function
# ---------------------------------------------------------------------------

def draw_cube(ax, cube):
    """
    Render the Rubik's Cube state onto a matplotlib Axes3D object.

    Reads the logical state from `cube` (a CubieCube instance) via its
    Kociemba facelet string. Never mutates the cube state.

    Args:
        ax: matplotlib Axes3D instance to draw on.
        cube: CubieCube instance.
    """
    ax.cla()

    facelet_str = cube.to_kociemba_string()

    # Build a color lookup: (x, y, z, face_idx) -> color
    color_lookup = {}
    for flet_idx, (x, y, z, face_idx) in _FACELET_MAP.items():
        ch = facelet_str[flet_idx]
        color_lookup[(x, y, z, face_idx)] = FACE_COLORS[ch]

    # Render all 26 visible cubies (skip the invisible center-of-cube at (0,0,0))
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == 0 and y == 0 and z == 0:
                    continue  # Skip invisible internal cube

                faces = _cube_faces(x, y, z)
                face_colors = []

                # Face ordering: 0=-X(L), 1=+X(R), 2=-Y(D), 3=+Y(U), 4=-Z(B), 5=+Z(F)
                for face_idx in range(6):
                    key = (x, y, z, face_idx)
                    if key in color_lookup:
                        face_colors.append(color_lookup[key])
                    else:
                        face_colors.append(INTERNAL_COLOR)

                poly = Poly3DCollection(
                    faces,
                    facecolors=face_colors,
                    edgecolors=EDGE_COLOR,
                    linewidths=0.5,
                )
                ax.add_collection3d(poly)

    # Draw "E" logo on the U-center (white center at position 0, 1, 0)
    # Top surface of U-center cubie is at y = 1 + CUBIE_SIZE/2 ≈ 1.46
    # Place text at y = 1.47 (just above surface to avoid z-fighting)
    ax.text(
        0, 1.47, 0,      # (x, y, z) - on the U-center face surface
        'E',
        fontsize=24,
        fontweight='bold',
        fontfamily='serif',
        color='#1a1a1a',
        ha='center', va='center',
    )

    # Set axis properties
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    ax.set_box_aspect([1, 1, 1])
    ax.set_axis_off()


def create_info_text(cube, ax, move_history=None):
    """
    Add informational text overlay showing cube status.

    Args:
        cube: CubieCube instance.
        ax: matplotlib Axes3D instance.
        move_history: optional list of move name strings.
    """
    status = "SOLVED ✓" if cube.is_solved() else "SCRAMBLED"
    legal = "Legal ✓" if cube.is_legal() else "ILLEGAL ✗"
    co_sum = f"CO sum mod 3 = {sum(cube.co) % 3}"
    eo_sum = f"EO sum mod 2 = {sum(cube.eo) % 2}"

    info = f"{status}  |  {legal}  |  {co_sum}  |  {eo_sum}"

    if move_history:
        last_moves = ' '.join(move_history[-10:])
        info += f"\nLast moves: {last_moves}"

    return info
