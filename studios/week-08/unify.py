"""Week 8 studio — the shared unification engine (GIVEN to you; do not modify).

This is the unifier from the Session-8A notebook, *unchanged*, plus the family
knowledge base it live-codes. Week 8 is about what unification and the occurs
check buy you — not about re-typing term plumbing — so the term representation,
the ``unify`` driver, ``resolve``, and the Prolog KB data are provided verbatim.

You write two things in ``starter.py``:

  Task 1  ``occurs``        -- rule 4 of unification, the one the deck omits.
  Task 2  ``forward_chain`` -- forward chaining in Python over the family rules,
                               reusing ``unify`` from this file.

Term representation:
    ``Var("X")``           a logic variable            (uppercase, by convention)
    ``Compound("f", a, b)`` a compound term ``f(a, b)``
    plain Python values     constants (``"john"``, ``"mary"``, ...)

Interface (identical to the notebook):
    unify(x, y, theta=None)      -> substitution dict (the MGU), or None
    unify_no_occurs(x, y)        -> same, occurs check REMOVED (i.e. Prolog)
    occurs(var, x, theta)        -> bool: does ``var`` appear inside ``x``?
    resolve(term, theta)         -> apply a substitution transitively
    resolved_mgu(theta)          -> resolve every binding in a substitution

⚠️ NOTE ON SWI-Prolog: Part 2 of the notebook shells out to ``swipl`` when it is
installed and prints the expected transcript otherwise. This module keeps the
same guard (see ``run_prolog`` / ``SWIPL``) so it imports with or without swipl,
and the provided tests never require it.
"""
import shutil
import subprocess


# ---- 1 · Terms (verbatim from the notebook) ---------------------------------

class Var:
    __slots__ = ("name",)
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name
    def __hash__(self):
        return hash(("Var", self.name))


class Compound:
    __slots__ = ("op", "args")
    def __init__(self, op, *args):
        self.op, self.args = op, args
    def __repr__(self):
        return f"{self.op}({', '.join(map(repr, self.args))})"
    def __eq__(self, other):
        return (isinstance(other, Compound) and self.op == other.op
                and self.args == other.args)
    def __hash__(self):
        return hash(("C", self.op, self.args))


def is_var(x):      return isinstance(x, Var)
def is_compound(x): return isinstance(x, Compound)

# Convenience constructors used across the notebook, tests and starter.
X, Y, Z = Var("X"), Var("Y"), Var("Z")
K      = lambda *a: Compound("Knows", *a)
f      = lambda *a: Compound("f", *a)
mother = lambda a: Compound("mother", a)


# ---- 2 · Unification (verbatim from the notebook) ---------------------------

def unify(x, y, theta=None):
    """Returns a substitution dict (the MGU), or None on failure."""
    if theta is None:
        theta = {}
    if theta is None:
        return None
    if x == y:
        return theta
    if is_var(x):
        return unify_var(x, y, theta)
    if is_var(y):
        return unify_var(y, x, theta)
    if is_compound(x) and is_compound(y):
        if x.op != y.op or len(x.args) != len(y.args):
            return None
        for a, b in zip(x.args, y.args):
            theta = unify(a, b, theta)
            if theta is None:
                return None
        return theta
    return None


def unify_var(var, x, theta, use_occurs_check=True):
    if var in theta:
        return unify(theta[var], x, theta)
    if is_var(x) and x in theta:
        return unify(var, theta[x], theta)
    if use_occurs_check and occurs(var, x, theta):
        return None                          # <-- rule 4: the occurs check
    return {**theta, var: x}


def occurs(var, x, theta):
    """Does `var` appear anywhere inside `x`?"""
    if var == x:
        return True
    if is_var(x) and x in theta:
        return occurs(var, theta[x], theta)
    if is_compound(x):
        return any(occurs(var, a, theta) for a in x.args)
    return False


# ---- 3 · Raw vs. resolved bindings (verbatim from the notebook) -------------

def resolve(term, theta):
    """Apply a substitution transitively -- turn raw bindings into resolved ones."""
    if is_var(term):
        return resolve(theta[term], theta) if term in theta else term
    if is_compound(term):
        return Compound(term.op, *[resolve(a, theta) for a in term.args])
    return term


def resolved_mgu(theta):
    return None if theta is None else {v: resolve(t, theta) for v, t in theta.items()}


# ---- 4 · The occurs check, DELETED (verbatim from the notebook) -------------
# Standard Prolog omits the occurs check for speed. That makes it technically
# UNSOUND. This is the two-line demonstration the notebook builds; the provided
# test pins that ``unify`` (with the check) rejects what this version accepts.

def unify_no_occurs(x, y, theta=None):
    """Same algorithm with the occurs check REMOVED -- i.e. what Prolog does."""
    if theta is None:
        theta = {}
    if x == y:
        return theta
    if is_var(x):
        return unify_var(x, y, theta, use_occurs_check=False)
    if is_var(y):
        return unify_var(y, x, theta, use_occurs_check=False)
    if is_compound(x) and is_compound(y):
        if x.op != y.op or len(x.args) != len(y.args):
            return None
        for a, b in zip(x.args, y.args):
            theta = unify_no_occurs(a, b, theta)
            if theta is None:
                return None
        return theta
    return None


# ---- 5 · The lecture table (verbatim from the notebook) ---------------------
# (p, q, resolved-MGU-or-None, note). The failures teach more than the successes;
# row 4 (X vs f(X)) is the occurs check and the one students get wrong.

