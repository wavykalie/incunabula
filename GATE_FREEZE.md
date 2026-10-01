the ten controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only) |# Gate freeze

**Frozen:** 2026-09-27 · **Corpus:** 6 fiction + 6 non-fiction volumes, 5+6 authors
**Suite status at freeze:** all ten controls pass (exit 0)

A book generated against these gates is a test against a *known instrument*. If a gate
changes afterwards, the freeze is what tells you the book was not tested against the thing
you are now looking at. Without it, a re-derived floor silently rewrites what a
generation run was evidence for — which is exactly what happened to `U1` earlier today,
when its published band turned out to come from a translated light novel.

## Manifest (FREEZE 4 - current)

| file | sha256 (first 16) | role |
|---|---|---|
| `tools/prose/deslop-check.sh` | `20e1976d20312974` | density + slop caps, HARD / DEMOTED / REPORT tiers (Freeze 12 - A22 self-scan re-keyed to a marker file) |
| `tools/prose/check-uniformity.py` | `61a9b72bf86d31c7` | U1–U6 cross-chapter rows |
| `tools/prose/check-drift.py` | `814ca33e9e684ee7` | voice drift, size-dependent floor (Freeze 2 - Spearman tie fix) |
| `tools/prose/check-arc.py` | `f2059aec8a9580cc` | A1 gate; A2–A4 report-only |
| `tools/prose/check-surplus.py` | `ff9e851c6f0b91ab` | S1–S4, report-only |
| `tools/prose/check-recoverable.py` | `591c61560d8c53b3` | tic × dialogue enrichment, report-only |
| `tools/prose/check-errata.py` | `e9724056d7a3f18c` | protocol validator, reads no prose (Freeze 3 - floor 30) |
| `tools/prose/check-length.py` | `6dd9d862d275bff3` | declared-length row `L1` (Freeze 2 - added after the sons-of-heaven-v2 run exposed the deletion incentive; Freeze 8 - exit 3 for ungoverned) |
| `tools/prose/check-names.py` | `6fcb3bd0dd1ae1c2` | cross-book cast-name collisions + default-name filter, reads no prose (Freeze 4 - added after the author found `Priya` in two books) |
| `tools/prose/calibration/NAME_FREQUENCY.tsv` | `f17e837f6f2ae0a5` | the name-frequency data `check-names.py` reads (Freeze 4) |
| `tools/prose/calibration/NAME_FREQUENCY.md` | `75f6fa0dae36f327` | provenance + the tier reasoning; frozen because it states what the tiers mean (Freeze 4) |
| `tools/prose/validate-controls.sh` | `f76ee16eaaddb943` | the ten controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only) |

Also frozen, because they change what the gates *see* rather than what they assert:

- `tools/prose/calibration/CALIBRATION.md` — every measurement behind the numbers
- `PRINTERS_COPY.md` — 25 rejected measures, 6 confirmed
- `ERRATA.md` — 32 entries
- `skills/` — the prose skills that generate the text under test

## Load-bearing thresholds at this freeze

| row | value | derived from |
|---|---|---|
| `U1` chapter-length CV | fail < 22%, warn < 28% | worst of 6 English fiction volumes = 33.4% |
| `U2` sentence-length spread | fail < 3.0, warn < 4.0 | published min 4.32 |
| `U3` coda share | fail > 25% of chapters | 0 of 50 published chapters |
| `U4` one-line paragraph share | **advisory by default** | 59% of 140 PD novels fail it |
| `U5` paragraph-length CV | fail < 55%, warn < 75% | 0 of 140 PD novels fail it |
| `U6` signature-frame spread | fail > 40% of chapters | worst published volume 23% |
| `D1` em dash | **report-only** | control sits at 0.00/1k; cap clears 14% of published chapters |
| `D2` rule of three | **report-only** | cap clears 18.6% of published chapters |
| `D3` adverb density | enforced | clears every published chapter; detector value unproven |
| `A25` antithesis | fail > 3/2000 | 1.5× the worst published chapter (0.93/1k) |
| `A1` reversals per bin | size-dependent, 0.35 at ≤2 windows | 0 of 40 published novel means fall below |
| drift | size-dependent, 3.41 at 4 ch → 1.40 at 20+ | worst published book at each chapter count |

**Convention-scoped rows.** A book declaring `positioning: nonfiction` carries `U1`, `U4`
and `U5` as advisory. A book declaring `paragraph_convention: commercial-dialogue` holds
`U4` to the market gate. `Sons of Heaven, Students of Dust` declares
`positioning: "nonfiction"`.

## What a pass does and does not mean

- A green run means the prose cleared the rows listed above. It does **not** mean the
  gates were all able to see the book's actual weaknesses — `A1` misses the AI control
  entirely, `D1` reads 0.00/1k on it, and the drift floor is known to miss roughly one
  real voice change in eight.
- Six of the rows are advisory or report-only, so a green run is partly a statement that
  nothing was *gated*, not that nothing was found.
- The gates are calibrated on 1813–1905 English prose. Nothing commercially recent is in
  the corpus, and a stylometric finding about period prose measures the period.

## Freeze 2 — 2026-09-27, supersedes Freeze 1

Raised during the `sons-of-heaven-v2` run, after two gates were corrected. Books drafted
under Freeze 1 keep it; this entry records the move and why, so neither hash set is
orphaned.

| file | freeze 1 | freeze 2 | why it moved |
|---|---|---|---|
| `check-drift.py` | `3f387eda5d8cdf70` | `819505b173b9afac` | `trend_of()` gave tied values sequential ranks, so a constant series became a 1,2,3..n ramp and correlated perfectly with chapter position by construction. It reported dialogue share at rho +1.00 for a book with zero quoted speech. Fixed, verified on synthetic input |
| `check-errata.py` | `fc8d54b8225f66a1` | `9b0b8034376561d0` | `REJECTED_FLOOR` raised 21 -> 23 -> 25 -> 26 as the Rejected registry grew. The floor is a memory, not a threshold |

A second update later the same session, also recorded here rather than re-hashed silently:
`check-errata.py` (`REJECTED_FLOOR` 26 -> 29) and `validate-controls.sh` (control 11 added)
moved again, and `check-length.py` was added to the manifest. The verifier caught its own
stale manifest, which is the intended behaviour of a guard whose hashes are the whole
mechanism.

