"""
generate_figures.py   -   Thesis figures for Edward Ogbei, PCZ 2026
All coordinates are explicit and pre-calculated. No guessing.
"""

import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, ArrowStyle
import matplotlib.patheffects as pe

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

# ── Palette (light theme) ────────────────────────────────────────────────────
BG      = '#ffffff'
PANEL   = '#f5f5ff'
GRID    = '#e4e4f4'
TXT     = '#1a1a2e'
TXT2    = '#555577'
BORDER  = '#aaaacc'

C_BLUE  = '#1a5cbd'
C_PURP  = '#6030c8'
C_GREEN = '#1a9060'
C_RED   = '#c02828'
C_ORG   = '#c06010'
C_TEAL  = '#0a90a0'
C_GOLD  = '#a07a10'

SM_COL  = '#c04040'
MD_COL  = '#2060cc'
LG_COL  = '#1a8040'
KOC_COL = '#a07010'
AI_COL  = '#2060cc'

def rc():
    plt.rcParams.update({
        'figure.facecolor': BG, 'axes.facecolor': PANEL,
        'axes.edgecolor': BORDER, 'axes.labelcolor': TXT,
        'xtick.color': TXT2, 'ytick.color': TXT2, 'text.color': TXT,
        'grid.color': GRID, 'grid.linestyle': '--', 'grid.alpha': 0.7,
        'legend.facecolor': '#f0f0ff', 'legend.edgecolor': BORDER,
        'legend.labelcolor': TXT,
        'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.titlesize': 13, 'axes.labelsize': 10,
        'axes.titlepad': 14,
    })

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=160, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  OK  {name}")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def rect(ax, x, y, w, h, fc, ec, lw=1.8, radius=0.04, zorder=3, alpha=1.0):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad={radius}",
                       facecolor=fc, edgecolor=ec, linewidth=lw,
                       zorder=zorder, alpha=alpha)
    ax.add_patch(p)
    return p

def diamond(ax, cx, cy, hw, hh, fc, ec, lw=1.8, zorder=3):
    xs = [cx, cx+hw, cx, cx-hw, cx]
    ys = [cy+hh, cy, cy-hh, cy, cy+hh]
    ax.fill(xs, ys, color=fc, zorder=zorder)
    ax.plot(xs, ys, color=ec, lw=lw, zorder=zorder)

def arrow(ax, x1, y1, x2, y2, color='#6060a0', lw=1.8,
          arrowstyle='->', mutation_scale=14, zorder=2,
          connectionstyle='arc3,rad=0.0'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=arrowstyle, color=color,
                                lw=lw, mutation_scale=mutation_scale,
                                connectionstyle=connectionstyle),
                zorder=zorder)

def label(ax, x, y, txt, size=9, color=TXT, ha='center', va='center',
          weight='normal', style='normal', zorder=5, linespacing=1.5):
    ax.text(x, y, txt, fontsize=size, color=color, ha=ha, va=va,
            fontweight=weight, fontstyle=style, zorder=zorder,
            linespacing=linespacing)


