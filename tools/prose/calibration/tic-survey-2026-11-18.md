# Tic survey — 2026-11-18

Cross-book measurement after `A27` was added to `tools/prose/deslop-check.sh`. Scope: **336
manuscripts** — 22 under `test-books/` including archives, and 314 study controls under
`tools/prose/study/books/` — measured against **1,247 published documents** (≥500 words) from
`tools/prose/calibration/corpus`, 6,419,470 words.

Every number below was counted with a regex, not estimated. Raw data:
`tools/prose/calibration/tic-survey-2026-11-18.tsv`.

---

## 1. Coldbrook Junction is not in this checkout

The name appears in three places, all of them *about* it rather than *by* it:

- `test-books/incunabula-test/RUN_REPORT.md:62` — "Coldbrook 9 fail / 2 pass" as a prose control
- `test-books/sons-of-heaven-v2/PROJECT_STATE.yaml:51` — "A1 does not detect the AI control
  (Coldbrook scores 0.533, inside the human range)"
- `test-books/_archive/validation-series-meta/book-1/*` — intake and canon files

No manuscript directory matches `coldbrook`, and no manuscript contains the word in its first
6,000 characters. **There is no Coldbrook text here to scan.** If a claim about Coldbrook's prose
is to be checked, the file has to be supplied; this survey will not infer it from the name.

The nearest in-tree analogue — an 18-chapter control with its own intake and canon — is
`validation-series/book-1`, title *"Merope book one"*. It is **the worst manuscript in the tree on
both tics below**, so it is the useful stand-in for the question that was actually being asked.

---

## 2. `A27` across the tree — the top of the distribution

| book | ch | words | A27 /1k | gloss | hands | did-not |
|---|---|---|---|---|---|---|
| `validation-series/book-1` (Merope 1) | 11 | 15,377 | **1.82** | 0.00 | 0.07 | **1.76** |
| `_archive/…/book-1` (same, archived) | 7 | 15,439 | 1.81 | 0.00 | 0.06 | 1.75 |
| `validation-series/book-2` (Merope 2) | 11 | 14,962 | **1.54** | 0.00 | 0.07 | **1.40** |
| `advent-horror` | 24 | 46,305 | **1.53** | 0.39 | 0.32 | 0.28 |
| `_archive/…/book-2` | 7 | 15,057 | 1.53 | 0.00 | 0.07 | 1.39 |
| `stall-twelve` | 3 | 6,160 | 0.97 | 0.00 | 0.00 | 0.00 |
| `the-origin-point` | 30 | 60,616 | 0.66 | 0.12 | 0.13 | 0.33 |
| `muzzle-and-marrow` | 10 | 16,685 | 0.66 | 0.00 | 0.12 | 0.48 |
| `the-emptying` | 6 | 7,685 | 0.65 | 0.00 | 0.65 | 0.65 |
| `the-parts-still-warm` | 13 | 130,060 | 0.64 | 0.02 | **1.13** | 0.70 |
| `under-three-coats` | 6 | 6,871 | 0.44 | 0.00 | 0.87 | **1.60** |
| highest study control (`study/B-17`) | 40 | 64,593 | 0.15 | 0.02 | 0.00 | 0.12 |

Published baseline: **0.02/1k**, worst single document **1.21/1k**.

**Four manuscripts sit above the worst published document**, and every one of them is a book this
workshop drafted. The 314 study controls top out at 0.15/1k. That is the shape of a house habit, not
a property of the corpus: this tic is being produced here, at 8–90× the published rate, and the
controls show it is avoidable.

---

## 3. What the rule set is missing

Each candidate was measured on the same 1,247 published documents. The test is not "does it feel
like a tic" but "does any manuscript in this tree exceed the worst published document". Two do.

### `A28` — the withheld-speech beat: **earns a row**

`did not say / move / answer / look / turn / stop`

| | rate /1k |
|---|---|
| published corpus | **0.06** (p90 0.26, worst document **1.33**) |
| `validation-series/book-1` | **1.76** (27 hits) |
| `under-three-coats` | **1.60** (11 hits) |
| `validation-series/book-2` | **1.40** (21 hits) |
| `marrow-light` | 0.94 (73 hits) |

Three manuscripts exceed the published maximum, one of them by 32 %. The construction is ordinary
narration — a person not answering is a scene — so this cannot be a gate; but at 1.76/1k it is the
book's default way of writing every pause. Proposed: **REPORT row, cap 2 per 1,000 words (warn
above 1 per 1,000)**.

