"""
HUMAN-READABLE DESCRIPTION:
This suite of tests verifies that the Kociemba wrapper correctly interacts with the external solver library and successfully returns valid solutions.
"""

"""
test_kociemba.py
----------------
Unit tests for the IDA* solver (pure Python Kociemba replacement).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.cube import CubieCube
from utils.scramble import generate_scramble
from solvers.kociemba_solver import solve_with_kociemba


class TestSolver:
    """Tests for the IDA* solver."""

    def test_solve_single_scramble(self):
        """Solve a short scramble and check the result."""
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F"])

        result = solve_with_kociemba(cube, max_depth=10)

        assert result["error"] is None
        assert result["validated"]
        assert result["num_moves"] <= 10
        assert result["solve_time"] > 0

    def test_solve_already_solved(self):
        """An already-solved cube should return an empty solution."""
        cube = CubieCube()
        result = solve_with_kociemba(cube)

        assert result["error"] is None
        assert result["num_moves"] == 0
        assert result["validated"]

    def test_solve_depth_1(self):
        """One-move scrambles should be solved in a small number of moves."""
        for move in ["U", "R", "F", "D", "L", "B"]:
            cube = CubieCube()
            cube.apply_move(move)
            result = solve_with_kociemba(cube, max_depth=5)
            assert result["error"] is None
            assert result["num_moves"] <= 3  # Two-phase may not be optimal
            assert result["validated"]

    def test_solve_depth_2(self):
        """Two-move scrambles should be solved in a small number of moves."""
        cube = CubieCube()
        cube.apply_sequence(["R", "U"])
        result = solve_with_kociemba(cube, max_depth=5)
        assert result["error"] is None
        assert result["num_moves"] <= 4  # Two-phase may not be optimal
        assert result["validated"]

    def test_solve_depth_3(self):
        """Three-move scrambles."""
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F"])
        result = solve_with_kociemba(cube, max_depth=8)
        assert result["error"] is None
        assert result["num_moves"] <= 6  # Two-phase may not be optimal
        assert result["validated"]

    def test_solution_restores_solved_state(self):
        """Verify that applying the solution restores the solved state."""
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F'", "D2"])
        result = solve_with_kociemba(cube, max_depth=10)

        assert result["error"] is None

        solution_moves = result["solution"].split()
        cube.apply_sequence(solution_moves)
        assert cube.is_solved()

    def test_illegal_cube_returns_error(self):
        """An illegal cube state should return an error."""
        cube = CubieCube()
        cube.co[0] = 1  # Break corner orientation invariant
        result = solve_with_kociemba(cube)
        assert result["error"] is not None

    def test_centers_fixed_in_facelet_string(self):
        """Centers must be at canonical positions after scrambling."""
        cube = CubieCube()
        cube.apply_sequence(["R", "U", "F"])
        s = cube.to_kociemba_string()
        assert s[4] == 'U'
        assert s[13] == 'R'
        assert s[22] == 'F'
        assert s[31] == 'D'
        assert s[40] == 'L'
        assert s[49] == 'B'
