"""
HUMAN-READABLE DESCRIPTION:
This file contains automated unit tests that ruthlessly verify the cube's core mechanics to ensure that permutations, orientations, and parity checks are working flawlessly.
"""

"""
test_cube.py
------------
Unit tests for the cubie-level Rubik's Cube simulator.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.cube import CubieCube
from core.cubie import Corner, Edge
from core.moves import MOVE_NAMES, ALL_MOVES


class TestSolvedState:
    """Tests for the initial solved state."""

    def test_solved_cube_is_solved(self):
        cube = CubieCube()
        assert cube.is_solved()

    def test_solved_cube_is_legal(self):
        cube = CubieCube()
        assert cube.is_legal()

    def test_solved_kociemba_string(self):
        cube = CubieCube()
        expected = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        assert cube.to_kociemba_string() == expected

    def test_centers_are_fixed_in_solved(self):
        cube = CubieCube()
        s = cube.to_kociemba_string()
        # Center positions: 4(U), 13(R), 22(F), 31(D), 40(L), 49(B)
        assert s[4] == 'U'
        assert s[13] == 'R'
        assert s[22] == 'F'
        assert s[31] == 'D'
        assert s[40] == 'L'
        assert s[49] == 'B'


class TestSingleMoves:
    """Tests that single moves produce unsolved but legal states."""

    @pytest.mark.parametrize("move", ["U", "D", "R", "L", "F", "B"])
    def test_single_move_not_solved(self, move):
        cube = CubieCube()
        cube.apply_move(move)
        assert not cube.is_solved()

    @pytest.mark.parametrize("move", MOVE_NAMES)
    def test_single_move_is_legal(self, move):
        cube = CubieCube()
        cube.apply_move(move)
        assert cube.is_legal()

    @pytest.mark.parametrize("move", MOVE_NAMES)
    def test_centers_never_move(self, move):
        cube = CubieCube()
        cube.apply_move(move)
        s = cube.to_kociemba_string()
        assert s[4] == 'U', f"U center moved after {move}"
        assert s[13] == 'R', f"R center moved after {move}"
        assert s[22] == 'F', f"F center moved after {move}"
        assert s[31] == 'D', f"D center moved after {move}"
        assert s[40] == 'L', f"L center moved after {move}"
        assert s[49] == 'B', f"B center moved after {move}"


class TestMoveIdentities:
    """Tests for algebraic identities of face rotations."""

    @pytest.mark.parametrize("face", ["U", "D", "R", "L", "F", "B"])
    def test_four_rotations_identity(self, face):
        """Applying the same face move 4 times returns to solved."""
        cube = CubieCube()
        for _ in range(4):
            cube.apply_move(face)
        assert cube.is_solved()

    @pytest.mark.parametrize("face", ["U", "D", "R", "L", "F", "B"])
    def test_move_and_inverse(self, face):
        """Applying a move then its inverse returns to solved."""
        cube = CubieCube()
        cube.apply_move(face)
        cube.apply_move(face + "'")
        assert cube.is_solved()

    @pytest.mark.parametrize("face", ["U", "D", "R", "L", "F", "B"])
    def test_double_move_is_two_singles(self, face):
        """X2 should equal X applied twice."""
        cube1 = CubieCube()
        cube1.apply_move(face)
        cube1.apply_move(face)

        cube2 = CubieCube()
        cube2.apply_move(face + "2")

        assert cube1 == cube2

    @pytest.mark.parametrize("face", ["U", "D", "R", "L", "F", "B"])
    def test_double_move_self_inverse(self, face):
        """X2 X2 = identity (double moves are self-inverse)."""
        cube = CubieCube()
        cube.apply_move(face + "2")
        cube.apply_move(face + "2")
        assert cube.is_solved()


class TestOrientationInvariants:
    """Tests that orientation sums are preserved."""

    def test_corner_orientation_sum_after_moves(self):
        cube = CubieCube()
        moves = ["R", "U", "F'", "D2", "L", "B'", "R2", "U'"]
        cube.apply_sequence(moves)
        assert sum(cube.co) % 3 == 0

    def test_edge_orientation_sum_after_moves(self):
        cube = CubieCube()
        moves = ["F", "R", "B'", "L2", "U", "D'", "F2", "R'"]
        cube.apply_sequence(moves)
        assert sum(cube.eo) % 2 == 0

    def test_legality_after_long_sequence(self):
        cube = CubieCube()
        sequence = [
            "R", "U", "R'", "U'", "R", "U", "R'", "U'",
            "F", "R", "U", "R'", "U'", "F'",
            "L", "D", "L'", "D'", "B2", "R2",
        ]
        cube.apply_sequence(sequence)
        assert cube.is_legal()


class TestKociembaRoundTrip:
    """Tests for to_kociemba_string / from_kociemba_string round trip."""

    def test_solved_round_trip(self):
        cube1 = CubieCube()
        s = cube1.to_kociemba_string()
        cube2 = CubieCube.from_kociemba_string(s)
        assert cube1 == cube2

    def test_scrambled_round_trip(self):
        cube1 = CubieCube()
        cube1.apply_sequence(["R", "U", "F'", "D2", "L", "B"])
        s = cube1.to_kociemba_string()
        cube2 = CubieCube.from_kociemba_string(s)
        assert cube1 == cube2

    def test_kociemba_string_length(self):
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F"])
        s = cube.to_kociemba_string()
        assert len(s) == 54

    def test_kociemba_string_valid_chars(self):
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F", "D'", "L2", "B"])
        s = cube.to_kociemba_string()
        valid = set("URFDLB")
        for ch in s:
            assert ch in valid


class TestCopy:
    """Tests for the copy method."""

    def test_copy_is_equal(self):
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F"])
        copy = cube.copy()
        assert cube == copy

    def test_copy_is_independent(self):
        cube = CubieCube()
        cube.apply_sequence(["R", "U"])
        copy = cube.copy()
        copy.apply_move("F")
        assert cube != copy


class TestApplySequence:
    """Tests for apply_sequence method."""

    def test_string_input(self):
        cube1 = CubieCube()
        cube1.apply_sequence("R U F")

        cube2 = CubieCube()
        cube2.apply_sequence(["R", "U", "F"])

        assert cube1 == cube2

    def test_empty_sequence(self):
        cube = CubieCube()
        cube.apply_sequence([])
        assert cube.is_solved()
