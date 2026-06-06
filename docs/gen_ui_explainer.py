"""
gen_ui_explainer.py - Web UI explainer, project limitations, and project importance.
Run: python docs/gen_ui_explainer.py
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
SCRS = os.path.join(ROOT, "docs", "figures")
OUT  = os.path.join(ROOT, "docs", "UI_Explainer.pdf")

NAVY  = colors.HexColor("#0d1b4b")
BLUE  = colors.HexColor("#1a3a8f")
STEEL = colors.HexColor("#3a5aaa")
DARK  = colors.HexColor("#1a1a2e")
GRAY  = colors.HexColor("#555577")
LGRAY = colors.HexColor("#f0f0fa")
GREEN = colors.HexColor("#1a6a40")
RED   = colors.HexColor("#8a2222")
STRIP = colors.HexColor("#e8ecf8")


def _styles():
    def s(name, **kw):
        return ParagraphStyle(name, **kw)
    return {
        "Title":    s("Title",   fontName="Helvetica-Bold",   fontSize=22,
                      leading=28, spaceAfter=8,  alignment=TA_CENTER, textColor=NAVY),
        "Subtitle": s("Sub",     fontName="Helvetica",         fontSize=12,
                      leading=17, spaceAfter=20, alignment=TA_CENTER, textColor=GRAY),
        "H1":       s("H1",      fontName="Helvetica-Bold",   fontSize=15,
                      leading=21, spaceAfter=6,  spaceBefore=20, textColor=NAVY),
        "H2":       s("H2",      fontName="Helvetica-Bold",   fontSize=12,
                      leading=17, spaceAfter=4,  spaceBefore=12, textColor=BLUE),
        "H3":       s("H3",      fontName="Helvetica-BoldOblique", fontSize=11,
                      leading=16, spaceAfter=3,  spaceBefore=8,  textColor=STEEL),
        "Body":     s("Body",    fontName="Helvetica",         fontSize=11,
                      leading=17, spaceAfter=8,  alignment=TA_JUSTIFY),
        "Bullet":   s("Bullet",  fontName="Helvetica",         fontSize=11,
                      leading=16, spaceAfter=4,  leftIndent=16),
        "Good":     s("Good",    fontName="Helvetica",         fontSize=11,
                      leading=16, spaceAfter=4,  leftIndent=16, textColor=GREEN),
        "Bad":      s("Bad",     fontName="Helvetica",         fontSize=11,
                      leading=16, spaceAfter=4,  leftIndent=16, textColor=RED),
        "Code":     s("Code",    fontName="Courier",           fontSize=9,
                      leading=13, spaceAfter=6,  spaceBefore=4,
                      backColor=colors.HexColor("#f4f4f8"),
                      leftIndent=14, rightIndent=14,
                      borderPadding=(4, 4, 4, 4), textColor=DARK),
        "Note":     s("Note",    fontName="Helvetica-Oblique", fontSize=10,
                      leading=14, spaceAfter=6,  textColor=GRAY,
                      leftIndent=14, rightIndent=14),
        "Caption":  s("Cap",     fontName="Helvetica-Oblique", fontSize=9,
                      leading=13, spaceAfter=10, alignment=TA_CENTER, textColor=GRAY),
    }


ST = _styles()


def hr():
    return HRFlowable(width="100%", thickness=0.6,
                      color=colors.HexColor("#aaaacc"), spaceAfter=6)


def h1(t):  return Paragraph(t, ST["H1"])
def h2(t):  return Paragraph(t, ST["H2"])
def h3(t):  return Paragraph(t, ST["H3"])
def p(t):   return Paragraph(t, ST["Body"])
def b(t):   return Paragraph(f"- {t}", ST["Bullet"])
def good(t):return Paragraph(f"✓ {t}", ST["Good"])
def bad(t): return Paragraph(f"✗ {t}", ST["Bad"])
def note(t):return Paragraph(f"<i>Note: {t}</i>", ST["Note"])
def sp(h=8):return Spacer(1, h)


def code(lines):
    if isinstance(lines, list):
        joined = "<br/>".join(l.replace(" ", "&nbsp;") for l in lines)
    else:
        joined = lines.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(joined, ST["Code"])


def img(fname, width=14*cm, caption=None):
    path = os.path.join(SCRS, fname)
    items = []
    if os.path.exists(path):
        items.append(Image(path, width=width, height=width*0.62))
    if caption:
        items.append(Paragraph(caption, ST["Caption"]))
    return items


def tbl(data, col_widths=None):
    if col_widths is None:
        col_widths = [4*cm] * len(data[0])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  10),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
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

def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        title="AI Rubik's Cube Solver - Web UI Explainer",
        author="Edward Ogbei",
    )

    story = []

    # Cover
    story += [
        sp(50),
        Paragraph("AI-Based Optimal Solver for the 3x3 Rubik's Cube", ST["Title"]),
        sp(10),
        Paragraph("Web Interface Explained, Project Limitations, and Why It Matters",
                  ST["Subtitle"]),
        hr(),
        Paragraph("Edward Ogbei | M.Sc. Artificial Intelligence | PCZ 2026",
                  ST["Subtitle"]),
        PageBreak(),
    ]

    # ---------------------------------------------------------------- SECTION 1
    story += [h1("1. The Web Control Panel - Explained in Detail"), hr()]

    story.append(p(
        "The screenshot below shows the right-side control panel of the web interface "
        "(http://localhost:8080). This panel communicates with the Python HTTP server "
        "via REST API calls - each button click sends an HTTP POST request to a specific "
        "endpoint on the local server."
    ))

    story += img("screenshot_08_ui_wide.png",
                 caption="Figure 1: The full web interface. Left: Three.js 3D cube. Right: control panel.")

    # --- ACTIONS section
    story.append(h2("1.1 ACTIONS - The Six Buttons"))
    story.append(p(
        "These buttons trigger operations on the cube. Each sends an HTTP request to "
        "the Python server (visualization/server.py), which updates the global cube state "
        "and returns a response."
    ))

    actions_data = [
        ["Button", "Endpoint called", "What it does"],
        ["Scramble (20)", "POST /scramble?n=20",
         "Applies 20 random legal moves. Each move is chosen randomly from the 18 HTM "
         "moves, with the constraint that no move immediately undoes the previous one. "
         "Result: a deeply scrambled cube that the AI cannot reliably solve."],
        ["Scramble (5)", "POST /scramble?n=5",
         "Applies 5 random moves - a shallow scramble well within the AI's reliable range "
         "(depths 1-5 show 77-100% solve rate). Good for demonstrating AI success."],
        ["Reset", "POST /reset",
         "Returns the cube instantly to the solved state (cp=[0..7], co=[0]*8, "
         "ep=[0..11], eo=[0]*12). No animation plays - the state jumps directly. "
         "The Three.js frontend then calls /state and re-renders all 26 cubies."],
        ["Solve (Kociemba Expert)", "POST /solve",
         "Runs the bidirectional BFS solver on the current cube state. "
         "Returns the optimal move sequence. The browser then plays each move as an animation. "
         "Reliable for scrambles up to depth 9. Named 'Kociemba' as shorthand for 'expert solver'."],
        ["AI Greedy", "POST /solve_ai",
         "Runs greedy inference: the MLP outputs move probabilities, the argmax is applied, "
         "repeat until solved or 50-move limit reached. Fast (2-5 ms) but no recovery from mistakes."],
        ["AI Beam Search (w=5)", "POST /solve_ai_beam",
         "Runs beam search with width 5: keeps 5 candidate solution paths alive at each step. "
         "Slower (5-55 ms) but significantly better than greedy at depths 4-7."],
    ]
    story.append(tbl(actions_data, col_widths=[3.5*cm, 3.5*cm, 9*cm]))
    story.append(sp(6))

    # --- Animation speed
    story.append(h2("1.2 Animation Speed Dropdown"))
    story.append(p(
        "Controls how fast each move animates in the Three.js 3D view. The options correspond "
        "to different durations for the layer-rotation animation:"
    ))
    for item in [
        "<b>Slow</b>: ~600 ms per move - good for explaining a solution step by step.",
        "<b>Normal</b>: ~300 ms per move - the default, smooth and watchable.",
        "<b>Fast</b>: ~100 ms per move - useful when running the benchmark with many moves.",
        "<b>Instant</b>: 0 ms - moves snap immediately, no animation played.",
    ]:
        story.append(b(item))
    story.append(p(
        "The animation queue ensures moves are always played in order, even when a solution "
        "of 8 or 10 moves is returned - the browser does not jump ahead."
    ))

    # --- STATUS
    story.append(h2("1.3 STATUS Panel"))
    story.append(p(
        "This panel shows the current state of the cube on the server. It is updated "
        "after every action by calling GET /state."
    ))
    status_data = [
        ["Field", "What it shows", "What it means"],
        ["State", "'Solved' or 'Scrambled'",
         "Whether the cube's current cp/co/ep/eo arrays match the solved configuration."],
        ["Legal", "'Yes' or 'No'",
         "Result of is_legal(). Checks: sum(co)%3=0, sum(eo)%2=0, parity match. "
         "Should always be 'Yes' for cubes modified through the UI."],
        ["Corners: Sum mod 3", "0 (always valid)",
         "The corner orientation invariant. If this showed a non-zero value, "
         "the cube would be in an unsolvable state."],
        ["Edges: Sum mod 2", "0 (always valid)",
         "The edge orientation invariant. Same principle as the corner one."],
    ]
    story.append(tbl(status_data, col_widths=[3.5*cm, 3.5*cm, 9*cm]))
    story.append(sp(6))

    # --- SOLUTION
    story.append(h2("1.4 SOLUTION Box"))
    story.append(p(
        "Displays the move sequence returned by the last solve call. Examples:"
    ))
    story.append(code([
        "Cube reset to solved state.       <- after Reset",
        "Solution: R U' F2 D R' L2 U      <- after BFS solve (7 moves)",
        "AI solved in 9 moves: R U R' U' F D' U2 R L  <- after AI Greedy",
        "Beam search: no solution found.   <- AI beam search failed (depth 8+)",
    ]))
    story.append(p(
        "When a solution is found, the browser automatically animates each move from the "
        "sequence in order at the selected animation speed."
    ))

    # --- MOVE HISTORY
    story.append(h2("1.5 MOVE HISTORY"))
    story.append(p(
        "A running log of every move applied to the cube since the last Reset. "
        "Maintained entirely on the client side (browser JavaScript). "
        "Useful for manually tracking what was done to the cube. "
        "In the screenshot showing 'U R' F'', three moves were applied manually: "
        "U (Up face 90 degrees clockwise), R' (Right face counter-clockwise), "
        "F' (Front face counter-clockwise)."
    ))

    # --- BENCHMARK
    story.append(h2("1.6 BENCHMARK RESULTS Table - Reading the Numbers"))
    story.append(p(
        "Clicking 'Run Benchmark Comparison' calls POST /compare_benchmark. "
        "The server runs N test scrambles (default 5) at each depth (1 through 5), "
        "tests both the AI greedy solver and the BFS expert solver on each, "
        "and returns a comparison table."
    ))

    bench_data = [
        ["Column", "Meaning"],
        ["Depth",     "Scramble depth: exactly how many random moves were applied."],
        ["AI %",      "Percentage of test scrambles the AI greedy solver solved within 50 moves."],
        ["Koc %",     "Percentage solved by the BFS (Kociemba) expert solver."],
        ["AI Time",   "Average time taken by the AI to produce a solution (in seconds)."],
        ["Koc Time",  "Average time taken by the BFS solver (in seconds)."],
    ]
    story.append(tbl(bench_data, col_widths=[3*cm, 13*cm]))
    story.append(sp(6))

    story.append(p(
        "<b>Reading the screenshot benchmark results:</b>"
    ))
    for item in [
        "<b>Depths 1-4 (AI 100%, Koc 100%)</b>: Both solvers work perfectly. "
        "At these shallow depths, the AI has learned the state space well during training.",
        "<b>Depth 5 (AI 80%, Koc 100%)</b>: The AI fails on 1 out of 5 tests - the model "
        "has a known ~77-89% success rate at depth 5. The BFS expert always succeeds.",
        "<b>AI times faster than Koc at depth 3-4</b>: The AI is just a matrix multiplication "
        "(fixed cost, ~2-5 ms). The BFS grows exponentially with depth. At depth 3-4, "
        "BFS is slow enough that AI becomes faster, even though AI takes more moves.",
        "<b>Koc 0.0459s at depth 5</b>: BFS at depth 5 explores ~15^5 = 759,375 states. "
        "Still fast overall, but noticeably slower than the AI's fixed 4.7 ms.",
    ]:
        story.append(b(item))

    story += img("screenshot_07_benchmark.png",
                 caption="Figure 2: Benchmark results panel showing AI vs Kociemba comparison.")

    # ---------------------------------------------------------------- SECTION 2
    story += [PageBreak(), h1("2. Known Limitations of the System"), hr()]

    story.append(p(
        "This section documents the known limitations honestly - what the system cannot do, "
        "where it is unreliable, and what would need to change to address each issue."
    ))

    # --- 2.1
    story.append(h2("2.1 The AI Cannot Solve Most Real Scrambles"))
    story.append(p(
        "A real 'scramble' in competitive speedcubing uses 20-25 moves. The AI's solve rate "
        "drops dramatically beyond depth 5:"
    ))

    solve_data = [
        ["Scramble Depth", "Greedy Solve Rate", "Beam (w=5) Rate", "Verdict"],
        ["1 - 3",  "100%",  "100%",  "Perfect - fully reliable"],
        ["4",       "97%",   "98%",  "Near-perfect"],
        ["5",       "77%",   "89%",  "Mostly reliable - use beam search"],
        ["6",       "31%",   "50%",  "Unreliable - coin flip"],
        ["7",       "13%",   "23%",  "Mostly fails"],
        ["8+",      "~3%",   "~9%",  "Almost always fails"],
        ["20 (real scramble)", "~0%", "~0%", "Cannot solve"],
    ]
    story.append(tbl(solve_data, col_widths=[4*cm, 3.5*cm, 3.5*cm, 5*cm]))
    story.append(sp(6))

    story.append(p(
        "<b>Root cause:</b> The model was trained with only 1,000 samples per depth level. "
        "At depth 6, the cube state space has billions of states; 1,000 samples covers "
        "an infinitesimally small fraction. The model encounters states at test time that "
        "bear no resemblance to anything it saw during training. "
        "Training with 50,000-100,000 samples per depth would significantly extend "
        "the reliable range."
    ))

    # --- 2.2
    story.append(h2("2.2 The Expert Solver Is Not True Kociemba"))
    story.append(p(
        "The UI labels the BFS solver as 'Kociemba Expert' - this is a simplification. "
        "The true Kociemba two-phase algorithm uses IDA* search with precomputed pruning tables "
        "and solves any scramble (up to God's Number = 20) in under 1 millisecond. "
        "The bidirectional BFS used here is exponential in depth and times out at roughly 9-10 moves."
    ))
    for item in [
        "Try 'Solve (Kociemba Expert)' after a 20-move scramble - it will return no solution.",
        "For scrambles of depth 6+, the BFS may take several seconds before timing out.",
        "The timeout is set to 30 seconds per solve attempt.",
    ]:
        story.append(bad(item))

    # --- 2.3
    story.append(h2("2.3 Single-User Server"))
    story.append(p(
        "The Python HTTP server stores the cube state as a single global variable (_cube). "
        "If two browser tabs are open simultaneously, they share the same cube state "
        "and will interfere with each other's actions. "
        "Opening Tab A and Tab B then clicking 'Scramble' in Tab A will affect what Tab B sees."
    ))
    story.append(p(
        "<b>Fix (not implemented):</b> Use per-session state with Flask's session mechanism, "
        "or make the API stateless (client sends full cube state with each request)."
    ))

    # --- 2.4
    story.append(h2("2.4 No Symmetry Exploitation"))
    story.append(p(
        "The Rubik's Cube has a 48-element symmetry group (24 rotations + 24 reflections). "
        "Two cube states related by a whole-cube rotation look physically identical but "
        "produce completely different 324-dimensional input vectors. "
        "The neural network treats them as unrelated states and must learn each separately."
    ))
    story.append(p(
        "<b>Impact:</b> The effective training data is 48x smaller than it could be. "
        "Augmenting each training scramble with all 48 equivalent orientations would "
        "give the same generalization as 48x more training data at zero extra computation cost."
    ))

    # --- 2.5
    story.append(h2("2.5 Greedy Solver Can Loop"))
    story.append(p(
        "The greedy solver has no memory of previously visited states. "
        "If the model repeatedly recommends move R for a given state, and applying R "
        "returns to the same state (which the model again classifies as 'apply R'), "
        "the solver loops until the 50-move limit terminates it. "
        "The 50-move limit is a safety measure, not a feature."
    ))
    story.append(p(
        "Beam search avoids this entirely: the visited-state set prevents any state "
        "from appearing in the beam twice."
    ))

    # --- 2.6
    story.append(h2("2.6 Solution Is Not Optimal"))
    story.append(p(
        "Neither the greedy solver nor the beam search guarantees an optimal (shortest) solution. "
        "The AI often takes more moves than the scramble depth:"
    ))
    for item in [
        "A depth-5 scramble might be solved in 7 or 8 AI moves instead of 5.",
        "A depth-7 scramble solved by beam search typically uses 9-10 moves.",
        "Only the BFS expert solver finds optimal solutions (for depths it can handle).",
    ]:
        story.append(b(item))

    # --- 2.7
    story.append(h2("2.7 CPU-Only Training Is Slow"))
    story.append(p(
        "Training to depth 5 on a laptop CPU takes approximately 30-60 minutes. "
        "Training to depth 8 can take 4-8 hours. "
        "The Google Colab notebook (train_on_colab.ipynb) uses a GPU and reduces this "
        "to 5-15 minutes for depth 5 and ~1 hour for depth 8."
    ))

    # ---------------------------------------------------------------- SECTION 3
    story += [PageBreak(), h1("3. Why This Kind of Project Matters"), hr()]

    story.append(p(
        "At first glance, teaching an AI to solve a toy puzzle might seem like an academic "
        "curiosity. But the Rubik's Cube problem is a microcosm of some of the most important "
        "challenges in modern AI and computer science. Here is why it matters."
    ))

    # --- 3.1
    story.append(h2("3.1 Combinatorial Explosion Is Everywhere"))
    story.append(p(
        "The cube's 43 quintillion states is a concrete, tangible example of combinatorial "
        "explosion - the phenomenon where the number of possible states grows so fast that "
        "exhaustive search becomes impossible. This problem appears constantly in real-world AI:"
    ))
    for item in [
        "<b>Logistics and routing:</b> Finding the optimal delivery route for 20 packages "
        "involves 20! = 2.4 quintillion possibilities. AI must find near-optimal solutions without "
        "checking all of them.",
        "<b>Protein folding:</b> A protein with 100 amino acids has an astronomically large "
        "space of possible conformations. AlphaFold2 uses neural networks to navigate this space.",
        "<b>Chess and Go:</b> Chess has ~10^120 possible game states; Go has ~10^170. "
        "No computer can search more than a tiny fraction. Neural networks (like AlphaGo) "
        "learn to evaluate positions and guide search efficiently.",
        "<b>Drug discovery:</b> The space of possible drug molecules is estimated at 10^60. "
        "AI models guide the search toward promising candidates.",
    ]:
        story.append(b(item))
    story.append(p(
        "The Rubik's Cube is a toy problem at 10^19 states, but the techniques developed "
        "for it - imitation learning, curriculum training, beam search guided by a neural "
        "network - directly translate to these larger problems."
    ))

    # --- 3.2
    story.append(h2("3.2 Imitation Learning Is a Fundamental AI Technique"))
    story.append(p(
        "This project uses <b>imitation learning</b>: train an AI by having it copy an expert. "
        "This is one of the most powerful and practical techniques in modern AI:"
    ))
    for item in [
        "<b>Autonomous driving:</b> Early self-driving cars were trained by recording human "
        "drivers and having the AI imitate their steering and braking decisions.",
        "<b>Large language models:</b> GPT and Claude were first trained to predict the next "
        "token in human-written text - essentially imitating human writing.",
        "<b>Robot manipulation:</b> Robots learn to pick and place objects by imitating "
        "human demonstrations captured with motion-capture suits.",
        "<b>Game playing:</b> AlphaGo started with imitation learning (copying human Go moves) "
        "before using reinforcement learning to surpass human performance.",
    ]:
        story.append(b(item))
    story.append(p(
        "The Rubik's Cube project demonstrates the full imitation learning pipeline: "
        "expert solver generates demonstrations, neural network learns to predict expert actions, "
        "curriculum learning makes the training tractable."
    ))

    # --- 3.3
    story.append(h2("3.3 Curriculum Learning Solves a Real Problem in AI Training"))
    story.append(p(
        "Training on hard examples from the start often fails: the AI gets overwhelmed, "
        "the gradient signal is too noisy, and learning stalls. "
        "Curriculum learning - starting easy and gradually increasing difficulty - "
        "is a principled solution that mirrors how humans and animals learn."
    ))
    story.append(p(
        "This principle now appears in many state-of-the-art AI systems:"
    ))
    for item in [
        "<b>Language model training:</b> Modern LLMs are often fine-tuned progressively - "
        "first on simple instruction-following, then on complex reasoning tasks.",
        "<b>Reinforcement learning:</b> DeepMind's MuJoCo robots learn to walk before "
        "they learn to run, and simple terrains before complex ones.",
        "<b>Math problem solving:</b> AI math tutors sequence problems by difficulty, "
        "using a solve-rate gate (similar to the 80% threshold here) to decide when a "
        "student is ready for harder material.",
    ]:
        story.append(b(item))

    # --- 3.4
    story.append(h2("3.4 Neural-Guided Search Is the Engine Behind Modern AI"))
    story.append(p(
        "The beam search in this project is a simple version of <b>neural-guided search</b>: "
        "use a neural network to evaluate which paths are most promising, "
        "then explore those paths preferentially. "
        "This combination of classical search algorithms with neural network guidance "
        "is at the heart of the most powerful AI systems ever built:"
    ))
    for item in [
        "<b>AlphaGo / AlphaZero:</b> Monte Carlo Tree Search guided by a policy network "
        "(which move to try next) and a value network (how good is this position). "
        "Defeated the world champion Go player in 2016.",
        "<b>AlphaFold2:</b> Iterative refinement of protein structure guided by "
        "attention-based neural networks that evaluate structural plausibility.",
        "<b>OpenAI o1 / o3:</b> Language models that perform extended 'chain-of-thought' "
        "reasoning by exploring multiple reasoning paths and selecting the best.",
        "<b>Theorem proving:</b> AI systems like Lean-Copilot use neural networks to "
        "guide proof search through exponentially large spaces of possible proof steps.",
    ]:
        story.append(b(item))

    # --- 3.5
    story.append(h2("3.5 The Cube as a Benchmark for AI Progress"))
    story.append(p(
        "The Rubik's Cube has been used as a benchmark problem in AI research for decades. "
        "Key milestones include:"
    ))
    milestone_data = [
        ["Year", "Achievement"],
        ["1981", "First computer program to solve any Rubik's Cube (brute force, very slow)"],
        ["1997", "First optimal solver (Kociemba two-phase algorithm, milliseconds on any state)"],
        ["2019", "OpenAI's 'Solving Rubik's Cube with a Robot Hand': RL + domain randomization, "
         "solved by a physical robotic hand"],
        ["2019", "DeepCubeA: deep reinforcement learning, learns to solve in near-optimal moves "
         "without any human demonstrations"],
        ["2026", "This project: imitation learning + curriculum training + beam search, "
         "interactive web demo, open-source educational implementation"],
    ]
    story.append(tbl(milestone_data, col_widths=[2*cm, 14*cm]))
    story.append(sp(6))

    story.append(p(
        "This project sits at the educational and accessible end of that timeline. "
        "It demonstrates the core principles (imitation learning, curriculum training, "
        "neural search) in a system small enough to train on a laptop in under an hour, "
        "inspect in a browser, and understand completely by reading the source code."
    ))

    # --- 3.6
    story.append(h2("3.6 Group Theory in Computer Science"))
    story.append(p(
        "The Rubik's Cube is a direct application of <b>group theory</b> - a branch of "
        "abstract algebra that studies mathematical structures where elements can be "
        "combined (composed). The cube's moves form a group:"
    ))
    for item in [
        "<b>Closure</b>: applying any two moves gives another valid move.",
        "<b>Identity</b>: the 'do nothing' operation is the solved state.",
        "<b>Inverses</b>: every move has an inverse (R and R' cancel each other).",
        "<b>Associativity</b>: (R then U) then F = R then (U then F).",
    ]:
        story.append(b(item))
    story.append(p(
        "Group theory is not just a curiosity - it underlies modern cryptography "
        "(RSA and elliptic curve cryptography both rely on group structure), "
        "physics (the Standard Model of particle physics is described by symmetry groups), "
        "and computer graphics (rotation groups define how 3D objects transform). "
        "The Rubik's Cube provides an intuitive, hands-on way to encounter these ideas."
    ))

    # --- 3.7
    story.append(h2("3.7 Educational Value"))
    story.append(p(
        "This project spans multiple disciplines in a single coherent system:"
    ))
    for item, color in [
        ("Abstract algebra / group theory (cube representation, move composition)", NAVY),
        ("Combinatorics (state space size, invariants, legality constraints)", NAVY),
        ("Machine learning (MLP, imitation learning, curriculum training, loss functions)", BLUE),
        ("Search algorithms (BFS, bidirectional BFS, beam search)", BLUE),
        ("Software engineering (REST API, client-server architecture, 3D rendering)", STEEL),
        ("Data engineering (dataset generation, curriculum scheduling, .npz format)", STEEL),
    ]:
        story.append(Paragraph(f"- {item}", ParagraphStyle(
            "tinted", fontName="Helvetica", fontSize=11, leading=16,
            spaceAfter=4, leftIndent=16, textColor=color
        )))

    story.append(p(
        "A student who understands this project from top to bottom has touched "
        "real concepts from six different fields of study. "
        "That is the most important thing this kind of project delivers."
    ))

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
