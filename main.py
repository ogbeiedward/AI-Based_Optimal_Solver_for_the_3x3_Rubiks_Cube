"""
HUMAN-READABLE DESCRIPTION:
This is the primary entry point for the project's terminal interface. It orchestrates user input, tying together the cube state, random scramblers, and the various solvers.
"""

"""
main.py
-------
Command-line interface for the Rubik's Cube simulator project.

Subcommands:
  visualize         Launch the interactive 3D matplotlib viewer
  scramble          Generate a random scramble and display it
  validate          Run validation checks on the cube and scramble module
  generate_dataset  Generate curriculum training datasets (depths 1..N)
  train             Train the AI solver using curriculum learning
  compare           Compare Kociemba vs AI solver on benchmark scrambles

This is the M.Sc. thesis:
  "AI-Based Optimal Solver for the 3x3 Rubik's Cube"
"""

import sys
import argparse

from core.cube import CubieCube
from core.moves import MOVE_NAMES
from utils.scramble import (
    generate_scramble, scramble_to_string,
    get_inverse_scramble, validate_scramble, scramble_to_kociemba,
)


def cmd_visualize(args):
    """Launch the interactive 3D Rubik's Cube viewer."""
    if args.web:
        from visualization.server import start_server
        start_server(port=args.port)
    else:
        from visualization.controls import InteractiveViewer
        viewer = InteractiveViewer()
        viewer.launch()


def cmd_scramble(args):
    """Generate and display a random scramble."""
    seed = args.seed
    length = args.length

    scramble = generate_scramble(length=length, seed=seed)
    inverse = get_inverse_scramble(scramble)

    print(f"\n  Scramble ({len(scramble)} moves):")
    print(f"    {scramble_to_string(scramble)}")
    print(f"\n  Inverse:")
    print(f"    {scramble_to_string(inverse)}")
    print(f"\n  Kociemba string:")
    print(f"    {scramble_to_kociemba(scramble)}")

    # Validate
    valid = validate_scramble(scramble, verbose=True)
    print(f"\n  Validation: {'PASSED ✓' if valid else 'FAILED ✗'}")
    print()


