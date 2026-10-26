"""Week 8 studio — starter (the occurs check + forward chaining).

You fill in two functions. Run ``python3 test_unify.py`` as you go.

  Task 1  ``occurs``        -- rule 4 of unification, the one the source deck
                               omits. It is two lines in the notebook, and it is
                               the whole point of the week: without it, unify
                               builds an infinite term and Prolog is unsound.
  Task 2  ``forward_chain`` -- forward chaining in Python over the family KB,
                               reusing ``unify`` from unify.py. Then, in the
                               demo, argue which direction fits which question:
                               forward (derive everything) vs. backward (Prolog,
                               query-driven).

The provided test ``test_occurs_check_rejects_cyclic_term`` asserts that the
occurs-checked ``unify`` REJECTS ``unify(X, f(X))`` while the occurs-check-free
version ACCEPTS it (building f(f(f(...)))). A guarantee you cannot watch fail is
a guarantee you have not understood.

Task 3 (the 25-minute NL -> FOL -> prover experiment) is Duel 2 — the Formalizer.
It is not a fill-in-the-blank; see README.md and ../../projects/duel-2-formalizer.md.
"""
from unify import (
    Var, Compound, is_var, is_compound, unify, resolve,
    FACTS, RULES,
)


# ---- Task 1: the occurs check -----------------------------------------------

def occurs(var, x, theta):
    """Does ``var`` appear anywhere inside ``x``, following bindings in ``theta``?

    Three cases:
      1. ``var == x``                          -> True   (found it)
      2. ``x`` is a bound variable             -> recurse into theta[x]
      3. ``x`` is a compound ``f(a, b, ...)``  -> True if var occurs in ANY arg
    Anything else (a constant, an unbound different variable) -> False.

    unify_var calls this before binding ``var`` to ``x``. Return True here and the
    binding is refused -- which is exactly why ``unify(X, f(X))`` fails.
    """
    # TODO: implement the three cases above (see the notebook, §2).
    raise NotImplementedError


# ---- Task 2: forward chaining over the family KB ----------------------------

def forward_chain(facts, rules):
    """Return the deductive closure of ``facts`` under ``rules`` as a set of
    ground Compound atoms.

    ``facts``  : an iterable of ground Compound terms (see unify.FACTS).
    ``rules``  : a list of (head, body) pairs where ``head`` is a Compound with
                 Var arguments and ``body`` is a list of Compound atoms
                 (see unify.RULES).

    Algorithm (naive forward chaining to a fixpoint):
      repeat until nothing new is added:
        for each rule (head, body):
          for each way of matching EVERY body atom against a known fact
              (accumulate the substitution with ``unify``):
            add ``resolve(head, theta)`` -- the now-ground head -- to the facts.

    Hint: write a small recursive helper ``match(body, theta)`` that yields every
    substitution unifying the whole body against ``facts``. ``unify`` is imported
    for you; pass a *copy* of theta so branches don't clobber each other.
    """
    # TODO: implement the fixpoint loop described above.
    raise NotImplementedError


# ---- Task 3 (the duel) — see README.md §"Task 2" and the Duel 2 spec --------
# NL -> FOL -> prover is Duel 2 (The Formalizer). Arm B's prompt (target syntax
# is non-negotiable — the prover parses it literally):
#
#   Translate to Prolog. Output only clauses, one per line, ending with a period.
#   Use lowercase for constants and predicates, uppercase for variables.
#   Then output the query on the last line prefixed with '?- '.
#
#   Text: {premises}
#   Question: {question}
#
# Score every arm per instance: correct / incorrect / NO-ANSWER (syntax error or
# non-termination). "No answer" is a legitimate third outcome this week — FOL is
# semi-decidable — map it onto scorecard axis 8. Use aicourse.llm.LLM for the
# model call and unify.run_prolog (swipl-guarded) or your own swipl wrapper for
# arms A/B. Do NOT trust the model's own verdict; run the prover.


if __name__ == "__main__":
    # Smoke test: exercise whatever you've filled in.
    print("Task 1 — occurs check:")
    try:
        print("  occurs(X, f(X), {}) =", occurs(Var("X"), Compound("f", Var("X")), {}))
        print("  occurs(X, f(Y), {}) =", occurs(Var("X"), Compound("f", Var("Y")), {}))
    except NotImplementedError:
        print("  not implemented yet")

    print("\nTask 2 — forward chaining over the family KB:")
    try:
        closure = forward_chain(FACTS, RULES)
        derived = sorted(str(a) for a in closure - set(FACTS))
        print(f"  {len(derived)} facts derived:")
        for a in derived:
            print("   ", a)
    except NotImplementedError:
        print("  not implemented yet")