A third update, recorded at the point the v2 manuscript reached its declared length.
`check-errata.py` moved once more (`REJECTED_FLOOR` 29 -> 30) as the Rejected registry
grew, and the verifier flagged its own manifest as stale rather than passing quietly.

**No gate that reads prose has moved since Freeze 1.** Verified by hash at the point the
book was finished:

    deslop-check.sh       f3651dfd18fcd166  Freeze 1
    check-uniformity.py   61a9b72bf86d31c7  Freeze 2
    check-drift.py        819505b173b9afac  Freeze 2
    check-arc.py          df9029bc2f4142c7  Freeze 1

`check-errata.py` validates the self-improvement protocol and reads no manuscript text, so
its movement cannot change any reading of `sons-of-heaven-v2`. That is the reason this
is Freeze 3 rather than an invalidated run, and the distinction is the whole point of
recording it instead of re-hashing silently: a freeze is a claim about the instrument,
and the claim is only worth anything if the exceptions are named.

Nothing else moved. `deslop-check.sh`, `check-uniformity.py`, `check-arc.py`,
`check-surplus.py`, `check-recoverable.py` and `validate-controls.sh` are unchanged from
Freeze 1.

**Consequence for the run.** The `sons-of-heaven-v2` gate results were taken against
Freeze 1 for uniformity, arc, deslop and surplus, and against the *fixed* drift tool for
the drift rows. The uniformity result — the one that failed on `U6` at 91% and drove 22
revisions — was against Freeze 1 and is unaffected, since that file did not change.

**Load-bearing thresholds are unchanged between freezes.** The `U1` re-derivation
(22%/28%) and the `A25` raise (3/2000) both landed before Freeze 1 was taken.

## Changing the freeze

Any edit to a file in the manifest ends the freeze for future runs. Do not re-freeze
silently: append the new hashes, the date, and the reason to this file, and re-run
`validate-controls.sh`. Existing books keep the freeze they were generated under — that
is the point of recording it.

## Freeze 4 — 2026-09-28, supersedes Freeze 3

Raised during the `the-origin-point` run, for a defect in the *suite* rather than in a book.

**A cast name shipped in two books and nothing in the suite could see it.** The coroner in
`the-origin-point` was named `Priya Raghunathan`; `Hollow Bridge` already had a co-lead also named `Priya`, and a reader persona in `incunabula-test` was also called Priya. The
author caught it. No gate did, and none could have: `check-uniformity` reads chapter to
chapter inside one book, `check-drift` reads prose shape, `check-arc` reads structure,
`check-errata` reads no manuscript at all. **Not one of them had ever opened a second book.**
A name is the only part of a cast that crosses a book boundary, and a returning reader is
the only reader positioned to notice.

`check-names.py` is added to close that. It is not a prose gate and reads no manuscript, so
adding it does not re-derive any floor from any book's own results.

**A second defect, in the verifier itself.** `check-length.py` had been listed in the
manifest since Freeze 2 with its hash *unquoted in backticks*, while every other row quoted
its own. `verify-freeze.sh` extracts rows with a regex that requires the backticks, so it
had been silently skipping the `L1` row — reporting `FREEZE HOLDS` on 8 of 9 files, and never
hashing the one gate that enforces the declared length floor. The `the-origin-point`
contract is 80,000 words, and the gate responsible for it was the one gate nobody was
checking. Fixed by quoting the hash; the gate file itself did not change and its hash is
identical before and after. The lesson generalises: **a freeze is only as good as the parser
that reads its manifest, and a silently-skipped row looks exactly like a passing one.**

**Two defects in `check-names.py` itself, found by its own first run and fixed before freeze.**

| defect | symptom | why it matters |
|---|---|---|
| harvester read free prose | reported `Paper Cage` (a comp title) and `Gives Rusk` (a sentence) as characters; 12 "first names" for a 7-person cast | a cast check that reads prose reports whatever else is capitalised, and the first clean PASS it produced was luck rather than correctness |
| `rstrip("'s")` on possessives | turned `Holli's` into `Holli` | `rstrip` takes a character *set*; the truncated name read as a different character and invented a collision that did not exist |
| single bare name part counted as a person | `Rusk's own signature` (a document) entered the protagonist's own first-name set | the book collided with itself |

Verified on a deliberate negative control — a copy of the book with the old name restored
fails with exit 1 and names Hollow Bridge — and against `incunabula-test`, whose reader personas
are correctly *not* read as cast. The gate has one real finding outstanding and it is not a
defect: **`Okafor` is shared.** `Sam Okafor` in `the-origin-point` and `Mrs. Okafor`, a
corner-store neighbour in `Hollow Bridge`. Reported as a surname warning, because a
shared surname is sometimes deliberate. The author has been told and has not yet ruled.

`verify-freeze.sh` was not modified. Fixing its manifest row was the correct repair; changing
the verifier to tolerate a second hash format would have made it more permissive at exactly
the moment it needed to be stricter.

### The default-name filter, added 2026-09-28 (same freeze)

The author's position, stated precisely because it is easy to collapse into one rule:
**names should carry meaning** — the flower, the ancestor, the thing the character is —
**and that must never become a program rule.** A gate enforcing it would be unable to
produce a plain name for a character who needs one, and would convert a preference into
a rule generating a different preference in disguise: choosing flowers because the gate
said flowers.

What belongs in the pipeline is the *opposite* move: a filter on the model's high-prior
names. So the two were separated.

**The premise was tested and is only half true.** The claim is that models converge on
familiar names. Measured across all four AI-generated books (72 files, 213,772 words),
looking for names appearing in 3+ independently-generated books — none of which read each
other — the result is **one token** (`In`). Cross-book convergence on given names is
**essentially zero.** What is real is not convergence *between* runs; it is a strong prior
*within* the training distribution, which is a different claim and needs a different
measurement.

**The 1813–1905 corpus cannot supply that measurement, and the reason is the same one
`U1` hit.** Nineteenth-century fiction names characters behind honorifics — *Miss Bennet*,
*Sir William*. Over 303 files / 945,924 words, the most frequent first tokens are `Miss`
(802), `Sir` (326), `Lady` (165), `Mrs` (116), `Mr` (69). `Elizabeth` appears **twice**;
`Roy` and `Ruth` appear **zero times in 946k words of published fiction.** A threshold
derived from that corpus would not measure model defaults — it would measure that
pre-1900 English prose does not often write names in the two-word capitalised form this
filter reads. `A stylometric finding about period prose measures the period`, and this is
that mistake again in a new place.

