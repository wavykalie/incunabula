---
name: rewrite
description: Re-derive an existing finished book under a changed drafting framework, contract, or gate baseline. Distinct from corrector, which revises passages inside a living text. Use when the rules the book was built under have changed - a chapter-length rule removed, a canon decision reversed, a gate re-baselined - and the whole book has to be re-measured and repaired against the new rules, not patched in place. Also use before shipping any book whose artifacts predate a repair.
---

# Rewrite — the book was built under different rules

Corrector revises a living text. This re-derives a book that was **finished under a
contract that has since changed**. The text may be excellent and still be wrong for the
new rules, because the rules are not in the prose.

Worked example: `validation-series/` Merope 1 and 2, re-derived 2026-09-28 after
`DRAFTING_FRAMEWORK.md` removed chapter-length targets. Record: `REWRITE.md` in that
project. Read it before improvising a sequence here.

## The mistake this skill exists to prevent

Running the gates, seeing rows fail, and editing until they pass. That produces a book
that satisfies a checker and a manuscript that has been damaged to do it. Every step
below exists because that mistake was made or nearly made, and each one is cheap now.

## Order of operations

### 1. Name the delta in one sentence

What changed, and when. "Chapter-length targets removed, `DRAFTING_FRAMEWORK.md`
committed `ae5fed6`." Not "the framework is different now." A vague delta produces a
vague rewrite, and you cannot tell afterwards whether it worked.

If you cannot name it in one sentence, stop and ask. You do not yet have a task.

### 2. Read `_archive/` before you decide what needs rewriting

`_archive/README.md` is the index. It was missing until 2026-09-29, and for two months
`_archive/hollow-bridge/book-genesis-v4/` — a complete checkout of the framework's
**previous version**, with its own git history and 19 skills — sat there undocumented.
Do not assume an archived subtree is an old manuscript.

Two questions this answers before you spend an hour:

- **Does a prior version of this decision already exist?** The v4 checkout answers
  "has anyone tried this and abandoned it" better than any design note in the live tree.
- **What is the before-state, physically?** If a previous rewrite of this book already
  re-chaptered it, the archive is the only place the earlier chapter division may still
  exist, and step 8 destroys it. Find it now, while you can still measure against it.

The general rule, from a recovery that succeeded once and failed once: check for the
previous version **before** the operation that replaces it, not after you notice it is
missing. Read `validation-series-meta/V1-MANUSCRIPT-RECOVERY.md` if you have not — it is
short, and it is the worked example behind step 8.

### 3. Establish that the book is *governed* before you trust a single number

A gate that exits 2 may mean "this book declares no such thing," or it may mean "this
book's state file is in an archive and nothing here can see it." Those are opposite
findings with identical output. `check-length.py` now separates them (exit 3,
UNGOVERNED) — use it. Note that one such file is `_archive/validation-series-meta/` — an
archive path, which is why step 2 comes first.

**Find `PROJECT_STATE.yaml` first, in the book's own root.** If it is not there, stop.
Every downstream measurement is a measurement of nothing. Do not continue and do not
report the result as a finding about the framework.

### 4. Measure before you touch anything

The pre-repair number is the control. Without it you cannot tell whether your repair
helped, and a rewrite that reports only its own output is unfalsifiable.

For the drafting framework that means: per-chapter word counts, range, ratio, CV. Write
them down where they will survive the session.

### 5. Read every flagged instance before editing it

Gates report **locations**, not verdicts. Verified on the same corpus: of 25 hits on one
row, 24 were the real construction and 1 was the regex matching `" not"` inside
`"nothing"`. Editing the correct sentence to dodge a substring charges the manuscript for
the instrument's error.

So: print each hit with its surrounding paragraph, and decide per instance. **Negation
folded into positive statement is the default repair** — it keeps the claim, removes the
tic, and usually produces a tighter sentence. But a construction doing work stays: in the
worked example, four antithesis hits in one chapter needed three cut, and the fourth was
kept because it was a character's dialogue, where the cadence *is* the voice.

Never repair by regex substitution. If you are about to run `sed` over prose, the reading
in step 5 did not happen.

### 6. Protect the stubs

A short chapter that contains a scene is not a defect. It is usually the reason the book
has any range at all. Read the shortest chapters **whole** — the judgement is whether a
chapter *ends* or merely stops, and you cannot make that call from a word count.

