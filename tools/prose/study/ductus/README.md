# ductus — why the primary arm has none, and what the sensitivity books are for

**Decision:** `DECISIONS.md` §3. Design §4 recommended one shared neutral test ductus for all
20 Arm B books. That recommendation is dropped, and the reason is a fact about this repo
rather than a taste about prose.

## The primary arm runs UNASSIGNED

- `ductus.yaml` says outright: *"No book carries one yet."*
- `skills/incunabula/SKILL.md` resolves an unassigned book as drafted under the root
  `COMMONPLACE.md` alone — *"the state every book in the catalogue was drafted in."*
- Design §4 says Arm B runs the pipeline **as it actually exists**. A test ductus is a voice
  no production book has ever run under, so it would turn Arm B into "the pipeline plus a
  voice nobody authored" — a different arm.
- REDTEAM.md M7 feared a neutral ductus would sit outside the register the gates were
  calibrated on. The calibration corpus is catalogue books, and those are unassigned, so the
  no-ductus register is the calibrated one. A ductus is what would leave it.

Every primary Arm B row therefore records `ductus_id = UNASSIGNED`. It is the tool's own
word, it satisfies `manifest.py`'s non-empty rule, and unlike a blank cell it can be checked
against `python tools/ductus.py contract`.

## The sensitivity arm is six books under two authored voices

`ductus/study-voice-a/` and `ductus/study-voice-b/` (at the repository root) are
**instruments**, not production voices. Neither is assigned in `BOOKS.yaml` and neither
should be. They were authored to contrast with each other on the axes the study measures —
A long, periodic, semicolon-forward; B short, declarative, dialogue-forward — so the arm can
tell a property of *voice* from a property of *one hand*.

| voice book | premise | genre | voice | compared with its twin |
|---|---|---|---|---|
| `B-02V` | `adv-02` | adventure | `study-voice-a` | `B-02` |
| `B-03V` | `com-01` | comedy | `study-voice-a` | `B-03` |
| `B-09V` | `his-01` | historical | `study-voice-a` | `B-09` |
| `B-02W` | `adv-02` | adventure | `study-voice-b` | `B-02` |
| `B-03W` | `com-01` | comedy | `study-voice-b` | `B-03` |
| `B-09W` | `his-01` | historical | `study-voice-b` | `B-09` |

Premises were picked by hash of `study-voice-a|<premise_id>`, first pick per genre, so the
selection is reproducible and was not made by looking at which premises seemed promising.

Each voice book is compared **to its own twin**, not to the other twenty. Held constant:
pipeline, premise, drafting model. Changed: the voice. The per-feature difference is
therefore the voice's reach on that feature, which is a cleaner quantity than three books
against twenty strangers.

The contract is authored for reach, not merit. It differs from the pipeline's default on
axes this study measures — sentence length, semicolons, colons, paragraph length, dialogue
share — so a large movement is an *upper bound* on what a typical voice does. Its long
uniform sentences may trip `tools/prose/check-uniformity.py`'s spread gate; if that happens
it is logged in the row's `deviations` as a gate outcome, not tuned away, because it is
REDTEAM M7's register risk actually firing.

With two voices the arm can separate the two: a feature both voices move the same way is a
property of having a voice at all; a feature they move in opposite directions, or by clearly
different magnitudes, is a property of the contract. A feature only one voice moves is that
hand's idiosyncrasy. Two is a contrast, not a population, so the result is reported as
"these two voices, on these three premises".

`analysis/voices.py` is that reading, and it needs `python run/dispatch.py --plan` first:
without voice books it writes nothing and says so, rather than emitting an empty table that
reads like a null result.

The voice books must be kept out of the primary analysis — `analyze.py --exclude-books V,W`
— or six extra books inflate Arm B's medians from 20 to 26. Their premise ids (`02V`,
`02W`) already differ from `02`, so they cannot enter the 20-pair comparison by accident.

## Using it

```bash
python tools/ductus.py contract <book-root> --ductus study-voice-a   # what a run drafts under
python tools/ductus.py check                                        # contract sections authored?
cd ductus/study-voice-a && sha256sum -c ductus.md.sha256             # unchanged since freezing
```

The digest lives in the sidecar beside the contract, so there is one number in one place. If
the contract changes after the first voice book is generated, that is a protocol deviation
and the affected books are reported as a separate voice version — never silently pooled.

`COMMONPLACE.md` in that directory is empty on purpose: no decisions have been taken under
this voice, and seeding it with invented taste would make taste a default.