**So the denominator is real-world name frequency**, a public dataset about actual people
rather than about transcription conventions:

| tier | source | size | severity |
|---|---|---|---|
| A | SSA national top 20, births 1926–2025 | 20 | **FAIL** |
| B | Nameberry top 100 girls + 100 boys, 2025 | 199 | **WARN** |

Tier B is deliberately not a failure. `Cora` is Nameberry #28 and is also the *correct*
name for a woman born in 1951 in a rural American county. Popularity measures what a name
is **now**; a cast is mostly people named long before now. What makes a popular name a tell
is **anachronism**, and a gate cannot know when a character was born — the author can, in
one sentence. A first pass of this gate carried a hand-written list of names that "felt
common," which is the very thing a measurement must not be; it was replaced by the TSV.

Data frozen alongside the gate so a result is attributable to a fixed file, not to whatever
a website served on the day. `verify-freeze.sh`'s row regex was widened from
`[a-z-]+\.(sh|py)` to also match `tsv` and `md` — otherwise the two data rows would have
sat in the manifest looking frozen while nothing hashed them, which is the same silent-skip
shape as the `check-length.py` bug above.

**Result across the catalogue: no book has a Tier-A name.** Three Tier-B warnings across
the three cast books (`Cora`, and two further names in the book — both correct for
their eras, which is the row working as intended rather than failing).

Verify a freeze with:

```bash
cd tools/prose && for f in deslop-check.sh check-uniformity.py check-drift.py \
  check-arc.py check-surplus.py check-recoverable.py check-errata.py; do
  printf "%-24s %s\n" "$f" "$(sha256sum $f | cut -c1-16)"; done
```

---

## Per-user preferences are not part of the instrument (2026-09-28)

`USER_PREFERENCES.md` is gitignored and untracked, and **nothing reads it** — no skill
branches on it, no gate opens it. `tools/prose/PREFERENCES.md` is the whole contract, and
it exists to be the only place that describes it.

This is recorded in the freeze because the reasoning is the thing most likely to be
undone by a well-meaning later change. The author holds preferences — that names should
carry meaning, that bad reviews are evidence, that some tics are personal rather than
measured. The tempting move is to encode one as a rule: `naming: thematic`, or a
`check-thematic-names.py` that returns non-zero. That would be the preference surviving
and the **authorship of it** not surviving, because:

- there is no corpus in which `Cora` scores worse than `Delphine`, so an enforcing check
  could only ever be a taste wearing a measurement's clothes;
- enforcement is a ratchet — a preference applied as guidance can be declined in a
  particular case, and that decline is information, while a preference applied as a gate
  can only be satisfied, so the cases where a plain name is right become violations to
  work around;
- if any skill branches on the file's presence, its absence becomes a behaviour and the
  shipped harness stops being the harness that was tested. Here, absent is
  indistinguishable from a user with no preferences, which is the correct default.

The asymmetry is deliberate: **a measurement can never launder itself into a preference,
and a preference can never launder itself into a measurement.** `ERRATA.md` is the
channel for the first — a wrong measurement, evidence required, re-derived and re-frozen.
`USER_PREFERENCES.md` is the channel for the second — a choice, reason required, read and
never enforced. `check-names.py` sits deliberately on the third side of both: it filters
names the model reaches for by default and is **blind to whether a name is good**, because
that question belongs to the author and the voice matrix.

To confirm the harness is still pristine:

```bash
grep -rn "USER_PREFERENCES" skills/ tools/ --include="*.md" --include="*.py" --include="*.sh"
```

Every hit should be documentation. A `if preferences:` conditional is the regression.

---

## Finding, 2026-09-28 — the naming preference was exercised and nothing moved

A demo book (`demo-galactic`, outside this repo) was run through the naming phase to test
`USER_PREFERENCES.md` §1 — thematic meaning — against a frozen suite. Result:

- `check-names.py` on five hand-derived names (St Swithin's Day, *hesper*, *parr*, Old
  English *anstice*, and one deliberately plain name): **OK**. No tier hit, no collision.
- Negative control with `Anstice` -> `Emma` and `Swithin` -> `Priya`: **FAIL**, 8 conflicts
  + 1 TIER-A. Both failure modes fire.
- **`FREEZE HOLDS 12/12`, byte-identical before and after.** The demo moved no gate.
- Pristine check: every `USER_PREFERENCES` hit in `skills/` and `tools/` is documentation.
  No branch. The demo produced names no gate could have produced, and no gate objected —
  which is the separation working, not the separation failing.

**The finding worth keeping.** Two name sets, one filtered, one judged, produced the same
verdict for different reasons and by different mechanisms. The gate asks *"did the model
reach for this?"* The preference asks *"did someone choose this?"* Both answered honestly
and neither could answer the other's question. Had the preference been enforced, the freeze
would have broken on 2026-09-28 and every prior result in this file would have become
unattributable — a preference entered through the gate would have retroactively
invalidated the measurements that came before it.

A gate that judges meaning would not merely be a bad gate. It would be a gate whose
existence changes what the frozen numbers mean.

---

## Freeze 5 — 2026-09-28: the two gates that read the premise phase

The audit that produced these found that every pre-existing gate begins at
`manuscript/chapters` and reads one book at a time, and that **zero gates read
`research/`**. The research phase produces the document that says what the book IS, and
it was entirely ungated. Two instruments added, neither of which touches prose.

### P1 `check-premise-distinct.py`
FAILS a book whose protagonist **profession AND engine** match a row in the frozen
PREMISE_LEDGER.tsv; WARNs on two axes matching; passes on one or none. The two-axis floor
is the design: same job in two books is normal in every series ever written, and a gate
that fired on profession alone would fail all of them.

**It is a collision check, not an originality check, and the distinction is load-bearing.**
Originality is a judgement about quality; collision is a fact about a catalogue. Only the
second is measurable here. A book can pass this and still be derivative — and it cannot
see the published world at all, so `Paper Cage` remains invisible to it.

Verified: collision fires (3 axes, exit 1) · unspent premise passes (exit 0) · same
profession with a different engine passes — the false-positive case the two-axis floor
exists for · a book declaring no axes exits 2 rather than passing · malformed ledger
rows are skipped loudly, because a ledger that drops rows silently hides the collision
it exists to find.

### C1 `check-comps.py`
FAILS a research file whose comp table contains a row with neither a `**VERIFIED` date +
source stamp nor a recorded falsification.

