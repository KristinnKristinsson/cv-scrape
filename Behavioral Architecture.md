# Behavioral Architecture — Minimal Spec (v4)

You are placing code. This document tells you *where each piece goes*. It contains
principles only, no examples. Apply the principles directly; do not wait for a sample
to imitate.

---

## The one rule

Organize every piece of code by **what it does**, never by **what it is for**.

- *What it is for* is intent — a feature, a theme, a story. It is invisible to the code
  and cannot be checked. Do not group by it.
- *What it does* is behavior. It can be checked. Group by it.

Two consequences, both mandatory:

1. If two pieces serve the **same feature** but **do different things**, they go in
   **different places**.
2. If two pieces serve **different features** but **do the same thing**, they are **one
   piece**, used more than once. Do not write it twice because the theme differs.

**When do two pieces do the same thing?** One piece does the same thing as another only
if it can serve both callers **without a parameter whose sole role is selecting behavior
by caller**. If unification requires such a flag, the flag is the theme returning as an
argument — they are different pieces. Do not duplicate because the theme differs; do not
merge because the surface matches.

---

## Naming

A name **reports** behavior that already exists. It never **prescribes** behavior that
should exist.

Write the behavior first; name it afterward, as an accurate (lossy) summary of what it
does.

If you ever reason "it is called X, **so it should also** do Y" — stop. The name is
writing the code. A name is a description, not a contract the behavior must grow to
satisfy.

---

## The categories

There are two axes. The first four categories are kinds of **doing** (verbs). The
fifth is a kind of **being** (noun). They are independent — a piece is placed by asking
which kind of thing it is, not which feature it belongs to.

### Logic — *decides*
Evaluates values **already in hand** and returns a determination. Changes nothing,
fetches nothing. Every value it reasons over arrived as an argument.
Deterministic: same input, same output, every time.
**Test:** could you run it twice with the same input, and get the same answer with
nothing else in the world changed? If yes, it is logic. If it mutates anything, it is
not. If it reaches out for a value — even without changing anything — it is not.

### Observation — *reads*
Fetches a value from the world without changing it: stored state, the clock, entropy,
another system's answer. It decides nothing and mutates nothing, yet it is not
deterministic — the world moves between calls.
**Test:** does running it change nothing in every condition of the world, and yet
possibly return different answers? Then it is observation. Logic may never contain one;
the flow performs the observation and hands the value in.

**Place by mechanism, never by noun.** Reading a value the world owns is observation.
Advancing a generator you own — a source whose next answer is determined by state you
hold — changes your own state, however unpredictable its output appears: that is an
effect. The same noun (time, randomness, a remembered answer) can name different pieces.
The tests decide; the noun does not.

### Effect — *changes state*
Takes the world in one condition and leaves it in another. All mutation lives here.
**Test:** is there **any** condition of the world in which running it changes something?
Then it is effect. Observation guarantees no change in every condition; effect does not.
Keep the change isolated here so logic stays pure.

**Convergence.** An effect may converge: it drives the world toward a condition and,
once the world is in that condition, changes nothing more. A converged run that changes
nothing is still an effect — the test is existential, not universal. Convergence is what
makes repetition safe; prefer it wherever an effect may be repeated.

**Atomicity.** Some invariants span a decision and a change: the check is valid only if
nothing moves before the change lands. That pair is **not** a logic piece plus an effect
piece — separating them opens a window in which the check goes stale, and the
architecture would be racing by design. It is **one effect**, whose decision lives inside
the same indivisible boundary as the change. Purity yields here; concede it explicitly.
The decision that remains outside the boundary is only the one that stays valid however
the world moves between check and change.

**The uncontrolled boundary.** An effect that crosses into a system you do not control
has three outcomes, not two: the change landed, the change was refused, or **no answer
came back**. The third is not an error; it is a determination — *unknown* — and it is a
tag like any other. An effect that can return unknown must be convergent, or paired with
an observation that can distinguish landed from not-landed. Otherwise repetition is
unsafe and the flow has nothing to route on.

### Interaction — *guards the boundary*
The point where input you **do not control** enters the system (a user, an external
caller, anything unpredictable). Its job is to receive the uncontrolled and constrain it
toward the predictable — validate, reject, normalize — before it reaches logic or
effect.
**Test:** does the input originate outside your control? Then it crosses here first, and
everything past this boundary may trust its input.

