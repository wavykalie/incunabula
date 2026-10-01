# PREFERENCES.md — how the harness consumes an optional per-user file

**There is no code that reads `USER_PREFERENCES.md`.** This file is the entire
mechanism, and that is deliberate: the contract is a written instruction to the agent, not
a program, because the difference between a preference and a rule is exactly whether
something can refuse you.

## The contract

**At the start of a book, look for `USER_PREFERENCES.md` at the repo root.**

| if it exists | if it does not |
|---|---|
| read it, and hold its preferences as **guidance for this book** | proceed with stock behaviour, silently |
| quote the relevant section when a decision turns on it | **do not mention that it is missing** |
| apply the *reason*, not the letter, so the guidance survives a case it was not written for | do not substitute a guess at what the user might have preferred |
| record, at the end of the book, which preferences applied and which did not fit | skip the step entirely |

**Nothing in `skills/` changes behaviour based on this file's contents.** No skill has a
conditional on it, no gate reads it, and `check-*.py` does not open it. A skill that
*appears* to enforce a preference has misread this document.

## Why there is no code

Three reasons, in order of how much they would have cost:

1. **A gate that reads preferences is a rule that reads preferences.** The moment a
   `check-thematic-names.py` exists and returns non-zero, "names should mean something"
   has become a threshold. It could then be argued with by someone who disagrees, and the
   user's preference would have to defend itself as a *measurement* — which it is not,
   because there is no corpus in which `Cora` scores worse than `Delphine`. The
   preference would survive; the user's authorship of it would not.
2. **Enforcement is a ratchet.** A preference applied as guidance can be declined in a
   particular case, and that decline is information. A preference applied as a gate can
   only be satisfied, so the interesting cases — where a plain name is right — become
   violations to work around rather than decisions to make.
3. **The file must be optional in the strongest sense.** If any skill branches on its
   presence, then its absence is a behaviour and its presence is a different behaviour,
   and the shipped harness is no longer the harness that was tested. Here, absence is
   indistinguishable from a user who has no preferences, which is the correct default.

## What the file may hold, and what it may not

`USER_PREFERENCES.md` (not shipped) may hold preferences, bad-review evidence, personal
prose tics, and structure/pacing standards. Each is stated as a preference with a
reason and a limit.

It may **not** hold anything the pipeline must obey. If a preference cannot be stated
without a "must", it is a specification, and specifications live in the gates where they
are frozen, hashed, and attributable.

## The distinction, stated once more because it is the load-bearing idea here

| | measured | chosen |
|---|---|---|
| example | `A25` fires above 3/2000 | "I dislike the word *leverage*" |
| derived from | 140 public-domain novels | you |
| arguable by | anyone, with the corpus | only you |
| changes when the data changes | threshold is re-derived | preference still stands |
| enforced by | a frozen gate | a reader, reading it |
| if you disagree | you are wrong and the corpus says so | you update the file |

The whole system is arranged so that a measurement can never launder itself into a
preference, and a preference can never launder itself into a measurement. `ERRATA.md` is
the channel for the first (a wrong measurement, with evidence, re-derived and re-frozen).
`USER_PREFERENCES.md` is the channel for the second (a choice, with a reason, read and
never enforced).

`GATE_FREEZE.md`'s Freeze 4 says the same thing about `check-names.py` from the other
side: the gate filters names the model reaches for by default, and the filter is
deliberately blind to whether a name is *good*. Those are different questions, they
belong to different files, and keeping them apart is what stops the second from becoming
a threshold without anyone deciding it should.

## Checking that the harness is still pristine

```bash
grep -rn "USER_PREFERENCES" skills/ tools/ --include="*.md" --include="*.py" --include="*.sh"
```

Every hit should be a document saying *this is how to use it*, never a branch on it. If a
future change adds a conditional — `if preferences: enforce(...)` — the harness has
stopped being pristine, and that change is the one to argue about.