**A stamp is a witness, not a proof.** This gate cannot tell a real book from an invented
one, and a fabricated citation with a stamp on it passes. Worse, it is blind to the error
that costs most: a real and perfectly on-point comp nobody thought of. *Paper Cage* was
missed while four fabricated titles sat in the file — the research was busy being wrong
about books that did not exist and had no attention left for the one that did.

**Two defects found and fixed during construction, both recorded because both were silent:**
1. Scanning every table row and guessing flagged four rows of the RISK REGISTER — a
   conclusions table — and passed the actual comp table only by luck.
2. The header regex then searched for `title` *anywhere* in a cell, so a risk row reading
   "| Something with *An Italic Title* in it |" re-anchored the gate onto the wrong table.
   It reported 0 unverified and exited 0 **while no longer watching the comp table at
   all.** A silent false pass. Fixed by matching the whole header cell rather than a word
   inside it.

On the live research file it correctly reports the comp table at line 19 and flags two
rows — `The Burning Girls` and `Apple Tree Yard` — which are marked "REAL — year and
genre wrong". Partial verification is not verification, which is the correct reading.

### New frozen files
| file | sha256 (first 16) | role |
|---|---|---|
| `tools/prose/check-premise-distinct.py` | `852541b840442e94` | premise job+engine collision vs the author's own catalogue (Freeze 5) |
| `tools/prose/check-comps.py` | `9f47751a6a45aefa` | comp-title verification stamps; reads research/, not prose (Freeze 5) |
| `tools/prose/calibration/PREMISE_LEDGER.tsv` | `1751102150c3ad6b` | the spent-premise data `check-premise-distinct.py` reads (Freeze 5) |

### What was NOT added, and why
No trope-density score. The moment "this book uses 14 detected tropes" is computable, the
number becomes the target and the book is engineered to sit just under it — the
redundancy problem manufactured rather than prevented. The five gates remain what they
have always been: measurements of one book's prose.

### Defect found in P1 after freezing, 2026-09-28 — self-collision

**`check-premise-distinct.py` compared the book under test against its own ledger row.**
A completed book is *in* the ledger — that is the ledger's purpose, and the seed file
carries rows for books already written — so running the gate on `the-origin-point`
reported "EXACT ENGINE + RELATIONSHIP: matches on profession + engine + relationship" and
exited 1. **The gate failed the finished book for being identical to itself.**

Found by running the new gate on the one real book in the catalogue, which is the only
thing that would have surfaced it. A gate that cannot be run on a completed book is a gate
nobody runs, and a gate that fires on itself teaches its reader to discount it.

Fixed by excluding the book under test's own ledger row, with the exclusion printed so it
is visible rather than silent. Verified both directions: the real book against its own row
now **passes** (exit 0, own row shown as excluded), and a new book carrying the same axes
still **fails** (exit 1, collision against `the-origin-point`). Hash re-recorded above;
this is a defect fix, not a threshold change, so no other row moved.

---

## Freeze 6 — 2026-09-28: the instrument class is closed

**This freeze raises no hash.** No gate file changed. `verify-freeze.sh` returns
`FREEZE HOLDS - 15/15` byte-identical to Freeze 5. Freeze 6 records a *policy* — what
may and may not become a new instrument — and exists so that the decision is not
re-litigated in a later session by someone who has forgotten it.

### The ruling

**No new gate. No new gate *class*.** Fifteen rows, five prose gates, two
research-reading gates, two data files, one control runner, and that is the instrument.

This is a refusal, not a gap. A gate that catches something real is still a cost: it is
a threshold somebody has to defend, a false-positive class that will eventually fire on
correct prose, and a number that can be gamed by writing to it. Every instrument added
so far has earned its place, and every one of them has also cost a session. The marginal
gate is no longer the problem to solve. The problem to solve is the *loop*, and the loop
is made of re-reporting, not of missing coverage.

**If a check is wanted, it becomes a checklist line inside an existing phase. It does not
become a script.** The distinction is not style. A script has an exit code, and an exit
code is a verdict, and a verdict is what the loop feeds on. A checklist line is read by
the author, who already knows the answer, and cannot generate a new session.

### The consolidation question, answered and closed

Asked directly: *can any gates be consolidated?* The answer is **no, and here is the
measurement** so it is not asked again.

The duplication is real and small. Across the five prose gates:

- the `CHAPTER` filename regex is **byte-identical in all five**;
- `load()` is **byte-identical in all five** (verified: same md5 of the same eight lines);
- `resolve()` differs only in blank lines and wrapping, and is semantically the same.

That is roughly fifteen lines, five times: about 75 duplicated lines.

Two refactors were considered and both refused.

**Merging the gates themselves — refused, permanently.** They measure different things
off different calibrations at different severities: `U1` hard-fails, `U4` is advisory,
`D1` is report-only. A merged binary cannot report *which* row failed, which is the
only part of the output anyone acts on. It would also collapse a 15-row attributable
manifest into a few opaque ones, and four books already carry results attributed to
specific hashes — so merging makes the *existing* catalogue unattributable retroactively.
That is the precise failure this file exists to prevent, and it would be caused by
tidying.

**Extracting the shared loader — refused *for now*, not forever.** It is mechanically
safe and genuinely good engineering, and it is the wrong move today for one reason: it
moves five hashes, which is a Freeze 6, which invalidates the attribution on every
finished book — in the same session whose purpose was to stop churn. 75 lines does not
buy that.

If it is ever done it is done **once, deliberately, as its own freeze**, with the old
hashes preserved and existing books keeping the freeze they were generated under. Never
as a side effect of cleaning up. This paragraph exists so that decision is a plan rather
than an accident.

### What replaces defect-hunting as the activity

Two things, both already in the catalogue, and the second is the one that matters:

1. `KNOWN_FINDINGS.md` — findings the author has declined, one line each, closed. A
   gate that produces one keeps firing; the *answer* moves to a table instead of to the
   next session's memory. Recognition closes the loop. Suppression would not, and would
   additionally be a lie in this file.
2. A **single full-manuscript sweep at the end of the book**, not per-chapter hunting.
   A chapter always has something in it. A whole book does not, and a whole-book pass
   terminates.

Per-chapter gate runs are now expected to be *quiet*. The drafting loop runs the prose
check and the ledger; everything else waits for the sweep. A finding that arrives outside
the sweep is a finding about a gate, not about the book, and goes to `ERRATA.md`.