### `A30` — the hand-placement beat: **earns a row**

`put his / her / both hand(s)`

| | rate /1k |
|---|---|
| published corpus | **0.01** (p90 0.00, worst document **0.73**) |
| `the-parts-still-warm` | **1.13** (147 hits) |
| its own draft, 2026-11-12 | 0.25 (34 hits) |
| `under-three-coats` | 0.87 |
| `the-emptying` | 0.65 |

The live manuscript runs **4.5× its own earlier draft** — this is a revision artifact, not a
first-draft habit, and it is 55 % above the worst published document. Proposed: **REPORT row, cap
1 per 1,000 (warn above 1 per 2,000)**.

### The gloss: **does not earn a row, and the reason matters**

`That was the part / thing`

`advent-horror` runs 18 instances at **0.39/1k**, which is roughly 490× the corpus rate and looks
alarming by ratio. By the test the rest of this file uses, it fails: the worst published document
is **0.44/1k**, so the book is *inside* the published distribution. 5 published hits across 5
documents in 6.4M words do this. A row here would be a gate in name only, and `DIRECTION.md`
already caps the gloss at one per story, and the book does not cleanly meet it: 18 instances
across 24 stories, with one chapter carrying two. The cap holds on average, not in every story. Recommendation: **leave it; re-measure if a second book repeats it.**

---

## 4. Checked and cleared — do not add these

Eleven constructions that look like tics and are not, by this evidence. Maximum manuscript rate
against the worst published document:

| construction | corpus /1k | worst doc | max manuscript | verdict |
|---|---|---|---|---|
| `and then` | 0.47 | 3.61 | 2.51 (advent-horror) | inside |
| `like a/the` | 0.67 | 4.94 | 2.26 (kagiroi-drift) | inside |
| `as if` | 0.43 | 5.11 | 2.36 (study control) | inside |
| `the way` (any sense) | 0.29 | 3.29 | 3.88 (book-2) | **above — but this is A27's denominator, not a new row** |
| `there was a` | 0.22 | 2.18 | 0.87 | inside |
| `for a moment` | 0.10 | 2.00 | 0.73 | inside |
| `for a while` | 0.05 | 1.69 | 1.02 | inside |
| `he/she had not` | 0.05 | 3.51 | 0.61 | inside |
| `in the dark` | 0.04 | 1.35 | 0.52 | inside |
| `the sound of` | 0.04 | 1.17 | 0.35 | inside |
| `something in the/his/her` | 0.02 | 1.43 | 0.29 | inside |
| `nobody said/moved` | 0.00 | 0.72 | 0.13 | inside |

The `the way` row is the useful control on the instrument: the *whole* phrase family is above the
published worst in `book-2` (3.88 vs 3.29), which is the same finding `A27` records on the
comparison subset — two independent measures agreeing, not two rows needed.

---

## 5. What this means

1. The tic is a **workshop habit**, not a corpus artifact: 4 of 22 manuscripts above the published
   worst, 0 of 314 controls.
2. **`A28` and `A30` are genuine gaps** — both exceed the worst published document in multiple
   manuscripts, both are body-language beats rather than vocabulary, and neither is in `A1`–`A27`.
3. The **gloss is a near-miss**, and adding a row for it would repeat the D1/D2 mistake this
   project has already recorded twice.
4. `A27`'s worst offenders are not the book that prompted it. `advent-horror` is fourth. The
   control books (`validation-series/book-1` and `-2`) are worse, and they are also the worst on
   `A28`.

## 6. Limits

- Caps proposed here are 1.5× the worst published **document**, following the convention in
  `deslop-check.sh`. They have not been re-derived against the 336-manuscript distribution, which
  is much wider than the published corpus; a cap set from it would be looser.
- Regex measures surface form. `did not say` includes ordinary narration where the beat is not a
  tic; the row is report-tier for that reason.
- Study controls are a mixed corpus (published and machine-crafted); they are used here as a
  second population, not as a gold standard.
- `A28` and `A30` were implemented on top of this survey as REPORT rows under Freeze 27; their
  caps, warn bands, the controls run and the manifest re-key are in `GATE_FREEZE.md`. The gloss
  keeps the id `A29` unassigned, per section 3.
