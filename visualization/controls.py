"""
HUMAN-READABLE DESCRIPTION:
This file binds keyboard inputs to cube rotations for the local matplotlib Python visualizer, so you can manually play the cube using your keyboard.
"""

"""
controls.py
-----------
Interactive keyboard controls for the matplotlib-based Rubik's Cube viewer.

Key bindings:
    Face moves (lowercase = clockwise, SHIFT = counterclockwise, number = double):
        u / U / 1  →  U  / U' / U2
        d / D / 2  →  D  / D' / D2
        l / L / 3  →  L  / L' / L2
        r / R / 4  →  R  / R' / R2
        f / F / 5  →  F  / F' / F2
        b / B / 6  →  B  / B' / B2

    Special:
        x          →  Random scramble (20-25 moves)
        s          →  Reset to solved state
        k          →  Reverse to original state
        Arrow keys →  Rotate camera view

    The 'x' key is used for scramble instead of 'r' to avoid conflict
    with the R face move binding.
"""

import sys
import os

import matplotlib.pyplot as plt

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cube import CubieCube
from utils.scramble import generate_scramble, scramble_to_string
from visualization.renderer3d import draw_cube, create_info_text
from core.moves import get_inverse_move_name


# ---------------------------------------------------------------------------
# Key-to-move mapping
# ---------------------------------------------------------------------------

# Lowercase keys → clockwise moves
_CLOCKWISE_MAP = {
    'u': 'U',
    'd': 'D',
    'l': 'L',
    'r': 'R',
    'f': 'F',
    'b': 'B',
}

# Uppercase (shift) keys → counterclockwise (prime) moves
_PRIME_MAP = {
    'U': "U'",
    'D': "D'",
    'L': "L'",
    'R': "R'",
    'F': "F'",
    'B': "B'",
}

# Number keys → double moves
_DOUBLE_MAP = {
    '1': 'U2',
    '2': 'D2',
    '3': 'L2',
    '4': 'R2',
    '5': 'F2',
    '6': 'B2',
}

# Camera rotation step in degrees
_CAMERA_STEP = 10


# ---------------------------------------------------------------------------
# Interactive viewer class
# ---------------------------------------------------------------------------

