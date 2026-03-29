"""
HUMAN-READABLE DESCRIPTION:
Unit tests to ensure our random scramble generator is actually random, respects the correct move notation, and doesn't output contradictory sequences.
"""

"""
test_scramble.py
----------------
Unit tests for the WCA-style scramble generator.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils.scramble import (
    generate_scramble, get_inverse_scramble,
    validate_scramble, scramble_to_kociemba,
)
from core.cube import CubieCube


class TestScrambleGeneration:
    """Tests for scramble generation."""

    def test_default_length(self):
        scramble = generate_scramble(seed=42)
        assert 20 <= len(scramble) <= 25

    def test_custom_length(self):
        scramble = generate_scramble(length=10, seed=42)
        assert len(scramble) == 10

    def test_deterministic_with_seed(self):
        s1 = generate_scramble(seed=123)
        s2 = generate_scramble(seed=123)
        assert s1 == s2

    def test_different_seeds_differ(self):
        s1 = generate_scramble(seed=1)
        s2 = generate_scramble(seed=2)
        assert s1 != s2

    def test_no_consecutive_same_face(self):
        scramble = generate_scramble(length=50, seed=42)
        for i in range(1, len(scramble)):
            face_a = scramble[i - 1][0]
            face_b = scramble[i][0]
            assert face_a != face_b, (
                f"Consecutive same face at positions {i-1} and {i}: "
                f"{scramble[i-1]} and {scramble[i]}"
            )

    def test_all_moves_are_valid(self):
        from core.moves import MOVE_NAMES
        valid_moves = set(MOVE_NAMES)
        scramble = generate_scramble(length=100, seed=42)
        for move in scramble:
            assert move in valid_moves


class TestInverseScramble:
    """Tests for inverse scramble generation."""

    def test_scramble_plus_inverse_is_solved(self):
        for seed in range(10):
            scramble = generate_scramble(seed=seed)
            cube = CubieCube()
            cube.apply_sequence(scramble)
            inverse = get_inverse_scramble(scramble)
            cube.apply_sequence(inverse)
            assert cube.is_solved(), f"Failed for seed {seed}"

    def test_inverse_length_matches(self):
        scramble = generate_scramble(seed=42)
        inverse = get_inverse_scramble(scramble)
        assert len(scramble) == len(inverse)


class TestValidation:
    """Tests for scramble validation."""

    def test_valid_scramble(self):
        scramble = generate_scramble(seed=42)
        assert validate_scramble(scramble)

    def test_multiple_scrambles_valid(self):
        for seed in range(20):
            scramble = generate_scramble(seed=seed)
            assert validate_scramble(scramble), f"Validation failed for seed {seed}"


class TestKociembaString:
    """Tests for Kociemba string output."""

    def test_kociemba_string_length(self):
        scramble = generate_scramble(seed=42)
        s = scramble_to_kociemba(scramble)
        assert len(s) == 54

    def test_kociemba_string_valid_chars(self):
        scramble = generate_scramble(seed=42)
        s = scramble_to_kociemba(scramble)
        valid = set("URFDLB")
        for ch in s:
            assert ch in valid

    def test_solved_produces_identity_string(self):
        scramble = []
        s = scramble_to_kociemba(scramble)
        assert s == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