### State — *is*
The data and objects the behaviors act upon. Group each by **what it is**, never by what
uses it. A model is an honest description of an entity.
**Test:** if a field is being added because one flow found it convenient, the flow is
writing the schema — stop. The entity is defined by what it is, not by who touches it.
(This is the naming rule, one layer down.)

---

## Acting on behavior

Sometimes a behavior must act on another behavior — inspect it, replace it, defer it,
multiply it, prevent it. Do not grow the flow a judgment for this, and do not invent a
category for it. **Reify:** make the inner behavior a value first. Then everything
already has a home — the pending behavior is state; deciding what it becomes is logic
over values in hand; performing what remains is effect; a queue of pending behaviors is
state, consumed by a flow. The plan becomes data, and every test above applies
unchanged.

---

## Flow — the altitude, and its body

Flow is how logic, observation, effect, interaction, and state combine into one path
from start to finish. It is the height from which the parts become a system — and it is
also **code**: the piece that sequences the others must live somewhere, and it lives
here.

A flow is placed by a **restriction**, not a verb: it makes **no decision and no direct
mutation of its own**. Only ordered calls — receive at the boundary, observe, decide,
change — and the routing between them.

A flow may **route**: choose which call runs next by the **tag** of a determination a
logic piece or atomic effect already returned — proceed or reject, replay or conflict,
reserved or insufficient, landed or refused or unknown. Routing includes selecting which
effects run, and stopping. Absence of an answer is a determination; a flow routes on
*unknown* as it routes on any tag. It may not **decide**: if a branch inspects raw
values to reach a determination, that determination is logic — extract it, and let the
flow route on the tag it returns. If you find a mutation in a flow, extract it to
effect. A flow that follows this restriction has nothing of its own to test; it is pure
sequence and dispatch, legible at a glance.

**Where a flow may stop.** A flow that performs more than one change, and cannot make
them indivisible, must satisfy this: after every step, the world is in a condition it
can remain in — or the flow includes the effect that returns it to one. That returning
effect is not a new kind of piece: it changes state, so it is an effect, named by what
it does; and if the same change serves another path, it is the same piece (consequence
2). *Returning the world* is a role the flow assigns, never a category. Only steps that
can leave an uninhabitable condition need a return; observations need none, and
convergent effects often need none.

Read the flow to find dependencies that live **between** parts and appear in **no single
part** — especially ordering dependencies (X must happen before Y is valid), and the
pairing of a change with the effect that returns the world when the path cannot
continue. These between-part dependencies are where a system stops being a pile of
understandable pieces and starts behaving as a whole. They are visible here or nowhere.
Watch them here. And when an ordering dependency hardens into an atomicity requirement —
the check must not merely precede the change but be indivisible from it — it leaves the
flow and becomes one effect (see Atomicity).

---

## How to place a piece

For each piece of code you write or place:

1. Name what it **does**, in one verb-phrase, from behavior alone. Ignore the feature it
   serves.
2. Route by that verb: a **decision over values in hand** → logic; a **fetch that
   changes nothing in any condition** → observation; a **change to state, in any
   condition** → effect; a **boundary receiving uncontrolled input** → interaction; a
   **thing that is** → state; a **sequence of calls that makes no decision and no
   mutation of its own** (it may route on determinations already returned, including
   *unknown*) → flow.
3. If the piece acts **on another behavior**, reify the inner behavior into a value,
   then place each resulting piece by step 2.
4. If a piece that does that same thing already exists, **use it** — applying the test
   under the one rule: same thing means no caller-selecting flag is needed. Do not
   duplicate because the theme differs; do not merge because the surface matches.
5. Only after every piece is placed, read them together as a **flow**, and look for
   dependencies between pieces that no single piece names — any check-and-change pair
   that must be indivisible, and any change that needs a return available when the path
   cannot continue.

---

## What this costs you

This structure is terse in rules and heavy in judgment. It does not decide placements
for you the way a conventional framework does; it requires you to reason about behavior
on every piece. That reasoning is the price. Pay it deliberately — the moment you place
something by what it is *for* instead of what it *does*, the structure has silently
begun to rot, and every such choice will look locally reasonable.

One more price, named plainly: flows grow longer wherever the world can be left
mid-change. The path that returns the world is code, and it is the longest path, not the
shortest. Legibility survives — the flow remains sequence and dispatch — but *at a
glance* is earned step by step, not granted.