### The one exception, and why it is not a sixteenth row

`tools/sync-skills.py --check` verifies that `incunabula/skills/` — the authoritative
copy — is byte-identical to what is installed in `~/.claude/skills/` and
`~/.agents/skills/`. It is deliberately **not** a sixteenth row.

It is not a gate because it measures nothing about a manuscript. Every one of the fifteen
rows answers a question about a book; this one answers a question about which copy of
the *tool* will run. That distinction matters more than it looks: a book drafted from
scratch against a stale installed copy would produce a real, plausible, completely
meaningless measurement. The failure is not visible in the manuscript — it is visible
only here.

It is exempt from the "raise no hash" rule because it moves no gate file. Adding a row
here would freeze a check *about the freeze mechanism*, and the next session to touch a
gate would have to re-record it. Run it explicitly, at the start of a drafting session
and after any edit under `skills/`:

    python tools/sync-skills.py            # sync repo -> both destinations
    python tools/sync-skills.py --check    # report only, exit 1 on drift

Superseded v4-named skills are moved to `~/_skills-quarantine-20260929/`, never deleted,
each with a `_SUPERSEDED_BY` provenance file. See `ERRATA.md`, 2026-09-29.

### Verified at this freeze

    deslop-check.sh          f3651dfd18fcd166  ok
    check-uniformity.py      61a9b72bf86d31c7  ok
    check-drift.py           819505b173b9afac  ok
    check-arc.py             df9029bc2f4142c7  ok
    check-surplus.py         ff9e851c6f0b91ab  ok
    check-recoverable.py     591c61560d8c53b3  ok
    check-errata.py          e9724056d7a3f18c  ok
    check-length.py          9d8f3a1b0bbbdfcf  ok
    check-names.py           6fcb3bd0dd1ae1c2  ok
    calibration/NAME_FREQUENCY.tsv f17e837f6f2ae0a5  ok
    calibration/NAME_FREQUENCY.md 75f6fa0dae36f327  ok
    validate-controls.sh     84a6bef3539efaa8  ok
    check-premise-distinct.py 852541b840442e94  ok
    check-comps.py           9f47751a6a45aefa  ok
    calibration/PREMISE_LEDGER.tsv d3f19efeaad10d73  ok
    FREEZE HOLDS - 15/15

### Defect found by shipping it, 2026-09-28 — the freeze was not portable

Committing the suite produced a defect that no amount of local testing could have found,
because the defect is *in the repository and not in the working copy*. Cloned clean and
verified:

    validate-controls.sh     24bfb66ff11d52aa  CHANGED (frozen 84a6bef3539efaa8)
    14 of 15 rows ok

The same file hashes `84a6bef3539efaa8` in the working copy the manifest was written
against. Git's default line-ending conversion rewrote CRLF to LF on commit, so **the blob
stored in the repository was not the file the hash was taken from.** The freeze was
verifiable on exactly one machine — the one that recorded it — and a freeze that only one
machine can check is a private note, not evidence.

Fixed by adding `.gitattributes` with `* -text`, which disables end-of-line conversion in
both directions, and re-staging the one affected file. All fifteen rows are now
byte-identical between the index, the working copy, and a fresh clone. **Verified by
cloning and re-running the verifier, not by re-running it locally** — which is the only
test that could have caught this, and is now the standing acceptance test for any change
to a frozen file:

    git clone <repo> /tmp/x && cd /tmp/x && bash tools/prose/verify-freeze.sh

**The rejected alternative.** Normalising the repository to LF and re-recording all
fifteen hashes would also have fixed it, and would have been a real Freeze 7 invalidating
the attribution on every finished book. Byte-exact storage moves no hash and costs one
file. The lesson generalises past line endings: **a hash computed on a working copy is a
claim about that copy until something has read it back from somewhere else.**

## Freeze 7 — one row moves on purpose, 2026-09-28

    deslop-check.sh    f3651dfd18fcd166 -> 1ccdd3aef10b9797   Freeze 1 -> Freeze 7
    14 of 15 rows unchanged.

Two defects in one row, both found the same way: by running the gate on a book it had
never been run on, then reading what it said. Neither was found by a control failing,
which is the point — the controls test the caps, and both of these were below the caps.

Freeze 6 closed the instrument class: no new gate, no new gate class. It did not close
*correctness of an existing gate*, and this is a correctness defect, found the only way
one ever is — by running the gate on a book it had never been run on.

**The defect.** Every sentence-level rule in `deslop-check.sh` splits on `[.!?] ` —
punctuation followed by a **space**. A stray CR sits exactly where that space belongs, so
the split never happens and the boundary is never seen. Fifteen of Merope's twenty-two
chapters carry `\r\r\n`, and the awk counted 22 sentences in a chapter that has 43. P1's
share was therefore computed against half the text it claimed to cover.

    book-1/chapter-01   P1  ok    "it is" x4   ->  FAIL  "it is" x5
    book-1/chapter-10   P1  ok    "they were" x2 -> FAIL "they were" x3
    book-2/chapter-05   P1  ok    "i have" x3  ->  ok    "that is" x5   (a different key is now top)

Those chapters were not passing those rows. They were evading them, and a green result
was being read as evidence — which is the specific harm this whole project keeps
refusing to accept.

**The fix, and what it deliberately does not do.** Normalise line endings once in the
read path, before any row is measured. No cap moved, no rule added, no gate added, no
threshhold re-derived. The numbers are now what the existing caps always meant. It is
fixed in the read path rather than per row because "this file is normalised" is a
property of the *read*, not of any single rule — and the function's existing cleanup
already removes any temporary copy, since it tests only whether `$f` differs from
`$orig`.

**Measured, including the part that is NOT broken.** Ordinary CRLF does *not* trigger
this. awk reads in text mode and eats one CR per LF, so a plain CRLF file arrives clean:
a synthetic CRLF control reads 4 sentences either way, and demo-magician's 34 CRLF
chapters are **byte-identical before and after this change** across 79,204 bytes of
output. Only a lone or doubled CR survives as a stray byte. An earlier survey had called
demo-magician clean because it tested for lone CR only; that test answered the wrong
question and happened to reach the right answer.

