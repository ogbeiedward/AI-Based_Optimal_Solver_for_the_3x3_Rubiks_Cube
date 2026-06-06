"""
gen_howto.py - comprehensive beginner-friendly project guide.
Run: python docs/gen_howto.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, Image,
                                 PageBreak, KeepTogether)
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "docs", "figures")
OUT  = os.path.join(ROOT, "docs", "Project_Howto_Guide.pdf")

NAVY  = colors.HexColor("#0d1b4b")
BLUE  = colors.HexColor("#1a3a8f")
STEEL = colors.HexColor("#3a5aaa")
DARK  = colors.HexColor("#1a1a2e")
GRAY  = colors.HexColor("#555577")
LGRAY = colors.HexColor("#f0f0fa")
STRIP = colors.HexColor("#e8ecf8")


def _styles():
    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "Title":    s("Title",   fontName="Helvetica-Bold",    fontSize=24,
                      leading=30, spaceAfter=8,  alignment=TA_CENTER,
                      textColor=NAVY),
        "Subtitle": s("Subtitle",fontName="Helvetica",          fontSize=13,
                      leading=18, spaceAfter=24, alignment=TA_CENTER,
                      textColor=GRAY),
        "H1":       s("H1",      fontName="Helvetica-Bold",    fontSize=16,
                      leading=22, spaceAfter=6,  spaceBefore=20,
                      textColor=NAVY),
        "H2":       s("H2",      fontName="Helvetica-Bold",    fontSize=13,
                      leading=18, spaceAfter=4,  spaceBefore=14,
                      textColor=BLUE),
        "H3":       s("H3",      fontName="Helvetica-BoldOblique", fontSize=11,
                      leading=16, spaceAfter=3,  spaceBefore=10,
                      textColor=STEEL),
        "Body":     s("Body",    fontName="Helvetica",          fontSize=11,
                      leading=17, spaceAfter=8,  spaceBefore=2,
                      alignment=TA_JUSTIFY),
        "Bullet":   s("Bullet",  fontName="Helvetica",          fontSize=11,
                      leading=16, spaceAfter=4,  leftIndent=18,
                      firstLineIndent=0),
        "SubBullet":s("SubBullet",fontName="Helvetica",         fontSize=10,
                      leading=15, spaceAfter=3,  leftIndent=36),
        "Code":     s("Code",    fontName="Courier",             fontSize=9,
                      leading=13, spaceAfter=6,  spaceBefore=4,
                      backColor=colors.HexColor("#f4f4f8"),
                      leftIndent=14, rightIndent=14,
                      borderPadding=(4, 4, 4, 4), textColor=DARK),
        "Note":     s("Note",    fontName="Helvetica-Oblique",   fontSize=10,
                      leading=14, spaceAfter=6,
                      textColor=GRAY, leftIndent=14, rightIndent=14),
        "Caption":  s("Caption", fontName="Helvetica-Oblique",   fontSize=9,
                      leading=13, spaceAfter=10, alignment=TA_CENTER,
                      textColor=GRAY),
        "Box":      s("Box",     fontName="Helvetica",           fontSize=11,
                      leading=16, spaceAfter=4,
                      backColor=STRIP, leftIndent=14, rightIndent=14,
                      borderPadding=(6, 6, 6, 6), textColor=DARK),
        "Def":      s("Def",     fontName="Helvetica-Bold",      fontSize=11,
                      leading=16, spaceAfter=2, spaceBefore=8,
                      textColor=BLUE),
    }


ST = _styles()


def hr():
    return HRFlowable(width="100%", thickness=0.6,
                      color=colors.HexColor("#aaaacc"), spaceAfter=6)


def h1(text):
    return Paragraph(text, ST["H1"])


def h2(text):
    return Paragraph(text, ST["H2"])


def h3(text):
    return Paragraph(text, ST["H3"])


def p(text):
    return Paragraph(text, ST["Body"])


def box(text):
    return Paragraph(text, ST["Box"])


def code(lines):
    if isinstance(lines, list):
        joined = "<br/>".join(
            line.replace(" ", "&nbsp;") for line in lines
        )
    else:
        joined = lines.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(joined, ST["Code"])


def note(text):
    return Paragraph(f"<i>Note: {text}</i>", ST["Note"])


def b(text):
    return Paragraph(f"- {text}", ST["Bullet"])


def sb(text):
    return Paragraph(f"   * {text}", ST["SubBullet"])


def defn(term, explanation):
    return [
        Paragraph(term, ST["Def"]),
        Paragraph(explanation, ST["Body"]),
    ]


def sp(h=8):
    return Spacer(1, h)


def img(fname, width=14 * cm, caption=None):
    path = os.path.join(FIGS, fname)
    items = []
    if os.path.exists(path):
        items.append(Image(path, width=width, height=width * 0.55))
    if caption:
        items.append(Paragraph(caption, ST["Caption"]))
    return items


def tbl(data, col_widths=None, hdr_color=None):
    if col_widths is None:
        col_widths = [4 * cm] * len(data[0])
    if hdr_color is None:
        hdr_color = NAVY
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  hdr_color),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  10),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LGRAY, colors.white]),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 10),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#aaaacc")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
        title="AI Rubik's Cube Solver - Complete Guide",
        author="Edward Ogbei",
    )

    story = []

    # ------------------------------------------------------------------ Cover
    story += [
        sp(50),
        Paragraph("AI-Based Optimal Solver", ST["Title"]),
        Paragraph("for the 3x3 Rubik's Cube", ST["Title"]),
        sp(12),
        Paragraph("A Complete Beginner's Guide to How It Works and How to Use It",
                  ST["Subtitle"]),
        hr(),
        Paragraph("Edward Ogbei | M.Sc. Artificial Intelligence | Politechnika Czestochowa 2026",
                  ST["Subtitle"]),
        PageBreak(),
    ]

    # ------------------------------------------------------------------ Intro
    story += [h1("Introduction - What Is This Project?"), hr()]

    story.append(p(
        "This project builds an artificial intelligence system that learns to solve a Rubik's Cube. "
        "The cube is one of the most famous combinatorial puzzles in the world: despite being a "
        "small physical object, it has over 43 quintillion (43,252,003,274,489,856,000) possible "
        "arrangements. Only one of those is the solved state."
    ))
    story.append(p(
        "Solving a Rubik's Cube by brute force - trying every possible sequence of moves - is "
        "completely impractical. Instead, this project teaches a neural network to imitate an "
        "expert solver, gradually learning to handle more and more difficult scrambles."
    ))
    story.append(p(
        "The system has four main parts that work together:"
    ))
    for item in [
        "<b>The Cube Engine</b> - a mathematical model of the cube's state stored as integer arrays.",
        "<b>The Expert Solver</b> - a search algorithm that finds optimal solutions and generates training data.",
        "<b>The Neural Network</b> - the AI model that learns to predict the next best move.",
        "<b>The Web Interface</b> - a 3D browser visualisation where you can interact with everything.",
    ]:
        story.append(b(item))

    story.append(sp(4))
    story.append(p(
        "This guide explains each part from the ground up. Every abbreviation is defined, every "
        "design choice is explained, and the mathematics is described in plain English. "
        "No prior knowledge of AI or Rubik's Cube theory is assumed."
    ))

    story += img("fig_01_system_architecture.png",
                 caption="Figure 1: The four components and how they interact.")

    # ------------------------------------------------------------------ S1
    story += [PageBreak(), h1("1. Quick Start - Running the Project"), hr()]

    story.append(p(
        "You need Python 3.10 or later. Open a terminal (Command Prompt or PowerShell on Windows, "
        "Terminal on Mac/Linux) and navigate to the project folder. Then install the required "
        "libraries with:"
    ))
    story.append(code("pip install -r requirements.txt"))
    story.append(p(
        "Once that finishes, start the web visualisation server:"
    ))
    story.append(code("python main.py visualize --web"))
    story.append(p(
        "Open your browser and go to <b>http://localhost:8080</b>. "
        "You will see a 3D Rubik's Cube on the left and a control panel on the right."
    ))
    story += img("screenshot_08_ui_wide.png",
                 caption="Figure 2: The web interface. Left: 3D cube. Right: control panel.")

    story.append(h2("1.1 What You Can Do in the Browser"))
    for item in [
        "Click any move button (U, U', R, R', etc.) to rotate a layer with animation.",
        "Click <b>Scramble (5)</b> for a shallow scramble or <b>Scramble (20)</b> for a hard one.",
        "Click <b>Solve (Kociemba Expert)</b> to solve with the reliable search-based solver.",
        "Click <b>AI Greedy</b> to let the neural network attempt a solve step by step.",
        "Click <b>AI Beam Search (w=5)</b> for the more powerful beam search solver.",
        "Use the speed dropdown to control how fast the animation plays.",
        "Click <b>Run Benchmark Comparison</b> to compare AI vs expert solver automatically.",
    ]:
        story.append(b(item))

    story.append(h2("1.2 Other Command-Line Tools"))
    cmd_data = [
        ["Command", "What it does"],
        ["python main.py validate",
         "Runs 7 tests to verify the cube engine is mathematically correct"],
        ["python main.py scramble -l 20",
         "Prints a random 20-move scramble sequence"],
        ["python main.py generate_dataset --max-depth 5",
         "Generates training data for depths 1 to 5"],
        ["python main.py train --max-depth 5 --epochs 50",
         "Trains the AI model using curriculum learning"],
        ["python main.py compare --max-depth 5 --num-tests 100",
         "Benchmarks AI vs expert solver and prints a results table"],
    ]
    story.append(tbl(cmd_data, col_widths=[7 * cm, 9 * cm]))

    # ------------------------------------------------------------------ S2
    story += [PageBreak(), h1("2. The Rubik's Cube as a Math Problem"), hr()]

    story.append(p(
        "Before diving into the code, it helps to understand what the Rubik's Cube actually is "
        "from a mathematical perspective. The cube is a <b>permutation group</b> - a set of states "
        "connected by operations (moves) that can be combined in sequence."
    ))

    story.append(h2("2.1 Why Are There 43 Quintillion States?"))
    story.append(p(
        "The cube has 20 moveable pieces: 8 corner pieces (each at a corner of the cube) "
        "and 12 edge pieces (each along an edge). The 6 centre pieces are fixed - they never move "
        "relative to each other and act as reference points for each face's colour."
    ))
    story.append(p(
        "If you could place the 8 corner pieces in any order and twist each independently, "
        "that would give 8! x 3^8 = 264,539,520 arrangements just for corners. "
        "Similarly, edges give 12! x 2^12 = 1,961,990,553,600 arrangements. "
        "Multiplied together, the theoretical maximum is about 519 quintillion - "
        "but the cube's physical constraints reduce this by a factor of 12, "
        "giving exactly 43,252,003,274,489,856,000 reachable states."
    ))

    story.append(h2("2.2 God's Number = 20"))
    story.append(p(
        "In 2010, a team of researchers proved that any scrambled Rubik's Cube can be solved in "
        "<b>at most 20 moves</b>. This is called God's Number - the maximum number of moves "
        "that the 'perfect solver' (God, if you will) would ever need. "
        "The AI in this project does not achieve God's Number - it often takes more moves - "
        "but it demonstrates that a neural network can learn useful solving strategies."
    ))

    story.append(h2("2.3 Half-Turn Metric (HTM)"))
    story.append(p(
        "<b>HTM</b> stands for Half-Turn Metric. It is a convention for counting moves. "
        "Under HTM, each quarter-turn (90 degrees) and each half-turn (180 degrees) both count "
        "as exactly 1 move. So R (turn right face 90 degrees clockwise), R' (turn right face "
        "90 degrees counter-clockwise), and R2 (turn right face 180 degrees) each count as 1 move."
    ))
    story.append(p(
        "The alternative is the Quarter-Turn Metric (QTM) where R2 would count as 2 moves. "
        "This project uses HTM throughout, giving 18 distinct move types (6 faces x 3 variants each)."
    ))

    story.append(h2("2.4 The Three Legality Invariants"))
    story.append(p(
        "Not every combination of piece positions is reachable by legal moves. "
        "Three mathematical constraints are preserved by every legal move and "
        "checked by the is_legal() function:"
    ))
    for item in [
        "The sum of all corner orientations must be divisible by 3 (you cannot twist just one corner).",
        "The sum of all edge orientations must be divisible by 2 (you cannot flip just one edge).",
        "The permutation parity of corners must equal the permutation parity of edges "
        "(you cannot swap just two pieces without also swapping two others).",
    ]:
        story.append(b(item))
    story.append(p(
        "These constraints mean that if you physically take apart a Rubik's Cube and reassemble "
        "it randomly, there is a 11/12 chance it will be in an illegal state - one that cannot "
        "be solved by any sequence of legal moves. The is_legal() check catches this."
    ))

    # ------------------------------------------------------------------ S3
    story += [PageBreak(), h1("3. The Cube Engine - How the Computer Stores the Cube"), hr()]

    story.append(p(
        "The cube engine (in the core/ folder) is the mathematical foundation of the whole project. "
        "It does not care about 3D graphics, colours painted on stickers, or the web interface. "
        "It stores the cube purely as numbers and applies moves using precomputed tables."
    ))

    story.append(h2("3.1 The Cubie Representation"))
    story.append(p(
        "Instead of tracking 54 coloured stickers, the engine tracks the 20 physical pieces "
        "by their position (<b>permutation</b>) and orientation. "
        "Think of it like tracking the 20 people sitting in 20 chairs, plus noting whether each "
        "person is sitting upright or leaning sideways."
    ))
    story.append(p(
        "The state is stored in four integer arrays:"
    ))
    arr_data = [
        ["Array", "Size", "What it stores", "Possible values"],
        ["cp", "8",  "Corner permutation - which corner piece is in each slot",
         "0 to 7"],
        ["co", "8",  "Corner orientation - twist of each corner piece",
         "0 (upright), 1 (CW 120 deg), 2 (CCW 120 deg)"],
        ["ep", "12", "Edge permutation - which edge piece is in each slot",
         "0 to 11"],
        ["eo", "12", "Edge orientation - whether each edge is flipped",
         "0 (normal), 1 (flipped)"],
    ]
    story.append(tbl(arr_data, col_widths=[1.5 * cm, 1.5 * cm, 6.5 * cm, 6.5 * cm]))
    story.append(sp(6))

    story.append(p(
        "In the solved state: cp = [0, 1, 2, 3, 4, 5, 6, 7], co = [0, 0, 0, 0, 0, 0, 0, 0], "
        "ep = [0, 1, 2, ..., 11], eo = [0, 0, ..., 0]. "
        "Every move updates these arrays according to a precomputed permutation and "
        "orientation-delta table defined in core/moves.py."
    ))

    story.append(h2("3.2 How Moves Are Applied"))
    story.append(p(
        "Each move is stored as two permutation arrays (one for corners, one for edges) "
        "and two orientation-delta arrays. Applying a move is just a lookup:"
    ))
    story.append(code([
        "# Example: applying move M to the cube",
        "new_cp[i] = self.cp[ move.corner_perm[i] ]",
        "new_co[i] = (self.co[ move.corner_perm[i] ] + move.corner_orient[i]) % 3",
        "",
        "new_ep[i] = self.ep[ move.edge_perm[i] ]",
        "new_eo[i] = (self.eo[ move.edge_perm[i] ] + move.edge_orient[i]) % 2",
    ]))
    story.append(p(
        "There is no floating-point arithmetic, no 3D rotation matrices - just integer lookups "
        "into arrays. This makes the engine extremely fast."
    ))

    story.append(h2("3.3 The 18 Moves"))
    story.append(p(
        "The six faces of the cube are U (Up), D (Down), R (Right), L (Left), F (Front), B (Back). "
        "Each face has three variants: a 90-degree clockwise turn (e.g. R), a 90-degree "
        "counter-clockwise turn (R', pronounced R-prime), and a 180-degree turn (R2). "
        "That gives 6 x 3 = 18 moves total."
    ))
    story.append(p(
        "The prime (') and double (2) variants are derived automatically by composing the base move:"
    ))
    story.append(code([
        "R2 = compose(R, R)        # applying R twice gives R2",
        "R' = compose(R2, R)       # applying R three times gives R-inverse",
    ]))
    story.append(note(
        "The notation R' (R-prime) means the reverse of R. If R turns the right face clockwise, "
        "then R' turns it counter-clockwise. Applying R then R' returns the cube to its previous state."
    ))

    story += img("fig_03_encoding.png",
                 caption="Figure 3: The cubie representation and one-hot encoding pipeline.")

    # ------------------------------------------------------------------ S4
    story += [PageBreak(), h1("4. Teaching the AI to See the Cube - State Encoding"), hr()]

    story.append(p(
        "The neural network works with numbers, not with concepts like 'this corner is twisted'. "
        "We need to convert the cube's state into a list of numbers that the network can process. "
        "This is called <b>state encoding</b> or <b>feature extraction</b>."
    ))

    story.append(h2("4.1 One-Hot Encoding - What Is It?"))
    story.append(p(
        "The cube has 54 facelets (9 per face, 6 faces). Each facelet has one of 6 possible "
        "colours: White (W), Red (R), Green (G), Yellow (Y), Orange (O), Blue (B). "
        "We could encode each colour as a single number (W=0, R=1, G=2, ...) but that would "
        "imply to the network that Orange (4) is somehow 'twice as much' as Red (1), "
        "which makes no sense."
    ))
    story.append(p(
        "Instead, we use <b>one-hot encoding</b>: each colour is represented as a list of 6 "
        "numbers where exactly one is 1 and the rest are 0."
    ))
    story.append(tbl(
        [
            ["Colour", "One-hot encoding"],
            ["White (index 0)",  "[1, 0, 0, 0, 0, 0]"],
            ["Red   (index 1)",  "[0, 1, 0, 0, 0, 0]"],
            ["Green (index 2)",  "[0, 0, 1, 0, 0, 0]"],
            ["Yellow (index 3)", "[0, 0, 0, 1, 0, 0]"],
            ["Orange (index 4)", "[0, 0, 0, 0, 1, 0]"],
            ["Blue  (index 5)",  "[0, 0, 0, 0, 0, 1]"],
        ],
        col_widths=[5 * cm, 11 * cm]
    ))
    story.append(sp(6))
    story.append(p(
        "Each facelet produces a 6-element list. With 54 facelets, we concatenate all 54 lists "
        "to get a single list of 54 x 6 = <b>324 numbers</b>. This 324-dimensional vector is the "
        "input to the neural network."
    ))

    story.append(h2("4.2 Why 324 Dimensions?"))
    story.append(p(
        "The number 324 comes from: 54 facelets x 6 possible colours = 324. "
        "Each of the 324 numbers is either 0.0 or 1.0 (a floating-point number, "
        "which the GPU or CPU can process very efficiently). Exactly 54 of the 324 numbers "
        "will be 1.0 (one per facelet), and the other 270 will be 0.0."
    ))
    story.append(note(
        "This encoding does NOT tell the network anything about the structure of the cube. "
        "Two cube states that look very similar physically can produce completely different "
        "324-number vectors. The network has to learn the patterns from scratch during training."
    ))

    # ------------------------------------------------------------------ S5
    story += [PageBreak(), h1("5. Generating Training Data - The Expert Solver"), hr()]

    story.append(p(
        "To train the neural network, we need thousands of examples of the form "
        "(cube state, correct next move). We get these by asking an expert solver to find "
        "the solution and then recording the first move it recommends."
    ))

    story.append(h2("5.1 What Is BFS?"))
    story.append(p(
        "<b>BFS</b> stands for <b>Breadth-First Search</b>. It is a classic algorithm for finding "
        "the shortest path through a graph (or in this case, the shortest sequence of moves to "
        "solve the cube). Here is how it works:"
    ))
    for item in [
        "Start from the scrambled cube state.",
        "Explore all states reachable in exactly 1 move (there are 18 of them).",
        "If none of them is solved, explore all states reachable in exactly 2 moves (up to 18 x 18 = 324).",
        "Continue expanding layer by layer until the solved state is found.",
        "The first path that reaches the solved state is guaranteed to be the shortest (optimal) solution.",
    ]:
        story.append(b(item))
    story.append(p(
        "The problem with BFS is that the number of states grows exponentially with depth. "
        "At depth d, there are roughly 15^d states to explore (slightly less than 18^d due to pruning). "
        "At depth 10, that is 15^10 = 576 billion states - far too many to explore in reasonable time."
    ))

    story.append(h2("5.2 Bidirectional BFS"))
    story.append(p(
        "The expert solver in this project uses <b>bidirectional BFS</b>, which is smarter: "
        "it searches forward from the scrambled state AND backward from the solved state simultaneously, "
        "meeting in the middle. If the solution is d moves long, bidirectional BFS only needs to "
        "explore states up to depth d/2 from each end, reducing the work from 15^d to roughly "
        "2 x 15^(d/2) - dramatically faster for moderate depths. "
        "In practice, this approach is reliable up to about 9 moves."
    ))

    story.append(h2("5.3 Why Use an Expert Solver Instead of Random Labels?"))
    story.append(p(
        "You might ask: why not just label each move randomly during training? "
        "The answer is that the AI learns by <b>imitation</b>. We want it to copy the behaviour "
        "of the expert. If we gave it random labels, it would learn to make random moves "
        "(which is useless). By using the BFS solver's recommendation as the label, "
        "we teach the AI to make the same move that an optimal solver would make."
    ))
    story.append(p(
        "This approach is called <b>imitation learning</b> (also called behaviour cloning). "
        "The expert generates the correct answers, and the AI learns to predict those answers "
        "given the input state."
    ))

    story.append(h2("5.4 Curriculum Learning - Start Easy, Get Harder"))
    story.append(p(
        "<b>Curriculum learning</b> is the idea of training on easy examples first and "
        "gradually making the training data harder - similar to how a student learns. "
        "In this project:"
    ))
    for item in [
        "First, generate 1,000 examples of cubes scrambled by exactly 1 move. Train the network on these.",
        "When the network can solve 80% of 1-move scrambles correctly, advance to 2-move scrambles.",
        "Generate 1,000 examples of 2-move scrambles, blend in 20% of the old data, and train again.",
        "Continue this process up to depth 5 (or deeper if requested).",
    ]:
        story.append(b(item))
    story.append(p(
        "Without curriculum learning, if you train on all difficulties simultaneously, "
        "the network tends to focus on easy examples (they are more common and produce lower loss) "
        "and never properly learns the harder ones. Starting easy and progressing forces "
        "the network to master each level before moving on."
    ))

    story.append(h2("5.5 The 80% Replacement Rule"))
    story.append(p(
        "When advancing from depth d to depth d+1, we keep only 20% of the old training data "
        "and generate 100% fresh samples at depth d+1. This 80% replacement rule serves two purposes:"
    ))
    for item in [
        "It keeps the dataset focused on the current difficulty level (the new, harder examples).",
        "The 20% retained from the old data prevents the network from 'forgetting' what it learned "
        "at shallower depths (a problem known as catastrophic forgetting).",
    ]:
        story.append(b(item))
    story.append(note(
        "The dataset for each depth level is saved as a .npz file (a compressed NumPy archive) "
        "in data/datasets/. You can regenerate these files at any time with: "
        "python main.py generate_dataset --max-depth 5 --samples 1000"
    ))

    story += img("fig_04_curriculum_flow.png",
                 caption="Figure 4: Curriculum flow - datasets at each depth level.")

    # ------------------------------------------------------------------ S6
    story += [PageBreak(), h1("6. The Neural Network - The AI Brain"), hr()]

    story.append(p(
        "The neural network is the core of the AI. It takes the 324-number cube state vector "
        "as input and outputs a probability for each of the 18 possible moves. "
        "The move with the highest probability is chosen as the next action."
    ))

    story.append(h2("6.1 What Is an MLP?"))
    story.append(p(
        "<b>MLP</b> stands for <b>Multi-Layer Perceptron</b>. It is one of the oldest and simplest "
        "types of neural network. 'Multi-layer' means it has several layers of artificial neurons "
        "stacked on top of each other. 'Perceptron' refers to the individual artificial neuron."
    ))
    story.append(p(
        "Each neuron in a layer takes in all outputs from the previous layer, multiplies each one "
        "by a <b>weight</b> (a learned number), adds them all together plus a <b>bias</b> "
        "(another learned number), and then passes the result through an <b>activation function</b>. "
        "The weights and biases are the 'knowledge' that the network acquires during training."
    ))

    story.append(h2("6.2 The Network Architecture"))
    story.append(p(
        "The MLP in this project has the following layers:"
    ))
    arch_data = [
        ["Layer", "Neurons", "Activation", "Trainable parameters", "What it does"],
        ["Input",    "324", "none",
         "0",
         "Receives the one-hot cube state vector"],
        ["Hidden 1", "256", "ReLU",
         "324 x 256 + 256 = 83,456",
         "First transformation, extracts low-level patterns"],
        ["Hidden 2", "256", "ReLU",
         "256 x 256 + 256 = 65,792",
         "Second transformation, combines patterns"],
        ["Hidden 3", "128", "ReLU",
         "256 x 128 + 128 = 32,896",
         "Third transformation, distils to key features"],
        ["Output",    "18", "Softmax",
         "128 x 18 + 18 = 2,322",
         "Outputs probability for each of 18 moves"],
        ["Total", "", "", "~184,466 params", ""],
    ]
    story.append(tbl(arch_data, col_widths=[2*cm, 2.2*cm, 1.8*cm, 4.5*cm, 5.5*cm]))
    story.append(sp(6))

    story.append(h2("6.3 What Is ReLU?"))
    story.append(p(
        "<b>ReLU</b> stands for <b>Rectified Linear Unit</b>. It is the activation function "
        "used in all three hidden layers. The formula is:"
    ))
    story.append(code(["ReLU(x) = max(0, x)"]))
    story.append(p(
        "This is extremely simple: if the input is negative, output 0. "
        "If the input is positive, output it unchanged. "
        "Despite its simplicity, ReLU is one of the most important inventions in modern deep learning."
    ))
    story.append(p(
        "<b>Why ReLU and not something else?</b> Before ReLU, sigmoid (S-shaped) and tanh "
        "(hyperbolic tangent) functions were used. These produce very small gradients (slopes) "
        "when their input is very large or very small, which makes learning slow or stops it "
        "entirely (the 'vanishing gradient problem'). ReLU avoids this because its gradient "
        "is always either 0 or 1, never shrinking to near-zero. "
        "It also makes the network's computation faster because max(0, x) is trivial to compute."
    ))

    story.append(h2("6.4 What Is Softmax?"))
    story.append(p(
        "The output layer has 18 neurons, one per possible move. These neurons produce raw "
        "numbers (called <b>logits</b>) that can be any value - positive or negative, small or large. "
        "We need to convert these raw numbers into probabilities (numbers between 0 and 1 that "
        "sum to 1). The <b>softmax</b> function does this:"
    ))
    story.append(code([
        "# For 18 logits z[0], z[1], ..., z[17]:",
        "softmax(z)[k] = exp(z[k]) / sum(exp(z[j]) for j in 0..17)",
    ]))
    story.append(p(
        "The exponential function (exp) ensures all values are positive. Dividing by the sum "
        "of all exponentials makes them add up to 1. The move with the highest logit gets the "
        "highest probability, but all 18 moves get some probability."
    ))
    story.append(p(
        "<b>Why softmax and not just picking the maximum?</b> During training, we need to know "
        "not just whether the network got the answer right, but by how much it was wrong and "
        "in which direction to adjust the weights. The probability distribution gives us this "
        "information through the loss function."
    ))

    story += img("fig_02_mlp_architecture.png",
                 caption="Figure 5: The MLP architecture. Input (324) through three hidden layers to output (18).")

    # ------------------------------------------------------------------ S7
    story += [PageBreak(), h1("7. The Loss Function - How We Measure Mistakes"), hr()]

    story.append(p(
        "During training, the network makes predictions, we compare them to the correct answers, "
        "and we measure how wrong the network was. This measurement is called the <b>loss</b> "
        "(also called the <b>error</b> or <b>cost</b>). We want to minimise the loss."
    ))

    story.append(h2("7.1 Cross-Entropy Loss - Explained Step by Step"))
    story.append(p(
        "The loss function used is <b>cross-entropy loss</b> (also written CE loss). "
        "Here is how it works:"
    ))
    story.append(p(
        "<b>Step 1 - The correct answer:</b> We have a training sample where the expert solver "
        "says 'the correct next move is R' (index 3 in our list of 18 moves). "
        "We represent this as a one-hot vector y:"
    ))
    story.append(code(["y = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"]))
    story.append(p(
        "y[3] = 1 (R is correct), all others are 0."
    ))
    story.append(p(
        "<b>Step 2 - The network's prediction:</b> The network outputs probabilities p "
        "over all 18 moves after applying softmax. For example:"
    ))
    story.append(code([
        "p = [0.02, 0.01, 0.03, 0.65, 0.05, ...]  # sums to 1.0",
        "# p[3] = 0.65 means the network is 65% confident the answer is R",
    ]))
    story.append(p(
        "<b>Step 3 - Compute the loss:</b> The cross-entropy loss formula is:"
    ))
    story.append(code([
        "L = -sum(y[k] * log(p[k]) for k in 0..17)",
        "  = -(y[3] * log(p[3]))    # because all other y[k] = 0",
        "  = -log(0.65)",
        "  = 0.431                  # relatively low loss - good prediction",
    ]))
    story.append(p(
        "If the network had predicted p[3] = 0.05 (only 5% confident about the correct answer), "
        "the loss would be -log(0.05) = 3.0 - much higher, signalling a much worse prediction."
    ))
    story.append(p(
        "<b>Why logarithm?</b> The log function has a special property: log(1) = 0 (perfect "
        "prediction gives zero loss) and log approaches negative infinity as the probability "
        "approaches 0 (being confidently wrong is very severely penalised). "
        "The negative sign turns this into a positive loss (since log of a probability is negative)."
    ))
    story.append(p(
        "<b>In summary:</b> Cross-entropy loss rewards the network for being confident and correct, "
        "and heavily penalises it for being confident and wrong. "
        "Being uncertain (probability around 1/18 = 0.055 for all moves) gives a moderate loss."
    ))
    story.append(p(
        "<b>Implementation note:</b> In PyTorch, we use CrossEntropyLoss which combines the "
        "softmax and the log-loss into one numerically stable operation. We pass the raw logits "
        "(not the softmax output) directly to CrossEntropyLoss during training. "
        "Softmax is only applied explicitly at inference time when we want to read the probabilities."
    ))

    # ------------------------------------------------------------------ S8
    story += [PageBreak(), h1("8. The Optimizer - How the Network Learns"), hr()]

    story.append(p(
        "Once we have the loss, we need to update the network's weights to reduce that loss "
        "in the future. This is done by an <b>optimizer</b>. The optimizer uses the "
        "<b>gradient</b> of the loss with respect to each weight to decide which direction "
        "to push that weight."
    ))

    story.append(h2("8.1 What Is a Gradient?"))
    story.append(p(
        "The gradient tells you the slope: 'if I increase this weight by a tiny amount, "
        "does the loss go up or down, and by how much?' If the gradient for weight w is positive, "
        "increasing w makes the loss worse, so we should decrease w. "
        "If the gradient is negative, we should increase w."
    ))
    story.append(p(
        "The basic update rule (called <b>gradient descent</b>) is:"
    ))
    story.append(code(["w = w - learning_rate * gradient(loss, w)"]))
    story.append(p(
        "The <b>learning rate</b> controls the step size. Too large and the weights jump around "
        "chaotically (divergence). Too small and learning is very slow. "
        "A common value is 0.001."
    ))

    story.append(h2("8.2 Adam Optimizer - Why Not Plain Gradient Descent?"))
    story.append(p(
        "<b>Adam</b> stands for <b>Adaptive Moment Estimation</b>. "
        "It was introduced in 2014 and has become the default optimizer for most deep learning "
        "tasks. Adam improves on plain gradient descent in two ways:"
    ))
    story.append(b(
        "<b>Momentum (beta1 = 0.9):</b> Instead of using just the current gradient, Adam keeps "
        "a running average of past gradients. This 'momentum' smooths out noisy gradient "
        "estimates, making training more stable. Think of it like a ball rolling down a hill - "
        "it does not stop and change direction at every small bump."
    ))
    story.append(b(
        "<b>Adaptive learning rates (beta2 = 0.999):</b> Adam tracks how large the gradients "
        "have been for each weight historically. Weights that have had large gradients get a "
        "smaller effective learning rate; weights with small gradients get a larger one. "
        "This adapts the step size per parameter automatically."
    ))
    story.append(p(
        "The parameters used in this project are:"
    ))
    story.append(code([
        "optimizer = torch.optim.Adam(model.parameters(), lr=0.001,",
        "                             betas=(0.9, 0.999))",
    ]))
    story.append(p(
        "<b>Why Adam and not SGD or others?</b> Adam is a safe default for classification tasks. "
        "It requires minimal hyperparameter tuning (lr=0.001 works well without any adjustment), "
        "it handles sparse gradients well (which arise with one-hot inputs), "
        "and it converges faster than plain stochastic gradient descent (SGD) in most cases."
    ))

    story.append(h2("8.3 Batch Training"))
    story.append(p(
        "Instead of computing the gradient on all training samples at once (which would be slow), "
        "training processes <b>mini-batches</b> of 64 samples at a time. "
        "The gradient from each batch is an approximation of the true gradient, "
        "but it is a good enough approximation and is much faster to compute. "
        "The training data is shuffled before each epoch to ensure each batch is a "
        "random sample of the dataset."
    ))
    story.append(p(
        "<b>Epoch:</b> One complete pass through the entire training dataset. "
        "The project trains for 50 epochs per depth level. "
        "With 1,000 samples and batch size 64, one epoch = 1000/64 = ~16 gradient updates."
    ))

    # ------------------------------------------------------------------ S9
    story += [PageBreak(), h1("9. Training Loop - Curriculum Learning in Detail"), hr()]

    story.append(p(
        "This section explains the full training loop and how all the pieces connect."
    ))

    story.append(h2("9.1 The Full Training Algorithm"))
    story.append(code([
        "for depth d from 1 to max_depth:",
        "    # Generate training data at this depth",
        "    dataset = generate_and_merge(d, samples=1000, keep_old=0.20)",
        "",
        "    # Train for 50 epochs",
        "    for epoch in range(50):",
        "        for batch in shuffle_and_batch(dataset, batch_size=64):",
        "            predictions = model(batch.states)       # forward pass",
        "            loss = CrossEntropy(predictions, batch.labels)",
        "            loss.backward()                         # compute gradients",
        "            optimizer.step()                        # update weights",
        "            optimizer.zero_grad()                   # reset gradients",
        "",
        "    # Gate: test if the model is ready for the next depth",
        "    solve_rate = evaluate(model, depth=d, n_tests=100)",
        "    if solve_rate < 0.80:                          # stopping criterion",
        "        print('Model stuck at depth', d, '- stopping')",
        "        break",
    ]))

    story.append(h2("9.2 The Stopping Criterion - The 80% Solve Rate Gate"))
    story.append(p(
        "After training at each depth level, the model is evaluated on 100 fresh scrambles "
        "at that depth (scrambles not seen during training). If the model cannot solve at least "
        "<b>80% of them</b>, training stops."
    ))
    story.append(p(
        "This is called the <b>solve rate gate</b> or <b>stopping criterion</b>. "
        "It serves as a quality check before advancing to harder examples. "
        "The reasoning is: if the model can only solve 50% of depth-4 scrambles, "
        "exposing it to depth-5 scrambles (which are harder) will just confuse it further. "
        "Better to stop and report what the model has achieved."
    ))
    story.append(p(
        "<b>What counts as 'solved'?</b> The model is given the scrambled cube and a maximum of "
        "50 moves. At each step, it picks the highest-probability move (greedy inference). "
        "If the cube reaches the solved state within 50 moves, it counts as success."
    ))
    story.append(p(
        "<b>Why 80% threshold?</b> 100% would be too strict - perfect performance at depth d "
        "does not guarantee the model will succeed at depth d+1. "
        "A lower threshold like 50% would allow advancement even when the model has barely "
        "learned anything. 80% is a practical balance that ensures solid learning at each level."
    ))

    story.append(h2("9.3 What the Loss Curves Show"))
    story.append(p(
        "If you plot the training loss over time, you will see a distinctive pattern: "
        "the loss drops steadily during training at depth d, then spikes up sharply when "
        "advancing to depth d+1 (because suddenly 80% of the data is harder examples), "
        "then drops again as the model adapts. This spike-and-recover pattern is expected "
        "and normal in curriculum learning."
    ))
    story += img("real_loss_curves.png",
                 caption="Figure 6: Training loss. The spikes occur at each depth transition.")

    # ------------------------------------------------------------------ S10
    story += [PageBreak(), h1("10. Solving with the AI - Inference Strategies"), hr()]

    story.append(p(
        "Once the network is trained, we use it to solve scrambled cubes. "
        "Two strategies are implemented: greedy and beam search."
    ))

    story.append(h2("10.1 Greedy Inference"))
    story.append(p(
        "Greedy inference is the simplest strategy:"
    ))
    for item in [
        "Encode the current cube state as a 324-number vector.",
        "Run it through the MLP to get 18 probabilities.",
        "Pick the move with the highest probability (argmax) - apply it.",
        "Repeat until the cube is solved or 50 moves have been used.",
    ]:
        story.append(b(item))
    story.append(p(
        "Greedy inference is fast (0.4 to 3.4 milliseconds per solve) but has no recovery "
        "mechanism. If it picks the wrong move, it cannot backtrack. "
        "Once a bad move is made, subsequent states may not resemble anything in the training "
        "data, and the solver can get hopelessly lost."
    ))

    story.append(h2("10.2 Beam Search - A Smarter Strategy"))
    story.append(p(
        "<b>Beam search</b> addresses this by keeping multiple candidate solutions alive "
        "at the same time. Instead of always committing to one best move, "
        "it maintains a 'beam' of the top-k most promising partial solutions."
    ))
    story.append(p(
        "Here is how beam search with width k=5 works step by step:"
    ))
    story.append(code([
        "# Initial beam: one candidate (the scrambled cube, no moves yet)",
        "beam = [(score=0.0, moves=[], state=scrambled_cube)]",
        "",
        "for step in range(max_moves=50):",
        "    candidates = []",
        "",
        "    for (score, moves, state) in beam:",
        "        # Get probabilities for all 18 moves from this state",
        "        probs = model.forward(encode(state))",
        "",
        "        # Extend by the top-5 moves from this state",
        "        for move_idx, prob in top_5(probs):",
        "            new_state = apply_move(state, move_idx)",
        "            if new_state in visited:  continue  # skip loops",
        "            new_score = score + log(prob)       # accumulate log-probability",
        "            candidates.append((new_score, moves + [move_idx], new_state))",
        "",
        "    # Keep only the top-k candidates by score",
        "    beam = top_k(candidates, k=5)",
        "",
        "    # Check if any beam reached the solved state",
        "    for (score, moves, state) in beam:",
        "        if state.is_solved():  return moves",
    ]))
    story.append(p(
        "<b>Log-probability scoring:</b> We use the logarithm of probabilities because "
        "multiplying many small probabilities together would produce extremely tiny numbers "
        "that computers cannot represent accurately. "
        "Adding logarithms is equivalent to multiplying the original probabilities "
        "(log(a x b) = log(a) + log(b)), and the numbers stay in a manageable range."
    ))
    story.append(p(
        "<b>Visited state set:</b> The visited set prevents the solver from revisiting the "
        "same cube state twice. Without this, the solver might undo and redo the same moves "
        "in a loop forever."
    ))
    story.append(p(
        "<b>Why is beam search better than greedy?</b> If the greedy best move turns out to "
        "be wrong, greedy has no way to recover. Beam search keeps 4 other candidates alive, "
        "so even if the first-choice path fails, another path in the beam may succeed. "
        "At depth 5, beam search improves solve rate from 77% (greedy) to 89% - a gain of 12 "
        "percentage points."
    ))

    story += img("fig_10_beam_search.png",
                 caption="Figure 7: Beam search with width 5. Each step expands all beams and keeps the best 5.")

    # ------------------------------------------------------------------ S11
    story += [PageBreak(), h1("11. The Web Interface"), hr()]

    story.append(p(
        "The web interface lets you interact with the cube, watch the AI solve it, "
        "and run comparisons - all in a browser, with 3D animation."
    ))

    story.append(h2("11.1 Three.js - 3D Graphics in the Browser"))
    story.append(p(
        "<b>Three.js</b> is a popular JavaScript library for creating 3D graphics in a web "
        "browser using WebGL (a low-level graphics API built into all modern browsers). "
        "It handles the rendering of the 3D cube: the 26 individual cubie meshes "
        "(8 corners + 12 edges + 6 face-centres), the coloured sticker materials, "
        "the camera, lighting, and the animated rotations."
    ))
    story.append(p(
        "Why 26 cubies and not 27? The centre-centre piece (deep inside the cube) is never "
        "visible and is not represented in the model."
    ))

    story.append(h2("11.2 REST API - How the Browser Talks to Python"))
    story.append(p(
        "<b>REST API</b> stands for Representational State Transfer Application Programming Interface. "
        "In plain terms: the browser sends HTTP requests (the same protocol used to load web pages) "
        "to the Python server, and the server responds with data (in JSON format) or performs an action."
    ))
    api_data = [
        ["Endpoint (URL)", "Method", "What it does"],
        ["/state",           "GET",  "Returns the current cube state as a 54-char string"],
        ["/move?m=R",        "POST", "Applies move R to the cube, returns new state"],
        ["/scramble?n=5",    "POST", "Scrambles the cube with n random moves"],
        ["/reset",           "POST", "Returns the cube to the solved state"],
        ["/solve",           "POST", "Solves with BFS and returns the move sequence"],
        ["/solve_ai",        "POST", "Solves with AI greedy and returns move sequence"],
        ["/solve_ai_beam",   "POST", "Solves with beam search and returns move sequence"],
        ["/compare_benchmark","POST","Runs automated comparison, returns statistics"],
    ]
    story.append(tbl(api_data, col_widths=[4.5*cm, 2*cm, 9.5*cm]))
    story.append(sp(6))

    story.append(h2("11.3 How the Animation Works"))
    story.append(p(
        "When the browser receives a sequence of moves from the server (e.g. ['R', 'U', 'R']), "
        "it does not jump immediately to the final state. Instead, it plays each move as an "
        "animation: the affected layer of cubies rotates smoothly over about 300 milliseconds, "
        "then snaps to the exact grid position to prevent floating-point drift. "
        "The animation queue ensures moves are played one at a time in order."
    ))

    # ------------------------------------------------------------------ S12
    story += [PageBreak(), h1("12. Results and Limitations"), hr()]

    story.append(p(
        "The trained model was evaluated on 100 test scrambles per depth. "
        "Here are the results:"
    ))

    solve_data = [
        ["Scramble Depth", "Greedy Rate", "Greedy Avg Moves", "Beam Rate (w=5)", "Beam Avg Moves", "Beam Avg Time"],
        ["1", "100%", "1.0",  "100%", "1.0",  "0.5 ms"],
        ["2", "100%", "2.0",  "100%", "2.0",  "1.0 ms"],
        ["3", "100%", "3.0",  "100%", "3.0",  "4.4 ms"],
        ["4",  "97%", "4.0",   "98%", "4.0",  "7.2 ms"],
        ["5",  "77%", "5.1",   "89%", "5.1", "11.1 ms"],
        ["6",  "31%", "6.1",   "50%", "6.9", "17.9 ms"],
        ["7",  "13%", "7.0",   "23%", "9.6", "30.2 ms"],
        ["8+",  "3%", "8.7",    "9%", "9.6", "varies"],
    ]
    story.append(tbl(solve_data,
                     col_widths=[3*cm, 2.5*cm, 3*cm, 3*cm, 3*cm, 2.5*cm]))
    story.append(sp(6))

    story.append(h2("12.1 What the Results Mean"))
    story.append(b(
        "<b>Depths 1-3 - perfect:</b> The model has effectively memorised the few hundred "
        "distinct cube states reachable at these shallow depths. Both greedy and beam search "
        "always find the solution."
    ))
    story.append(b(
        "<b>Depth 5 - beam search gap:</b> Beam search gives 89% vs greedy's 77%, a 12 "
        "percentage point improvement. This is where beam search earns its extra computation time."
    ))
    story.append(b(
        "<b>Depth 6+ - sharp decline:</b> Performance drops steeply because the model was trained "
        "with only 1,000 samples per depth. At depth 6, there are billions of possible cube states "
        "but only 1,000 training examples - the model has never seen the vast majority of inputs "
        "it encounters during evaluation. More training data would improve this significantly."
    ))

    story.append(h2("12.2 Known Limitations"))
    for item in [
        "<b>BFS solver depth ceiling:</b> The expert solver (bidirectional BFS) times out for "
        "scrambles deeper than about 9 moves. It is NOT the true Kociemba two-phase algorithm "
        "(which handles any depth in milliseconds). The naming in the UI is a simplification.",
        "<b>No symmetry exploitation:</b> The Rubik's Cube has a 48-element symmetry group "
        "(rotations and reflections of the whole cube that produce equivalent states). "
        "The network ignores this - two equivalent states by symmetry get different inputs and "
        "the network has to learn them separately. Exploiting symmetry could improve generalisation.",
        "<b>Single-user server:</b> The Python HTTP server stores the cube state in a global "
        "variable. Multiple browser tabs accessing it simultaneously will interfere with each other.",
        "<b>Greedy loops:</b> Without the beam search visited-state check, greedy inference "
        "can get stuck applying the same move repeatedly. The 50-move hard limit ensures termination.",
    ]:
        story.append(b(item))

    story += img("real_solve_rate_bars.png",
                 caption="Figure 8: Solve rates by depth. Beam search consistently outperforms greedy.")

    # ------------------------------------------------------------------ S13
    story += [PageBreak(), h1("13. Project File Structure"), hr()]

    struct_data = [
        ["Path", "What it contains"],
        ["core/cube.py",
         "CubieCube class: state arrays, apply_move(), is_solved(), is_legal()"],
        ["core/moves.py",
         "All 18 move definitions (permutation + orientation-delta tables)"],
        ["core/state_encoder.py",
         "One-hot encoder: cube state -> 324-dim float32 vector"],
        ["solvers/kociemba_solver.py",
         "Bidirectional BFS expert solver (training oracle + web UI)"],
        ["solvers/ai_solver.py",
         "RubiksMLP definition, training loop, greedy solve, beam search"],
        ["data/dataset_generator.py",
         "Curriculum dataset generation with 80% replacement rule"],
        ["data/datasets/",
         "Pre-generated .npz dataset files (depth 1-8 + latest)"],
        ["data/models/ai_solver.pt",
         "Pre-trained MLP weights (ready to use, no training needed)"],
        ["visualization/server.py",
         "Python HTTP server + REST API endpoints"],
        ["visualization/index.html",
         "Three.js 3D frontend (self-contained single-page app)"],
        ["experiments/",
         "Benchmarking and ablation experiment scripts"],
        ["docs/figures/",
         "All figures used in the thesis and documentation"],
        ["main.py",
         "CLI entry point for all commands (train, visualize, compare, etc.)"],
        ["train_on_colab.ipynb",
         "Jupyter notebook for GPU-accelerated training on Google Colab"],
        ["requirements.txt",
         "All Python library dependencies"],
    ]
    story.append(tbl(struct_data, col_widths=[5.5*cm, 10.5*cm]))

    # ------------------------------------------------------------------ S14
    story += [PageBreak(), h1("14. Glossary - All Abbreviations Explained"), hr()]

    glossary = [
        ("Adam", "Adaptive Moment Estimation. An optimization algorithm for training neural "
         "networks. Combines momentum (averaging past gradients) with adaptive learning "
         "rates (adjusting the step size per weight). Parameters: lr=0.001, beta1=0.9, beta2=0.999."),

        ("BFS", "Breadth-First Search. A graph search algorithm that explores all states "
         "reachable in 1 step, then 2 steps, etc. Guaranteed to find the shortest path "
         "but exponentially slow for deep searches."),

        ("CE", "Cross-Entropy. The loss function used for multi-class classification. "
         "Measures how wrong the predicted probability distribution is relative to the "
         "true one-hot target. Formula: L = -sum(y_k * log(p_k))."),

        ("CLI", "Command-Line Interface. A text-based way of interacting with a program "
         "by typing commands in a terminal. Example: python main.py train --epochs 50."),

        ("CPU", "Central Processing Unit. The main processor of a computer. "
         "Adequate for training this small model; a GPU would be 10-50x faster."),

        ("GPU", "Graphics Processing Unit. A processor originally designed for graphics "
         "that is also very efficient for matrix multiplications used in neural network training."),

        ("HTM", "Half-Turn Metric. A convention where each quarter-turn and half-turn "
         "(90 or 180 degrees) counts as 1 move. Gives 18 distinct move types."),

        ("HTTP", "HyperText Transfer Protocol. The protocol used by web browsers to "
         "communicate with servers. The web interface uses HTTP to send move commands "
         "and receive cube state updates."),

        ("JSON", "JavaScript Object Notation. A text format for representing structured data. "
         "The server and browser exchange data in JSON format."),

        ("lr", "Learning Rate. Controls how large the weight update steps are during training. "
         "Set to 0.001 in this project."),

        ("MLP", "Multi-Layer Perceptron. A type of neural network with fully connected layers. "
         "Input -> Hidden layers -> Output. The AI model in this project is an MLP."),

        ("npz", "NumPy compressed archive format. A file that stores multiple NumPy arrays "
         "in a single compressed file. Used to store training datasets."),

        ("pt", "PyTorch file extension for saved model weights. Created with torch.save(), "
         "loaded with torch.load()."),

        ("ReLU", "Rectified Linear Unit. Activation function: ReLU(x) = max(0, x). "
         "Used in all three hidden layers. Avoids vanishing gradients."),

        ("REST", "Representational State Transfer. An architecture style for web APIs "
         "where actions are represented as HTTP requests to specific URL endpoints."),

        ("QTM", "Quarter-Turn Metric. Alternative to HTM where R2 counts as 2 moves. "
         "God's Number under QTM is 26. This project uses HTM."),

        ("SGD", "Stochastic Gradient Descent. A simpler optimizer than Adam that updates "
         "weights using only the current batch's gradient. Not used in this project "
         "(Adam is used instead)."),

        ("Softmax", "A function that converts a vector of raw numbers into a probability "
         "distribution (values between 0 and 1 that sum to 1). Applied to the network's "
         "output layer at inference time."),

        ("WebGL", "Web Graphics Library. A browser API for rendering 3D graphics using "
         "the GPU. Three.js uses WebGL under the hood."),
    ]

    for term, explanation in glossary:
        story += defn(term, explanation)
        story.append(sp(2))

    # ------------------------------------------------------------------ S15
    story += [PageBreak(), h1("15. Quick Reference"), hr()]
    story.append(p("Copy-paste commands for common tasks:"))
    story.append(code([
        "# Install all dependencies",
        "pip install -r requirements.txt",
        "",
        "# Start the web simulation (then open http://localhost:8080)",
        "python main.py visualize --web",
        "",
        "# Validate the cube engine (checks 7 mathematical properties)",
        "python main.py validate",
        "",
        "# Print a random 20-move scramble sequence",
        "python main.py scramble -l 20",
        "",
        "# Generate training datasets for depths 1 to 5",
        "python main.py generate_dataset --max-depth 5 --samples 1000",
        "",
        "# Train the AI model (curriculum learning, depths 1-5)",
        "python main.py train --max-depth 5 --epochs 50 --threshold 0.80",
        "",
        "# Benchmark AI vs expert solver (100 tests per depth)",
        "python main.py compare --max-depth 5 --num-tests 100",
        "",
        "# Custom server port",
        "python main.py visualize --web --port 9000",
        "",
        "# GPU training via Google Colab",
        "# Open train_on_colab.ipynb and run all cells",
    ]))

    story.append(sp(20))
    story.append(hr())
    story.append(Paragraph(
        "Edward Ogbei | PCZ M.Sc. Artificial Intelligence | 2026",
        ST["Caption"]
    ))

    doc.build(story)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    build()