def cmd_validate(args):
    """Run a comprehensive validation suite."""
    print("\n" + "=" * 60)
    print("  RUBIK'S CUBE VALIDATION SUITE")
    print("=" * 60)

    all_passed = True

    # Test 1: Solved state
    print("\n  [1] Solved state checks:")
    cube = CubieCube()
    checks = [
        ("is_solved()", cube.is_solved()),
        ("is_legal()", cube.is_legal()),
        ("Kociemba string", cube.to_kociemba_string() == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"),
    ]
    for name, result in checks:
        status = "✓" if result else "✗"
        print(f"    {status} {name}: {result}")
        all_passed = all_passed and result

    # Test 2: Move + inverse = identity
    print("\n  [2] Move + inverse = identity (all 6 faces):")
    for face in ["U", "D", "R", "L", "F", "B"]:
        cube = CubieCube()
        cube.apply_move(face)
        cube.apply_move(face + "'")
        result = cube.is_solved()
        status = "✓" if result else "✗"
        print(f"    {status} {face} -> {face}' = identity: {result}")
        all_passed = all_passed and result

    # Test 3: Four rotations = identity
    print("\n  [3] Four rotations = identity (all 6 faces):")
    for face in ["U", "D", "R", "L", "F", "B"]:
        cube = CubieCube()
        for _ in range(4):
            cube.apply_move(face)
        result = cube.is_solved()
        status = "✓" if result else "✗"
        print(f"    {status} {face}^4 = identity: {result}")
        all_passed = all_passed and result

    # Test 4: All 18 moves preserve legality
    print("\n  [4] All 18 moves preserve legality:")
    for move in MOVE_NAMES:
        cube = CubieCube()
        cube.apply_move(move)
        result = cube.is_legal()
        status = "✓" if result else "✗"
        print(f"    {status} {move:3s} -> legal: {result}")
        all_passed = all_passed and result

    # Test 5: Orientation invariants after complex sequence
    print("\n  [5] Orientation invariants after complex sequence:")
    cube = CubieCube()
    seq = ["R", "U", "F'", "D2", "L", "B'", "R2", "U'", "F", "D", "L'", "B2"]
    cube.apply_sequence(seq)
    co_ok = sum(cube.co) % 3 == 0
    eo_ok = sum(cube.eo) % 2 == 0
    legal_ok = cube.is_legal()
    print(f"    {'✓' if co_ok else '✗'} Corner orientation sum mod 3 = {sum(cube.co) % 3}")
    print(f"    {'✓' if eo_ok else '✗'} Edge orientation sum mod 2 = {sum(cube.eo) % 2}")
    print(f"    {'✓' if legal_ok else '✗'} State is legal: {legal_ok}")
    all_passed = all_passed and co_ok and eo_ok and legal_ok

    # Test 6: Scramble + inverse = solved (10 seeds)
    print("\n  [6] Scramble + inverse = solved (seeds 0-9):")
    for seed in range(10):
        scramble = generate_scramble(seed=seed)
        result = validate_scramble(scramble)
        status = "✓" if result else "✗"
        print(f"    {status} Seed {seed}: {len(scramble)} moves -> valid: {result}")
        all_passed = all_passed and result

    # Test 7: Centers never move
    print("\n  [7] Centers never move (all 18 moves):")
    center_ok = True
    for move in MOVE_NAMES:
        cube = CubieCube()
        cube.apply_move(move)
        s = cube.to_kociemba_string()
        if s[4] != 'U' or s[13] != 'R' or s[22] != 'F' or s[31] != 'D' or s[40] != 'L' or s[49] != 'B':
            print(f"    ✗ Centers moved after {move}!")
            center_ok = False
            all_passed = False
    if center_ok:
        print("    ✓ All centers fixed after every move")

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("  ALL VALIDATIONS PASSED ✓")
    else:
        print("  SOME VALIDATIONS FAILED ✗")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# New: Dataset generation command
# ---------------------------------------------------------------------------

def cmd_generate_dataset(args):
    """Generate curriculum training datasets and display statistics."""
    from data.dataset_generator import generate_curriculum_dataset
    from data.dataset_stats import print_dataset_stats

    print("\n" + "=" * 62)
    print("  CURRICULUM DATASET GENERATION")
    print("=" * 62)
    print(f"  Max depth    : {args.max_depth}")
    print(f"  Samples/depth: {args.samples:,}")
    print(f"  Keep fraction: {args.keep_fraction:.0%}")
    print(f"  Output dir   : {args.output_dir}")
    print(f"  Seed         : {args.seed}")

    result = generate_curriculum_dataset(
        max_depth=args.max_depth,
        samples_per_depth=args.samples,
        keep_fraction=args.keep_fraction,
        dataset_dir=args.output_dir,
        seed=args.seed,
        verbose=True,
        bfs_timeout=args.bfs_timeout,
    )

    # Show final statistics
    if result["states"] is not None:
        print_dataset_stats(
            states=result["states"],
            labels=result["labels"],
            depths=result["depths"],
        )
    else:
        print("\n  [WARNING] No dataset was generated.")


# ---------------------------------------------------------------------------
# New: Train command
# ---------------------------------------------------------------------------

def cmd_train(args):
    """Train the AI solver using curriculum learning."""
    import torch
    from solvers.ai_solver import RubiksMLP, train_model

    print("\n" + "=" * 62)
    print("  AI SOLVER — CURRICULUM TRAINING")
    print("=" * 62)
    print(f"  Max depth       : {args.max_depth}")
    print(f"  Samples/depth   : {args.samples:,}")
    print(f"  Epochs/depth    : {args.epochs}")
    print(f"  Batch size      : {args.batch_size}")
    print(f"  Learning rate   : {args.lr}")
    print(f"  Solve threshold : {args.threshold:.0%}")
    print(f"  Seed            : {args.seed}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device          : {device}")

    model = RubiksMLP()
    print(f"  Model params    : {model.get_parameter_count():,}")

    history = train_model(
        model=model,
        max_depth=args.max_depth,
        samples_per_depth=args.samples,
        epochs_per_depth=args.epochs,
        solve_threshold=args.threshold,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        seed=args.seed,
        verbose=True,
        device=device,
    )

    # Summary table
    print("\n" + "=" * 62)
    print("  TRAINING SUMMARY")
    print("=" * 62)
    print(f"  {'Depth':>6}  {'Samples':>9}  {'Solve Rate':>11}")
    print(f"  {'-----':>6}  {'---------':>9}  {'-----------':>11}")
    for r in history["depth_results"]:
        print(f"  {r['depth']:>6}  {r['num_training_samples']:>9,}  "
              f"{r['solve_rate']:>11.1%}")

    # Save model
    if args.save_model:
        import os
        os.makedirs(os.path.dirname(args.save_model), exist_ok=True)
        torch.save(model.state_dict(), args.save_model)
        print(f"\n  Model saved to: {args.save_model}")

    print()


# ---------------------------------------------------------------------------
# New: Compare command
# ---------------------------------------------------------------------------

def cmd_compare(args):
    """Compare Kociemba vs AI solver on a shared benchmark set."""
    from experiments.ai_vs_kociemba import run_comparison

    print("\n" + "=" * 62)
    print("  KOCIEMBA vs AI SOLVER — COMPARISON")
    print("=" * 62)
    print(f"  Test cubes per depth : {args.num_tests}")
    print(f"  Max scramble depth   : {args.max_depth}")
    print(f"  Model path           : {args.model_path or 'None (untrained)'}")

    run_comparison(
        num_tests=args.num_tests,
        max_depth=args.max_depth,
        model_path=args.model_path,
        seed=args.seed,
    )


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Rubik's Cube Simulator — M.Sc. AI Thesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py visualize                       Launch interactive 3D viewer
  python main.py scramble                        Generate a random scramble
  python main.py scramble -l 25                 25-move scramble
  python main.py validate                        Run full validation suite
  python main.py generate_dataset               Generate datasets (depths 1-5)
  python main.py generate_dataset --max-depth 8 Depths 1-8, 1000 samples each
  python main.py train --max-depth 5            Train AI up to depth 5
  python main.py compare --max-depth 5          Kociemba vs AI comparison
        """,
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Visualize command (updated)
    viz_parser = subparsers.add_parser('visualize', help='Launch interactive 3D viewer')
    viz_parser.add_argument('--web', action='store_true',
                             help='Launch the Three.js web-based viewer (default: False)')
    viz_parser.add_argument('--port', type=int, default=8080,
                             help='Port for the web viewer (default: 8080)')

    # Scramble command (unchanged)
    scr_parser = subparsers.add_parser('scramble', help='Generate a random scramble')
    scr_parser.add_argument('-l', '--length', type=int, default=None,
                            help='Number of moves (default: random 20-25)')
    scr_parser.add_argument('-s', '--seed', type=int, default=None,
                            help='Random seed for deterministic generation')

    # Validate command (unchanged)
    subparsers.add_parser('validate', help='Run validation suite')

    # Generate dataset command (NEW)
    gen_parser = subparsers.add_parser(
        'generate_dataset',
        help='Generate curriculum training datasets'
    )
    gen_parser.add_argument('--max-depth', type=int, default=5,
                            help='Maximum scramble depth (default: 5)')
    gen_parser.add_argument('--samples', type=int, default=1000,
                            help='New samples per depth level (default: 1000)')
    gen_parser.add_argument('--keep-fraction', type=float, default=0.20,
                            help='Fraction of old dataset to keep (default: 0.20)')
    gen_parser.add_argument('--output-dir', type=str,
                            default='data/datasets',
                            help='Output directory for dataset files')
    gen_parser.add_argument('--bfs-timeout', type=float, default=5.0,
                            help='Max BFS seconds per sample (default: 5.0)')
    gen_parser.add_argument('--seed', type=int, default=42,
                            help='Random seed (default: 42)')

    # Train command (NEW)
    train_parser = subparsers.add_parser(
        'train',
        help='Train the AI solver with curriculum learning'
    )
    train_parser.add_argument('--max-depth', type=int, default=5,
                              help='Maximum curriculum depth (default: 5)')
    train_parser.add_argument('--samples', type=int, default=1000,
                              help='Training samples per depth (default: 1000)')
    train_parser.add_argument('--epochs', type=int, default=50,
                              help='Epochs per depth level (default: 50)')
    train_parser.add_argument('--batch-size', type=int, default=64,
                              help='Batch size (default: 64)')
    train_parser.add_argument('--lr', type=float, default=1e-3,
                              help='Learning rate (default: 0.001)')
    train_parser.add_argument('--threshold', type=float, default=0.8,
                              help='Solve rate threshold to advance depth (default: 0.8)')
    train_parser.add_argument('--save-model', type=str,
                              default='data/models/ai_solver.pt',
                              help='Path to save trained model')
    train_parser.add_argument('--seed', type=int, default=42,
                              help='Random seed (default: 42)')

    # Compare command (NEW)
    cmp_parser = subparsers.add_parser(
        'compare',
        help='Compare Kociemba vs AI solver'
    )
    cmp_parser.add_argument('--num-tests', type=int, default=50,
                            help='Number of test cubes per depth (default: 50)')
    cmp_parser.add_argument('--max-depth', type=int, default=5,
                            help='Max scramble depth to test (default: 5)')
    cmp_parser.add_argument('--model-path', type=str,
                            default='data/models/ai_solver.pt',
                            help='Path to trained AI model (.pt file)')
    cmp_parser.add_argument('--seed', type=int, default=99,
                            help='Random seed (default: 99)')

    args = parser.parse_args()

    if args.command == 'visualize':
        cmd_visualize(args)
    elif args.command == 'scramble':
        cmd_scramble(args)
    elif args.command == 'validate':
        cmd_validate(args)
    elif args.command == 'generate_dataset':
        cmd_generate_dataset(args)
    elif args.command == 'train':
        cmd_train(args)
    elif args.command == 'compare':
        cmd_compare(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
