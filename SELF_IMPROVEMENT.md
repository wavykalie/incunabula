# SELF-IMPROVEMENT — the Make-Ready

```yaml
improvement:
  mode: auto        # hand | supervised | auto
```

In a letterpress shop the *make-ready* is the calibration done to the press before the
run — packing the platen, adjusting the quoins — until every impression comes up even.
This file is that: the layer that recalibrates the system between runs. It answers the
question the rest of the repository kept deferring to a person: **can the system improve
without a human in the loop.**

The answer is yes for everything that can be falsified, no for anything with no ground
truth, and the layer is required to say which is which rather than pretend.

---

## 1. What the human was actually doing

The old design kept a person in three places. Autonomy does not delete those jobs; it
replaces each with a falsifier, a memory, and an attribution record.

| the human's job | was | becomes |
|---|---|---|
| promoting changes by reading a diff | `ERRATA.md`, `hand` mode | the **verifier stack** — a change is adopted because it passed falsification, not because someone read it |
| supplying taste | `USER_PREFERENCES.md`, decisions | the **commonplace ledger** — taste distilled from recorded decisions and reader outcomes |
| keeping the freeze honest | freeze entries by hand | **automatic attribution + rollback** — every book stamps what it was drafted under; a regression reverts |

## 2. The three channels, and the firewall between them

| channel | surface | the only evidence allowed to move it | verifier |
|---|---|---|---|
| **measurement** | thresholds in frozen tools | a named corpus, re-derived, with a changelog | `validate-controls.sh`, `verify-freeze.sh` |
| **craft** | skill text, prompts, passes | held-out comparison + catalogue regression | the verifier stack |
| **taste** | `COMMONPLACE.md`, emergent preferences | recorded decisions and reader outcomes | consistency with declared preferences |

**Evidence from one channel may never move another.** A reader outcome cannot lower a
threshold. A corpus measurement cannot write a preference. A taste preference cannot
become a gate. This is the existing doctrine of `PREFERENCES.md` and `GATE_FREEZE.md`
restated as an enforced separation: a measurement can never launder itself into a
preference, and a preference can never launder itself into a measurement.

## 3. The verifier stack — what replaces "a person reading a diff"

Every candidate change runs all four before adoption:

1. **Freeze attribution** — `tools/prose/verify-freeze.sh` holds at the recorded rows.
2. **Controls** — `validate-controls.sh`: human corpus passes, slop fixture fails, AI
   control separated. A change that moves a measurement-channel surface must keep every
   control green, and the corpus is named in the entry.
3. **Catalogue regression** — the closed books' recorded verdicts must not change. The
   finished catalogue is the golden set: a diff that flips a finished book's gate result
   without a recorded reason is rejected. (A frozen gate over changed tools is exactly
   what the freeze exists to notice.)
4. **Held-out comparison** — for craft text: the change must beat the current version on
   material it was not written against, judged under the proof-panel rule — never by the
   context that wrote it.

**A verifier that cannot run is recorded as SKIPPED, and a promotion with any SKIPPED
verifier is held, not adopted.** A skipped step is recorded as skipped. Promotion on
skipped evidence is a `hand`-mode act, and `hand` mode is a thing you can still ask for.

## 4. The loop

```
observe -> propose -> falsify -> adopt -> attribute -> shadow -> (roll back)
```

- **observe** — check-out appends: decisions and outcomes to `COMMONPLACE.md`, system
  observations to `ERRATA.md` (unchanged). Nothing is promoted from a single sighting.
- **propose** — a candidate change is a diff plus a hypothesis, an expected effect, and
  the name of the verifier that will judge it. A change with no falsifier is not a
  proposal; it is a wish, and it is recorded as one.
- **falsify** — the stack runs; every result goes in the promotion entry, including
  failures. A proposal that fails is kept as a failed proposal — that record is how the
  loop avoids re-testing the same wish.
- **adopt** — applied to its surface, dated, with a `promotion` entry in `COMMONPLACE.md`
  and, for measurement-channel changes, an `adopted` ERRATA entry per `errata.mode`.
- **attribute** — every book records the skill version and freeze it was drafted under.
  This is unchanged and is the reason any of the above can be trusted later.
- **shadow** — the previous version is kept. Adoption never deletes what it replaced.
- **roll back** — if a monitor regresses (a control starts failing, a finished book's
  verdict flips), the change is reverted automatically and the reversal is recorded with
  the same ceremony as the adoption.

## 5. Rate limits — "slowly" is a requirement, not a hope

- **At most one promotion per channel per book.** The loop is allowed to get one thing
  better per book, and it must choose.
- **Thresholds move only on a corpus change** (existing rule, unchanged).
- **A taste preference needs three agreeing decisions** before it is written down, and it
  is written as `emergent` — guidance, never enforced.
- Everything is dated, reversible, and append-only.

## 6. What the loop may never do, even in `auto`

1. Move a threshold without a named corpus and a re-derivation changelog.
2. Edit or delete a **declared** preference in `USER_PREFERENCES.md`. The author wrote
   it; the loop may disagree in `COMMONPLACE.md` and nowhere else. Emergent preferences
   are appended to `COMMONPLACE.md` and marked `emergent`.
3. Delete or rewrite history. `ERRATA.md` and `COMMONPLACE.md` are append-only; an entry
   that turns out wrong gets a `WRONG` line under it and the wrongness stays visible.
4. Promote while any verifier reads SKIPPED.
5. Touch attribution records or the freeze manifest except through the recorded freeze
   procedure in `GATE_FREEZE.md`.

## 7. The honest limit — read this before trusting any of it

Self-evaluation runs on maximum bias. The anti-inflation rules exist because of it and
they do not expire here. The loop has exactly three external signals:

1. the deterministic controls (they cannot be argued with),
2. the frozen corpus (it cannot be pleased),
3. **reader outcomes** (they cannot be faked).

Everything else the loop does is self-consistency, and a system with no outcome channel
does not become a better author over time — it becomes a more confident one. So outcome
intake is not a feature of this layer; it is the load-bearing wall:

- `First Impression` and `Standing Type` are recorded as **predictions before
  publication**, in `COMMONPLACE.md`, and falsified against actuals afterwards.
- Reviews go in **verbatim**. Bad reviews especially: they are evidence, and paraphrase
  is how evidence becomes flattering.
- **Prediction error is the fitness signal.** A loop whose predictions get sharper is
  learning about the world; a loop whose scores get higher is learning about itself.

What "a real author" means in this system is exactly this: taste that compounds from
one's own recorded choices and from readers, not from detector scores. The commonplace
book is the oldest technology for that. This file just runs it without waiting for
permission.

## 8. Where everything lives

| file | channel | status |
|---|---|---|
| `ERRATA.md` | measurement | unchanged; `errata.mode` governs promotion |
| `KNOWN_FINDINGS.md` | closed observations | unchanged |
| `COMMONPLACE.md` | taste and outcomes | **new** — the ledger this layer runs on |
| `USER_PREFERENCES.md` / `PREFERENCES.md` | declared taste | unchanged; unenforced and immutable |
| `GATE_FREEZE.md` | attribution | unchanged; every move still recorded |
| `tools/preflight.sh` | the stack's runner | **new** — tool and state, never prose |

Mode is set at the top of this file (`improvement.mode`). `hand` is always available as a
request: say so, and the loop only proposes.