**The guard that did not fire.** The first version detected CR with `grep -q $'\r'`. It
never fired, and would have shipped as a fix that was not a fix: the file under test has
86 CR bytes and `grep -c $'\r'` on it prints `0`. On this platform grep cannot see the
character the fix is about. The detector is now `tr -cd '\r' | wc -c`, which sees all 86.
**A guard that reports a condition it did not detect is the worst kind of defect in a
gate**, and the only defence is to confirm the guard fires before trusting it — which is
the same lesson as the clone test above, one layer down: *a check that has never been seen
to fail is not yet known to work.*

**The second defect: A25 matched inside a word.** The regex had no word boundary after
`not`, so `was NOTHING in it worth the walk. It was ...` matched — the pattern took
`was not` and then `hing in it worth the walk` as the intervening clause. That is a
substring accident wearing the costume of an antithesis formula. Reading all 25 A25 hits
in Merope out one at a time: **24 are the real construction, 1 is that accident.** Fixed
by adding `\b`, one character.

The direction of the fix is the argument for it: adding a word boundary can only ever
*remove* matches, so no cap moved and nothing that passed can start failing. Leaving it
would have meant editing a correct sentence in a finished book to dodge a substring —
charging the manuscript for the instrument's error, which is backwards. The positive
control still fails A25 at 4.12/1k, so the tic it exists to catch is still caught.

**Acceptance.** `verify-freeze.sh` 15/15 with the new row recorded. The positive control
still fails the gate (`slop-fixture.md`, unchanged behaviour). `validate-controls.sh`
exits 2, not run — the calibration corpus is commercial prose and deliberately not
shipped, so the caps remain UNVERIFIED by that path and this change did not alter them.
Regression run, old gate from `HEAD` against new, four targets:

    demo-magician (34 ch, 77k w)   IDENTICAL  79,204 bytes
    slop-fixture.md                IDENTICAL   3,202 bytes
    validation-series/book-1       DIFFERS    14 rows, 2 newly FAIL
    validation-series/book-2       DIFFERS     9 rows, 0 newly FAIL

**The other half: the files.** The gate now normalises its read, but the Merope chapters
were still carrying `\r\r\n` on disk. All 22 rewritten as plain LF, with the text verified
identical apart from line endings and every gate row unchanged — which is the expected
result, since the gate was already normalising. `demo-magician` was left untouched: it is
plain CRLF, which this platform reads correctly, and touching it would be churn.

**One more correction to the record.** While fixing this, a locator written earlier was
found to disagree with the gate on 22 of 22 chapters, and three separate causes were
isolated: it read files with Python's universal newlines, it compared A25 as `n*1000 > 3*w`
when that cap is `3/2000`, and it printed rows whose keys could not match the gate's. All
three were bugs in the locator, not the gate. It now agrees on all 22 chapters, which is
the only reason any of the numbers above can be trusted — **and the lesson is the third
recurrence of the same shape: the instrument was right and the thing measuring it was
wrong, three times in a row.**

## Freeze 8 — one row moves on purpose, 2026-09-28

    check-length.py    9d8f3a1b0bbbdfcf -> 2e9823d9d75b7cef   Freeze 2 -> Freeze 8
    14 of 15 rows unchanged.

A third defect, in a different gate, with the same underlying cause: **an absence was being
read as a decision.**

`declared_target()` returned `None` both when a book had no `PROJECT_STATE.yaml` and when
it had one that declared no target. The caller printed one sentence for both and exited 2.
The two conditions mean opposite things — *this book has no length contract* (a decision,
and after `DRAFTING_FRAMEWORK.md` a legitimate one) versus *nothing here can say what
length this book owes* (ungoverned).

Both validation-series Merope books have their `PROJECT_STATE.yaml` in
`_archive/validation-series-meta/`. So this gate exited 2 for a reason that had nothing to
do with the drafting framework — **and in this very session that exit 2 was read aloud as
evidence that the framework had removed the books' length targets.** It had not. The
archived file still carried `average_words_per_chapter_planned: 2450` and
`chapter_count_planned: 7`, against books that have eleven chapters.

This is `KF-004` again, later the same day, committed by the person who wrote it down: *a
gate that exits 0 and a gate that ran are different claims.* The clause this time was about
exit **2**, and the fix is that 2 and 3 now say different things.

    book with a state file, no target declared   exit 2   NOT APPLICABLE - a decision
    book with NO state file                      exit 3   UNGOVERNED - nothing to run against
    book short of its declared length            exit 1   LENGTH FAILURE

Verified across three books in one run: `demo-magician` exit 1, unchanged; Merope 1 and 2
exit 3, where they previously reported exit 2. No cap moved, no threshold re-derived, and
the only behaviour change is that a condition which used to be invisible now says its own
name. Precedence is failure, then ungoverned, then not-applicable, so a real length failure
is never masked by a missing file in a second book.

**What produced it — and it is not the gate.** The deletion layer. Archiving is governed by
a real policy (`maintenance-protocol.md`: never delete a canonical source, archive only
once no active phase reads it, keep the provenance line), and that policy was followed to
the letter. The metadata was superseded, so it was archived. But it was archived *out of
the book's own directory and into a different top-level project*, where no gate can see it,
and nothing in the policy says a gate may still be reading that path. **The policy governs
files. It does not govern the gates' view of where those files live.** That gap belongs to
the protocol, not the freezer.

---

## Freeze 9 — `validate-controls.sh` `84a6bef3539efaa8` → `e940b825763c2281`

**The caps are no longer assumed. They have been run.**

Every threshold in `deslop-check.sh`, `check-uniformity.py` and `check-drift.py` was derived from
published prose, and every derivation is written down in `calibration/CALIBRATION.md`. Written
down is not the same as re-checkable. Until this run the answer to "are the caps still calibrated"
was **exit 2, not run** — and the reason given was that no corpus existed.

That reason was false. **449 documents of published fiction and non-fiction were installed** under
three names (`montgomery`, `multivolume`, `nonfiction`), and `validate-controls.sh` was looking for a
fourth one (`elaina`) that has never shipped. The corpus is deliberately untracked —
`calibration/.gitignore` excludes it, for the same reason and with the same reasoning as
`USER_PREFERENCES.md`: it is somebody else's copyright, so a clone must supply its own.

So the gate was not reporting an absent corpus. It was reporting that *the path it was told to
look in* was absent, in the same voice it would use for a genuinely empty one. **Exit 2 said
not-run and hid not-configured.** That is the same defect class as Freeze 8 — one message, two
conditions — and it was sitting in the one gate whose job is to say whether the others are
trustworthy.

