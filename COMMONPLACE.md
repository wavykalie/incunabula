# COMMONPLACE — the taste ledger

A writer's commonplace book: what was chosen, why, and what the readers said. This is the
taste channel's ledger (`SELF_IMPROVEMENT.md` §2). Like `ERRATA.md` it is **append-only**;
an entry that turns out wrong gets a `WRONG` line under it and the wrongness stays visible.

The distinction that keeps this file from becoming a rule book: **nothing here is
enforced.** `decisions` and `emergent` preferences are guidance the next book reads at
intake and may decline with a reason — and that decline is itself an entry. A gate reads
nothing in this file. The moment something here returns non-zero, it has become a
threshold and belongs in `ERRATA.md` instead, behind the corpus rule.

## Entry types

### `decision` — the atomic unit of taste

One real editorial choice, made between named alternatives, with the reason. Not
"the chapter went well" — a fork where another road was visible.

```
### YYYY-MM-DD — decision — one line naming the choice
- **book:**    which project
- **chose:**   what was done
- **over:**    what was declined, as specifically as possible
- **reason:**  why, in the author's terms
- **source:**  who decided — author | agent | prompted by the author
```

### `preference` — distilled taste

```
### YYYY-MM-DD — preference — one line stating the preference
- **status:**  emergent | declared
- **from:**    the decision entries it was distilled from (>= 3), or the author's hand
- **reason:**  why it generalises past the cases seen so far
- **limit:**   the case where it should be declined — every preference needs one
```

`declared` preferences live in `USER_PREFERENCES.md`, are written only by the author, and
are immutable to the loop. `emergent` preferences are distilled here from three agreeing
decisions, never enforced, and may be revised by later entries.

### `outcome` — what the readers did

```
### YYYY-MM-DD — outcome — book and signal
- **predicted:** the First Impression / Standing Type claim, verbatim, as recorded before publication
- **actual:**    sales, reviews, blind-read verdicts — verbatim where possible
- **error:**     where the prediction was wrong, stated plainly
- **lesson:**    what this falsifies, or "none yet"
```

Bad reviews are entered verbatim. Paraphrase is how evidence becomes flattering.

### `promotion` — a change the loop adopted

```
### YYYY-MM-DD — promotion — what changed and on which surface
- **surface:**  craft | measurement | taste
- **hypothesis:** what it was supposed to improve
- **verifiers:** each stack result, including SKIPPED and failures
- **reverts:**  how to undo it, and what monitor would trigger the undo
```

---

## Seeded from the record so far

### 2026-09-28 — decision — rewrite the prose, not the instrument
- **book:**  validation-series (Merope)
- **chose:** rewrote a sentence to be unambiguous after A18 flagged a genuine non-gerund as a gerund litany
- **over:**  waiving the row, or relaxing the gate to accommodate the author's rhythm
- **reason:** frozen instruments do not accommodate one author's rhythm; the false positive had a real cause and the prose could carry the meaning without the ambiguity
- **source:** agent proposed, author accepted (recorded as KF-003)

