"""Week 7 studio — REFERENCE SOLUTION (instructor-only).

A filled-in copy of ``starter.py``: identical function names and signatures, so
the *provided* ``test_dpll.py`` passes when this module is imported in place of
``starter``. Verify with ``studios/_verify_solutions.py`` (which aliases this file
to the name ``starter`` and runs the unmodified test).

DO NOT ship this to students — it is excluded via ``studios/.gitignore``. The
teaching walkthrough lives in ``solution.ipynb`` (which imports this file rather
than re-pasting it, so the two never drift).

The whole week hangs on one distinction: the SOUND agent moves only where the KB
*proves* there is no pit; the RECKLESS agent treats UNKNOWN as safe. The provided
``test_reckless_agent_is_unsound`` watches the reckless one make exactly the move
the sound one structurally cannot — so ``reckless_frontier`` must genuinely omit
the entailment check.
"""
from dpll import Pv, entails


# ---- Task 1: the ASK step ---------------------------------------------------

def provably_safe(kb, x, y) -> bool:
    """Does the KB PROVE there is no pit at (x, y)?  i.e.  KB ⊨ ¬P(x,y).

    ¬P(x,y) is the literal ``-Pv(x, y)`` wrapped as a one-clause CNF, and
    ``entails`` answers by checking that ``KB ∧ P(x,y)`` is unsatisfiable.
    """
    return entails(kb, [frozenset({-Pv(x, y)})])


def provably_pit(kb, x, y) -> bool:
    """Does the KB PROVE there is a pit at (x, y)?  i.e.  KB ⊨ P(x,y)."""
    return entails(kb, [frozenset({Pv(x, y)})])


# ---- Task 1: the act step, two ways -----------------------------------------

def sound_frontier(kb, squares) -> list:
    """The SOUND agent. Return only the squares that are PROVED safe.

    It moves only where it can prove there is no pit; UNKNOWN is never treated as
    safe. If nothing is proved safe it returns [] — an honest agent then stops or
    takes a *declared* risk.
    """
    return [sq for sq in squares if provably_safe(kb, *sq)]


def reckless_frontier(kb, squares) -> list:
    """The UNSOUND agent — the mistake, implemented on purpose so we can watch it.

    It skips the entailment-for-safety check and moves anywhere NOT proved to be a
    pit, i.e. it treats UNKNOWN as safe. This is exactly the "probably safe" ≠
    "provably safe" error the LLM makes in Task 2.
    """
    return [sq for sq in squares if not provably_pit(kb, *sq)]


if __name__ == "__main__":
    from dpll import kb_from_percepts, classify, load_scenarios
    sc = load_scenarios()["wumpus"]
    base = sc["base_percepts"]
    frontier = [tuple(s) for s in sc["frontier"]]
    kb = kb_from_percepts(base)

    print("Percepts: (1,1) no breeze, (2,1) breeze.\n")
    for (x, y) in frontier:
        print(f"  ({x},{y}): {classify(kb, x, y)}")

    print("\nsound_frontier :", sound_frontier(kb, frontier))
    print("reckless_frontier:", reckless_frontier(kb, frontier))
