"""Provided tests for the week-8 studio.

Run: ``python3 test_unify.py``. Prints one line per test; exits non-zero on any
failure. No SWI-Prolog required — the Prolog half of the studio (Duel 2) is not
unit-tested here; these tests pin the unifier, the occurs check, and forward
chaining, all in pure Python.

The centrepiece is ``test_occurs_check_rejects_cyclic_term``. It asserts that the
occurs-checked ``unify`` REJECTS ``unify(X, f(X))`` while the occurs-check-free
version (i.e. what standard Prolog does) ACCEPTS it and builds an infinite term.
Watching that guarantee fail — on purpose — is how you learn the guarantee is real.
"""
import sys

from unify import (
    Var, Compound, unify, unify_no_occurs, resolved_mgu, is_compound,
    LECTURE_CASES, FACTS, RULES, X, f,
)
import starter as s


def _c(op, *args):
    return Compound(op, *args)


# ---- unifier + occurs check (exercise unify.py, always available) -----------

def test_unify_matches_lecture_table():
    """The five cases from the lecture, as assertions. Row 4 is the occurs check."""
    for p, q, expected, note in LECTURE_CASES:
        got = resolved_mgu(unify(p, q))
        assert got == expected, (
            f"MISMATCH on {p} vs {q}: got {got}, expected {expected} ({note})"
        )
    print(f"  ok  unify reproduces all {len(LECTURE_CASES)} lecture-table cases")


def test_occurs_check_rejects_cyclic_term():
    """The point of the week: delete the occurs check and unsoundness appears.

    WITH the check, ``unify(X, f(X))`` fails (returns None). WITHOUT it, the
    binding ``{X: f(X)}`` is produced — a self-reference that unrolls into the
    infinite term f(f(f(...))). We verify both, and walk the cycle a bounded
    number of steps so the demonstration never actually hangs.
    """
    # WITH occurs check: the binding is refused.
    assert unify(X, f(X)) is None, (
        "occurs-checked unify(X, f(X)) must FAIL — that is the whole guarantee"
    )

    # WITHOUT occurs check: the binding is accepted (this is what Prolog does).
    theta = unify_no_occurs(X, f(X))
    assert theta is not None and X in theta, (
        "unify_no_occurs(X, f(X)) should bind X (Prolog omits the check for speed)"
    )
    bound = theta[X]
    # The binding is self-referential: X is bound to f(X), whose argument is X.
    assert is_compound(bound) and bound.op == "f" and bound.args[0] == X, (
        f"expected the cyclic binding X = f(X), got X = {bound}"
    )

    # Follow it a few steps by hand: f(X) -> f(f(X)) -> ... never terminates.
    term = bound
    for _ in range(4):
        term = Compound("f", term)
    depth = 0
    node = term
    while is_compound(node):
        node, depth = node.args[0], depth + 1
    assert depth >= 5, "the substituted term should keep growing without bound"
    print("  ok  occurs check rejects X = f(X); removing it builds an infinite term")


# ---- student code (starter.py — NotImplementedError until you fill it in) ---

def test_student_occurs_matches_expected():
    """``starter.occurs`` must implement all three cases, including through theta."""
    A, B, C = Var("A"), Var("B"), Var("C")
    cases = [
        (A, A, {},                          True,  "var occurs in itself"),
        (A, _c("f", A), {},                 True,  "var occurs inside a compound"),
        (A, _c("f", B), {},                 False, "different var does not occur"),
        (A, "tom", {},                      False, "var does not occur in a constant"),
        (A, B, {},                          False, "unbound distinct var"),
        (A, B, {B: _c("f", A)},             True,  "occurs THROUGH a binding"),
        (A, _c("g", _c("h", B), C), {C: A}, True,  "occurs via a bound arg"),
    ]
    for var, x, theta, expected, note in cases:
        got = s.occurs(var, x, theta)
        assert got == expected, (
            f"occurs({var}, {x}, {theta}) = {got}, expected {expected} ({note})"
        )
    print(f"  ok  starter.occurs matches all {len(cases)} expected cases")


def test_forward_chain_derives_family_closure():
    """``starter.forward_chain`` must derive exactly the family/taxonomy closure."""
    closure = set(s.forward_chain(FACTS, RULES))

    must_contain = [
        _c("father", "tom", "bob"),
        _c("father", "bob", "ann"),
        _c("father", "bob", "pat"),
        _c("grandparent", "tom", "ann"),
        _c("grandparent", "tom", "pat"),
        _c("ancestor", "tom", "bob"),
        _c("ancestor", "bob", "ann"),
        _c("ancestor", "tom", "ann"),   # recursive step
        _c("ancestor", "tom", "pat"),   # recursive step
        _c("inherits", "bird", "flies"),
        _c("inherits", "bluebird", "flies"),   # via the isa chain
    ]
    for fact in must_contain:
        assert fact in closure, f"forward_chain did not derive {fact}"

    must_not_contain = [
        _c("father", "tom", "ann"),          # tom is not ann's parent
        _c("ancestor", "ann", "tom"),        # ancestry is not symmetric
        _c("inherits", "vertebrate", "flies"),  # no fact seeds this
    ]
    for fact in must_not_contain:
        assert fact not in closure, f"forward_chain wrongly derived {fact}"

    # The closure must be a superset of the original facts (monotone).
    assert set(FACTS) <= closure, "forward_chain must not drop known facts"
    print(f"  ok  forward_chain derived the family closure "
          f"({len(closure) - len(FACTS)} new facts)")


TESTS = [
    test_unify_matches_lecture_table,
    test_occurs_check_rejects_cyclic_term,
    test_student_occurs_matches_expected,
    test_forward_chain_derives_family_closure,
]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
        except NotImplementedError:
            print(f"  --  {t.__name__}: starter function not implemented yet")
            failed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    if failed:
        print(f"\n{failed}/{len(TESTS)} failed")
        sys.exit(1)
    print(f"\nall {len(TESTS)} tests pass")


if __name__ == "__main__":
    main()