### 2026-09-28 — decision — names are chosen at planning and fixed before prose
- **book:**  demo-galactic (naming phase), then marrow-light
- **chose:** hand-derived thematic names (St Swithin's Day, *hesper*, *parr*, *anstice*, one deliberately plain), and at cast declaration renamed Wren and Delphine at planning time to clear the name gate
- **over:**  letting the model name characters in the draft and filtering afterwards
- **reason:** names should carry meaning, and the right place for that judgment is planning — where a rename costs a line, not a chapter
- **source:** author's declared preference, exercised by the agent

### 2026-09-28 — preference — the gate filters defaults; meaning is not its question
- **status:** declared (see `USER_PREFERENCES.md` §1 and `GATE_FREEZE.md`, Freeze 4)
- **from:**  the demo-galactic naming run, where a filtered set and a judged set produced the same verdict by different mechanisms
- **reason:** "did the model reach for this?" and "did someone choose this?" are different questions and neither can answer the other's
- **limit:**  a character who needs a plain name gets one; thematic naming is never a program rule

### 2026-09-30 — outcome — Hollow Bridge: no prediction was recorded
- **predicted:** none. First Impression and Standing Type were not recorded before publication.
- **actual:** published, live on Amazon 2026-09-22. No sales or review data has been entered here.
- **error:** the prediction channel did not exist when this book shipped. That is the data the loop most needs and cannot recover.
- **lesson:** from the next book onward, both indices are recorded here at delivery, before publication. This entry stays as the reminder of what skipping it costs.

---

## Reading order at intake

1. `SELF_IMPROVEMENT.md` §2 — the firewall, so nothing here is mistaken for a rule.
2. This file, newest first — what has been chosen, and what the readers have said.
3. `USER_PREFERENCES.md` if present — declared taste, held as guidance.

At check-out, append `decision` and `outcome` entries; distill `emergent` preferences
only at three agreeing decisions; write `promotion` entries only through the verifier
stack. The loop's own bookkeeping is subject to the same rule as everything else here:
a record that was never seen being written is not evidence.

### 2026-09-30 — decision — chapter-end Guidance is apparatus, not prose
- **book:**  sons-of-heaven-v2
- **chose:** each chapter closes with a `## Guidance` block distilled from that chapter's own material, written to be quiet to every frozen row (no coda formula, no signature frame, no listicle pattern)
- **over:** weaving the counsel into the narrative; a book-end summary chapter; formulaic "takeaways" lists
- **reason:** the nonfiction reader wants the usable thing at the chapter's edge, and the narrative earns it first; keeping it as visibly separate apparatus preserves both the prose and the instrument's meaning
- **source:** author directed the apparatus, agent designed the quiet form

### 2026-09-30 — decision — reader-facing lines must unpack their own reference
- **book:**  sons-of-heaven-v2
- **chose:** rewrote "Read the Tuesday / an unfiled Tuesday" as "Judge by the paperwork", with the reference spelled out
- **over:** keeping the compressed insider phrasing
- **reason:** the author asked what it meant; a guidance line that needs the chapter remembered has failed at the one job it has. Compression is for the narrative, where the referent is in the reader's hands
- **source:** author, by asking the question

### 2026-09-30 — decision — a contract breach is carried, not padded
- **book:**  marrow-light
- **chose:** resolved the 21,931-word L1 shortfall by the author's option 3: carry the failure in FINISHED.md as fact, floor unmoved
- **over:** expanding short chapters to the number (the named padding failure), or quietly re-declaring the floor after the result was visible
- **reason:** the outline records all 45 rows written, so no genuine material is missing; the author delegated the decision but did not authorise a lie about why the book is short. A recorded miss is evidence; a padded pass is contamination
- **source:** author delegated 2026-09-30; agent resolved within the author's own three options

### 2026-09-30 — decision — the pilot's numbers are the evidence, not a defect to edit
- **book:**  muzzle-and-marrow
- **chose:** left the chapter lengths untouched; U1 (CV 12.1%) and L1 (5,314 short) carried as the pilot's findings in FINISHED.md
- **over:** expanding or compressing chapters to land in the U1 band, or padding to the floor
- **reason:** this is the only book drafted from scratch under the framework; its measured result is what it exists to produce. Editing the before-state destroys the measurement, which is the maintenance-protocol lesson wearing a different hat
- **source:** agent proposed, framework's own recorded position ("recorded, not repaired") confirms

### 2026-09-30 — preference — spoken formulas are voice; narrative formulas are tic
- **status:** emergent
- **from:** marrow-light ch07 ("which is why I need to be—", left), muzzle-and-marrow ch07 ("a door to/of the centre", left), muzzle-and-marrow ch08 ("it is not closed because of me", left); against 23 narrative formulas rewritten across both books
- **reason:** a character is allowed the antithesis; the narrator reaching for it is the machine's habit. The gate cannot tell the speakers apart, so the reader has to, and the fix is applied at the narrator's desk only
- **limit:** when a character hammers the formula repeatedly, or the formula sits in free indirect discourse where the narrator's voice is the character's, it counts as narrative and gets rewritten

### 2026-10-12 — promotion (craft) — evidence-required passes, chapter floor, gated words, human checkpoints
- **from:** ERRATA 2026-10-12 (kitsch-reprise v1: 30 stubs averaging 754w with 7 chapter-level passes claimed and none artifacted)
- **changed:** skills/incunabula/SKILL.md maintenance gate (+4 bullets: artifact-required passes; gated-words progress; 2,000w/50% chapter floor with waivers; grade-C diagnostic-only + human-owned checkpoints); skills/incunabula-auto/SKILL.md (+no-dispatcher rule: checkpoints belong to the human where no fresh critic exists; critic-role self-votes retired); new tools/check-pass-evidence.py (hygiene, unfrozen, same class as check-registry.py)
- **over:** leaving the engine text untouched and enforcing the rules book-locally only
- **reason:** the failure was systemic (a pass without an artifact is indistinguishable from a skipped one), so the fix belongs in the shared text; book-local rules die with the book
- **falsifier:** held-out = books 2-4 (every chapter must carry its pass file; check-pass-evidence exit 0 required before phase advance); catalogue regression = finished-book verdicts unchanged (no frozen file touched; verify-freeze HOLDS confirmed post-change)
- **shadow:** git 8219b98 + working-tree diff; previous skill text recoverable via git
- **source:** author approved 2026-10-12 ("Apply it"); agent drafted, verifier stack run (sync --check OK, freeze HOLDS, preflight PASS, errata protocol OK)

### 2026-10-13 — promotion (craft, framework-level, author-directed) — the gate runner: one command, and not-run is never a pass
- **from:** the 2026-10-13 systems audit: books reaching `status: complete` with zero gated words and no pass files (quiet-hours, la-merienda); `check-length.py` disarmed by self-declared contracts and by `status: in_progress` used as a deferral; skill text naming `tools/deslop-check.sh` at a path that does not exist (the tools live under `tools/prose/`); the prose gate in the engine naming two of its four tools; quoin counted as "eight operations" in three places and nine in a fourth; DRAFTING_FRAMEWORK.md's "as long as it takes" read as licence for 300-word chapters against the engine's 2,000-word floor
- **changed:** new `tools/run-gates.sh` (process tooling, unfrozen, same exemption class as `preflight.sh` — it runs the frozen instruments and measures nothing new, so it is deliberately not a GATE_FREEZE row and moves no hash); `skills/incunabula/SKILL.md` (the prose gate names all four tools at their real paths and delegates to `bash tools/run-gates.sh <book-root>`; every "gate passes" phase transition now means a CLEAR runner verdict — exit 1 and exit 2 both block; new `gates` command; the chapter-length waiver stops being routine: a second consecutive waiver, or one leaving the running total behind the outline's plan, is a stop-the-line event escalated to the human); `skills/incunabula-auto/SKILL.md` (checkpoints two and three require a runner verdict before they may pass); `skills/quoin/SKILL.md` ("The Eight Operations" heading corrected — there are nine operations; five of nine, including operation 9); tool paths corrected to `tools/prose/` in catchword, composing, deslopify, press-ledger, proof-panel, proof-pull, and the codex pipeline manifest; `DRAFTING_FRAMEWORK.md` (the rule scoped: it forbids quotas, not the stub detector — the floor is a detector with recorded waivers, never a target to write to; numbers legitimately live in three places now, not "two, and only two")
- **over:** enforcement by checklist prose an agent could skip and still declare victory; a chapter-length rule that read two ways depending on which document the run opened first
- **reason:** the audit found the skipping was structural, not malicious: a dozen separate commands to remember at seventeen phase boundaries with nothing checking the remembering, and tool paths in the skill text that did not resolve. One command with a not-run-is-never-pass exit code closes it at the only place it can close — the moment of claiming a phase. The contradictions were fixed in the direction the evidence runs: quotas produce filler (DRAFTING_FRAMEWORK's finding, intact) and no floor produces stubs and half-length books (ERRATA 2026-10-12's finding); a floor-with-waivers holds both
- **falsifier:** held-out = the next from-scratch run must record a `run-gates.sh` verdict at every phase boundary and cannot reach `status: complete` with 0 gated words (`check-pass-evidence.py` exit 0 required before delivery); regression = `verify-freeze.sh` HOLDS (no frozen hash moved) and every finished book's gate verdicts unchanged (the suite itself is untouched — `demo-magician` reads the same rows before and after)
- **shadow:** working-tree diff only — several `skills/` files carried uncommitted changes at session start, so the author should commit after review to make rollback exact
- **source:** author directed 2026-10-13 ("Make the commonplace entry first. Then wire it into skills. Then fix the contradictions in the skills"); agent drafted; verifier stack run post-change (sync-skills, check-errata, verify-freeze, preflight)

### 2026-10-13 — promotion (craft, framework-level, author-directed) — the registry refuses a finished claim with no evidence
- **from:** the same audit, remaining step 1: `status: complete` in BOOKS.yaml was claimable with 0 gated words and no pass files (quiet-hours reached it; five registered books carried it), and nothing at the record level refused the claim — `check-pass-evidence.py` existed but nobody ran it at the moment of setting the status
- **changed:** tools/check-registry.py (+direction 3: a `complete`/`published` claim is refused when chapters carry no pass evidence or gated words are 0; `published` included because it is a strictly stronger claim and would otherwise be an escape hatch; a claim that cannot be checked is refused too, per not-run-is-never-pass); tools/check-pass-evidence.py (refactored to expose `evidence_report()` — the evidence convention now lives in one file and the two checkers cannot drift apart; CLI output and exit codes unchanged, verified byte-identical on quiet-hours)
- **over:** an evidence check that existed as a tool but not as a condition of any claim
- **reason:** the audit showed the skipping was claimable: an agent sets `status: complete` and no check disagrees. The refusal belongs where the claim is made. `published` is included not by scope creep but because leaving it out would let the same claim through one line lower in the vocabulary
- **falsifier:** held-out = a registry where a complete-but-unevidenced book passes (synthetic control covers all four branches: evidenced-and-words silent, missing-evidence refused, zero-gated-words refused, published refused; positive control still exits 0); regression = check-pass-evidence CLI unchanged (quiet-hours output byte-identical) and verify-freeze HOLDS
- **shadow:** working-tree diff; previous text recoverable from git HEAD for check-registry.py and check-pass-evidence.py (both unmodified in HEAD at session start)
- **source:** author directed 2026-10-13 ("Make check-registry.py refuse status: complete when pass evidence is missing or gated words is 0"); agent drafted; verifier stack run post-change

**Immediate consequence, left for the author to decide:** the real registry now exits 1 — `demo-magician`, `muzzle-and-marrow`, `marrow-light`, `sons-of-heaven-v2`, `kagiroi-drift` all claim `complete` with 0 gated words, and `quiet-hours` remains unregistered. The repair is either the missing `evaluations/*chNN*pass*` files or a status that tells the truth (the demo books are described as fixtures in README.md); the checker deliberately re-judges no delivered manuscript and edits no book.

### 2026-10-13 — promotion (craft, framework-level, author-directed) — the contract gets a plan to answer to
- **from:** the same audit's remaining steps: `check-length.py` reads its length contract from the book's own `PROJECT_STATE.yaml`, so a band rewritten after the output was visible made the gate agree with itself and pass; the outline's numbers had no checker at all (ERRATA 2026-10-12: "the outline records a number the draft never meets", the-origin-point at 48% of floor); the freeze manifest named nineteen frozen files and verified twelve (ERRATA 2026-10-13, the seven rows Freeze 5/13 left below the scan line); and a book could carry its own stale copy of the gates (`test-books/incunabula-test/tools/check-uniformity.py` fails U1 at 30% where the frozen copy fails at 22%)
- **changed:** new `tools/check-progress.py` (unfrozen, same hygiene class as `check-pass-evidence.py` — it fails on records that contradict each other, never on prose; row `C1` fails a length contract that contradicts the outline's plan and is deliberately never deferred by `status: in_progress`; row `L2` reports running words against the outline's plan — the number the stop-the-line rule already named; the contract vocabulary is imported from frozen `check-length.py`, so one reader defines what a contract is); `tools/init-book.py` (+intake validation: a plan outside the declared band, or a floor above its ceiling, is refused before anything is created; plan keys written at creation; the verify step now judges THIS registration and reports pre-existing registry debt separately); `tools/check-registry.py` (direction 1 narrowed: only `complete`/`published` owe a manuscript on disk — a drafting book with no chapters yet is the intake state the pipeline creates, and the old rule made init-book's own verify step unpassable); `tools/run-gates.sh` (+`check-progress.py` row, contract class); `skills/incunabula/SKILL.md` (runner description names contract-vs-plan; the stop-the-line bullet names rows `L2`/`C1`); `GATE_FREEZE.md` (the seven frozen rows joined the manifest region with their exact recorded hashes — no check changed, no hash moved); `tools/prose/verify-freeze.sh` (+completeness guard: a manifest-shaped frozen row the scanner does not actually verify fails the check and names the file); `tools/preflight.sh` (+row 6, embedded instruments: a book-carried copy of an instrument is FAIL, matched by instrument name so a book's own tools remain its apparatus; the row deletes nothing); `ERRATA.md` (entry for the seven unchecked frozen files)
- **over:** leaving the contract self-declared with nothing to check it against; leaving the running total to a book-local script each book re-invents (`the-origin-point/track_words.py`); leaving seven frozen files unchecked because their rows sat in the wrong region; leaving stale gate copies in the workspace where a shell could run them
- **reason:** each gap closes at the only place it can: the contract is pinned to a second record the drafting loop does not rewrite in the same breath (the outline), the freeze ledger verifies what it lists, and the stale-copy trap is flagged where it lies. `C1` deliberately does not defer under `status: in_progress`: L1's deferral exists because a draft is not a delivery (Freeze 11), but the contract and the plan are declarations and drafting changes neither — the deferral was itself named in the audit as cover. A single-figure contract stays advisory and no tolerance is invented for it, the rule L1 already follows
- **falsifier:** held-out = every `check-progress.py` branch tested synthetic (agree exit 0; plan under floor and over ceiling exit 1; no plan exit 2; no state exit 3) and the real the-origin-point row (C1 ok on 91,580 in 80-95k; L2 shows 60,616 running against the outline's plan with ch08 under the drafting floor); a synthetic intake with a plan outside the band is refused before creation; regression = `verify-freeze.sh` FREEZE HOLDS at 19/19 rows (guard proven by injection both ways), `check-errata.py` OK (54 entries), `run-gates.sh` verdicts unchanged apart from the new row (quiet-hours still FAIL on pass evidence), and the check-registry branch matrix re-proven after the narrowing (evidenced silent; missing-evidence, zero-gated and published refused; drafting-without-chapters silent; complete-without-manuscript refused; control exits 0)
- **shadow:** working-tree diff only — nothing here is committed; the author commits after review
- **source:** author directed 2026-10-13 ("lets keep going with the improvement pass"); agent drafted; verifier stack run post-change

**Immediate consequences, left for the author to decide:** (1) the registry stays red until the five complete-but-unevidenced books and unregistered quiet-hours are repaired (unchanged from the previous entry — write the `evaluations/*chNN*pass*` files or give truthful statuses); (2) `preflight.sh` is red on six rows naming `test-books/incunabula-test/tools/` — quarantining those instrument copies under `_archive/` (or deleting them) is the author's call, the row deletes nothing. **Resolved 2026-10-13 at author direction:** the six gate copies quarantined to `test-books/incunabula-test/_archive/tools/` (nothing deleted; recorded in the book's `maintenance/PRUNING_LOG.md`, with a restraint entry for the book's own tools that stayed) — preflight green.