LECTURE_CASES = [
    (K("john", X), K("john", "mary"), {X: "mary"},
     "variable binds to a constant"),
    (K("john", X), K(Y, mother(Y)),   {Y: "john", X: mother("john")},
     "nested; Y propagates into X after resolution"),
    (K("john", X), K("mary", Z),      None,
     "constants clash: john vs mary"),
    (f(X, "a"),    f("b", X),         None,
     "X cannot be both b and a"),
    (X,            f(X),              None,
     "OCCURS CHECK -- would build an infinite term"),
]


# ---- 6 · Part 2 data — the family KB (verbatim from the notebook) -----------

FAMILY_KB = """
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).
male(tom).
male(bob).
female(ann).
female(pat).

father(X, Y) :- parent(X, Y), male(X).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% The animal taxonomy from deck 05 slide 7 -- otherwise orphaned content.
isa(bluebird, bird).
isa(bird, vertebrate).
hascovering(bird, feathers).
hasproperty(bird, flies).
hassize(bluebird, small).

% Inheritance in ONE line. This is what propositional logic could not express.
inherits(X, P) :- hasproperty(X, P).
inherits(X, P) :- isa(X, Y), inherits(Y, P).
"""

# The left-recursion break (verbatim from the notebook): logic identical, control
# broken. ``swipl`` hangs on it -- see the notebook's §9.
BROKEN_KB = FAMILY_KB.replace(
    "ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).",
    "ancestor(X, Y) :- ancestor(X, Z), parent(Z, Y).   % <-- LEFT RECURSION")


# ---- 7 · The family KB, encoded as terms for the Python forward-chainer -----
# This is FAMILY_KB above, hand-encoded so ``starter.forward_chain`` can run over
# it with no Prolog parser. Ground FACTS are Compound terms; each RULE is a
# (head, body) pair where body is a list of Compound atoms with Var objects.
# GIVEN -- you consume these; you do not edit them.

def _c(op, *args):
    return Compound(op, *args)

FACTS = frozenset({
    _c("parent", "tom", "bob"),
    _c("parent", "bob", "ann"),
    _c("parent", "bob", "pat"),
    _c("male", "tom"),
    _c("male", "bob"),
    _c("female", "ann"),
    _c("female", "pat"),
    _c("isa", "bluebird", "bird"),
    _c("isa", "bird", "vertebrate"),
    _c("hascovering", "bird", "feathers"),
    _c("hasproperty", "bird", "flies"),
    _c("hassize", "bluebird", "small"),
})

def _rules():
    # Each rule uses FRESH variables so bindings never leak between rules.
    A, B, C = Var("A"), Var("B"), Var("C")
    father  = (_c("father", A, B),      [_c("parent", A, B), _c("male", A)])
    A, B, C = Var("A"), Var("B"), Var("C")
    grandp  = (_c("grandparent", A, C), [_c("parent", A, B), _c("parent", B, C)])
    A, B    = Var("A"), Var("B")
    anc1    = (_c("ancestor", A, B),    [_c("parent", A, B)])
    A, B, C = Var("A"), Var("B"), Var("C")
    anc2    = (_c("ancestor", A, B),    [_c("parent", A, C), _c("ancestor", C, B)])
    A, B    = Var("A"), Var("B")
    inh1    = (_c("inherits", A, B),    [_c("hasproperty", A, B)])
    A, B, C = Var("A"), Var("B"), Var("C")
    inh2    = (_c("inherits", A, B),    [_c("isa", A, C), _c("inherits", C, B)])
    return [father, grandp, anc1, anc2, inh1, inh2]

RULES = _rules()


# ---- 8 · SWI-Prolog runner (guarded — never required) -----------------------
# The notebook shells out to ``swipl`` when present and prints the expected
# transcript otherwise. Kept here so the file behaves identically, but nothing in
# the studio (and none of the tests) depends on swipl being installed.

SWIPL = shutil.which("swipl")

EXPECTED_TRANSCRIPT = """
$ swipl family.pl

?- father(X, ann).
X = bob.

?- father(bob, X).
X = ann ;
X = pat.

?- trace.
?- ancestor(tom, ann).
   Call: (10) ancestor(tom, ann)
   Call: (11) parent(tom, ann)
   Fail: (11) parent(tom, ann)
   Redo: (10) ancestor(tom, ann)
   Call: (11) parent(tom, _123)
   Exit: (11) parent(tom, bob)
   Call: (11) ancestor(bob, ann)
   Call: (12) parent(bob, ann)
   Exit: (12) parent(bob, ann)
   Exit: (11) ancestor(bob, ann)
   Exit: (10) ancestor(tom, ann)
true.
"""


def run_prolog(query, kb_path="family.pl", timeout=20):
    """Run one query against a KB file if swipl is installed; else return the
    expected transcript. Returns (available: bool, output: str)."""
    if not SWIPL:
        return False, EXPECTED_TRANSCRIPT.strip()
    r = subprocess.run(
        [SWIPL, "-q", "-g", f"({query.rstrip('.')} -> true ; true)",
         "-g", "halt", kb_path],
        capture_output=True, text=True, timeout=timeout)
    return True, (r.stdout + r.stderr).strip()


def write_kb(path="family.pl", broken=False):
    """Write FAMILY_KB (or BROKEN_KB) to disk so swipl can consume it."""
    with open(path, "w") as fh:
        fh.write(BROKEN_KB if broken else FAMILY_KB)
    return path
