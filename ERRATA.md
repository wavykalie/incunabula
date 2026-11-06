# ERRATA

The printer's errata sheet: corrections issued after the impression, and observations that
have not yet become corrections.

**Append-only.** Entries are added; entries are never edited to look better than they were.
An entry that turned out to be wrong gets a `WRONG` line under it, and the wrongness stays
visible. That is the point — a ledger with no recorded mistakes is a ledger being curated,
and a curated ledger cannot be trusted with the job.

**Amended 2026-10-14 — standing claims are repaired in place.** Append-only governs
history: a dated entry records what was measured on its date, and is never rewritten.
It does not make a claim immortal. Text outside the dated entries — a heading, a tally,
a count in prose — describes the program **as it is now**, and the program moves. When
the live program contradicts one of those standing claims,
`tools/prune-stale.py` (the self-prune) corrects it in place and keeps the old wording
verbatim in `maintenance/PRUNING_LOG.md`, in the maintenance-protocol §7 format. A
claim inside a dated entry is never edited: it is reported with the number the program
now has, for the author to rule on, because a record of what was true then is history
and not drift. This is the one carve-out from append-only, author direction 2026-10-14,
and it is exactly this wide.

This file feeds `PRINTERS_COPY.md`. It is the destination that `check-uniformity.py` has
needed since it was written: *"Reproducing the same exemption across books is itself the
pattern this check exists to catch."* The system identified a rule waived three times as
something that should be escalated, and had nowhere to escalate it to. This is that place.

## How an entry is promoted

Nothing here is a rule. An entry becomes a rule in `PRINTERS_COPY.md` only through the
protocol in its §7, and in the default `hand` mode that means a person, reading a diff.

**Three states, and the middle one is the trap:**

| state | meaning | may change a threshold |
|---|---|---|
| `observed` | one book did this | never |
| `proposed` | N books agree and the corpus is named | never — proposals move to the *registry*, not the gate |
| `adopted` | a person applied it to `PRINTERS_COPY.md`, with a diff | only on a corpus change, and only by hand |

A book that trips a rule twice writes a line. It does not move the gate. The reason is in
`PRINTERS_COPY.md` §4 and it is the finding this whole layer exists to respect: a
stylometric finding about human prose is a finding about **the sampled humans**. A threshold
re-derived from six books somebody liked has laundered a period confound into a permanent
constant, and nothing downstream will ever be able to tell.

Set `errata.mode` in `PROJECT_STATE.yaml` to change promotion behaviour — `hand` (default),
`bulk` (auto-promote observations to the project-local copy at three agreeing books), or
`auto` (thresholds may also re-derive, with a printed changelog and never without a named
corpus).

## Entry format

```
### YYYY-MM-DD — one line naming the observation
- **row:**      U4 | A1 | S1 | (brief | delegation) — what it touches
- **observed:** what happened, in one sentence
- **n:**        how many books, and how many independent
- **evidence:** file, tool, corpus, or the number
- **motive:**   aesthetic | privacy — required, and it is a human's account
- **state:**    observed | proposed | adopted
- **proposes:** what would change in PRINTERS_COPY.md, or "none"
```

`check-errata.py` validates this file against that format and against `PRINTERS_COPY.md`'s
own rules. It fails on a missing motive, a missing state, an undated entry, or a `proposed`
entry with no `n`.

---


---

## The ledger

**One entry, and it is the only one a fresh install should carry.** A new ledger is
empty, and this file is where your own findings accumulate — seeding it with somebody
else's would make the record a default rather than evidence.

The entry below is not a finding about prose. It records the constraint that produced
it, in the ledger's own format, so that the next person to notice an entry in a fresh
install does not have to guess why it is here.

### 2026-10-15 — the validator requires an entry, so the template ships one
- **row:**      (brief) — the record layer's own shape
- **observed:** `tools/prose/check-errata.py` fails on a ledger with no entries in the
               required format, so an empty template cannot pass the guard on a fresh
               install. The alternative was to ship somebody else's findings as the seed.
- **n:**        1 — every install, from the first run
- **evidence:** `tools/prose/check-errata.py`, run against an empty ledger
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. If the guard should accept an empty ledger, that is a change to a
               frozen instrument, and it goes through the freeze procedure in
               `GATE_FREEZE.md` — not through this entry.

