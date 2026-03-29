# Chapter 2: Problem Definition and Mathematical Background

## 2.1 The Rubik's Cube as a Combinatorial Problem

The 3x3x3 Rubik's Cube is a mechanical puzzle consisting of 26 visible
sub-cubes (cubies) arranged around a fixed internal mechanism. Each face
of the cube can be rotated by 90, 180, or 270 degrees independently.
The goal is to transform any scrambled configuration back to the solved
state, in which every face displays a single uniform color.

## 2.2 Physical Structure

The 26 visible cubies are classified into three types:

- **8 corner cubies**: located at the vertices of the cube, each showing
  exactly 3 colored faces.
- **12 edge cubies**: located at the midpoints of each edge, each
  showing exactly 2 colored faces.
- **6 center cubies**: located at the center of each face, each showing
  exactly 1 colored face. Centers are fixed to the internal mechanism
  and do not move relative to each other.

The six center cubies define the color of each face and serve as
fixed reference points for all computations.

## 2.3 State Space

### 2.3.1 Permutation Components

A cube state can be represented as:

    s = (sigma_c, o_c, sigma_e, o_e)

where:

- sigma_c in S_8 is a permutation of the 8 corner cubies
- o_c in Z_3^8 is a vector of corner orientations (values 0, 1, or 2)
- sigma_e in S_12 is a permutation of the 12 edge cubies
- o_e in Z_2^12 is a vector of edge orientations (values 0 or 1)

### 2.3.2 Counting Without Constraints

Without any constraints, the number of possible configurations would be:

    |S_unrestricted| = 8! * 3^8 * 12! * 2^12
                     = 40320 * 6561 * 479001600 * 4096
                     = 519,024,039,293,878,272,000

### 2.3.3 Physical Constraints

Real cube physics impose three constraints that reduce the state space
by a factor of 12:

**Constraint 1: Corner orientation**

    sum(o_c[i], i = 0..7) = 0 (mod 3)

When a corner cubie is twisted, the total twist of all corners must
remain zero modulo 3. This is because each face rotation preserves
the total corner orientation sum. This reduces the space by a factor of 3.

**Constraint 2: Edge orientation**

    sum(o_e[i], i = 0..11) = 0 (mod 2)

Similarly, the total edge flip of all edges must remain zero modulo 2.
Each face rotation preserves this invariant. This reduces the space by
a factor of 2.

**Constraint 3: Permutation parity**

    parity(sigma_c) = parity(sigma_e)

The corner permutation and edge permutation must have the same parity
(both even or both odd). A single face rotation always produces an
even permutation when considering corners and edges together. This
reduces the space by a factor of 2.

### 2.3.4 Total Number of Legal States

Applying all three constraints:

    |S| = 8! * 3^7 * 12! * 2^10
        = 40320 * 2187 * 479001600 * 1024
        = 43,252,003,274,489,856,000

This equals approximately 4.3 * 10^19 legal configurations.

### 2.3.5 Why Illegal States Cannot Exist

It is physically impossible to reach an illegal state through legal
face rotations starting from the solved state. The three constraints
are invariants of the group of face rotations: any sequence of legal
moves preserves all three constraints simultaneously. To create an
illegal state, one would need to physically disassemble the cube and
reassemble it with a corner twisted, an edge flipped, or two pieces
swapped.

## 2.4 Formal Problem Definition

### 2.4.1 State Space

Let S denote the set of all legal cube states:

    S = { (sigma_c, o_c, sigma_e, o_e) : all three constraints hold }

    |S| = 43,252,003,274,489,856,000

### 2.4.2 Move Set

The move set M consists of 18 face rotations:

    M = { U, U', U2, D, D', D2, R, R', R2, L, L', L2, F, F', F2, B, B', B2 }

where:
- X denotes a 90-degree clockwise rotation of face X
- X' denotes a 90-degree counter-clockwise rotation (inverse of X)
- X2 denotes a 180-degree rotation (self-inverse)

Note: center cubies are never moved by any element of M. They remain
fixed at their canonical positions.

### 2.4.3 Goal State

The goal state G is the identity configuration:

    G = (id, 0, id, 0)

where id is the identity permutation and 0 is the zero orientation
vector. In this state, every cubie is in its home position with
orientation 0.

### 2.4.4 Transition Function

The transition function T: S x M -> S applies a move to a state:

    T(s, m) = s'

where s' is the new state after applying move m to state s. The
transition function is implemented via permutation composition and
orientation addition modulo 3 (corners) or modulo 2 (edges).

For corners:

    sigma_c'[i] = sigma_c[m.cp[i]]
    o_c'[i] = (o_c[m.cp[i]] + m.co[i]) mod 3

For edges:

    sigma_e'[i] = sigma_e[m.ep[i]]
    o_e'[i] = (o_e[m.ep[i]] + m.eo[i]) mod 2

### 2.4.5 Problem Statement

Given a state s in S, find a sequence of moves:

    m_1, m_2, ..., m_k in M

such that:

    T(T(...T(s, m_1), m_2)..., m_k) = G

The sequence (m_1, ..., m_k) is called a solution. The value k is the
solution length (number of moves).

An optimal solution is one that minimizes k.

## 2.5 God's Number

In 2010, Rokicki et al. proved that every legal configuration of the
3x3x3 Rubik's Cube can be solved in at most 20 moves (in the half-turn
metric, where each element of M counts as one move). This upper bound
is tight: there exist configurations that require exactly 20 moves.

This value is known as God's Number:

    max_{s in S} min_{(m_1,...,m_k)} k = 20

The proof was completed using a combination of mathematical analysis
and massive distributed computation.

## 2.6 Algebraic Structure

The set of legal cube states under the operation of move composition
forms a group, known as the Rubik's Cube group. This group is a
subgroup of S_8 x Z_3^8 x S_12 x Z_2^12, restricted by the three
physical constraints.

The group is generated by the six basic face rotations:

    <U, D, R, L, F, B>

Every element of the move set M can be expressed in terms of these
six generators and their inverses. The group has order
43,252,003,274,489,856,000.

## 2.7 Solving Approaches

### 2.7.1 Heuristic Search (Kociemba Two-Phase Algorithm)

Herbert Kociemba's two-phase algorithm is the standard heuristic
approach for finding near-optimal solutions:

- Phase 1 reduces the cube to the subgroup H = <U, D, R2, L2, F2, B2>,
  which has 2,217,093,120 elements.
- Phase 2 solves within H to reach the identity state.

The algorithm uses precomputed pruning tables and typically finds
solutions of 20 moves or fewer in under a second.

### 2.7.2 Machine Learning Approaches

Supervised learning approaches train a neural network to predict the
next move given the current cube state. The network learns from expert
demonstrations (solutions produced by an optimal or near-optimal solver).

Key design choices:
- State encoding: one-hot encoding of the 54 facelets (dimension 324)
- Network architecture: multi-layer perceptron (MLP)
- Training strategy: curriculum learning with progressive depth increase

## 2.8 References

1. Rokicki, T., Kociemba, H., Davidson, M., & Dethridge, J. (2010).
   "God's Number is 20." Available at: http://www.cube20.org/

2. Kociemba, H. "The Two-Phase Algorithm."
   Available at: http://kociemba.org/cube.htm

3. Singmaster, D. (1981). "Notes on Rubik's Magic Cube."
   Penguin Books.

4. Joyner, D. (2008). "Adventures in Group Theory: Rubik's Cube,
   Merlin's Machine, and Other Mathematical Toys." Johns Hopkins
   University Press.