| control | result |
|---|---|
| 1 human prose passes the scanner | **ok** — 3 documents, 0 failing |
| 2 synthetic slop fails | **ok** — 16 failing rows |
| 3 AI prose is discriminated | *skip* — no control supplied |
| 4 published volumes vary | **ok** — v01 61ch, v02 38ch, v05 60ch |
| 5 a uniform manuscript fails | **ok** — U1 CV 0.8%, U5 CV 0% |
| 6 published prose holds one voice | **ok** |
| 7 a voice shift fails | **ok** — D1 4.53 against a 1.94 fail line |
| 8 the REPORT tier cannot fail | **ok** — D1/D2 over cap, neither printed FAIL |
| 9 the monotone arc fixture fails | **ok** — A1 0.150 |
| 10 non-fiction volumes are not flagged uniform | **ok** — 6 volumes, CV 28.2–113.7% |
| 11 a book short of declared length fails | **ok** — and a book inside range passes |

`ALL CONTROLS PASS`, **exit 0**, fiction and non-fiction both.

**No cap moved.** Not one threshold changed in this freeze. The instruments are the same
instruments that produced the Merope and `incunabula-test` numbers; what changed is that those
numbers are now attributable to a verified instrument rather than to an unverified one.

**Control 3 still skips** — no AI-written control is installed, so the discrimination control did
not run. It is reported as `skip` in the output rather than folded into the pass, and it should
stay that way: a suite that reported 11/11 while one control was skipped would be making the
claim this whole file exists to prevent. `AI_CONTROL=<path>` runs it.

**What changed in the file.** Only the exit-2 path, and only its message. When the configured
corpus is missing but `calibration/corpus/` is not, it now lists what it found and prints the
command that runs the full suite. Not-gone and not-pointed-at are now different sentences.

---

## Freeze 10 — 2026-09-29: `validate-controls.sh` `e940b825763c2281` → `2a570938b8d2b938`

**Found by cloning this repository clean and running the suite as a new user would.**
That is the only test that could have found it, and it is the test this file's whole
premise argues for.

### What was broken

The suite checked for the calibration corpus before running anything and exited 2
immediately if it was absent. The corpus is deliberately not shipped — it is published
commercial prose and somebody else's copyright — so **every fresh clone hit this on the
first run.**

The consequence was worse than an unhelpful error. Control 2 is the positive control:
synthetic slop must fail the scanner. Its fixture, `calibration/slop-fixture.md`, ships
in this repository and needs no corpus. It was unreachable. A new user therefore could
not watch the harness reject bad prose, while the evidence sat in its own tree.

Worse, the summary on a partial run read:

    ALL CONTROLS PASS - the caps ... are still calibrated
    against published prose, fiction and non-fiction.

off the back of controls that only ever saw fixtures written for this purpose. That is a
claim the run does not support, and it is the same failure the file exists to prevent.

### What changed

Only `validate-controls.sh`. No cap, no threshold, no gate semantics.

- The missing corpus no longer aborts the run. It sets a flag, prints the same
  instructions, and the controls that need only shipped fixtures proceed.
- Controls that cannot run report **`skip`** and are counted. Six of them previously
  printed **`FAIL`** for having read nothing, which is the same not-run-as-pass confusion
  in a louder key: it trains people to ignore the FAIL column.
- One `FAIL` is deliberately left alone — the "gate failed without reporting a row" case
  in control 5, which is only reachable once a fixture *has* been synthesised. There it
  is a real defect in the gate.
- The final summary separates what the run proved from what it did not, and still exits
  **2**. Not-run must never read as pass, and the fix was never to make it read as pass.

### Verified both ways

| run | result |
|---|---|
| fresh clone, no corpus | **exit 2** — 6 controls proven, 5 skipped |
| full suite, corpus installed | **exit 0**, `ALL CONTROLS PASS`, unchanged |

The second row is the regression test. A change to the runner that only ever made it
exit 2 would have satisfied the first row perfectly and broken the instrument for
everyone who does have a corpus.

### What a partial run does and does not establish

**Proven without any corpus:** the scanner fails synthetic slop (16 failing rows); the
REPORT tier cannot fail anything; a book short of its declared length fails; a monotone
arc fails. That is the harness detecting bad output, and it is the part that depends on
nobody else's copyright.

**Not proven:** that the caps still match published human prose. Until `HUMAN_CORPUS` is
pointed at reference text, the thresholds are unverified in that direction and
`calibration/CALIBRATION.md` is the only evidence for them. The summary says so in
those words rather than in a footnote.

### The recurring failure, eleventh instance

Instrument honest, gap filled with the more comfortable story. The convenient story here
was "the suite needs the corpus, so nothing can run without it" — which was true of
seven controls, false of six, and served nobody. Found by using the thing rather than
reading it, which is the whole argument for stress-testing a harness by handing it
demands nobody designed it for.

Earlier ten: KF-004, KF-005, Freeze 8, Freeze 9, deletion-layer escalation,
archive-as-graveyard, three-copies, the from-scratch U1 failure, the re-partition
evidence, the drafting-rule re-derivation.

**Cheaper fix applied:** name the state, don't build a detector. The state was "not-run",
it is now printed as not-run, and it is counted. No new gate — Freeze 6 holds, and this
is the runner reporting its own coverage rather than a new measurement of a manuscript.

---

## 2026-09-30 — the make-ready layer: recorded, and deliberately not a gate

**No manifest row moved. `verify-freeze.sh` holds 15/15, unchanged.** Freeze 6 holds:
no new gate, no new gate class. What was added measures the tool and the process, never
a manuscript.

Three files, in the same exemption class as `tools/sync-skills.py --check` (Freeze 6's
"one exception"): they answer a question about *which instrument will run*, not a
question about a book, so they are not rows and are not hashed here.

| file | what it asks |
|---|---|
| `SELF_IMPROVEMENT.md` | the autonomous promotion protocol — what replaces a person reading a diff |
| `COMMONPLACE.md` | the taste channel's ledger — decisions, outcomes, emergent preferences |
| `tools/preflight.sh` | freeze attribution, installed skill copy, state hygiene, mode — before a session starts |

The preflight encodes four past failure classes as rows: stale skill copies (meaningless
measurements), a broken freeze (unattributable results), a state file that will not parse
(KF-004), and stray CR that hides from grep (KF-005 — it counts with `tr`, never `grep`).
Every row names its own state, including SKIPPED, because a gate that cannot distinguish
absent from not-run is the recurring defect in this file.

