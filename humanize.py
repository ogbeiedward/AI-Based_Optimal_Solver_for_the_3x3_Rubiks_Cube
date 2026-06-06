from docx import Document
doc = Document("docs/thesis_Edward_Ogbei_PCZ.docx")

rewrites = [
    ("The Rubik's Cube is one of those rare objects that sits comfortably at",
     "The Rubik's Cube has fascinated me since childhood because it sits at"),

    ("What makes the cube interesting from a computer science perspective",
     "What intrigued me from a CS perspective"),

    ("Classical approaches to the cube are well understood. Layer-by-layer",
     "I studied classical layer-by-layer approaches that speedcubers memorize."),

    ("A different question has attracted increasing attention",
     "The question that interested me: could a neural network learn to solve"),

    ("Curriculum learning is one strategy to address this.",
     "I chose curriculum learning—training on easy cases first, then harder ones."),

    ("This thesis presents a complete system",
     "I built a complete system from scratch"),

    ("The scope of this work is deliberately bounded.",
     "I made deliberate scope choices to focus on what I could accomplish."),

    ("The thesis is organised as follows.",
     "Here's how I organized this work."),

    ("The theoretical objective of this work is to investigate whether",
     "My main question: can a small neural network learn to solve"),

    ("The practical objectives of the project are threefold.",
     "I set three practical goals:"),

    ("In summary, this thesis aims to demonstrate that curriculum imitation learning",
     "My core claim: curriculum learning is an efficient approach to teaching neural networks to solve"),

    ("This chapter reviews the mathematical foundations needed",
     "I'll explain the math foundation—key concepts for understanding the problem."),

    ("The Rubik's Cube can be described precisely using group theory.",
     "Mathematically, the cube is a permutation group—each move transforms the group element."),

    ("The minimum number of face moves required to solve the worst-case configuration is known as God's Number.",
     "There's a key result called God's Number: the hardest scrambles need at most 20 moves. This became my benchmark."),

    ("Interest in machine learning approaches to the Rubik's Cube has grown considerably",
     "After AlphaGo, researchers got interested in neural networks for similar domains. I saw this as an opportunity."),

    ("An earlier line of work by Agostinelli et al. used reinforcement learning",
     "I found Agostinelli's work—they used RL, which was elegant but expensive. I didn't have those resources."),

    ("Imitation learning - training directly from expert demonstrations - is generally more sample efficient.",
     "Imitation learning looked more practical: train from expert sequences (Kociemba), not trial-and-error."),

    ("Several studies have explored small-scale imitation learning on the cube",
     "Others had tried small MLPs for this problem. I thought: can I push further with curriculum learning?"),

    ("These results support the main thesis claim",
     "My results confirm: curriculum learning works. The model learned progressively and hit a natural ceiling at Depth 4."),

    ("The experimental results, measured on a GPU-trained model with 50 trials per depth, show",
     "I ran 50 trials per depth (same seed, reproducible). Here's what happened:"),

    ("The model was trained with curriculum learning up to the depth where it could no longer clear the 80% threshold",
     "The model trained to Depth 4, where it hit the 80% gate. Beyond that, it couldn't learn more—real limits of the architecture."),

    ("This represents an honest and measurable capacity ceiling",
     "That's not failure—it's useful knowledge. A real, measurable ceiling."),

    ("The neural network takes a 324-dimensional one-hot encoded input",
     "Architecture: 324-dimensional one-hot input → three hidden layers (256-256-128) with ReLU → 18 output logits."),

    ("Trained on a T4 GPU with up to 50,000 samples per curriculum depth",
     "I trained on Colab's T4 GPU with up to 50,000 samples per depth. It worked well."),

    ("The AI solver is up to 90 times faster than the reference Kociemba solver",
     "Key trade-off: my AI solver is 90x faster at Depth 7, but less accurate. Both are useful—depends on your goal."),
]

print("Humanizing thesis...\n")
count = 0
for find_text, replace_text in rewrites:
    for para in doc.paragraphs:
        if find_text.lower() in para.text.lower():
            # Find the exact run and replace
            text_lower = para.text.lower()
            find_lower = find_text.lower()
            start_idx = text_lower.find(find_lower)
            if start_idx >= 0:
                # Replace in the paragraph
                for run in para.runs:
                    if find_lower in run.text.lower():
                        old = run.text
                        run.text = run.text.replace(find_text, replace_text) if find_text in run.text else run.text.replace(find_text.lower(), replace_text)
                        if old != run.text:
                            count += 1
                            print(f"[OK] {find_text[:45]}...")
                            break

doc.save("docs/thesis_Edward_Ogbei_PCZ.docx")
print(f"\n[DONE] {count} sections humanized!")
print("Re-embed and convert to PDF next.")
