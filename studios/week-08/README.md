# Week 8 Studio — Unification, the Occurs Check & Prolog

**Companion to** [`../../weeks/week-08.md`](../../weeks/week-08.md) — Session 8B.
**Time budget:** Recap 5 · Breakouts 45 · Demos 20 · Debrief 10 (80 min total).
**Deliverables:** all provided tests pass, a forward-vs-backward writeup, and
progress on Duel 2 (the three-arm NL → FOL → prover experiment).

> **Recap (5 min).** *Unify `p(X, f(Y), b)` with `p(a, f(b), Z)`.* Do it on
> screen together, then read the answer off `unify` in `unify.py`.

## Files in this folder

| File | Purpose | You edit it? |
|---|---|---|
| [`unify.py`](unify.py) | Given: the unifier + occurs check + `resolve`, the family KB, and the term-encoded `FACTS`/`RULES` — verbatim from the notebook | ❌ |
| [`starter.py`](starter.py) | **Tasks 1–2** — implement `occurs` (the occurs check) and `forward_chain` | ✅ |
| [`test_unify.py`](test_unify.py) | Provided tests, incl. `test_occurs_check_rejects_cyclic_term` | ❌ |

There is deliberately **no swipl dependency** in this folder. `unify.py` keeps
the notebook's swipl guard (`run_prolog`, `SWIPL`) so it imports whether or not
SWI-Prolog is installed, and the tests are pure Python. You still need `swipl`
for the live Prolog demos and for Duel 2 — `swipl --version` must work (verified
back in week 1, not here).

## Task 1 — The occurs check (10 min)

Open `starter.py` and implement `occurs(var, x, theta)`. It is two lines in the
notebook and it is the whole reason this week has a studio: it is *rule 4* of
unification, the one the source deck omits. Three cases:

1. `var == x` → `True`
2. `x` is a bound variable → recurse into `theta[x]`
3. `x` is a compound `f(a, …)` → `True` if `var` occurs in **any** argument

Then run:

```bash
python3 test_unify.py
```

Read `test_occurs_check_rejects_cyclic_term` carefully — it is the point of the
week. It asserts that the occurs-checked `unify(X, f(X))` **fails**, while the
occurs-check-free `unify_no_occurs(X, f(X))` **succeeds**, producing the binding
`{X: f(X)}` — a self-reference that unrolls into `f(f(f(…)))`, an infinite term.
That is not a broken test. Standard Prolog omits the occurs check *for speed*,
which makes it technically **unsound**. Two lines of code, and a formal guarantee
is gone. Be the kind of engineer who knows the trade was made.

Fast-finishing pairs: *when does omitting the occurs check actually bite in
practice, and why is it nonetheless the standard Prolog default?* One sentence.

## Task 2 — Forward chaining over the family KB (15 min)

Still in `starter.py`. Implement `forward_chain(facts, rules)`: the deductive
closure of the family/taxonomy KB (`FACTS`, `RULES` in `unify.py`, encoded from
the same `FAMILY_KB` the notebook writes to `family.pl`). Compute it to a
**fixpoint** — repeatedly match every rule body against the known facts (with the
given `unify`) and add the now-ground head, until nothing new appears.

This is the same knowledge Prolog answers *backward*, computed *forward*. The
discussion is the deliverable:

| Question | Better direction | Why |
|---|---|---|
| "What can *everyone* take / what is *all* derivable?" | **Forward** (data-driven) | derives everything once |
| "Can *this* student take *this* course?" | **Backward** (Prolog, goal-driven) | expands only what's relevant |

Forward chaining derives irrelevant facts; backward chaining risks infinite loops
on left recursion (the `ancestor` reorder in the notebook — `BROKEN_KB`). Be able
to state which failure mode belongs to which direction.

## Task 3 — NL → FOL → prover: this is Duel 2 (25 min)

