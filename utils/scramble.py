"""
HUMAN-READABLE DESCRIPTION:
This utility file contains the logic for generating random yet valid Rubik's cube scrambles, mimicking official WCA (World Cube Association) tournament standards.
"""

"""
scramble.py
-----------
WCA-style random scramble generator for the 3x3 Rubik's Cube.

Features:
  - Configurable scramble length (default: 20 to 25 moves)
  - No consecutive moves on the same face
  - Avoids trivial inverse redundancy (e.g., R followed by R')
  - Deterministic when a seed is provided
  - Generates inverse scramble for validation
  - Returns Kociemba-compatible facelet strings
  - Full validation: scramble + inverse = solved state
"""

import random
from core.cube import CubieCube
from core.moves import MOVE_NAMES, get_inverse_move_name


# The six face names, used for filtering consecutive moves
FACE_NAMES = ["U", "D", "R", "L", "F", "B"]

# Opposite face pairs: if the previous move is on one face,
# and the move before that was on the opposite face,
# we should avoid a third move on the first face's axis.
OPPOSITE_FACES = {
    "U": "D", "D": "U",
    "R": "L", "L": "R",
    "F": "B", "B": "F",
}

# Group moves by face
MOVES_BY_FACE = {}
for move in MOVE_NAMES:
    face = move[0]
    if face not in MOVES_BY_FACE:
        MOVES_BY_FACE[face] = []
    MOVES_BY_FACE[face].append(move)


def _get_face(move_name):
    """Extract the face letter from a move name (e.g., 'R' from \"R'\")."""
    return move_name[0]


def generate_scramble(length=None, seed=None):
    """
    Generate a WCA-style random scramble.

    Args:
        length: number of moves. If None, a random length between 20 and 25
                (inclusive) is chosen.
        seed: optional integer seed for deterministic generation.

    Returns:
        list of move name strings (e.g., ["R", "U'", "F2", ...]).
    """
    rng = random.Random(seed)

    if length is None:
        length = rng.randint(20, 25)

    scramble = []

    for _ in range(length):
        # Determine which faces are allowed
        allowed_faces = list(FACE_NAMES)

        if len(scramble) >= 1:
            last_face = _get_face(scramble[-1])
            # Cannot repeat the same face consecutively
            allowed_faces = [f for f in allowed_faces if f != last_face]

            if len(scramble) >= 2:
                second_last_face = _get_face(scramble[-2])
                # If the last two moves are on opposite faces,
                # do not allow the first face again (avoids e.g., U D U sequences)
                if OPPOSITE_FACES.get(last_face) == second_last_face:
                    allowed_faces = [
                        f for f in allowed_faces if f != second_last_face
                    ]

        # Pick a random allowed face
        face = rng.choice(allowed_faces)

        # Pick a random move on that face (regular, prime, or double)
        move = rng.choice(MOVES_BY_FACE[face])
        scramble.append(move)

    return scramble


def get_inverse_scramble(scramble):
    """
    Compute the inverse of a scramble sequence.

    The inverse undoes the scramble: applying scramble then inverse
    returns to the original state.

    Args:
        scramble: list of move name strings.

    Returns:
        list of inverse move name strings, in reversed order.
    """
    return [get_inverse_move_name(m) for m in reversed(scramble)]


def scramble_to_string(scramble):
    """
    Convert a scramble list to a single space-separated string.

    Args:
        scramble: list of move name strings.

    Returns:
        Space-separated string of moves.
    """
    return ' '.join(scramble)


def scramble_to_kociemba(scramble):
    """
    Apply a scramble to a solved cube and return the Kociemba facelet string.

    Args:
        scramble: list of move name strings.

    Returns:
        54-character Kociemba facelet string.
    """
    cube = CubieCube()
    cube.apply_sequence(scramble)
    return cube.to_kociemba_string()


def validate_scramble(scramble, verbose=False):
    """
    Validate a scramble by checking:
      1. Applying scramble then its inverse returns to solved state
      2. The scrambled cube satisfies all legality invariants
      3. Corner orientation sum is 0 mod 3
      4. Edge orientation sum is 0 mod 2
      5. Permutation parity is valid

    Args:
        scramble: list of move name strings.
        verbose: if True, print validation details.

    Returns:
        True if all checks pass.

    Raises:
        AssertionError: if any check fails and verbose is True.
    """
    # Apply scramble
    cube = CubieCube()
    cube.apply_sequence(scramble)

    # Check legality of scrambled state
    legal = cube.is_legal()
    if verbose:
        print(f"Scrambled state is legal: {legal}")
        print(f"Corner orientation sum mod 3: {sum(cube.co) % 3}")
        print(f"Edge orientation sum mod 2: {sum(cube.eo) % 2}")

    if not legal:
        return False

    # Apply inverse scramble
    inverse = get_inverse_scramble(scramble)
    cube.apply_sequence(inverse)

    solved = cube.is_solved()
    if verbose:
        print(f"Scramble + inverse = solved: {solved}")

    return solved


def generate_scramble_at_depth(depth, seed=None):
    """
    Generate a scramble of exactly the given depth (number of moves),
    following WCA-style constraints.

    This is useful for curriculum learning where we need scrambles
    of a specific depth.

    Args:
        depth: exact number of moves.
        seed: optional integer seed for deterministic generation.

    Returns:
        list of move name strings.
    """
    return generate_scramble(length=depth, seed=seed)
