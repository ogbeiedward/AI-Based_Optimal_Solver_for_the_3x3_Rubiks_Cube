"""
HUMAN-READABLE DESCRIPTION:
These unit tests validate the state_encoder, ensuring that the cube's physical state translates perfectly into the dense neural-network compatible tensors.
"""

"""
test_encoder.py
---------------
Unit tests for the state encoder module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from core.cube import CubieCube
from core.state_encoder import (
    encode_state, decode_state, encode_facelet_string,
    ENCODING_DIM, NUM_MOVES, MOVE_LABELS, MOVE_TO_INDEX,
)


class TestEncoding:
    """Tests for one-hot encoding."""

    def test_output_shape(self):
        cube = CubieCube()
        vec = encode_state(cube)
        assert vec.shape == (ENCODING_DIM,)  # (324,)

    def test_output_dtype(self):
        cube = CubieCube()
        vec = encode_state(cube)
        assert vec.dtype == np.float32

    def test_one_hot_property(self):
        """Each group of 6 values should have exactly one 1.0."""
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F'"])
        vec = encode_state(cube)
        for i in range(54):
            group = vec[i * 6:(i + 1) * 6]
            assert np.sum(group) == 1.0, f"Facelet {i} does not have exactly one 1.0"
            assert np.max(group) == 1.0
            assert np.min(group) == 0.0


class TestDecoding:
    """Tests for the decode round-trip."""

    def test_solved_round_trip(self):
        cube = CubieCube()
        original = cube.to_kociemba_string()
        vec = encode_state(cube)
        decoded = decode_state(vec)
        assert decoded == original

    def test_scrambled_round_trip(self):
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F'", "D2", "L", "B"])
        original = cube.to_kociemba_string()
        vec = encode_state(cube)
        decoded = decode_state(vec)
        assert decoded == original


class TestMoveLabels:
    """Tests for move label consistency."""

    def test_num_moves(self):
        assert NUM_MOVES == 18

    def test_all_labels_present(self):
        assert len(MOVE_LABELS) == 18

    def test_index_mapping_round_trip(self):
        for name in MOVE_LABELS:
            idx = MOVE_TO_INDEX[name]
            assert MOVE_LABELS[idx] == name

    def test_indices_are_0_to_17(self):
        indices = sorted(MOVE_TO_INDEX.values())
        assert indices == list(range(18))