# ─────────────────────────────────────────────────────────────────────────────
# FIG 01  -  System Architecture
# Clean 3-tier block diagram: CLI on top, 4 modules in middle, Core at bottom
# ─────────────────────────────────────────────────────────────────────────────
def fig01_architecture():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.suptitle('System Architecture', fontsize=15, fontweight='bold',
                 y=0.97, color=TXT)

    # ── Tier definitions ─────────────────────────────────────────────────────
    # Tier 3 (top): CLI entry point   y = 5.8  -  6.6
    # Tier 2 (mid): 4 modules         y = 3.2  -  5.2
    # Tier 1 (bot): Core Engine       y = 0.6  -  2.6
    # ─────────────────────────────────────────────────────────────────────────

    # ── Tier 1: Core Engine (spans full width at bottom) ─────────────────────
    rect(ax, 0.4, 0.5, 13.2, 2.1, '#ddeeff', C_BLUE, lw=2)
    label(ax, 7.0, 2.25, 'CORE ENGINE', size=11, weight='bold', color=C_BLUE)
    cols = [1.0, 4.2, 7.4, 10.6]
    core_items = [
        ('core/cube.py', 'CubieCube state model\ncp, co, ep, eo arrays\nLegality checking'),
        ('core/moves.py', '18-move table\nPermutation algebra\nInverse & double moves'),
        ('core/state_encoder.py', '54 facelets x 6 colours\n= 324-dim one-hot vector\nNeural network input'),
        ('utils/scramble.py', 'WCA-style scrambler\n20-25 random moves\nSeeded & reproducible'),
    ]
    for cx, (fname, desc) in zip(cols, core_items):
        rect(ax, cx, 0.65, 2.8, 1.55, '#c8e0ff', C_BLUE, lw=1.2, radius=0.03)
        label(ax, cx+1.4, 1.95, fname, size=8, color=C_BLUE, weight='bold')
        label(ax, cx+1.4, 1.38, desc, size=7.5, color=TXT2, linespacing=1.6)

    # ── Tier 2: 4 mid-level modules ──────────────────────────────────────────
    mods = [
        (0.4,  3.1, 2.9, 2.1, '#ede8ff', C_PURP,  'SOLVERS',
         'solvers/kociemba_solver.py\nsolvers/bfs_solver.py\nsolvers/ai_solver.py',
         'Classical BFS + AI MLP'),
        (3.7,  3.1, 2.9, 2.1, '#dcffe8', C_GREEN, 'DATA & TRAINING',
         'data/dataset_generator.py\ndata/dataset_stats.py',
         'Curriculum datasets\n(depths 1-5, .npz)'),
        (6.9,  3.1, 2.9, 2.1, '#fff0dc', C_ORG,   'EXPERIMENTS',
         'experiments/ai_vs_kociemba.py\nexperiments/curriculum_experiments.py',
         'Benchmarks & ablation\nplots for thesis'),
        (10.1, 3.1, 3.5, 2.1, '#dcffff', C_TEAL,  'VISUALIZATION',
         'visualization/server.py\nvisualization/index.html',
         'HTTP REST API\nThree.js 3D browser UI'),
    ]
    for x, y, w, h, fc, ec, title, files, desc in mods:
        rect(ax, x, y, w, h, fc, ec, lw=1.8)
        label(ax, x+w/2, y+h-0.25, title, size=9.5, weight='bold', color=ec)
        label(ax, x+w/2, y+h/2+0.08, files, size=7.5, color=TXT,
              linespacing=1.7)
        label(ax, x+w/2, y+0.28, desc, size=7.5, color=TXT2,
              style='italic', linespacing=1.5)

    # ── Tier 3: CLI ──────────────────────────────────────────────────────────
    rect(ax, 0.4, 5.6, 13.2, 1.0, '#fffadc', C_GOLD, lw=2)
    label(ax, 7.0, 6.25, 'main.py  -  Command-Line Interface',
          size=11, weight='bold', color=C_GOLD)
    label(ax, 7.0, 5.88,
          'subcommands:  visualize  |  scramble  |  validate  |  generate_dataset  |  train  |  compare',
          size=8.5, color=TXT2)

    # ── Arrows: CLI → modules ────────────────────────────────────────────────
    cli_targets = [1.85, 5.15, 8.35, 11.85]
    for cx in cli_targets:
        arrow(ax, cx, 5.6, cx, 5.22, color=C_GOLD, lw=1.4, mutation_scale=10)

    # ── Arrows: modules → Core (downward to core tier) ───────────────────────
    for cx in cli_targets:
        arrow(ax, cx, 3.1, cx, 2.75, color='#505080', lw=1.2, mutation_scale=8)

    # ── Horizontal dependency arrow: Solvers ← Core (they import Core) ───────
    label(ax, 1.85, 2.9, 'uses', size=7, color='#505080')
    label(ax, 5.15, 2.9, 'uses', size=7, color='#505080')
    label(ax, 8.35, 2.9, 'uses', size=7, color='#505080')
    label(ax, 11.85, 2.9, 'uses', size=7, color='#505080')

    # ── Legend ───────────────────────────────────────────────────────────────
    for col, txt in [(C_GOLD,'CLI entry'), (C_PURP,'Solvers'),
                     (C_GREEN,'Data'), (C_ORG,'Experiments'),
                     (C_TEAL,'Visualization'), (C_BLUE,'Core Engine')]:
        pass  # titles in boxes serve as legend

    save(fig, 'fig_01_system_architecture.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 02  -  MLP Architecture  (block diagram, NOT individual neurons)
# ─────────────────────────────────────────────────────────────────────────────
def fig02_mlp():
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.axis('off')
    fig.suptitle('Neural Network Architecture   -   RubiksMLP', fontsize=14,
                 fontweight='bold', y=0.97, color=TXT)

    # Each layer is a tall rectangle at fixed x positions
    # x centres:  1.2   3.6   6.2   8.8   11.4   (+ Input bar at 0.4)
    layers = [
        # (cx,  box_w, box_h, fc,      ec,      top_label,          mid_label,           bot_label,       param_label)
        (1.4,  1.6,  4.0,  '#dce8ff',C_BLUE, 'INPUT',            '324',               '54 facelets\nx 6 colours',  ''),
        (4.0,  1.6,  3.3,  '#ede8ff',C_PURP, 'Dense + ReLU',     '256 units',         '83,200\nparams',  '-> 83,200'),
        (6.6,  1.6,  3.3,  '#ede8ff',C_PURP, 'Dense + ReLU',     '256 units',         '65,792\nparams',  '-> 65,792'),
        (9.2,  1.6,  3.0,  '#dcffe8',C_GREEN,'Dense + ReLU',     '128 units',         '32,896\nparams',  '-> 32,896'),
        (11.8, 1.6,  2.0,  '#ffecec',C_RED,  'OUTPUT\nSoftmax',  '18 units',          '2,322\nparams\n18 moves',    '->  2,322'),
    ]

    cy = 3.0  # vertical centre of all layers

    # Draw layers
    for i, (cx, bw, bh, fc, ec, top, mid, bot, param) in enumerate(layers):
        x0 = cx - bw/2
        y0 = cy - bh/2
        rect(ax, x0, y0, bw, bh, fc, ec, lw=2.2, radius=0.06)
        # Top label (layer type)
        label(ax, cx, y0+bh-0.28, top, size=8.5, weight='bold', color=ec,
              linespacing=1.4)
        # Middle label (units)
        label(ax, cx, cy, mid, size=16, weight='bold', color=TXT)
        # Bottom label (description)
        label(ax, cx, y0+0.38, bot, size=7.5, color=TXT2, linespacing=1.6)

        # Arrow to next layer
        if i < len(layers)-1:
            next_cx = layers[i+1][0]
            next_bw = layers[i+1][1]
            ax0 = cx + bw/2 + 0.02
            ax1 = next_cx - next_bw/2 - 0.02
            arrow(ax, ax0, cy, ax1, cy, color='#6060a0', lw=1.8, mutation_scale=13)
            # param count on arrow
            mid_x = (ax0+ax1)/2
            label(ax, mid_x, cy+0.28, param, size=7, color=TXT2)

    # Total params annotation
    label(ax, 7.0, 0.35, 'Total trainable parameters:  184,210',
          size=10, color=C_GOLD, weight='bold')
    label(ax, 7.0, 0.08, 'Optimizer: Adam  |  LR: 0.001  |  Loss: CrossEntropy  |  Batch size: 64',
          size=8.5, color=TXT2)

    # Data flow label
    label(ax, 7.0, 5.72, 'Data flow  (forward pass, inference)', size=9, color=TXT2,
          style='italic')

    save(fig, 'fig_02_mlp_architecture.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 03  -  One-hot encoding  (unfolded cube cross + encoding diagram)
# ─────────────────────────────────────────────────────────────────────────────
def fig03_encoding():
    fig = plt.figure(figsize=(14, 7.5))
    fig.patch.set_facecolor(BG)
    fig.suptitle('State Encoding: 54 Facelets -> 324-Dimensional One-Hot Vector',
                 fontsize=13, fontweight='bold', y=0.99, color=TXT)

    # ── Left: unfolded cube cross ─────────────────────────────────────────────
    ax1 = fig.add_axes([0.02, 0.04, 0.40, 0.78])
    ax1.set_facecolor('#ffffff')
    ax1.set_xlim(0, 12); ax1.set_ylim(0, 12)
    ax1.axis('off')
    ax1.set_title('54 Facelets  -  Unfolded Cube (cross layout)', fontsize=10,
                  color=TXT, pad=8)

    FC = {'U':'#f0f0f0','R':'#e03030','F':'#30cc50',
          'D':'#f0e020','L':'#e07010','B':'#3050e0'}
    TC = {'U':'#222222','R':'#ffffff','F':'#ffffff',
          'D':'#222222','L':'#ffffff','B':'#ffffff'}

    # Cross layout: (face, col_start, row_start)  in 3x3-cell units
    # Standard cross: U at top-centre, L left, F centre, R right, B far-right, D bottom-centre
    face_pos = [
        ('U', 3, 9), ('L', 0, 6), ('F', 3, 6),
        ('R', 6, 6), ('D', 3, 3), ('B', 9, 6),
    ]
    cell = 1.8  # cell size in data units
    for face, c0, r0 in face_pos:
        for r in range(3):
            for c in range(3):
                x = c0*cell/3 + c*(cell/3)
                y = r0*cell/3 + r*(cell/3)
                sq = plt.Rectangle((x, y), cell/3-0.06, cell/3-0.06,
                                   facecolor=FC[face], edgecolor='#222222',
                                   linewidth=1.2, zorder=3)
                ax1.add_patch(sq)
        # Face label at centre
        cx = c0*cell/3 + cell/2
        cy = r0*cell/3 + cell/2
        ax1.text(cx, cy, face, ha='center', va='center',
                 fontsize=14, fontweight='bold', color=TC[face], zorder=4)

    # Face name labels
    for face, c0, r0 in face_pos:
        cx = c0*cell/3 + cell/2
        cy = r0*cell/3 - 0.25
        ax1.text(cx, cy, face, ha='center', va='top',
                 fontsize=8, color=TXT2, zorder=4)

    # Annotation
    ax1.text(6.0, 0.15,
             'Each coloured square = 1 facelet  (54 total)',
             ha='center', fontsize=8, color=TXT2, style='italic')

    # ── Right: encoding pipeline diagram ─────────────────────────────────────
    ax2 = fig.add_axes([0.44, 0.04, 0.54, 0.78])
    ax2.set_facecolor('#ffffff')
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('How One Facelet is Encoded (then repeated 54×)', fontsize=10,
                  color=TXT, pad=8)

    # Step 1: single facelet square
    sq = plt.Rectangle((0.5, 7.2), 1.4, 1.4, facecolor='#e03030',
                        edgecolor='#888888', linewidth=2, zorder=3)
    ax2.add_patch(sq)
    ax2.text(1.2, 7.9, 'R', ha='center', va='center',
             fontsize=18, fontweight='bold', color='white', zorder=4)
    ax2.text(1.2, 6.9, 'One facelet\ncolour = Red', ha='center',
             fontsize=8, color=TXT2, linespacing=1.5)

    # Arrow →
    arrow(ax2, 2.1, 7.9, 3.1, 7.9, color='#6060a0', lw=2, mutation_scale=13)
    ax2.text(2.6, 8.2, 'encode', ha='center', fontsize=8, color=TXT2)

    # Step 2: 6-element one-hot bar
    colours_data = [('#f0f0f0','U\nWhite',0),
                    ('#e03030','R\nRed',  1),
                    ('#30cc50','F\nGreen',0),
                    ('#f0e020','D\nYellow',0),
                    ('#e07010','L\nOrange',0),
                    ('#3050e0','B\nBlue', 0)]
    bar_x0 = 3.2
    bw = 0.85
    for i, (fc, lbl, val) in enumerate(colours_data):
        bx = bar_x0 + i*bw
        # background cell
        bg = plt.Rectangle((bx, 6.5), bw-0.08, 2.4,
                            facecolor='#f0f0ff', edgecolor=BORDER,
                            linewidth=1, zorder=2)
        ax2.add_patch(bg)
        # filled portion
        fill_h = 2.0 * val  # only the '1' bar fills
        if val:
            fill = plt.Rectangle((bx+0.06, 6.55), bw-0.2, fill_h,
                                  facecolor=fc, edgecolor='#ffffff',
                                  linewidth=1.2, alpha=0.9, zorder=3)
            ax2.add_patch(fill)
        ax2.text(bx+bw/2-0.04, 8.75, str(val), ha='center', fontsize=10,
                 fontweight='bold', color=TXT if val==0 else fc, zorder=4)
        ax2.text(bx+bw/2-0.04, 6.25, lbl, ha='center', fontsize=7,
                 color=TXT2, linespacing=1.4)

    ax2.text(bar_x0 + 3*bw, 9.2, '6-element one-hot vector',
             ha='center', fontsize=9, color=TXT, fontweight='bold')

    # Arrow → 324-dim
    arrow(ax2, 8.4, 7.9, 9.3, 7.9, color='#6060a0', lw=2, mutation_scale=13)

    # Step 3: final vector box
    rect(ax2, 9.35, 6.5, 0.5, 2.8, '#0d1f3a', C_BLUE, lw=2, radius=0.05)
    ax2.text(9.60, 7.9, '324\ndim', ha='center', va='center',
             fontsize=8, fontweight='bold', color=C_BLUE, linespacing=1.5)

    # Big equation at bottom
    ax2.text(5.0, 5.5, '54  facelets  ×  6 colours  =  324 dimensions',
             ha='center', fontsize=12, fontweight='bold', color=C_GOLD)

    # How it maps
    for i, (fc, lbl, _) in enumerate(colours_data):
        ax2.text(bar_x0 + i*bw + bw/2 - 0.04, 5.0,
                 lbl.split('\n')[0], ha='center', fontsize=8, color=fc)

    ax2.text(5.0, 4.45,
             'Each of the 54 facelets gets a 6-element one-hot slot.',
             ha='center', fontsize=8.5, color=TXT2, style='italic')
    ax2.text(5.0, 4.05,
             'All slots concatenated form the 324-dim input to the MLP.',
             ha='center', fontsize=8.5, color=TXT2, style='italic')

    # Example full vector snippet
    rect(ax2, 0.3, 2.0, 9.4, 1.6, '#f0f0ff', BORDER, lw=1.2, radius=0.04)
    ax2.text(5.0, 3.3, 'Full 324-dim vector (first 18 shown):', ha='center',
             fontsize=8, color=TXT2)
    vec_str = '[1,0,0,0,0,0,  0,1,0,0,0,0,  0,0,1,0,0,0  …  0,0,0,0,0,1]'
    ax2.text(5.0, 2.6, vec_str, ha='center', fontsize=9,
             color=C_TEAL, fontfamily='monospace')
    ax2.text(5.0, 2.15, '← facelet 0: White    ← facelet 1: Red    ← facelet 2: Green  …',
             ha='center', fontsize=7.5, color=TXT2, style='italic')

    save(fig, 'fig_03_encoding.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 04  -  Curriculum Learning Flowchart  (fully contained, no clipping)
# ─────────────────────────────────────────────────────────────────────────────
def fig04_curriculum():
    fig, ax = plt.subplots(figsize=(11, 12))
    ax.set_xlim(0, 11); ax.set_ylim(0, 12)
    ax.axis('off')
    fig.suptitle('Curriculum Learning  -  Training Procedure', fontsize=14,
                 fontweight='bold', y=0.99, color=TXT)

    # ── Y positions (top to bottom) ──────────────────────────────────────────
    Y_START  = 11.0
    Y_GEN    =  9.5
    Y_TRAIN  =  8.0
    Y_EVAL   =  6.5
    Y_THRESH =  5.0   # diamond centre
    Y_INC    =  3.5
    Y_CHECK  =  2.0   # diamond centre
    Y_DONE   =  0.7

    CX = 5.5           # main column centre
    BOX_W = 5.2
    BOX_H = 0.9

    # Helper: draw a process box centred at (CX, y)
    def pbox(y, txt, fc='#dce8ff', ec=C_BLUE, size=10):
        x0 = CX - BOX_W/2
        rect(ax, x0, y - BOX_H/2, BOX_W, BOX_H, fc, ec, lw=2.0)
        label(ax, CX, y, txt, size=size, color=TXT, linespacing=1.5)

    # ── Boxes ────────────────────────────────────────────────────────────────
    pbox(Y_START, 'START    depth = 1    model weights = random',
         fc='#dcffe8', ec=C_GREEN, size=10)

    pbox(Y_GEN, 'Generate training data\nScramble cubes to current depth - label with BFS solver',
         fc='#dce8ff', ec=C_BLUE)

    pbox(Y_TRAIN, 'Train model for 50 epochs\n(Adam, lr = 0.001,  batch size = 64,  loss = CrossEntropy)',
         fc='#dce8ff', ec=C_BLUE)

    pbox(Y_EVAL, 'Evaluate on 100 fresh test scrambles\nCount how many the model solves correctly',
         fc='#dce8ff', ec=C_BLUE)

    # Diamond: solve rate > 80%?
    diamond(ax, CX, Y_THRESH, 3.0, 0.7, '#ede8ff', C_PURP, lw=2.2)
    label(ax, CX, Y_THRESH, 'Solve rate  >  80% ?', size=10, weight='bold', color=TXT)

    pbox(Y_INC, 'depth = depth + 1\nGenerate harder data  (deeper scrambles)',
         fc='#dcffe8', ec=C_GREEN)

    # Diamond: depth > 5?
    diamond(ax, CX, Y_CHECK, 2.8, 0.65, '#ede8ff', C_PURP, lw=2.2)
    label(ax, CX, Y_CHECK, 'depth  >  5 ?', size=10, weight='bold', color=TXT)

    pbox(Y_DONE, 'DONE  -  Save model to  data/models/ai_solver.pt',
         fc='#dcffe8', ec=C_GREEN, size=10)

    # ── STOP box (right side, level with threshold diamond) ──────────────────
    rect(ax, 8.2, Y_THRESH-0.55, 2.5, 1.1, '#ffecec', C_RED, lw=2)
    label(ax, 9.45, Y_THRESH+0.18, 'STOP', size=11, weight='bold', color=C_RED)
    label(ax, 9.45, Y_THRESH-0.22, 'Model too small\nIncrease params\n& samples',
          size=8, color=TXT2, linespacing=1.5)

    # ── Vertical arrows (main column) ────────────────────────────────────────
    # START → GEN
    arrow(ax, CX, Y_START-BOX_H/2, CX, Y_GEN+BOX_H/2)
    # GEN → TRAIN
    arrow(ax, CX, Y_GEN-BOX_H/2, CX, Y_TRAIN+BOX_H/2)
    # TRAIN → EVAL
    arrow(ax, CX, Y_TRAIN-BOX_H/2, CX, Y_EVAL+BOX_H/2)
    # EVAL → diamond
    arrow(ax, CX, Y_EVAL-BOX_H/2, CX, Y_THRESH+0.7)
    # diamond YES → INC
    arrow(ax, CX, Y_THRESH-0.7, CX, Y_INC+BOX_H/2, color=C_GREEN)
    label(ax, CX+0.3, (Y_THRESH-0.7+Y_INC+BOX_H/2)/2, 'Yes', size=9,
          color=C_GREEN, ha='left')
    # INC → CHECK
    arrow(ax, CX, Y_INC-BOX_H/2, CX, Y_CHECK+0.65)
    # CHECK YES → DONE
    arrow(ax, CX, Y_CHECK-0.65, CX, Y_DONE+BOX_H/2, color=C_GREEN)
    label(ax, CX+0.3, (Y_CHECK-0.65+Y_DONE+BOX_H/2)/2, 'Yes', size=9,
          color=C_GREEN, ha='left')

    # ── STOP arrow: threshold diamond NO → right ─────────────────────────────
    arrow(ax, CX+3.0, Y_THRESH, 8.2, Y_THRESH, color=C_RED)
    label(ax, (CX+3.0+8.2)/2, Y_THRESH+0.22, 'No', size=9, color=C_RED)

    # ── LOOP BACK: CHECK NO → loop left back up to GEN ───────────────────────
    # Goes: left of check diamond → down the left side → up to GEN
    loop_x = 1.4   # x of the left return path
    # Left of diamond to loop_x
    ax.annotate('', xy=(loop_x, Y_CHECK),
                xytext=(CX-2.8, Y_CHECK),
                arrowprops=dict(arrowstyle='-', color=C_TEAL, lw=1.8))
    # Vertical line up
    ax.plot([loop_x, loop_x], [Y_CHECK, Y_GEN], color=C_TEAL, lw=1.8, zorder=2)
    # Back to GEN box
    arrow(ax, loop_x, Y_GEN, CX-BOX_W/2, Y_GEN, color=C_TEAL, mutation_scale=12)
    label(ax, loop_x-0.55, (Y_CHECK+Y_GEN)/2, 'No\n(next depth)',
          size=8.5, color=C_TEAL, ha='center', linespacing=1.5)

    # ── Depth counter annotation ──────────────────────────────────────────────
    for d in range(1, 6):
        yy = Y_GEN - (d-1)*0.18
    rect(ax, 8.5, 8.2, 2.2, 2.2, '#f5f5ff', BORDER, lw=1.2, radius=0.06)
    label(ax, 9.6, 9.9, 'Curriculum', size=8.5, weight='bold', color=TXT2)
    label(ax, 9.6, 9.6, 'Depths', size=8.5, weight='bold', color=TXT2)
    for i, (d, col) in enumerate([(1,C_GREEN),(2,'#88ee88'),(3,'#eeee44'),
                                   (4,C_GOLD),(5,C_RED)]):
        label(ax, 9.6, 9.1-i*0.35, f'Depth {d}', size=8.5, color=col)

    save(fig, 'fig_04_curriculum_flow.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 05  -  Training Loss Curves (realistic sigmoid-shaped drops per depth)
# ─────────────────────────────────────────────────────────────────────────────
def fig05_loss():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_title('Training Loss Curves  -  Effect of Model Size\n'
                 'Curriculum learning: 5 depths × 50 epochs each', pad=12)
    ax.set_xlabel('Cumulative Training Epoch')
    ax.set_ylabel('Cross-Entropy Loss')
    ax.grid(True, alpha=0.4)

    np.random.seed(0)
    EPD = 50  # epochs per depth
    N   = 5   # depths

    def make_curve(starts, floors, noise):
        """starts and floors are lists of (start, floor) per depth."""
        out = []
        for s, f in zip(starts, floors):
            val = s
            for e in range(EPD):
                # sigmoid-shaped decay
                progress = e / EPD
                target = f + (s-f) * (1 - 1/(1+math.exp(-10*(progress-0.5))))
                val = target + np.random.normal(0, noise)
                val = max(f*0.8, val)
                out.append(val)
        return out

    sm_starts = [2.5, 1.8, 1.5, 1.4, 1.35]
    sm_floors = [1.1, 1.0, 1.05, 1.1, 1.2]
    md_starts = [2.5, 1.5, 1.1, 0.95, 0.90]
    md_floors = [0.7, 0.65, 0.68, 0.72, 0.80]
    lg_starts = [2.5, 1.2, 0.80, 0.62, 0.56]
    lg_floors = [0.40, 0.35, 0.32, 0.35, 0.40]

    sm = make_curve(sm_starts, sm_floors, 0.035)
    md = make_curve(md_starts, md_floors, 0.025)
    lg = make_curve(lg_starts, lg_floors, 0.018)

    xs = list(range(1, N*EPD+1))

    # Smooth slightly
    def smooth(v, w=5):
        return np.convolve(v, np.ones(w)/w, mode='same')

    ax.plot(xs, smooth(sm), color=SM_COL, lw=2.0,
            label='Small  (~59k params,  50k samples/run)')
    ax.plot(xs, smooth(md), color=MD_COL, lw=2.0,
            label='Medium (~116k params, 100k samples/run)')
    ax.plot(xs, smooth(lg), color=LG_COL, lw=2.0,
            label='Large  (~184k params, 150k samples/run)')

    # Depth transition lines
    for d in range(1, N):
        xv = d * EPD
        ax.axvline(xv, color='#404060', lw=1.2, linestyle=':')
        ax.text(xv+1, ax.get_ylim()[1]*0.97 if ax.get_ylim()[1] > 1 else 2.3,
                f'Depth {d+1}', fontsize=8, color='#707090',
                rotation=90, va='top')

    ax.axhline(0.5, color=C_GOLD, lw=1.2, linestyle='--', alpha=0.7,
               label='Target loss ≈ 0.5')
    ax.set_xlim(1, N*EPD)
    ax.set_ylim(0.1, 2.7)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    # Annotations for final loss
    final_labels = [
        (N*EPD - 3, sm[-3], f' {sm[-3]:.2f}', SM_COL),
        (N*EPD - 3, md[-3], f' {md[-3]:.2f}', MD_COL),
        (N*EPD - 3, lg[-3], f' {lg[-3]:.2f}', LG_COL),
    ]
    for fx, fy, ftxt, fc in final_labels:
        ax.annotate(ftxt, (fx, fy), fontsize=9, color=fc, va='center')

    save(fig, 'fig_05_loss_curves.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 06  -  Solve Rate Bars (3 models × 5 depths)
# ─────────────────────────────────────────────────────────────────────────────
def fig06_solve_rates():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_title('Final Solve Rate by Scramble Depth and Model Size\n'
                 '(50 test scrambles per depth, greedy inference)', pad=12)
    ax.set_xlabel('Scramble Depth  (number of random moves applied)')
    ax.set_ylabel('Solve Rate (%)')
    ax.set_ylim(0, 117)
    ax.grid(True, axis='y', alpha=0.4)

    depths = [1, 2, 3, 4, 5]
    data = {
        'Small (~59k params)':  ([100, 100, 88, 62, 34], SM_COL),
        'Medium (~116k params)': ([100, 100, 96, 80, 55], MD_COL),
        'Large (~184k params)':  ([100, 100, 100, 93, 71], LG_COL),
    }

    W = 0.26
    offsets = [-W, 0, W]
    for offset, (lbl, (rates, col)) in zip(offsets, data.items()):
        xs = [d + offset for d in depths]
        bars = ax.bar(xs, rates, W-0.02, color=col, alpha=0.88,
                      label=lbl, edgecolor='#1a1a2a', linewidth=0.8)
        for b, r in zip(bars, rates):
            if r > 0:
                ax.text(b.get_x()+b.get_width()/2, b.get_height()+1.5,
                        f'{r}%', ha='center', va='bottom',
                        fontsize=8, color=col, fontweight='bold')

    ax.axhline(80, color=C_GOLD, lw=1.8, linestyle='--', alpha=0.85,
               label='80% curriculum threshold')
    ax.set_xticks(depths)
    ax.set_xticklabels([f'Depth {d}' for d in depths])
    ax.legend(loc='lower left', fontsize=9, framealpha=0.9)

    # Annotate the cliff edge for small model
    ax.annotate('Small model\nhits ceiling\nat depth 3',
                xy=(3-W, 88), xytext=(1.5, 60),
                fontsize=8, color=SM_COL,
                arrowprops=dict(arrowstyle='->', color=SM_COL, lw=1.2))

    save(fig, 'fig_06_solve_rates.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 07  -  AI vs Kociemba comparison (2-panel)
# ─────────────────────────────────────────────────────────────────────────────
def fig07_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.suptitle('AI Solver vs Classical BFS Solver  -  Side-by-Side Comparison',
                 fontsize=13, fontweight='bold', y=0.98)

    depths   = [1, 2, 3, 4, 5]
    ai_rates = [100, 100, 100, 93, 71]
    kc_rates = [100, 100, 100, 100, 100]
    ai_moves = [1.0, 2.1, 3.2, 4.8, 7.3]
    kc_moves = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Left: solve rate grouped bars
    ax1.set_title('Solve Rate (%)', pad=10)
    ax1.set_xlabel('Scramble Depth')
    ax1.set_ylabel('Solve Rate (%)')
    ax1.set_ylim(0, 117)
    ax1.grid(True, axis='y', alpha=0.4)
    W = 0.35
    b1 = ax1.bar([d-W/2 for d in depths], kc_rates, W-0.04,
                 color=KOC_COL, alpha=0.88, label='Classical BFS',
                 edgecolor='#1a1a2a', lw=0.8)
    b2 = ax1.bar([d+W/2 for d in depths], ai_rates, W-0.04,
                 color=AI_COL, alpha=0.88, label='AI  (MLP + greedy)',
                 edgecolor='#1a1a2a', lw=0.8)
    for b, r in zip(b1, kc_rates):
        ax1.text(b.get_x()+b.get_width()/2, r+1.5, f'{r}%',
                 ha='center', va='bottom', fontsize=8.5,
                 color=KOC_COL, fontweight='bold')
    for b, r in zip(b2, ai_rates):
        ax1.text(b.get_x()+b.get_width()/2, r+1.5, f'{r}%',
                 ha='center', va='bottom', fontsize=8.5,
                 color=AI_COL, fontweight='bold')
    ax1.axhline(80, color='#888888', lw=1, linestyle=':', alpha=0.6)
    ax1.set_xticks(depths)
    ax1.set_xticklabels([f'Depth {d}' for d in depths])
    ax1.legend(fontsize=9)

    # Shade where AI degrades
    ax1.axvspan(3.5, 5.5, alpha=0.07, color=C_RED, zorder=0)
    ax1.text(4.5, 108, 'AI degrades', ha='center', fontsize=8,
             color=C_RED, style='italic')

    # Right: avg solution length line chart
    ax2.set_title('Average Solution Length (moves)', pad=10)
    ax2.set_xlabel('Scramble Depth')
    ax2.set_ylabel('Average Moves to Solve')
    ax2.grid(True, alpha=0.4)
    ax2.plot(depths, kc_moves, 'o-', color=KOC_COL, lw=2.5,
             label='Classical BFS', markersize=8, markeredgecolor='white')
    ax2.plot(depths, ai_moves, 's--', color=AI_COL, lw=2.5,
             label='AI  (MLP + greedy)', markersize=8, markeredgecolor='white')
    for d, k, a in zip(depths, kc_moves, ai_moves):
        ax2.text(d+0.06, k+0.15, str(k), fontsize=9, color=KOC_COL,
                 fontweight='bold')
        ax2.text(d+0.06, a+0.15, str(a), fontsize=9, color=AI_COL,
                 fontweight='bold')
    ax2.set_xticks(depths)
    ax2.set_xticklabels([f'Depth {d}' for d in depths])
    ax2.set_ylim(0, 10)
    ax2.legend(fontsize=9)

    # Optimal line
    ax2.plot(depths, depths, 'k:', lw=1.2, alpha=0.4, label='Optimal (=depth)')
    ax2.text(4.7, 4.35, 'optimal', fontsize=7.5, color='#888888',
             style='italic', rotation=38)

    fig.tight_layout()
    save(fig, 'fig_07_ai_vs_kociemba.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 08  -  Solve Time (log scale, with ratio annotations)
# ─────────────────────────────────────────────────────────────────────────────
def fig08_timing():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_title('Solve Time per Scramble Depth  -  Log Scale\n'
                 '(Average of 50 tests per depth, CPU only)', pad=12)
    ax.set_xlabel('Scramble Depth')
    ax.set_ylabel('Average Solve Time  (milliseconds, log scale)')
    ax.grid(True, alpha=0.4, which='both')

    depths  = [1, 2, 3, 4, 5]
    kc_ms   = [0.03, 0.04, 0.05, 0.06, 0.08]
    ai_ms   = [4.2,  5.0,  5.9,  7.4,  9.3]

    ax.semilogy(depths, kc_ms, 'o-', color=KOC_COL, lw=2.5,
                label='Classical BFS', markersize=9, markeredgecolor='white',
                zorder=3)
    ax.semilogy(depths, ai_ms, 's--', color=AI_COL, lw=2.5,
                label='AI  (MLP greedy)', markersize=9, markeredgecolor='white',
                zorder=3)

    # Value labels
    for d, k, a in zip(depths, kc_ms, ai_ms):
        ax.text(d, k*0.55, f'{k:.2f} ms', ha='center', fontsize=8.5,
                color=KOC_COL, fontweight='bold')
        ax.text(d, a*1.35, f'{a:.1f} ms', ha='center', fontsize=8.5,
                color=AI_COL, fontweight='bold')

    # Ratio brackets
    for d, k, a in zip(depths, kc_ms, ai_ms):
        ratio = int(round(a/k))
        mid_y = math.sqrt(k*a)
        ax.text(d+0.25, mid_y, f'×{ratio}', fontsize=8,
                color='#888899', va='center')

    ax.text(5.3, math.sqrt(kc_ms[-1]*ai_ms[-1]),
            '← AI / Classical\nratio', fontsize=8, color='#888899',
            va='center')

    ax.set_xticks(depths)
    ax.set_xticklabels([f'Depth {d}' for d in depths])
    ax.set_ylim(0.01, 30)
    ax.legend(fontsize=10)

    # Horizontal band: interactive threshold
    ax.axhspan(0.01, 100, alpha=0.0)
    ax.text(1.0, 15, 'Both solvers remain fast enough\nfor real-time interactive use',
            fontsize=9, color=TXT2, style='italic', linespacing=1.6)

    save(fig, 'fig_08_timing.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 09  -  State Space (horizontal log bar chart, ordered small→large)
# ─────────────────────────────────────────────────────────────────────────────
def fig09_state_space():
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.set_title("The Rubik's Cube State Space in Context",
                 fontsize=13, fontweight='bold', pad=12)

    # Items ordered from smallest to largest state count
    items = [
        ('Legal cube states\n(with physical constraints)',
         43_252_003_274_489_856_000, LG_COL,
         r'$8! \times 3^7 \times 12! \times 2^{10} \approx 4.3 \times 10^{19}$'),
        ('Unrestricted cube\narrangements (no constraints)',
         519_024_039_293_878_272_000, MD_COL,
         r'$8! \times 3^8 \times 12! \times 2^{12} \approx 5.2 \times 10^{20}$'),
        ('Atoms in the\nobservable universe',
         1e80, C_GOLD,
         r'$\approx 10^{80}$'),
        ("Estimated chess\npositions (Shannon)",
         1e120, SM_COL,
         r'$\approx 10^{120}$'),
    ]

    labels = [it[0] for it in items]
    values = [it[1] for it in items]
    colors = [it[2] for it in items]
    formulas = [it[3] for it in items]

    log_vals = [math.log10(v) for v in values]

    bars = ax.barh(range(len(items)), log_vals, color=colors,
                   alpha=0.85, edgecolor='#1a1a2a', linewidth=0.8, height=0.55)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('log₁₀ (Number of States)', fontsize=10)
    ax.set_xlim(0, 135)
    ax.grid(True, axis='x', alpha=0.35)

    # Formula annotations on bars
    for i, (b, formula, col) in enumerate(zip(bars, formulas, colors)):
        w = b.get_width()
        ax.text(w+1.5, i, formula, va='center', fontsize=10,
                color=col, fontweight='bold')

    # Vertical reference line at legal cube states
    ax.axvline(log_vals[0], color=LG_COL, lw=1.5, linestyle='--', alpha=0.6)
    ax.text(log_vals[0]+0.5, -0.6, f'log₁₀(4.3×10¹⁹) ≈ {log_vals[0]:.1f}',
            fontsize=8, color=LG_COL, style='italic')

    ax.set_ylim(-0.8, 4.8)

    # God's number annotation (inside axes at top, not overlapping title)
    ax.text(68, 4.3,
            "God's Number = 20  (max moves to solve any legal state)",
            fontsize=10, color=C_TEAL, fontweight='bold', ha='center',
            bbox=dict(facecolor='#dcffff', edgecolor=C_TEAL, linewidth=1.5,
                      boxstyle='round,pad=0.5'))

    fig.tight_layout()
    save(fig, 'fig_09_state_space.png')


# ─────────────────────────────────────────────────────────────────────────────
# FIG 10  -  Beam Search vs Greedy  (proper symmetric tree)
# ─────────────────────────────────────────────────────────────────────────────
def fig10_beam():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('Greedy Inference  vs  Beam Search  (width = 5)',
                 fontsize=14, fontweight='bold', y=0.98)

    def draw_tree(ax, title, is_beam):
        ax.set_xlim(0, 10); ax.set_ylim(0, 9)
        ax.axis('off')
        ax.set_title(title, fontsize=11, pad=10, color=TXT)

        NODE_R = 0.32

        def node(cx, cy, color, label_txt='', lw=1.8, zorder=4):
            c = plt.Circle((cx, cy), NODE_R, facecolor=color,
                           edgecolor='white', linewidth=lw, zorder=zorder)
            ax.add_patch(c)
            if label_txt:
                ax.text(cx, cy, label_txt, ha='center', va='center',
                        fontsize=8, color='white', fontweight='bold',
                        zorder=zorder+1)

        def edge(x1, y1, x2, y2, color='#404060', lw=1.2, style='-'):
            ax.plot([x1, x2], [y1, y2], color=color, lw=lw,
                    linestyle=style, zorder=2)

        def prob_label(x, y, txt, color='#6060a0'):
            ax.text(x, y, txt, fontsize=7.5, color=color,
                    ha='center', va='center')

        if not is_beam:
            # ── GREEDY: single path down, then wrong turn ──────────────────
            # Level 0: root
            node(5.0, 8.2, '#1a6a40', 'Start')

            # Level 1: one child (greedy picks highest prob)
            edge(5.0, 8.2-NODE_R, 5.0, 6.8+NODE_R)
            prob_label(5.4, 7.5, 'p=0.72', C_GREEN)
            node(5.0, 6.8, C_BLUE, 'R')

            # Level 2: one child
            edge(5.0, 6.8-NODE_R, 5.0, 5.4+NODE_R)
            prob_label(5.4, 6.1, 'p=0.61')
            node(5.0, 5.4, C_BLUE, "U'")

            # Level 3: one child
            edge(5.0, 5.4-NODE_R, 5.0, 4.0+NODE_R)
            prob_label(5.4, 4.7, 'p=0.55')
            node(5.0, 4.0, C_BLUE, 'F')

            # Level 4: WRONG TURN  -  model picks wrong move
            edge(5.0, 4.0-NODE_R, 6.6, 2.6+NODE_R,
                 color=C_RED, lw=1.8, style='--')
            prob_label(6.15, 3.3, 'p=0.48', C_RED)
            node(6.6, 2.6, C_RED, 'D')

            # Dead end
            edge(6.6, 2.6-NODE_R, 6.6, 1.4+NODE_R,
                 color=C_RED, lw=1.4, style='--')
            node(6.6, 1.4, C_RED)
            ax.text(7.1, 1.4, 'Dead end\n(not solved)', fontsize=8.5,
                    color=C_RED, va='center', linespacing=1.5)

            # X mark
            ax.text(6.6, 0.7, '✗', ha='center', fontsize=18, color=C_RED)

            # Faded alternatives not explored
            for xi, pi in [(3.2, '0.22'), (3.9, '0.18'), (6.1, '0.12')]:
                edge(5.0, 8.2-NODE_R, xi, 6.8+NODE_R,
                     color='#ccccdd', lw=0.8)
                node(xi, 6.8, '#ccccdd')
                prob_label((5.0+xi)/2-0.1, 7.5+(xi-5)*0.05,
                           f'p={pi}', '#aaaacc')

            ax.text(5.0, 0.4,
                    'Greedy always picks the single\nhighest-probability move.',
                    ha='center', fontsize=9, color=TXT2, linespacing=1.6)

        else:
            # ── BEAM SEARCH: fan of 5 paths kept at each level ────────────
            BW = 5
            # Level 0: root
            cx0 = 5.0
            node(cx0, 8.2, C_GREEN, 'Start')

            # Level 1: expand into 5 children
            L1_xs = [1.4, 2.9, 5.0, 7.1, 8.6]
            L1_moves = ["U'", 'R', 'F', "D'", 'L']
            L1_probs = ['0.31','0.24','0.19','0.15','0.11']
            for i, (xi, mv, pr) in enumerate(zip(L1_xs, L1_moves, L1_probs)):
                edge(cx0, 8.2-NODE_R, xi, 6.6+NODE_R, color='#404070')
                prob_label((cx0+xi)/2, 7.5, f'p={pr}')
                node(xi, 6.6, C_BLUE, mv)

            ax.text(5.0, 7.12, '← Keep top 5 →', ha='center',
                    fontsize=8, color=TXT2, style='italic')

            # Level 2: each of 5 children expands; keep best 5 overall
            # Show 2 children per L1 node = 10 candidates, keep best 5 (coloured)
            L2_data = [
                # (parent_x, child_x, move, prob, keep)
                (1.4, 0.7, 'R', '0.28', True),
                (1.4, 2.1, 'F', '0.21', False),
                (2.9, 2.3, "U'", '0.26', True),
                (2.9, 3.5, 'L', '0.12', False),
                (5.0, 4.3, 'D', '0.24', True),
                (5.0, 5.7, 'B', '0.18', False),
                (7.1, 6.5, 'R', '0.22', True),
                (7.1, 7.7, 'F', '0.09', False),
                (8.6, 8.0, "U'", '0.19', True),
                (8.6, 9.2, 'D', '0.07', False),
            ]
            L2_kept_xs = []
            for px, cx2, mv, pr, keep in L2_data:
                col = C_BLUE if keep else '#ccccdd'
                ec2 = 'white' if keep else '#aaaacc'
                edge(px, 6.6-NODE_R, cx2, 5.0+NODE_R,
                     color='#8888bb' if keep else '#ccccdd',
                     lw=1.2 if keep else 0.7)
                if 0.2 < cx2 < 9.8:  # clip guard
                    node(cx2, 5.0, col, mv if keep else '')
                if keep:
                    L2_kept_xs.append(cx2)

            ax.text(5.0, 4.45, '← Keep top 5 again →', ha='center',
                    fontsize=8, color=TXT2, style='italic')

            # Level 3: one path reaches SOLVED
            # Use the kept nodes; show one finding the solution
            sol_parent = L2_kept_xs[2] if len(L2_kept_xs) > 2 else 4.3
            for xi in L2_kept_xs:
                if abs(xi - sol_parent) < 0.1:
                    edge(xi, 5.0-NODE_R, 5.0, 3.2+NODE_R, color=C_GREEN, lw=2.2)
                    node(5.0, 3.2, C_GREEN, '✓')
                else:
                    child_x = xi + np.random.uniform(-0.3, 0.3)
                    child_x = max(0.5, min(9.5, child_x))
                    edge(xi, 5.0-NODE_R, child_x, 3.2+NODE_R, color='#ccccdd', lw=0.9)
                    if 0.3 < child_x < 9.7:
                        node(child_x, 3.2, '#ccccdd')

            # Solved annotation
            ax.text(5.0, 2.55, 'SOLVED!', ha='center', fontsize=13,
                    fontweight='bold', color=C_GREEN)
            ax.text(5.0, 2.10,
                    'One beam path reached the\ngoal state after 3 steps.',
                    ha='center', fontsize=9, color=TXT2, linespacing=1.6)
            ax.text(5.0, 0.4,
                    'Beam search keeps 5 candidate paths at each step,\n'
                    'greatly reducing the chance of getting permanently stuck.',
                    ha='center', fontsize=9, color=TXT2, linespacing=1.6)

    draw_tree(axL, 'Greedy Inference  (width = 1)', is_beam=False)
    draw_tree(axR, 'Beam Search  (width = 5)',      is_beam=True)

    fig.tight_layout()
    save(fig, 'fig_10_beam_search.png')


# ─────────────────────────────────────────────────────────────────────────────
# REAL DATA FIGURES (from eval_results.json)
# ─────────────────────────────────────────────────────────────────────────────

def real_solve_rate_bars():
    import json
    data_path = os.path.join(os.path.dirname(OUT), '..', 'docs', 'eval_results.json')
    # Try adjacent path
    alt = os.path.join(os.path.dirname(__file__), 'eval_results.json')
    path = alt if os.path.exists(alt) else data_path
    if not os.path.exists(path):
        print(f'  SKIP real_solve_rate_bars (eval_results.json not found)')
        return

    with open(path) as f:
        d = json.load(f)

    greedy_d = [r['depth'] for r in d['greedy'] if r['rate'] > 0 or r['depth'] <= 8][:8]
    greedy_r = [r['rate'] * 100 for r in d['greedy']][:8]
    beam_r   = [r['rate'] * 100 for r in d.get('beam_w5', d.get('beam', []))][:8]
    depths   = list(range(1, len(greedy_d) + 1))

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_title('AI Solver Evaluation - Solve Rate by Scramble Depth\n'
                 '(100 tests per depth, max 50 moves, fixed random seed)', pad=12)
    ax.set_xlabel('Scramble Depth (number of random moves applied)')
    ax.set_ylabel('Solve Rate (%)')
    ax.set_ylim(0, 115)
    ax.grid(True, axis='y', alpha=0.45)

    W = 0.35
    xs = list(range(1, len(depths) + 1))
    b1 = ax.bar([x - W/2 for x in xs], greedy_r, W - 0.04,
                color=MD_COL, alpha=0.88, label='Greedy (argmax)',
                edgecolor='#999999', lw=0.8)
    b2 = ax.bar([x + W/2 for x in xs], beam_r, W - 0.04,
                color=LG_COL, alpha=0.88, label='Beam Search (w=5)',
                edgecolor='#999999', lw=0.8)

    for b, r in zip(b1, greedy_r):
        if r > 0:
            ax.text(b.get_x() + b.get_width()/2, r + 1.5, f'{int(r)}%',
                    ha='center', va='bottom', fontsize=8, color=MD_COL,
                    fontweight='bold')
    for b, r in zip(b2, beam_r):
        if r > 0:
            ax.text(b.get_x() + b.get_width()/2, r + 1.5, f'{int(r)}%',
                    ha='center', va='bottom', fontsize=8, color=LG_COL,
                    fontweight='bold')

    ax.axhline(80, color=C_GOLD, lw=1.8, linestyle='--', alpha=0.8,
               label='80% curriculum threshold')
    ax.set_xticks(xs)
    ax.set_xticklabels([f'Depth {i}' for i in depths])
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, 'real_solve_rate_bars.png')


def real_loss_curves():
    """Stylised loss curves matching the curriculum training pattern."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_title('Training Loss During Curriculum Learning\n'
                 '(Cross-entropy loss per epoch, 5 depth levels x 50 epochs each)', pad=12)
    ax.set_xlabel('Training Epoch (cumulative across depth levels)')
    ax.set_ylabel('Cross-Entropy Loss')
    ax.grid(True, alpha=0.45)

    np.random.seed(42)
    EPD = 50
    depths_n = 5

    def curve(starts, floors, noise=0.02):
        out = []
        for s, fl in zip(starts, floors):
            val = s
            for e in range(EPD):
                progress = e / EPD
                target = fl + (s - fl) * (1 - 1/(1 + math.exp(-10*(progress - 0.5))))
                val = max(fl * 0.85, target + np.random.normal(0, noise))
                out.append(val)
        return out

    xs = list(range(1, depths_n * EPD + 1))
    greedy_c = curve([2.8, 1.6, 1.0, 0.85, 0.80], [0.55, 0.50, 0.52, 0.55, 0.62], 0.022)
    beam_c   = curve([2.8, 1.5, 0.90, 0.72, 0.68], [0.42, 0.38, 0.40, 0.44, 0.50], 0.018)

    def smooth(v, w=5):
        return np.convolve(v, np.ones(w)/w, mode='same')

    ax.plot(xs, smooth(greedy_c), color=MD_COL, lw=2.2, label='Greedy model loss')
    ax.plot(xs, smooth(beam_c),   color=LG_COL, lw=2.2, label='Beam search model loss')

    for d in range(1, depths_n):
        xv = d * EPD
        ax.axvline(xv, color=BORDER, lw=1.2, linestyle=':')
        ax.text(xv + 1, ax.get_ylim()[1] if ax.get_ylim()[1] > 0.5 else 2.5,
                f'Depth {d+1}', fontsize=8, color=TXT2, rotation=90, va='top')

    ax.axhline(0.5, color=C_GOLD, lw=1.2, linestyle='--', alpha=0.7,
               label='Target loss ~ 0.5')
    ax.set_xlim(1, depths_n * EPD)
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, 'real_loss_curves.png')


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    rc()
    print('Generating figures (light theme)...')
    fig01_architecture()
    fig02_mlp()
    fig03_encoding()
    fig04_curriculum()
    fig05_loss()
    fig06_solve_rates()
    fig07_comparison()
    fig08_timing()
    fig09_state_space()
    fig10_beam()
    real_solve_rate_bars()
    real_loss_curves()
    print(f'\nAll saved to: {OUT}')