The 25-minute studio block is the launch of **Duel 2 — The Formalizer**, not a
fill-in-the-blank. It is the same architecture you met in weeks 6 and 7 (LLM as
*semantic parser*, sound solver for inference — Logic-LM, LINC, LLM-Modulo), now
targeting **FOL / Prolog**. See the spec — it governs the deliverable, the
grading, and the required directory layout:

> **[`../../projects/duel-2-formalizer.md`](../../projects/duel-2-formalizer.md)**

The three arms (20 FOLIO-style problems, ≥ 3 difficulty levels):

| Arm | Pipeline |
|---|---|
| **A — Hand** | you hand-translate to Prolog → `swipl` |
| **B — Hybrid** | LLM translates to Prolog → `swipl` |
| **B′** | arm B + self-refinement (feed the solver's error back, ≤ 3 retries) |
| **C — Direct** | LLM answers from the natural-language problem |

Arm B's prompt fixes the target syntax exactly (the prover parses it literally):

```
Translate to Prolog. Output only clauses, one per line, ending with a period.
Use lowercase for constants and predicates, uppercase for variables.
Then output the query on the last line prefixed with '?- '.

Text: {premises}
Question: {question}
```

Per arm, per instance, record: **correct / incorrect / no-answer**, wall-clock,
tokens, and solver time separately from LLM time. **"No answer" is a legitimate
third outcome this week** — FOL is *semi-decidable*, so a search that never halts
is expected behaviour, not a crash. Map it onto **scorecard axis 8**, and set a
prover timeout (`call_with_time_limit/2`) so the lesson isn't a hung terminal.

Classify **every** arm-B translation error — this taxonomy is the core Duel 2
deliverable:

- **Quantifier scope wrong** (`∀∃` vs `∃∀`) — most common, most damaging
- `∀` paired with `∧` instead of `→`
- Predicate arity inconsistent between clauses
- Hallucinated premises not in the source text
- Missing premises

Use `aicourse.llm.LLM` for the model call and `unify.run_prolog` (swipl-guarded)
or your own `swipl` wrapper for arms A/B. **Never trust the model's own verdict —
run the prover.**

## Demos (20 min)

- Ask for **quantifier-scope errors** specifically: they are visually obvious in
  Prolog and they change the answer, which makes them ideal teaching examples.
- Then ask: *could you detect this error automatically, without the ground truth?*
  Partly — a prover finding a contradiction, or a KB that entails everything, is a
  signal. This is where self-refinement (arm B′) comes from.
- Solicit the **reversible-relation** demo from Session A: `father(X, ann).` and
  `father(bob, X).` answered by one clause. There is no Python this short.

## Debrief (10 min)

- FOL's expressiveness is what makes real knowledge bases possible; its cost is
  **semi-decidability**. Unification is the computational core (Robinson 1965).
- The occurs check is a real guarantee. You watched it fail on request — that is
  what `test_occurs_check_rejects_cyclic_term` is for. Prolog trades it for speed.
- `Algorithm = Logic + Control` cuts both ways: `BROKEN_KB` has *identical logic*
  and *broken control*. When control is wrong you must think procedurally anyway.
- Arm B works because translation is a language task and inference is a mechanical
  one. **Use each tool where it is strong** — third week running this pattern has
  won. State it unprompted.
- Week 9 gives the solver more power: from deduction to *planning*.

## Links

- Session 8A notebook — [`../../notebooks/week-08-unification-prolog.ipynb`](../../notebooks/week-08-unification-prolog.ipynb)
- Slides — [`../../slides/week-08/deck.md`](../../slides/week-08/deck.md)
- **Duel 2 — The Formalizer** — [`../../projects/duel-2-formalizer.md`](../../projects/duel-2-formalizer.md)
- Duel scorecard (axis 8: "no answer") — [`../../resources/duel-scorecard.md`](../../resources/duel-scorecard.md)
- AI policy (`AI_LOG.md`) — [`../../resources/ai-policy.md`](../../resources/ai-policy.md)