An entry is added when a book trips something, an instrument is found to be wrong,
or a measurement is re-derived. `tools/prose/check-errata.py` validates every entry
against the format above and against `PRINTERS_COPY.md`'s rules, and it is the
mechanism by which this layer improves rather than merely accumulates.

**Nothing here is a rule until it is adopted, and adoption is a person's act.** An
entry that turns out to be wrong gets a `WRONG` line under it; the wrongness stays
visible, because a ledger with no recorded mistakes is a ledger being curated.

### 2026-10-15 — the anti-AI catalog merged into one home
- **row:**      (merge) — the record layer's own shape
- **observed:** The `humanizer` skill's 24-pattern catalog and `setting`'s anti-AI tell
               list described the same tells as `deslopify/references/style_guide.md`
               under two other roofs — the same catalog in three places, with the
               scanner as the mechanical fourth. All three are now one catalog in the
               deslopify guide. The duplicates were folded in, not appended, and where
               two lists described one tell the sharper wording won: negative
               parallelism, tricolon, vague attributions, em dashes, the serves-as
               dodge, superficial analyses, false ranges, "despite its challenges",
               grandiose inflation. Tells that existed in only one list moved in whole:
               promotional tone, insisting on notability, synonym cycling, chatbot
               residue, knowledge-cutoff hedging, sycophancy, filler, over-hedging,
               generic positive endings, title-case headings, named emotions,
               over-smooth transitions, dramatic And openers, decorating metaphors, the
               pseudo-profound closing. `humanizer`'s constructive half ("add a pulse")
               is the guide's second half; its per-chapter checklist moved to the
               `deslopify` skill. `setting` now references the catalog and restates
               nothing. The scanner is untouched, per the audit's own constraint.
- **n:**        1 — one catalog, one checklist
- **evidence:** `skills/deslopify/references/style_guide.md`, `skills/_archive/humanizer/MOVED.md`
- **motive:**   aesthetic
- **state:**    observed
- **proposes:** none. Three lists of the same tells is redundancy in the documentation,
               not a measurement; no threshold, rule, or regex moved.

### 2026-11-06 — V3 gates, and U5's warn line moves to the measured p10
- **row:**      V3 (new) | U5
- **observed:** `check-dialogue-tags.py` gains V3, the first row in that class with a
               measured population: the whole-book breath-family share of tagged spans,
               fail above 0.107, warn above 0.082. The corpus is 167 public-domain
               English novels (stratum C-dist-2 of `tools/prose/study`, frozen extractor
               v2, disjoint from the 140 novels in `calibration/`), where 5% of books
               exceed the fail line. The pipeline's fifteen books run at median 0.168 and
               11 of 15 exceed it; the twenty naive-draft books exceed it six times. U5's
               warn line moves 75 -> 73.7, that stratum's p10, which fires on 12 of the
               fifteen pipeline books and none of the naive ones.
- **n:**        167 human books; 35 pipeline and naive-draft books
- **evidence:** `tools/prose/study/STUDY_REPORT.md` section 5.3;
               `tools/prose/study/corpus/dist-features-2/cdist.csv`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** none further. The fail line is a corpus percentile and may not move on a
               book's failure; the 1.5x headroom convention does not apply to a two-sided
               band, and tightening the fail line to the p10 would fail 26% of humans.

### 2026-11-06 — four study measures enter the Rejected registry
- **row:**      (registry) — `PRINTERS_COPY.md` section 4
- **observed:** The prose-tell study's AI-term cap, weather-opener gate, cross-book
               name-reuse threshold and opening-similarity row are recorded as rejected,
               each with the arm-level count that killed it. The Rejected registry goes
               30 -> 34 entries, and `REJECTED_FLOOR` in `tools/prose/check-errata.py`
               is raised to 34 in the same change.
- **n:**        1 change; the counts behind it come from 167 human books and 35
               pipeline/naive books
- **evidence:** `PRINTERS_COPY.md` section 4; `tools/prose/check-errata.py`
- **motive:**   aesthetic
- **state:**    adopted
- **proposes:** none. The rows now work in the other direction: a future proposal that
               reaches for one of them has to argue with the count that rejected it.
