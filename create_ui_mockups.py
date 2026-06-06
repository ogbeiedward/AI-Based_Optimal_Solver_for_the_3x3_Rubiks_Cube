"""
Create UI mockup figures 7.1, 7.2, 7.3 with light backgrounds
Shows conceptual views of the web interface
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

FIG_DIR = "docs/figures"
os.makedirs(FIG_DIR, exist_ok=True)

# Light theme colors
BG = '#f0f2f5'
PANEL = '#ffffff'
TEXT = '#1a1a2e'
BORDER = '#d0d7e3'
ACCENT = '#2563eb'
GREEN = '#16a766'
ORANGE = '#b45309'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': PANEL,
    'text.color': TEXT,
    'savefig.facecolor': BG,
    'font.family': 'DejaVu Sans',
})

# ─────────────────────────────────────────────────────────────────────────────
# Figure 7.1: Full web interface with solved cube
# ─────────────────────────────────────────────────────────────────────────────
def fig_71_interface():
    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Header
    ax.text(0.3, 7.5, "Rubik's Cube AI Solver", fontsize=18, fontweight='bold',
            color=TEXT)
    ax.text(0.3, 7.15, "Interactive visualization with Three.js 3D rendering",
            fontsize=10, color='#666')

    # Left panel: 3D cube visualization area
    left_panel = FancyBboxPatch((0.2, 1.5), 8.5, 5.5,
                               boxstyle="round,pad=0.1",
                               facecolor=PANEL, edgecolor=BORDER, lw=2)
    ax.add_patch(left_panel)
    ax.text(4.5, 6.6, "3D Cube Visualization", ha='center', fontsize=11,
            fontweight='bold', color=TEXT)

    # Draw simple cube representation
    cube_x, cube_y = 4.5, 4.5
    cube_size = 1.2
    # Front face (white and colors)
    colors_face = [['W', 'W', 'W'], ['W', 'W', 'W'], ['W', 'W', 'W']]
    for i in range(3):
        for j in range(3):
            x = cube_x - 1 + j * 0.4
            y = cube_y - 1 + i * 0.4
            rect = Rectangle((x, y), 0.35, 0.35,
                            facecolor='#ffffff', edgecolor='#333', lw=1)
            ax.add_patch(rect)
            ax.text(x + 0.175, y + 0.175, 'W', ha='center', va='center',
                   fontsize=8, fontweight='bold')

    ax.text(cube_x, cube_y - 1.8, "Solved - Ready to scramble",
            ha='center', fontsize=9, color=GREEN, fontweight='bold')

    # Right panel: Controls sidebar
    right_panel = FancyBboxPatch((9.2, 1.5), 4.3, 5.5,
                                boxstyle="round,pad=0.1",
                                facecolor=PANEL, edgecolor=BORDER, lw=2)
    ax.add_patch(right_panel)
    ax.text(11.35, 6.6, "Controls", ha='center', fontsize=11,
            fontweight='bold', color=TEXT)

    # Control buttons
    btn_y = 6.0
    buttons = [
        ("Scramble (Depth 5)", ACCENT),
        ("Solve (Kociemba)", GREEN),
        ("Solve (AI Greedy)", '#7c3aed'),
        ("Solve (AI Beam)", '#2563eb'),
    ]

    for btn_text, btn_color in buttons:
        btn = FancyBboxPatch((9.5, btn_y - 0.35), 3.7, 0.45,
                            boxstyle="round,pad=0.05",
                            facecolor=btn_color, alpha=0.15,
                            edgecolor=btn_color, lw=1.5)
        ax.add_patch(btn)
        ax.text(11.35, btn_y - 0.125, btn_text, ha='center', va='center',
               fontsize=8.5, color=btn_color, fontweight='bold')
        btn_y -= 0.65

    # Status box
    status_box = FancyBboxPatch((9.5, 1.9), 3.7, 1.2,
                               boxstyle="round,pad=0.05",
                               facecolor='#f0f0f0', edgecolor=BORDER, lw=1)
    ax.add_patch(status_box)
    ax.text(11.35, 2.85, "Status", ha='center', fontsize=9,
           fontweight='bold', color=TEXT)
    ax.text(11.35, 2.5, "Solution: None", ha='center', fontsize=7.5,
           color='#666')
    ax.text(11.35, 2.15, "Moves: 0  |  Time: 0 ms", ha='center', fontsize=7.5,
           color='#666')

    ax.set_title("Fig. 7.1: Full Web Interface - Solved Cube State",
                fontsize=12, fontweight='bold', pad=20, color=TEXT)

    fig.savefig(os.path.join(FIG_DIR, "fig_7_1_interface.png"),
               dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("  OK  fig_7_1_interface.png")

# ─────────────────────────────────────────────────────────────────────────────
# Figure 7.2: Kociemba solve in progress
# ─────────────────────────────────────────────────────────────────────────────
def fig_72_kociemba_solving():
    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    ax.text(0.3, 7.5, "Rubik's Cube AI Solver", fontsize=18, fontweight='bold',
            color=TEXT)
    ax.text(0.3, 7.15, "Kociemba solver executing - bidirectional BFS",
            fontsize=10, color=ORANGE)

    # Left panel
    left_panel = FancyBboxPatch((0.2, 1.5), 8.5, 5.5,
                               boxstyle="round,pad=0.1",
                               facecolor=PANEL, edgecolor=BORDER, lw=2)
    ax.add_patch(left_panel)
    ax.text(4.5, 6.6, "3D Cube Visualization (Solving...)", ha='center',
            fontsize=11, fontweight='bold', color=TEXT)

    # Scrambled cube visualization
    cube_x, cube_y = 4.5, 4.5
    scrambled_colors = [['R', 'W', 'G'], ['Y', 'O', 'B'], ['W', 'Y', 'R']]
    color_map = {'W': '#ffffff', 'R': '#ef4444', 'G': '#22c55e',
                 'Y': '#eab308', 'O': '#f97316', 'B': '#3b82f6'}
    for i in range(3):
        for j in range(3):
            x = cube_x - 1 + j * 0.4
            y = cube_y - 1 + i * 0.4
            col = scrambled_colors[i][j]
            rect = Rectangle((x, y), 0.35, 0.35,
                            facecolor=color_map.get(col, '#ccc'),
                            edgecolor='#333', lw=1)
            ax.add_patch(rect)

    ax.text(cube_x, cube_y - 1.8, "Solving... (Step 15 of 20)",
            ha='center', fontsize=9, color=ORANGE, fontweight='bold')

    # Progress bar
    progress_x, progress_y = 2, 1.8
    progress_bg = Rectangle((progress_x, progress_y), 6, 0.3,
                           facecolor='#e5e7eb', edgecolor=BORDER)
    ax.add_patch(progress_bg)
    progress = Rectangle((progress_x, progress_y), 6 * 0.75, 0.3,
                        facecolor=ORANGE, alpha=0.7)
    ax.add_patch(progress)
    ax.text(progress_x + 3, progress_y - 0.4, "75% complete",
           ha='center', fontsize=8, color=ORANGE)

    # Right panel
    right_panel = FancyBboxPatch((9.2, 1.5), 4.3, 5.5,
                                boxstyle="round,pad=0.1",
                                facecolor=PANEL, edgecolor=BORDER, lw=2)
    ax.add_patch(right_panel)
    ax.text(11.35, 6.6, "Solution", ha='center', fontsize=11,
            fontweight='bold', color=TEXT)

    # Solution steps
    ax.text(9.5, 6.2, "Moves found:", fontsize=8, fontweight='bold',
           color=TEXT)
    moves_text = "U, R, U', R'\nD, B, D', B'\nU, U, R, U..."
    ax.text(9.5, 5.5, moves_text, fontsize=7, family='monospace',
           color='#666', verticalalignment='top')

    # Stats
    status_box = FancyBboxPatch((9.5, 1.9), 3.7, 1.2,
                               boxstyle="round,pad=0.05",
                               facecolor='#f0f0f0', edgecolor=BORDER, lw=1)
    ax.add_patch(status_box)
    ax.text(11.35, 2.85, "Status", ha='center', fontsize=9,
           fontweight='bold', color=TEXT)
    ax.text(11.35, 2.5, "Solver: Kociemba (BFS)", ha='center', fontsize=7.5,
           color='#666')
    ax.text(11.35, 2.15, "Time: 45 ms  |  States: 2840", ha='center',
           fontsize=7.5, color='#666')

    ax.set_title("Fig. 7.2: Kociemba Solve in Progress - Animated Sequence",
                fontsize=12, fontweight='bold', pad=20, color=TEXT)

    fig.savefig(os.path.join(FIG_DIR, "fig_7_2_kociemba_solve.png"),
               dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("  OK  fig_7_2_kociemba_solve.png")

# ─────────────────────────────────────────────────────────────────────────────
# Figure 7.3: AI Beam Search solve
# ─────────────────────────────────────────────────────────────────────────────
def fig_73_ai_beam():
    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    ax.text(0.3, 7.5, "Rubik's Cube AI Solver", fontsize=18, fontweight='bold',
            color=TEXT)
    ax.text(0.3, 7.15, "AI Beam Search (width=5) solver - neural network inference",
            fontsize=10, color=ACCENT)

    # Left panel
    left_panel = FancyBboxPatch((0.2, 1.5), 8.5, 5.5,
                               boxstyle="round,pad=0.1",
                               facecolor=PANEL, edgecolor=BORDER, lw=2)
    ax.add_patch(left_panel)
    ax.text(4.5, 6.6, "3D Cube Visualization (AI Solving)", ha='center',
            fontsize=11, fontweight='bold', color=TEXT)

    # Cube nearing solution
    cube_x, cube_y = 4.5, 4.5
    nearly_solved = [['W', 'W', 'R'], ['W', 'W', 'G'], ['Y', 'Y', 'B']]
    color_map = {'W': '#ffffff', 'R': '#ef4444', 'G': '#22c55e',
                 'Y': '#eab308', 'O': '#f97316', 'B': '#3b82f6'}
    for i in range(3):
        for j in range(3):
            x = cube_x - 1 + j * 0.4
            y = cube_y - 1 + i * 0.4
            col = nearly_solved[i][j]
            rect = Rectangle((x, y), 0.35, 0.35,
                            facecolor=color_map.get(col, '#ccc'),
                            edgecolor='#333', lw=1)
            ax.add_patch(rect)

    ax.text(cube_x, cube_y - 1.8, "Nearing solution (Step 8 of 12)",
            ha='center', fontsize=9, color=ACCENT, fontweight='bold')

    # Right panel
    right_panel = FancyBboxPatch((9.2, 1.5), 4.3, 5.5,
                                boxstyle="round,pad=0.1",
                                facecolor=PANEL, edgecolor=BORDER, lw=2)
    ax.add_patch(right_panel)
    ax.text(11.35, 6.6, "Solution", ha='center', fontsize=11,
            fontweight='bold', color=TEXT)

    # Solution steps
    ax.text(9.5, 6.2, "Moves found:", fontsize=8, fontweight='bold',
           color=TEXT)
    moves_text = "R, U', R, U\nR, U', R', U'\nF, R, U..."
    ax.text(9.5, 5.5, moves_text, fontsize=7, family='monospace',
           color='#666', verticalalignment='top')

    # Stats
    status_box = FancyBboxPatch((9.5, 1.9), 3.7, 1.2,
                               boxstyle="round,pad=0.05",
                               facecolor='#f0f0f0', edgecolor=BORDER, lw=1)
    ax.add_patch(status_box)
    ax.text(11.35, 2.85, "Status", ha='center', fontsize=9,
           fontweight='bold', color=TEXT)
    ax.text(11.35, 2.5, "Solver: AI Beam (width=5)", ha='center',
           fontsize=7.5, color='#666')
    ax.text(11.35, 2.15, "Time: 2.3 ms  |  Paths: 5 active", ha='center',
           fontsize=7.5, color='#666')

    ax.set_title("Fig. 7.3: AI Beam Search Solver - Neural Network Inference",
                fontsize=12, fontweight='bold', pad=20, color=TEXT)

    fig.savefig(os.path.join(FIG_DIR, "fig_7_3_ai_beam.png"),
               dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print("  OK  fig_7_3_ai_beam.png")

# Generate all figures
print("Creating UI mockup figures with light background...\n")
fig_71_interface()
fig_72_kociemba_solving()
fig_73_ai_beam()

print(f"\nAll UI mockups created in {FIG_DIR}/")