### 7. Re-measure, and treat a collapse as a failed hypothesis

The spread must survive the repair. If chapters re-clump after you have removed a tic,
then the spread was coming from the plan, not the content, and the new framework's
premise is wrong. Report that; do not smooth it over.

Numbers that came out this way, and are worth recognising:

| book | had targets | range | CV |
|---|---|---|---|
| Merope 1 | **yes** | 4.8× → **4.9×** | 40.9% → **41.0%** |
| Merope 2 | **yes** | 4.6× → **4.6×** | 40.0% → **39.9%** |
| The Trick | yes | 2.4× | 23.7% |

**Corrected 2026-09-29.** These rows previously read `had targets: no` for Merope, and that
was wrong. Merope was drafted to a declared 7 × ~2,450 and scored CV 5.8% / 10.9%; the
40% figures are the same prose re-partitioned into eleven chapters afterwards. The `no`
described a file, not a drafting. Evidence in `ERRATA.md` 2026-09-29.

Read the row as a caution about **artifact provenance**, not as support for dropping
targets. All three books here were written to targets.

Repairs that shrink a book are evidence the rule took hold. Patches that pad it are
evidence you are arguing with a gate.

### 8. Rebuild the artifacts. This is not optional.

In the worked example the shipped EPUBs predated the rewrite by three days and carried
the old text in every chapter. The manuscript was clean and the artifact was a lie, and
nothing in the gates looks inside a ZIP.

Rebuild, then **verify by reading the artifact back** — open it, grep for a sentence you
introduced, and confirm the sentence you replaced is absent. A build that exits 0 has
still only proven it ran. Byte-identical output after a real text change is a bug report,
not a coincidence; check it.

**And before any of that: if the rewrite re-chapters, archive the manuscript it is
replacing.** In the worked example the 7 → 11 re-chapter overwrote seven chapter files in
place. The v1 metadata was archived correctly; the v1 manuscript was not, and survived only
inside an already-built EPUB that no index pointed at. Every gate stayed green throughout,
because the gates read the *current* manuscript and that one was complete. **A frozen gate
over missing inputs passes.**

The check is cheap and it is the whole safeguard: after any re-chaptering, the pre-rewrite
chapter files must be readable somewhere outside the live book directory. If they are not
yet, that is step 2's job, not step 8's — but step 8 is where you find out you skipped it.

### 9. Record what the rewrite did *not* prove

Say plainly which parts of the new contract the book was never under. In the worked
example: the Merope books were re-chaptered from seven planned chapters to eleven
specifically to break uniform lengths, under a state file declaring
`average_words_per_chapter_planned: 2450`. So they are evidence that a spread **survives
a repair** under the new framework. They are not evidence that drafting under the new
framework *produces* that spread. Two books re-derived after the fact are not two books
drafted under the rule.

That sentence is worth more than a paragraph of congratulation. A rewrite report that
overstates what it demonstrated will be believed by the next person who reads it.

## What this skill must not do

- **Add a gate.** The instrument class is closed (`GATE_FREEZE.md`, Freeze 6). A check
  you want becomes a line in a sweep document, not a script. If a rewrite needs a
  measurement nobody has, write it down in the record and leave the gate count alone.
- **Move a frozen hash without a Freeze entry.** Changing an existing gate for
  correctness is allowed and was done twice (Freeze 7). Changing it to make a book pass
  is not a rewrite step, it is a different activity, and it needs its own name.
- **Delete anything to make a book look tidy.** Superseded work is archived with a
  reason and a provenance line (`maintenance/PRUNING_LOG.md`). Archived out of a book's
  own directory, it disarms the gates that read it — see step 3.
- **Assume an archive is a graveyard.** `hollow-bridge/book-genesis-v4/` is the previous
  version of this framework, not superseded manuscript. Read `_archive/README.md`, and
  add to it in the same commit that archives — see step 2.
- **Report a gate you did not see run.** Exit 0 and "ran" are different claims, and exit
  2 and 3 now mean different things from each other.

## Output

A `REWRITE.md` in the project holding: the delta, the before and after measurements, what
was repaired and why each repair took the form it did, the artifacts rebuilt and verified,
the rows still open, and — under its own heading — what the rewrite did not prove.