**Two skills edited, recorded because `skills/` is on the also-frozen list:**
`press-ledger` (check-in/check-out now run the preflight and append to `COMMONPLACE.md`)
and `incunabula-auto` (preflight before dispatch). Both are state and dispatch skills;
neither generates prose, so what the gates *see* is unchanged. The prose skills that
generate text under test are untouched.

**The instrument-class question, answered before it is asked.** `SELF_IMPROVEMENT.md`
can adopt changes to skills and taste without a person, but the three-channel firewall
forbids it from moving any threshold in this manifest without a named corpus
re-derivation — the same rule as `errata.mode: auto`. The freeze does not stand in the
way of self-improvement; it is the boundary that makes self-improvement attributable.

Pristine check unchanged: every `USER_PREFERENCES` hit in `skills/` and `tools/` is
still documentation.

## Freeze 11 — 2026-10-01: two rows learn a state they were missing, one control added

Raised from the 2026-10-01 all-books suite (`SUITE-2026-10-01.md`), where two gates
produced findings that were about their own blind spots rather than about a book.
Both were observed in ERRATA the same day with n=1 each — no second agreeing book,
so neither proposal earned promotion by the errata table's own rule. What authorised
applying them anyway was a human ruling: the author reviewed the evidence, accepted
both proposals as correct-by-construction (a rule cannot convict its own calibration
book; a draft is not a delivery), and ordered them applied. That is the hand mode the
errata protocol reserves to a person, and it is recorded as that and not dressed up
as corpus agreement.

| file | freeze 10 | freeze 11 | what moved |
|---|---|---|---|
| `deslop-check.sh` | `1ccdd3aef10b9797` | `3d3f31fa100942d6` | A22 (excluded-book residue) demotes to report-only when the scan root is the excluded book's own manuscript. Its pattern IS that book's plot vocabulary; a self-scan can only re-find the calibration. The rule is untouched for every other book, and the self-scan still prints the count. |
| `check-length.py` | `2e9823d9d75b7cef` | `6dd9d862d275bff3` | A book whose own state file declares `status: in_progress` exits 4 (recorded, with its progress printed) instead of exit 1. Every other value and every absence keeps the old behaviour: a finished book short of its floor is still LENGTH FAILURE, because that is the row that cannot lie at delivery time. |
| `validate-controls.sh` | `2a570938b8d2b938` | `ebdec4a40ef785e4` | Control 12: a synthesized in-progress book must exit 4, and the same book finished must fail short again. Both arms, so the control cannot be satisfied by a gate that stopped failing anything. |

No cap, threshold or regex moved. The suite is re-run below before this freeze is
trusted, per the protocol this file exists to enforce.

**Also created the same day, deliberately NOT in the manifest** (the make-ready
class of 2026-09-30: they measure which books exist, never a manuscript):
`BOOKS.yaml` (the registry the suite reads), `tools/check-registry.py` (both-direction
coverage — created because this same suite had silently omitted `marrow-light/`), and
`tools/init-book.py` (scaffold-and-register, so a book cannot exist unregistered).

---

## Freeze 12 — 2026-10-01: the instrument is de-identified

The author took this repository public and directed that the private published book
used as the deslop calibration control be excluded from it. Every occurrence of the
book's title and slug is renamed to a synthetic stand-in — **Hollow Bridge**, slug
`hollow-bridge` — its ISBN is removed, and its character names are dropped from the
narrative records. **No cap, threshold, regex, or measurement moved.** The numbers in
`calibration/CALIBRATION.md`, `ERRATA.md` and the suite reports refer to the same
chapters under the new name; the instrument is byte-identical except for names and the
one mechanism change below. This is a redaction made at the author's direction and
recorded as such, so nobody later mistakes it for a re-derivation.

Rows that moved for the rename only:

| file | freeze 11 | freeze 12 | what moved |
|---|---|---|---|
| `check-arc.py` | `df9029bc2f4142c7` | `f2059aec8a9580cc` | the control book's name in a comment and one printed line |
| `check-drift.py` | `819505b173b9afac` | `814ca33e9e684ee7` | the control book's name in a comment |
| `validate-controls.sh` | `ebdec4a40ef785e4` | `f76ee16eaaddb943` | the control table names the control book under the new name |
| `calibration/PREMISE_LEDGER.tsv` | `d3f19efeaad10d73` | `1751102150c3ad6b` | the control book's premise row carries the new slug |

One row moved for a mechanism:

| file | freeze 11 | freeze 12 | what moved |
|---|---|---|---|
| `deslop-check.sh` | `3d3f31fa100942d6` | `20e1976d20312974` | A22's self-scan demotion no longer greps the scanned path for the control book's slug — that hardcoded string was itself a mention of the private book. It now demotes when a `SELFSCAN` marker file exists at the book root (the directory three levels above `manuscript/chapters/<file>`), so the mechanism is name-free and any book can declare itself the calibration control the same way. Verified three ways: the control book, marker present, produces output byte-identical to the Freeze 11 gate across all 11 chapters; `demo-magician` (34 chapters) is byte-identical; marker removed, the control book's A22 rows hard-FAIL again (6 rows, exit 1) — the demotion demonstrably keys on the marker, not the path. |

Supporting changes, none of them manifest rows:

- `BOOKS.yaml` no longer lists the control book. Private books on disk are handled by
  `.registry-private` — gitignored, the same mechanism shape as `USER_PREFERENCES.md` —
  which `tools/check-registry.py` reads to prune the direction-2 scan. A fresh clone
  with no such file is the correct default, and the registry check reports 9 books.
- `tools/check-registry.py` drops its own hardcoded private directory name the same way.
- Three complete demo books (`demo-magician`, `muzzle-and-marrow`, `marrow-light`) ship
  under `demo-books/` as runnable fixtures, grep-verified before shipping to carry no
  private-book mention.
- The historical records (`ERRATA.md`, `CALIBRATION.md`, `PRINTERS_COPY.md`,
  `SUITE-2026-10-01.md`, `COMMONPLACE.md`, `KNOWN_FINDINGS.md`, `skills/`) carry the new
  name in place of the old one; findings, numbers, and dates are unchanged.

Controls re-run at this freeze, corpus installed and the AI control supplied:
**all twelve controls behave, zero skips — `ALL CONTROLS PASS`, exit 0.** Control 3
(the discrimination control) still separates the control book: 6 of 11 chapters fail,
5 pass. `verify-freeze.sh`: 15 files, all ok.
