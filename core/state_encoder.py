"""
HUMAN-READABLE DESCRIPTION:
This utility handles converting the 3D cube's complex mathematical state into numerical formats (like One-Hot encoding) so that Neural Networks and AI models can understand it.
"""

"""
state_encoder.py
----------------
One-hot encoding of a Rubik's Cube state for neural network input.

Encoding scheme:
  - 54 facelets, each with 6 possible colors
  - One-hot encode each facelet: 6 binary values
  - Total input dimension: 54 * 6 = 324

The encoding is deterministic and reversible.
"""

import numpy as np
from core.cubie import Color, COLOR_CHARS, CHAR_TO_COLOR


# Number of facelets on a standard 3x3 Rubik's Cube
NUM_FACELETS = 54

# Number of possible colors per facelet
NUM_COLORS = 6

# Total encoded vector length
ENCODING_DIM = NUM_FACELETS * NUM_COLORS  # 324

# Mapping from Color enum to one-hot index
COLOR_TO_INDEX = {c: int(c) for c in Color}

# Mapping from index to Color enum
INDEX_TO_COLOR = {v: k for k, v in COLOR_TO_INDEX.items()}


def encode_state(cube):
    """
    Encode a CubieCube state as a one-hot vector of shape (324,).

    Args:
        cube: a CubieCube instance.

    Returns:
        numpy array of shape (324,) with dtype float32.
        Each group of 6 consecutive values represents one facelet,
        with exactly one 1.0 and five 0.0 values.
    """
    facelet_str = cube.to_kociemba_string()
    return encode_facelet_string(facelet_str)


# Pre-calculate mapping for vectorized encoding
_CHAR_MAP = np.zeros(256, dtype=np.int32)
for ch, color in CHAR_TO_COLOR.items():
    _CHAR_MAP[ord(ch)] = COLOR_TO_INDEX[color]

def encode_facelet_string(facelet_str):
    """
    Encode a 54-character Kociemba facelet string as a one-hot vector.
    Uses vectorized NumPy for high performance.
    """
    # Convert string to byte array of ASCII values
    chars = np.frombuffer(facelet_str.encode('ascii'), dtype=np.uint8)
    
    # Map characters to color indices (0-5)
    color_indices = _CHAR_MAP[chars]
    
    # Create one-hot matrix (54, 6)
    one_hot = np.zeros((NUM_FACELETS, NUM_COLORS), dtype=np.float32)
    one_hot[np.arange(NUM_FACELETS), color_indices] = 1.0
    
    # Flatten to (324,)
    return one_hot.ravel()


def decode_state(vec):
    """
    Decode a one-hot vector back to a 54-character facelet string.

    Args:
        vec: numpy array of shape (324,).

    Returns:
        54-character string of facelet colors.
    """
    chars = []
    for i in range(NUM_FACELETS):
        start = i * NUM_COLORS
        color_index = int(np.argmax(vec[start:start + NUM_COLORS]))
        color = INDEX_TO_COLOR[color_index]
        chars.append(COLOR_CHARS[color])
    return ''.join(chars)


# ---------------------------------------------------------------------------
# Move index mapping
# ---------------------------------------------------------------------------

# Standard ordering of all 18 moves for the neural network output layer.
# This must match the ordering used during training.
MOVE_LABELS = [
    "U", "U'", "U2",
    "R", "R'", "R2",
    "F", "F'", "F2",
    "D", "D'", "D2",
    "L", "L'", "L2",
    "B", "B'", "B2",
]

MOVE_TO_INDEX = {name: idx for idx, name in enumerate(MOVE_LABELS)}
INDEX_TO_MOVE = {idx: name for idx, name in enumerate(MOVE_LABELS)}
NUM_MOVES = len(MOVE_LABELS)  # 18