class InteractiveViewer:
    """
    Manages the interactive matplotlib 3D Rubik's Cube viewer.

    Encapsulates the cube state, figure, axes, move history,
    and camera angles. Handles keyboard events and redraws.
    """

    def __init__(self):
        self.cube = CubieCube()
        self.move_history = []
        self.elev = 25.0
        self.azim = -50.0
        self.fig = None
        self.ax = None
        self._info_text = None
        self._controls_texts = []
        self._solve_texts = []
        self._solve_info = None  # dict from solver result

    def launch(self):
        """Create the matplotlib window and start the interactive loop."""
        self.fig = plt.figure(
            figsize=(16, 8),
            facecolor='#2b2b2b',
        )
        self.fig.canvas.manager.set_window_title(
            "Rubik's Cube 3D Simulator - M.Sc. AI Thesis, Edward Ogbei"
        )

        # Leave left margin for controls, right margin for solve info
        self.ax = self.fig.add_axes([0.20, 0.05, 0.55, 0.90], projection='3d')
        self.ax.set_facecolor('#2b2b2b')

        # Draw on-screen controls legend
        self._draw_controls_panel()

        # Connect keyboard handler
        self.fig.canvas.mpl_connect('key_press_event', self._on_key)

        # Initial draw
        self._redraw()

        # Show controls help in terminal too
        self._print_controls()

        plt.show()

    def _redraw(self):
        """Redraw the cube and update status text."""
        draw_cube(self.ax, self.cube)
        self.ax.view_init(elev=self.elev, azim=self.azim)

        # Update info text
        if self._info_text is not None:
            self._info_text.remove()

        info = create_info_text(self.cube, self.ax, self.move_history)
        self._info_text = self.fig.text(
            0.5, 0.02, info,
            ha='center', va='bottom',
            fontsize=10,
            fontfamily='monospace',
            color='#cccccc',
            backgroundcolor='#1a1a1a',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a1a', alpha=0.8),
        )

        # Draw/update solve info panel on the right
        self._draw_solve_panel()

        self.fig.canvas.draw_idle()

    def _apply_move(self, move_name):
        """Apply a move to the cube and redraw."""
        self.cube.apply_move(move_name)
        self.move_history.append(move_name)
        self._redraw()

    def _scramble(self):
        """Apply a random scramble."""
        scramble = generate_scramble()
        self.cube = CubieCube()
        self.cube.apply_sequence(scramble)
        self.move_history = list(scramble)
        print(f"\n  Scramble: {scramble_to_string(scramble)}")
        self._redraw()

    def _reset(self):
        """Reset to solved state."""
        self.cube = CubieCube()
        self.move_history = []
        self._solve_info = None
        print("\n  Cube reset to solved state.")
        self._redraw()

    def _reverse(self):
        """Reverse the cube to the original state."""
        if self.cube.is_solved():
            print("\n  Cube is already solved!")
            self._solve_info = {'status': 'Already solved', 'num_moves': 0, 'solve_time': 0.0, 'solution': ''}
            self._redraw()
            return

        print("\n  Reversing...")
        solution_moves = []
        for move in reversed(self.move_history):
            solution_moves.append(get_inverse_move_name(move))

        self._solve_info = {
            'status': 'Reversed ✓',
            'num_moves': len(solution_moves),
            'solve_time': 0.0,
            'solution': ' '.join(solution_moves),
        }
        print(f"  Reversed {len(solution_moves)} moves")
        print(f"    {' '.join(solution_moves)}")

        # Apply sequence to the cube
        self.cube.apply_sequence(solution_moves)
        self.move_history.extend(solution_moves)
        self._redraw()

    def _on_key(self, event):
        """Handle keyboard events."""
        key = event.key

        if key is None:
            return

        # Face moves — clockwise (lowercase)
        if key in _CLOCKWISE_MAP:
            move = _CLOCKWISE_MAP[key]
            print(f"  Move: {move}")
            self._apply_move(move)
            return

        # Face moves — counterclockwise (shift + key, shows as uppercase)
        if key in _PRIME_MAP:
            move = _PRIME_MAP[key]
            print(f"  Move: {move}")
            self._apply_move(move)
            return

        # Face moves — double (number keys)
        if key in _DOUBLE_MAP:
            move = _DOUBLE_MAP[key]
            print(f"  Move: {move}")
            self._apply_move(move)
            return

        # Special commands
        if key == 'x':
            self._scramble()
            return

        if key == 's':
            self._reset()
            return

        if key == 'k':
            self._reverse()
            return

        # Camera rotation — arrow keys
        if key == 'left':
            self.azim -= _CAMERA_STEP
            self._redraw()
            return

        if key == 'right':
            self.azim += _CAMERA_STEP
            self._redraw()
            return

        if key == 'up':
            self.elev = min(self.elev + _CAMERA_STEP, 90)
            self._redraw()
            return

        if key == 'down':
            self.elev = max(self.elev - _CAMERA_STEP, -90)
            self._redraw()
            return

    def _draw_controls_panel(self):
        """Draw on-screen controls legend on the left side of the figure."""
        # Remove any previous controls texts
        for t in self._controls_texts:
            try:
                t.remove()
            except Exception:
                pass
        self._controls_texts = []

        # Panel background
        import matplotlib.patches as mpatches
        bg = mpatches.FancyBboxPatch(
            (0.005, 0.05), 0.175, 0.90,
            boxstyle='round,pad=0.01',
            facecolor='#1e1e1e', edgecolor='#444444', linewidth=1,
            transform=self.fig.transFigure, zorder=5,
        )
        self.fig.patches = [p for p in self.fig.patches
                           if not isinstance(p, mpatches.FancyBboxPatch)]
        self.fig.patches.append(bg)

        # Title
        x0 = 0.015
        lines = [
            (0.92, '⌨  KEYBOARD CONTROLS', 10, 'bold', '#ffffff'),
            (0.87, '─' * 26, 8, 'normal', '#555555'),
            (0.83, 'FACE MOVES', 9, 'bold', '#88ccff'),
            (0.79, 'u d l r f b    →  CW', 8, 'normal', '#cccccc'),
            (0.75, 'U D L R F B    →  CCW', 8, 'normal', '#cccccc'),
            (0.71, '1 2 3 4 5 6    →  ×2', 8, 'normal', '#cccccc'),
            (0.66, '─' * 26, 8, 'normal', '#555555'),
            (0.62, 'MOVE LEGEND', 9, 'bold', '#88ccff'),
            (0.58, '1→U2 2→D2 3→L2', 8, 'normal', '#aaaaaa'),
            (0.54, '4→R2 5→F2 6→B2', 8, 'normal', '#aaaaaa'),
            (0.49, '─' * 26, 8, 'normal', '#555555'),
            (0.45, 'SPECIAL', 9, 'bold', '#ffcc44'),
            (0.41, 'x           →  Scramble', 8, 'normal', '#cccccc'),
            (0.37, 's           →  Reset', 8, 'normal', '#cccccc'),
            (0.33, 'k           →  Reverse', 8, 'normal', '#80ff90'),
            (0.28, '─' * 26, 8, 'normal', '#555555'),
            (0.24, 'CAMERA', 9, 'bold', '#88ffaa'),
            (0.20, '← → ↑ ↓    →  Rotate', 8, 'normal', '#cccccc'),
            (0.16, '─' * 26, 8, 'normal', '#555555'),
            (0.13, 'CO: Corner Orientation', 7.5, 'normal', '#aaccff'),
            (0.11, '    (Must sum to 0 mod 3)', 7.5, 'normal', '#888888'),
            (0.08, 'EO: Edge Orientation', 7.5, 'normal', '#aaccff'),
            (0.06, '    (Must sum to 0 mod 2)', 7.5, 'normal', '#888888'),
            (0.03, 'M.Sc. Thesis - E. Ogbei', 7.5, 'normal', '#555555'),
        ]

        for y_pos, text, fontsize, weight, color in lines:
            t = self.fig.text(
                x0, y_pos, text,
                fontsize=fontsize,
                fontweight=weight,
                fontfamily='monospace',
                color=color,
                transform=self.fig.transFigure,
                zorder=10,
            )
            self._controls_texts.append(t)

    def _draw_solve_panel(self):
        """Draw solve info panel on the right side of the figure."""
        import matplotlib.patches as mpatches

        # Remove previous solve texts
        for t in self._solve_texts:
            try:
                t.remove()
            except Exception:
                pass
        self._solve_texts = []

        # Right panel background
        # Check if we already have a right panel patch, remove it
        self.fig.patches = [p for p in self.fig.patches
                           if not (isinstance(p, mpatches.FancyBboxPatch)
                                   and hasattr(p, '_is_solve_panel'))]

        bg = mpatches.FancyBboxPatch(
            (0.78, 0.05), 0.21, 0.90,
            boxstyle='round,pad=0.01',
            facecolor='#1e1e1e', edgecolor='#444444', linewidth=1,
            transform=self.fig.transFigure, zorder=5,
        )
        bg._is_solve_panel = True
        self.fig.patches.append(bg)

        x0 = 0.79

        # Header
        t = self.fig.text(x0, 0.92, '🧩  REVERSE INFO', fontsize=10,
                          fontweight='bold', fontfamily='monospace',
                          color='#ffffff', transform=self.fig.transFigure, zorder=10)
        self._solve_texts.append(t)

        t = self.fig.text(x0, 0.87, '─' * 26, fontsize=8,
                          fontfamily='monospace', color='#555555',
                          transform=self.fig.transFigure, zorder=10)
        self._solve_texts.append(t)

        if self._solve_info is None:
            # No solve performed yet
            t = self.fig.text(x0, 0.82, 'STATUS', fontsize=9,
                              fontweight='bold', fontfamily='monospace',
                              color='#88ccff', transform=self.fig.transFigure, zorder=10)
            self._solve_texts.append(t)
            t = self.fig.text(x0, 0.78, 'Press K to reverse', fontsize=8,
                              fontfamily='monospace', color='#888888',
                              transform=self.fig.transFigure, zorder=10)
            self._solve_texts.append(t)

            # Show cube state info
            t = self.fig.text(x0, 0.72, '─' * 26, fontsize=8,
                              fontfamily='monospace', color='#555555',
                              transform=self.fig.transFigure, zorder=10)
            self._solve_texts.append(t)
            t = self.fig.text(x0, 0.68, 'CUBE STATE', fontsize=9,
                              fontweight='bold', fontfamily='monospace',
                              color='#88ccff', transform=self.fig.transFigure, zorder=10)
            self._solve_texts.append(t)
            state_str = 'Solved ✓' if self.cube.is_solved() else f'{len(self.move_history)} moves applied'
            state_color = '#80ff90' if self.cube.is_solved() else '#ffcc44'
            t = self.fig.text(x0, 0.64, state_str, fontsize=8,
                              fontfamily='monospace', color=state_color,
                              transform=self.fig.transFigure, zorder=10)
            self._solve_texts.append(t)
        else:
            info = self._solve_info
            lines = [
                (0.82, 'STATUS', 9, 'bold', '#88ccff'),
                (0.78, info['status'], 9, 'bold',
                 '#80ff90' if 'Reversed' in info['status'] else '#ff6666'),
                (0.73, '─' * 26, 8, 'normal', '#555555'),
                (0.69, 'MOVES USED', 9, 'bold', '#ffcc44'),
                (0.65, str(info['num_moves']), 22, 'bold', '#ffffff'),
                (0.60, '─' * 26, 8, 'normal', '#555555'),
                (0.56, 'REVERSE TIME', 9, 'bold', '#88ffaa'),
                (0.52, f"{info['solve_time']:.4f}s", 14, 'bold', '#ffffff'),
            ]

            for y_pos, text, fontsize, weight, color in lines:
                t = self.fig.text(x0, y_pos, text, fontsize=fontsize,
                                  fontweight=weight, fontfamily='monospace',
                                  color=color, transform=self.fig.transFigure,
                                  zorder=10)
                self._solve_texts.append(t)

            # Solution string (wrapped)
            if info.get('solution'):
                t = self.fig.text(x0, 0.47, '─' * 26, fontsize=8,
                                  fontfamily='monospace', color='#555555',
                                  transform=self.fig.transFigure, zorder=10)
                self._solve_texts.append(t)
                t = self.fig.text(x0, 0.43, 'SOLUTION', fontsize=9,
                                  fontweight='bold', fontfamily='monospace',
                                  color='#88ccff', transform=self.fig.transFigure,
                                  zorder=10)
                self._solve_texts.append(t)

                # Split solution into lines of ~20 chars
                sol = info['solution']
                sol_lines = []
                words = sol.split()
                current = ''
                for w in words:
                    if len(current) + len(w) + 1 > 22:
                        sol_lines.append(current)
                        current = w
                    else:
                        current = (current + ' ' + w).strip()
                if current:
                    sol_lines.append(current)

                y = 0.39
                for sl in sol_lines[:6]:  # max 6 lines
                    t = self.fig.text(x0, y, sl, fontsize=7.5,
                                      fontfamily='monospace', color='#cccccc',
                                      transform=self.fig.transFigure, zorder=10)
                    self._solve_texts.append(t)
                    y -= 0.035
                if len(sol_lines) > 6:
                    t = self.fig.text(x0, y, '...', fontsize=7.5,
                                      fontfamily='monospace', color='#888888',
                                      transform=self.fig.transFigure, zorder=10)
                    self._solve_texts.append(t)

    @staticmethod
    def _print_controls():
        """Print control instructions to the terminal."""
        print("\n" + "=" * 60)
        print("  RUBIK'S CUBE 3D SIMULATOR — Interactive Controls")
        print("=" * 60)
        print()
        print("  Face Moves:")
        print("    u/d/l/r/f/b        → Clockwise  (U, D, L, R, F, B)")
        print("    Shift + u/d/l/r/f/b → Counter-CW (U', D', L', R', F', B')")
        print("    1/2/3/4/5/6        → Double     (U2, D2, L2, R2, F2, B2)")
        print()
        print("  Special:")
        print("    x                  → Random scramble")
        print("    s                  → Reset to solved")
        print("    k                  → Reverse to original state")
        print()
        print("  Camera:")
        print("    ← → ↑ ↓           → Rotate view")
        print()
        print("=" * 60)
        print()
