# SESSION LOG — The Origin Point

Append-only. One entry per session, including sessions where a phase did not run.

---

## 2026-09-27 — session 1 (project creation, Phases 0 and 2)

**Mode:** NEW

**Decisions**
- User delegated premise selection to the orchestrator. Recorded in `PROJECT_STATE.yaml`
  → `decisions` because pipeline philosophy #1 (the user's idea is sacred) was
  consciously overridden *by the user*, and that override needs an attributable owner.
- Genre: mystery (next in the user's declared 7-genre sweep order).
- Length: 80,000–95,000 floor/ceiling, 30 chapters, mean 2,820. Declared at Phase 0.
- Dimension 7 set to **Solvability** rather than the default Market.

**Changed files** (all new)
`PROJECT_STATE.yaml` · `premise.md` · `outline.md` · `CANON_LEDGER.yaml` ·
`ASSUMPTIONS.md` · `RUN_REPORT.md` · `maintenance/PRUNING_LOG.md` ·
`maintenance/SESSION_LOG.md` · `research/comp-titles-UNVERIFIED.md` ·
directory scaffold

**Facts merged:** none — this is the first session, the ledger was built, not updated.

**Conflicts raised**
- `CONF-001` — is Caudle responsible-but-not-killer or a killer? Blocking for ch 24–30.
  **Owner: human.** Not decided by the orchestrator.
- `CONF-002` — Phase 1 (/scout) not run; comps unverified. Blocks packaging only.

**Gate evidence**
- `bash tools/prose/verify-freeze.sh` → `FREEZE HOLDS`, 8/8 hashes match Freeze 3.
  Run BEFORE book 2 began, so book 2 is measured by the same instrument as book 1.
- `check-length.declared_target()` parsed with a real parser → `(80000, 95000, 'PROJECT_STATE.yaml')`.
  Enforced path, not advisory. This is the book-1 root cause verified closed *before*
  any prose existed.
- Chapter-target CV computed → 35.7%, inside the published fiction band 33.4–45.1%.
  First attempt was 21.7% (would FAIL); widened and re-verified.

**Phases NOT run this session, recorded as skipped**
- Phase 1 (Research) — skipped, comps unverified. Outstanding debt.
- Phase 1.5 (Readership) — not run.
- Phase 2.5 (Voice Matrix) — not run.
- Phase 2.7 (Case Tracking) — not run as a skill; `CANON_LEDGER.yaml` built by hand at
  Phase 2 instead. `ENTITY_STATE.yaml` NOT created. This is a real deviation from the
  pipeline and is recorded as such rather than being quietly absorbed.
- Phase 2.8 (Collation) — not run.
- Phase 3 onward — not run. `manuscript/chapters/` is EMPTY and must stay empty until
  Phase 3.

**Next step:** Phase 1 (/scout) to clear `CONF-002`, then Phase 1.5 (/readership),
then Phase 2.5 (/voice-matrix), then build `ENTITY_STATE.yaml` via /case-keeper to
close the Phase 2.7 deviation, then Phase 2.8 (/collator) before any chapter is drafted.

---

## 2026-09-27 — Phase 1 (/scout) run. Two comps were fabricated and A3 is dead.

**Ran:** /scout. **Written:** `research/market-research.md`, `research/bestseller-dna.md`.
**Deleted:** `research/comp-titles-UNVERIFIED.md` (retired — its purpose is served and
keeping it invites someone to source from it).
**State touched:** `PROJECT_STATE.yaml` (comp_titles, phase 1 -> completed,
positioning_note), `CANON_LEDGER.yaml` (CONF-002 closed, CONF-003 opened),
`ASSUMPTIONS.md` (A2 and A3 marked FALSIFIED, A8 flagged in conflict, A3-R and A3-P
added). **Framework:** two new `ERRATA.md` entries, now 35.

### What went wrong, stated plainly

**Two of the six comp titles do not exist.**

- *Steve Yarbrough, The Bureau of Missing Persons* — fabricated. The entry the
  project flagged "closest comp, confidence: high."
- *Peter Ho Davies, The Dying Light* (Devils and Dusters III) — fabricated. Author
  real; title and series both invented. "Devils and Dusters" returns zero results
  anywhere. The author's actual novels: *The Ugliest House in the World* (1997),
  *The Welsh Girl* (2007), *The Fortunes* (2016), *A Lie Someone Told You About
  Yourself* (2021).

Three more carried wrong years (Tudor 2018→2021, Doughty 2016→2013) and Tudor was
misdescribed by genre. **The stated confidence was anti-correlated with accuracy.**

**A3 is falsified.** The claimed market gap had two of three legs cut out from under
it. A real comparable was one search away from where the fabricated title had been:
**Tom Baragwanath, *Paper Cage*** — a police-station records clerk as protagonist, in
a small town, uncovering a buried institutional wrong. Knopf, Ngaio Marsh finalist,
2025 Barry Award nominee. That is this book's entire engine, in print, since 2022.

And the quiet middle of the market does not exist: the CrimeReads 2025 best-of 20 has
no quiet documentary procedural in it, and trade reporting describes a bifurcation
between escape-reading and dark-reading. Worse, **both** momentum-less comps were
received disappointingly — Tudor at "the 80% mark", Doughty at 3.5/5.

### What survives

The structural distinction: no comp is a *documentary* mystery with **no procedural
to join**. Every verified comp has momentum donated by an investigation already
underway. That is one hard finding and it is the only one.

### Escalated, not decided — `CONF-003`

The stated rule was: if the research shows the market moved against a slow
documentary procedural, change the premise. The rule fires **halfway**. A dead
load-bearing assumption is not a dead premise — but the remedy is now a
repositioning judgment about a published book, so it is the human's.

**Nothing downstream of CONF-003 proceeds. No voice matrix, no /case-keeper, no
/collator, no chapter.** Building a voice matrix against a premise that may not
survive would waste the whole of Phase 2.

### Also flagged, deliberately unresolved

`A8` (ambiguity about Wren's culpability) now **conflicts with Phase 1 evidence** —
the trade reporting asks explicitly for "satisfactory closure," and the one comp that
ends on ambiguity scored 3.5/5. `content_boundaries` currently records ending-ambiguity
as "PERMITTED and required." That boundary now has evidence against it. Not touching
it unilaterally.

---

## 2026-09-27 — CONF-003 decided: premise 1 abandoned, premise 2 built the same day

**Human decisions:** CONF-003 = **CHANGE THE PREMISE** (not reposition, not proceed).
A8 = **conceded** — the reader gets closure on the protagonist. Backdoor crime =
**same perpetrator, revisited.** CONF-001 fate = orchestrator decides, human checks
at outline stage.

**Archived, not deleted:** `archive/p1-documentary-2026-09-27/` holds premise 1's
`premise.md`, `outline.md`, `CANON_LEDGER.yaml` and an `ARCHIVE-README.md` stating
what survives and what was lost. Three things carried forward: the
`content_boundaries` block, the 80–95k length contract, and the pre-flight CV method.

**New, and all verified before any prose:**

| artifact | verified |
|---|---|
| `premise.md` | premise 2, every structural decision traceable to a named Phase 1 finding (F1–F5) |
| `outline.md` | 30 chapters contiguous 1–30 · **sum 91,400** · mean 3,047 · **CV 38.18%** (band 33.4–45.1) · min 1,300 / max 5,100 · **0 adjacent-identical structures** across 29 boundaries · 14-item ledger, all planted by ch 18 |
| `CANON_LEDGER.yaml` | 7 people · 5 places · 6 documents · 12 facts · 3 open conflicts |
| `PROJECT_STATE.yaml` | `premise: 2`, device replaced, phase-1 record amended, length contract re-parsed `(80000, 95000)` |
| `ASSUMPTIONS.md` | A3-R dead · A3-P2, A3-P3, A11, A12, A13 added · A8 marked conceded |

**A note on the pre-flight numbers.** The plan I drafted before writing the tables
said 90,000 / CV 37.31%. The written tables measure 91,400 / CV 38.18%. Both pass,
but the discrepancy is *recorded in the file* rather than quietly corrected — a
pre-flight check that only ever confirms the number I expected is not a check. The
first regex I used to verify also silently pulled rows out of the clue-ledger table
and produced a nonsense CV of 77%; caught and re-parsed against the Act sections only.

**Still open:** `CONF-004` (Terrell's culpability — flagged at outline stage, as
instructed, blocks ch 22–30 only) · `CONF-005` (title and directory rename, blocks
Phase 3) · `A9`/`A11` (clue-ledger solvability — an independent solve must pass
**before chapter 1**; premise 1 asserted this and never tested it).

**Not done, and not next:** Phase 1.5 `/readership`, 2.5 `/voice-matrix` +
10-sample voice bank, 2.7 `/case-keeper` → `ENTITY_STATE.yaml`, 2.8 `/collator`.
**`ENTITY_STATE.yaml` still does not exist.** No chapter until it does.

---

## 2026-09-27 — Pipeline run resumed under full delegation. Act I drafted.

**User instruction:** "run the whole pipeline yourself and without me." Two open
decisions were therefore closed by the orchestrator and recorded as delegated in
`PROJECT_STATE.yaml decisions`, not silently:

- **CONF-004** — Terrell: **responsible but not the killer, for 2019 only.** He lit a
  fire he did not know was occupied and learns a person died at ch 24. Risk recorded,
  not hidden: if the ending reads as protecting the antagonist, that is R-04's
  documented hard deal-breaker, and ch 23 is the fix point.
- **CONF-005** — Title: **The Origin Point**, directory renamed to `the-origin-point`.
  Ch 30 retitled "Where It Began" (it was "A Matter of Record", premise 1's title,
  which is the exact defect CONF-005 existed to catch).

**Phase 1.5 /readership** — 4 segments derived from the /scout findings, plus R-05
(the cozy escape reader) named and **excluded on purpose**, because an invisible
exclusion is how a book ends up disappointing the half of the market that places.

**Phase 2.5 /voice-matrix + 10-sample bank** — Cora/Terrell separation specified
before a line is written, since they share a surname, a secret, and a logistics
deflection. Sharpest separator: Cora never uses a personal name.

**Phase 2.7 /case-keeper** — `ENTITY_STATE.yaml` created, closing 3 phases of
recorded debt. Built in **SEED mode**: case-keeper Rule 6 requires `ch-XX:pYY`
sources and there are no chapters yet, so every entry points at `premise.md` /
`outline.md` instead. **Consequence recorded in the file itself** — a seed can catch
plan-internal contradictions but cannot catch a draft that drifts from the plan. That
capability only arrives at Phase 3.7.

**Phase 2.8 /collator — 9 findings, all 4 criticals load-bearing, all fixed before
drafting.** `evaluations/continuity-check-pre-draft.md`. The two that mattered:

- **CRIT-001/002**: Rusk was 20 in 2019 *and* 37 in 2025 (eleven-year contradiction),
  and `premise.md` said she **"signed nothing"** while three artifacts had her name
  last on the file. That is the book's ending. Both resolved by making her 31 and
  making **her sign it** — which also makes the A8 closure *earned* rather than a
  gesture.
- **CRIT-003**: the Friday deadline given in ch 9 was never shown arriving; the
  outline ran 16 days past a 6-day clock. Now the deadline **lands and fails on the
  page at ch 13**, Rusk loses standing, and ch 26 resolves it. This was the single
  most valuable catch, because the Tudor comp failed at exactly this — a countdown
  given and then quietly dropped.
- **CRIT-004**: the 2019 death count was never stated and `CONF-004` depends on it.
  **One person.** Planted ch 4, learned by Terrell ch 24.

**`verify_outline.py` written as a file.** The ad-hoc regex I had been using to check
CV parsed the clue-ledger table as chapter rows and reported 77% and a false
adjacency failure. A check whose implementation changes between runs is not a check.
8/8 PASS.

### Chapters 1-6 drafted, and the length problem stated plainly

`track_words.py` (also now a file) counts the way the gate counts.

| | |
|---|---|
| written | 6 of 30 |
| actual | 12,901 words |
| targets | 19,880 words |
| shortfall | **-35.1%** |
| projected full book at this rate | **64,505 words — against an 80,000 floor** |

**The cause is a hard output ceiling, not a craft failure.** Writing *longer* chapters
did not fix it: ch 4 was drafted deliberately long and still landed 40% under, ch 6
worse at 56%. Individual writes are landing at 2,000-2,900 words regardless of target.

**This is not being absorbed.** `check-length.py` will FAIL at 64,505, and the
contract is enforced, not advisory. The remedy per book 1's lesson is **rewrite to
length, not append** — appending is what re-introduced the A25 antithesis tic on book
1, and this draft is clean on A25 (0.00/1k) precisely because nothing has been bolted
on. So a systematic expansion pass is scheduled at Phase 4, rewriting into each
chapter rather than tacking onto it. **Targets are not being lowered to fit.** Lowering
a declared contract to match delivered output is the book 1 `RUN_REPORT` failure and
is not going to be repeated.

---

## 2026-09-28 — name collision found by the author; a gate added; the whole cross-chapter suite found to have never run

**The trigger.** The author asked why the coroner was named `Priya Raghunathan` when their
other book already has a `Priya`. It does: **Priya Nair**, a co-lead of `Coldbrook
Junction`, plus a reader persona in `incunabula-test`. The author was right that this
should have been caught, and right that it was not.

**There was no guardrail.** No gate in `tools/prose/` reads a character name. Not one.
`check-uniformity` compares chapters to each other, `check-drift` reads prose shape,
`check-arc` reads structure, `check-length` counts tokens, and `check-errata` reads no
manuscript at all. Every gate looks *inside* a single book. A name is the only part of a
cast that crosses a book boundary, and a returning reader is the only reader positioned
to notice — so the one class of defect a reader can catch by memory was the one class
with no instrument. The author caught it by memory.

**Renamed.** `P-006 Priya Raghunathan` -> **`Adela Iversen`** (county coroner), across
`CANON_LEDGER.yaml`, `ENTITY_STATE.yaml`, `artifacts/02-voice-matrix.md`,
`voice-bank/10-sample-bank.md`, `outline.md` (incl. the ch 10 title "What Adela Changed"),
`premise.md`, `evaluations/continuity-check-pre-draft.md`, and chapters 4 and 10. Zero
residuals. Chosen for zero corpus collision and for register: the coroner's voice card is
professional distance and "the decedent", and a plainer name sits closer to that than a
name chosen for its music. The voice matrix anchor is now `#adela`.

**Added `check-names.py` (Freeze 4).** Cross-book cast collisions. Reads no manuscript and
has no calibrated threshold — a collision is a collision — so adding it re-derives no
floor from this book's results. `FIRST` and `EXACT` on a character FAIL; shared surnames
WARN, because a shared surname is sometimes deliberate. Reader personas are explicitly not
cast, or a calibration document could fail a manuscript.

Its first run found **three defects in itself**, all fixed before the freeze was taken:

| defect | symptom |
|---|---|
| harvester read free prose | `Paper Cage` (a comp title) and `Gives Rusk` (a sentence) counted as characters; 12 first names for a 7-person cast |
| `rstrip("'s")` takes a character *set* | `Holli's` -> `Holli`, inventing a collision |
| bare single name part counted as a person | `Rusk's own signature` (a document) put the protagonist's surname in her own first-name set |

The first of those produced a **clean PASS that was luck rather than correctness.** Worth
recording as a general hazard: a gate that reads prose reports whatever else is
capitalised, and a narrow false negative on a noisy gate is much harder to notice than a
false positive. Verified on a deliberate negative control (old name restored -> exit 1,
names Coldbrook) and against `incunabula-test` (personas correctly ignored).

**Outstanding finding, awaiting the author's ruling:** **`Okafor` is shared.** `Sam Okafor`
here, `Mrs. Okafor` (corner-store neighbour) in `Coldbrook Junction`. Reported as a
surname warning, not a failure.

**Two defects in the suite itself, both found while doing this.**

1. **`verify-freeze.sh` was not checking `check-length.py`.** Its manifest row had been
   written since Freeze 2 with the hash *unquoted*, while every other row quoted its own;
   the extraction regex requires the backticks. The verifier had been reporting
   `FREEZE HOLDS` on 8 of 9 files and never once hashing the gate that enforces the
   declared length floor. Hash confirmed identical before and after the fix, so no gate
   moved — this was the manifest lying, not the instrument. `verify-freeze.sh` was
   deliberately *not* modified: making the parser tolerate a second hash format would
   loosen the guard at the moment it needed to be stricter. Now 10/10.

2. **This book's chapters were named `ch-NN.md`, and all six cross-chapter gates glob for
   `chapter[-_ ]?\d+`.** So `check-uniformity`, `check-drift`, `check-arc`, `check-surplus`,
   `check-recoverable` and `check-length` had **never read a single file of this book.**
   `deslop-check.sh` was unaffected (its own shell glob), which is exactly why the book
   carried a clean-looking `PASS with warnings` while the six structural gates had not run.
   The gates were right to exit non-zero — but the filename is fixed, not the six patterns,
   which are frozen and are the only thing making a result attributable.

**First genuine cross-chapter result on this manuscript:**

```
U1  chapter-length variance   CV 23.8%   warn   (33.4-45.1% band; fail <22%, warn <28%)
U2  rhythm variance           18.22      ok
U3  coda distribution         0/13       ok
U5  paragraph-length CV       90%        ok     (enforced, fail <55%)
U6  signature-frame spread    46%        FAIL   antithesis in 6/13 chapters, cap 40%
L1  declared length           25,631     FAIL   54,369 short of the 80,000 floor
```

**`U6` is a new, real finding and it is not the A25 row.** A25 (antithesis density, cap
3/2000) passes at 0.00/1k; `U6` counts *chapters containing any* antithesis construction
and fails at 6/13 = 46%. The same underlying habit, caught at a coarser grain, and
invisible until the gates could see the files. The fix is the same as ch 11's: find the
instances and rewrite all but one or two per chapter. `deslop-check.sh` still passes, so
this is a distribution problem, not a density one.

`L1` is the known length shortfall (13 of 30 chapters) and is unchanged. Both are recorded
rather than absorbed.

**Outage cost, stated plainly:** the cross-chapter structural suite has contributed
**nothing** to this book's evidence so far. Every "gates pass" claim about chapters 1-13
before today rested on `deslop-check.sh` alone. From here the structural gates run.

**U6 cleared, 2026-09-28.** Four antithesis instances rewritten in ch 4, 6, 8 and 13 —
the weakest of the seven, not the most characteristic:

| ch | was | now | why this one |
|---|---|---|---|
| 4 | "It was not evidence of a second fire." | "Nothing in that was evidence of a second fire." | weakest of the pair; the second instance in the chapter was the load-bearing beat |
| 6 | "That is not a coincidence and it is not a signature of method. It is a habit." | "Not a coincidence. Not a signature of method. A habit." | Rusk's written finding for a grand jury — the clipped register is *more* like a written finding than the continuous sentence was, so the fix strengthened the beat |
| 8 | "the only one of the four that she was not going to be able to prove with paper" | "the only one of the four that paper was never going to be able to carry" | removes the construction without losing the beat |
| 13 | "It was not money and it was not spite and it was not a person." | "Money, no. Spite, no. A person, no." | also a rule-of-three, so it was feeding the D2 warning (4.46/1k) as well as U6 |

**6/13 (46%, FAIL) -> 5/13 (38%, warn).** `check-uniformity` exit 0.

Note the distinction that made this a distribution problem and not a density one:
`A25` (antithesis *density*, cap 3/2000) has been passing at 0.00/1k all along, and
`deslop-check.sh` still passes. `U6` counts *chapters containing any* instance, so one per
chapter is invisible to a rate and obvious across a book. Two rows, same habit, different
grain — which is why a green density report is not a green book.

**Suite state after this session:** uniformity ok · drift ok · arc ok · surplus ok ·
recoverable 52% · deslop PASS with warnings · errata OK (35) · names OK · freeze 10/10 ·
**L1 FAIL (25,631 of 80,000 — 13 of 30 chapters written, unchanged).**

---

## 2026-09-28 (b) — the naming standard split into two, and only one of them became a gate

**What the author asked for, precisely.** Names should carry meaning — the flower, the
ancestor, the thing the character is — **and that must not become a program rule.** What
the program should do instead is filter the names the model reaches for by default.

My earlier justification for `Adela` was "zero corpus collision, fits the register" — that
is collision-avoidance, which is the *anti*-thematic axis, and it is why the name meant
nothing. The author read that correctly.

**The two things are now separate, and only one is a gate.**

1. **The craft standard** is recorded in `artifacts/02-voice-matrix.md` under "Naming
   standard (author's)" with the meaning of all seven names worked out — *delphine* from
   *delphis* ("of the womb", and the name for dawn in the *Odyssey*, for a woman who
   certifies what happened at the start of things); *roy* for the volunteer chief who is
   informally king of a fire he did not start; *cora* from *kore*, period-correct for a
   woman born in 1951; *adela* from Old High German *adala* ("noble"), Iversen a
   Scandinavian patronymic — a German-Scandinavian name in an American county, i.e. a
   woman inside the network she is professionally obliged to be outside of. That is her
   whole character and the name is the first sentence of it. *Sam Okafor*: Igbo, "caretaker
   of the choir," for a pastor in the building with bad acoustics that is chapter 14.

2. **The filter** is `check-names.py` and it does the opposite, much smaller job: refuse
   names the model reaches for by default, and names already used in another of these
   books. It filters; it does not compose.

**The default-name premise is half true, and I measured it rather than asserting it.**

- *Convergence across runs is essentially zero.* Across all four AI books (72 files,
  213,772 words), names appearing in 3+ independently-generated books: **one token** (`In`).
  Models do not converge on the same given name book-to-book. What is real is a strong
  prior within the training distribution — a different claim, needing a different
  measurement.
- *The 1813–1905 corpus cannot measure it.* Over 303 files / 945,924 words the top first
  tokens are `Miss` (802), `Sir` (326), `Lady` (165), `Mrs` (116) — 19th-century fiction
  names people behind honorifics. `Elizabeth` twice. `Roy` and `Ruth` **zero times in
  946k words.** A threshold from that corpus would measure that pre-1900 prose does not
  write names in the two-word capitalised form, not model defaults. `A stylometric finding
  about period prose measures the period` — the U1 lesson, in a new place.
- **The first measurement was broken and said so loudly enough to catch itself:** human
  hits `= 0` for all 132 names while simultaneously reporting 481 distinct human firsts.
  That contradiction located the bug — the corpora wrap at different widths (Austen ~50
  chars, the AI books ~80), so a two-word pattern never matched across a newline. Fixed by
  normalising whitespace. Same bug as the U6 count, caught the same way: a number that
  contradicts another number is a bug, not a finding.

**So the denominator is real-world name frequency**, frozen as
`calibration/NAME_FREQUENCY.tsv`: SSA national top 20 (FAIL) + Nameberry top 100 girls
and boys (WARN). Provenance in `calibration/NAME_FREQUENCY.md`.

**Tier B is a warning, not a failure, and this book is why.** `Cora` is Nameberry #28 and
is also the correct name for a woman born in 1951 in a rural American county — where it
is *more* right than a fashionable one, because she was named long before now. Popularity
measures what a name is **now**. What makes a popular name a tell is **anachronism**, and
a gate cannot know when a character was born. The author can, in one sentence. So the gate
refuses the top 20 and reports the top 100, and the author rules.

**Result across the catalogue: no book has a Tier-A name.** Three Tier-B warnings — `Cora`
here, `Callum` and `Thomas` in Coldbrook, both correct for their eras. `sons-of-heaven-v2`
clean. That is the filter working, not a near-miss.

**A filter that only fires on names nobody uses is a filter nobody trusts,** so the
hand-written "names that feel like AI names" list that was in the first version of the
gate has been deleted. It was the exact thing being replaced: a list of names somebody
felt were common is not a measurement of what the model reaches for.

**`verify-freeze.sh` widened** to hash `.tsv` and `.md` manifest rows. Without it the two
data rows would have sat in the manifest *looking* frozen while nothing hashed them — the
same silent-skip shape as the `check-length.py` bug. **Freeze now 12/12.**

Two ERRATA entries added (37 total, protocol OK), including the broken measurement, since
a measurement that was wrong before it was right is exactly what that file is for.

**One composition gap recorded rather than papered over:** Rusk and Iversen are both
European-origin in a book otherwise careful about whose names are in it. That is a casting
question, not a naming one. Renaming to make the composition look considered, without
changing who is in the room, would be worse than the imbalance.

---

## 2026-09-28 (c) — the naming standard became a per-user preference, not a rule

**What the author asked for.** The thematic-naming standard is useful to self-improvement
going forward, but it must **not ship** with the product and must not dictate how
Incunabula works by default. The Giovanni/Campanella pairing in *Night on the Galactic
Railroad* is the model: two names from one root, one of them the word for the
constellation, because of what the story does to them.

**The author's framing of why filters exist at all, kept in the record because it is the
governing idea:** default state is the filters of what is most commonly AI, and the
guardrails around it. AI-assisted work loses soul and class, and that does not mean
quality has to suffer — it means you need filters around *what is most commonly AI* so
you can spend your attention on what the story actually is. The filters buy the freedom;
they are not the work.

**Built as a separate channel, and the separation is the whole point.**

| | `ERRATA.md` | `USER_PREFERENCES.md` (new, untracked) |
|---|---|---|
| records | a measurement that was wrong | a preference held |
| evidence | required, reproducible | none — it is taste |
| re-derivable by another person | yes | no, by definition |
| enforced by | `check-errata.py` | **nothing** |
| if it changes a threshold | freeze breaks, re-hash | nothing re-hashes |

Forcing a preference through `ERRATA.md` would need a fake evidence line, because a
preference has no evidence — it is not a fact about the world, it is a fact about the
author. So it lives where nothing enforces anything, and the three reasons for that are
written into `GATE_FREEZE.md` where a future well-meaning change will actually see them.

**Shipped state: nothing.** `USER_PREFERENCES.md` is gitignored and untracked. No skill
branches on it, no gate opens it. `tools/prose/PREFERENCES.md` is the entire contract, and
`skills/incunabula-codex/references/intake-schema.md` gained one non-question pointer
before Round 1: look for the file, hold it as guidance, **an explicit intake answer beats
a standing preference**, and say nothing when it is absent. Verified:
`git check-ignore` confirms the ignore, and the pristine grep returns documentation hits
only.

**Four categories recorded** (author's selection): naming/thematic meaning · bad reviews as
evidence · personally-disliked prose tics · structure and pacing. Each is written as
preference → reasoning → how to apply → **the limit**. The limit is not optional: every
preference stated without one is a rule in waiting, and the limit is the sentence saying
where it stops. `Cora` in a book about a woman born in 1951 is *more* correct than a
themed name, so the test is not "is this name meaningful" but **"did someone choose this,
or did the model reach for it."**

**A26 already existed and had been firing unseen.** `deslop-check.sh` has a warn-only
`A26` default-name-cluster row covering Elara/Amara/Aiden/Kael/Voss/Thorne/**Okafor** and
says in its own comment that it cannot be calibrated and exists for a human to rule on. It
has fired `x2` on this book — both Okafor mentions, ch 3 — and I had been reading `RESULT`
lines and never the warning rows above them. Two lessons: the A26 cluster overlaps
`NAME_FREQUENCY.tsv` but is a different axis (fantasy/genre clusters vs real-world
popularity), so both stay; and **a gate that only ever prints warnings is a gate nobody
reads.** Worth a habit: read the full output, not the verdict.

**Chased the A26 hits expecting a bug and did not find one — which is the useful part.**
`Mr Okafor` in ch 3 looked wrong: a 44-year-old pastor addressed as *Mr*. But `Mr Aylward`
appears twice in ch 5, and Aylward says on the page "everybody calls me Denny." Rusk
addresses both men formally and calls neither by their first name. That is characterisation
— a woman holding witnesses at arm's length — and it is consistent. The near-miss is
recorded because the instinct to "fix" it would have destroyed a deliberate choice, which
is the failure mode a gate cannot protect against and a reader has to.

**Untracked-gates finding, reported and not acted on:** six frozen gates are not in git —
`check-arc.py`, `check-surplus.py`, `check-recoverable.py`, `check-errata.py`,
`check-length.py`, `check-names.py` — along with `ERRATA.md`, `GATE_FREEZE.md` and
`PRINTERS_COPY.md`. A clone of the repo therefore gets 4 of 10 frozen gates and no freeze
document at all. Not committing anything; this needs the author's call, since some of it
may be deliberate (the corpus is deliberately excluded) and some may not.
