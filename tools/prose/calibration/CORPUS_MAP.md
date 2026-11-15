# CORPUS_MAP — what the corpora are, what they can answer, and what they cannot

**Status: map and plan, 2026-11-12.** Nothing in `deslop-check.sh`, `CALIBRATION.md` or any
cap is touched by this document. It records what is on disk, why one corpus cannot serve
every genre, and what it would take to widen or separate them. The one action it recommends
that needs a signature is per-lane caps, and section 6 says why that is a freeze event.

Read with: `CALIBRATION.md` (the evidence record), `LANES.tsv` (the registry),
`tools/prose/corpus-report.py` (this map, measured and re-runnable),
`tools/prose/study/corpus/SOURCE_POLICY.md` (how new text may legally arrive).

---

## 1. What is actually installed

Measured 2026-11-12 by walking each directory and counting documents and words.

| directory | documents | words | works | era | registered as a lane |
|---|---|---|---|---|---|
| `corpus/elaina` (registered path) | 48 | 175,144 | 1 (a series, 3 volumes) | unrecorded | `light-novel`, **governing** |
| `corpus/montgomery` | 3 | 279,281 | 3 | 1923–27 | `native-control` |
| `corpus/multivolume` | 303 | 945,924 | 6 | 1813–1897 | `era-prepublished` (new) |
| `corpus/nonfiction` | 143 | 1,337,286 | 8 | 18th–early 20th c. | `nonfiction-discursive` (new) |
| `corpus/prescriptive` | 134 | 963,331 | 7 | 19th–early 20th c. | `prescriptive-advice` (new) |
| `corpus/action-voice` | 178 | 837,388 | 5 | 1997–2019 | `action-voice`, **governing** (installed 2026-11-12) |
| `corpus/weird-texture` | 10 | 55,656 | 1 | 2014 | `weird-texture`, study (new) |
| `corpus/layers` | 410 | 233,271 | 7 works in 410 docs | 19th–early 20th c. | `layers`, study only (new) |
| `study/corpus/sources-v2.tsv` | 0 rows | 0 | 0 | modern | the modern registry |

Counts are `corpus-report.py`'s, which strips headings the way `ductus-fit.py` does; a
plain `wc -w` reads a few hundred words higher on the large corpora.

**Total prose on disk: 4,827,281 words**, counting the light-novel lane and the
893,044 in the two new lanes. Before this map, 454,425 of them (12%) were reachable by a
lane that governed or controlled a book. Now 1,291,813 (27%) are, a further 55,656 sit in a
study lane that cannot govern, and 3.48M are measured by nothing. Registering them changed
no number — which is the point of doing it as a registry change and not a calibration.

### 1a. The borrow list arrived — 2026-11-12

Six works, supplied by the author as local copies. They were not one register, and the
registry now says so instead of averaging them:

| work | words | mean sentence | sentences ≤ 8 words | mean paragraph |
|---|---|---|---|---|
| Child, *Killing Floor* (1997) | 138,558 | 8.7 | 59.1% | 33.6 |
| Abercrombie, *The Blade Itself* (2006) | 197,230 | 13.0 | 36.9% | 37.7 |
| Sanderson, *Mistborn* (2006) | 215,199 | 11.1 | 43.4% | 27.5 |
| Bennett, *City of Stairs* (2014) | 146,334 | 14.8 | 37.2% | 25.3 |
| Muir, *Gideon the Ninth* (2019) | 140,067 | 17.0 | 28.2% | 40.9 |
| **`action-voice`** | **837,388** | **12.8** | **42.9%** | **31.7** |
| VanderMeer, *Annihilation* (2014) → `weird-texture` | 55,656 | 18.1 | 20.0% | 59.4 |

**Why VanderMeer is not in the action lane.** Five of the six sit in one band on every row
the throttle is made of. *Annihilation* is last on all three — the longest sentences, a
third of the short-sentence share of the next-slowest work, and paragraphs nearly twice the
lane's mean — because it is weird fiction, and the uncanny is made physical there by
slowing down. Averaged in, it would have dragged the lane's profile toward a register this
book is not trying to be in, and the tool whose job is to say "your book is slower than its
lane" would have been measuring its own corpus wrong. It keeps a home as `weird-texture`,
one work, role `study`: a texture reference, never a threshold source, exactly as the
registry's own rule requires. *Borne* was named in the brief and **not supplied**; the lane
is one work until a second arrives.

**What the lane settles.** The Parts Still Warm contract's three pace numbers — mean
sentence ≤ 16, ≥ 30% of sentences at eight words or fewer, mean paragraph ≤ 45 — sit inside
the band five published kinetic books occupy, and each is cleared by at least three of the
five. Those numbers were previously set from the draft's own best chapters; they are now
checked against a register.

**What had to be fixed to read them.** Four of the six were read by `extract.py`
unchanged. *City of Stairs* is a MOBI, which that tool could not open at all: it now reads
PalmDOC text records and splits on the format's own page-break marker, and the records
turned out to be mixed encoding — cp1252 apostrophes beside UTF-8 em dashes — which cost
4,790 characters until the repair pass. *Killing Floor*'s epub keeps nine chapters in one
spine document; it is cut at the bare-number chapter headings its author wrote, so the
lane's documents are chapters instead of 23k-word blocks. Dialogue is set in single quotes
in Abercrombie (British typesetting) and had been counted as 0% speech until `ductus-fit`'s
`QUOTED` read both conventions.

**Document size is not uniform across these works** — Killing Floor chapters, *City of
Stairs* page sections at ~8k words, *Annihilation* chapters at ~5k — and every cap is a
per-document rate. A coarse document reads a smoother tail than the same prose cut at its
chapters. Recorded, not corrected: splitting a book at boundaries its publisher did not
mark would be inventing documents.

---

## 2. Five flaws, each with its number

**Flaw 1 — every cap in the gate came from one series by one author.**
The eight caps in `deslop-check.sh` (D1 10, D2 5, D3 26, A23 3, A24 1, A25 1.5, P1 6, P3 7)
were derived from `light-novel`: three volumes of *Wandering Witch* — 175,144 words, one
author, one translator. That is below the 5–10 book rule this project applies to lanes, and
it violates the one-work-per-author rule by construction. The caps are not a genre's
thresholds; they are a series' habits with a plausible story attached.

**Flaw 2 — the governing lane was not installed where it is registered.** *(Repaired
2026-11-14. Kept here because the flaw is what the `INSTALLED ELSEWHERE` status existed to
show.)* `LANES.tsv` points `light-novel` at `tools/prose/calibration/corpus/elaina`, and that
directory did not exist in this checkout: the only copy sat under
`test-books/incunabula-test/tools/calibration/corpus/elaina`. The fit tool's book-carried
fallback resolves a missing path relative to the book being measured, so for any book
outside that one test tree `ductus-fit.py --lane light-novel` exited **3 NOT RUN** — the
lane that set every cap could not be re-measured here at all.

The copy was moved to its registered path on 2026-11-14 (51 files, byte-identical before
and after; the change is recorded in `maintenance/PRUNING_LOG.md`), the lane's status is now
`INSTALLED`, and `corpus-report.py` reads it as 48 documents / 175,144 words **MATCH**. The
repair settles where the text is, not what it can say: **Flaw 1 stands** — the lane is now
measurable, and it is still one series by one author. A second copy remains under
`test-books/_archive/validation-series-meta/tools/calibration/corpus/elaina`, kept with the
archived `validate-controls.sh` that defaults to it.

**Flaw 3 — era is not an axis, and it confounds the rows that matter.**
The only corpus that meets the lane size rule is `multivolume`: 6 books, 945,622 words, all
1813–1897. Every era-sensitive row moves with era, which `CALIBRATION.md` already states
rather than hides — a 1.5× line from that corpus "would fail contemporary commercial prose,
and no modern corpus exists here to check that". This is why M2 (subject openings) and M4
(texture) are printed and not enforced. The refusal is honest; it is also the corpus
telling us it cannot answer the question.

**Flaw 4 — genre is a word in a lane name, not a dimension.**
The registry had a `register` field and no era, no work count, no statement of what a lane
could answer. `light-novel` is a genre *and* an era *and* a medium (translated), and
`action-voice` is a genre with no text. Two books in different genres were compared on the
same eight numbers because there was nowhere to say they were different. The registry now
carries `works`, `era`, `status`, `answers` and `cannot`, read by header name — no tool
needs to learn the schema to keep working.

**Flaw 5 — the modern strata are empty, and the plan for them has not started.**
`sources-v2.tsv` holds a header and no rows; `check-sources.py` exits 2, which is NOT RUN
and not a pass. `SOURCE_POLICY.md` sets the bar for C-mod at roughly 30 modern works before
it can be a threshold source. Zero exist.

---

## 3. The axes a corpus has to carry

Four, and a lane is a point in that space rather than a folder of books.

| axis | what it decides | why it cannot be folded into another |
|---|---|---|
| **era** | sentence length, paragraphing, em-dash use, dialogue share — all drift hard after 1900 | `CALIBRATION.md` measures sentence length falling from 37.7 words pre-1830 to 15.9 post-1939. A threshold from one era is a threshold for that era. |
| **register** | the caps themselves: density, tics, negation, texture | this is what the eight caps measure, and it is what a book's ductus chooses |
| **genre** | incident density, chapter shape, dialogue share, how violence is priced | a thriller and a literary horror can share a register and not a chapter shape; only some rows are genre-sensitive, and the report separates them |
| **medium** | translated prose, web serial, audiobook-first | translation is a rewriting pass: it suppresses idiom and flattens sentence variance. A translated corpus is a different signal, not a genre. |

**The rule that follows:** a lane may govern a book only if it differs from that book on
none of the four. Anything else is a cross-check, never a threshold — which is what
`native-control` already is, and what `multivolume` should be named.

---

## 4. The lanes this book should have

Role vocabulary, unchanged: `governing` (sets thresholds for the books it names),
`control` (can refute a rule, never set one), `planned` (registered, no text), `study`
(measured for a question, not a register).

| lane | role | text on disk | what it can answer | what it cannot |
|---|---|---|---|---|
| `light-novel` | governing | 3 vols, 175k (installed at registered path) | what that series does; the eight current caps | anything about a second author, a second register, or modern commercial prose |
| `action-voice` | **governing** | 5, 837k, 1997–2019 | the action register's pace, and which current caps it already fails | a thriller's number specifically: one of the five is contemporary, four are secondary-world |
| `weird-texture` | study (new) | 1, 56k, 2014 | what dense physical texture costs in sentence length and short share | anything at one work; pace; the action register |
| `native-control` | control | 3, 279k, 1923–27 | whether a rule from the light-novel lane is a rule of prose or of one translator | modern idiom, genre, anything after 1927 |
| `era-prepublished` | control (new) | 6, 946k, 1813–1897 | era-relative questions; the era confound itself | anything contemporary; it is the confound, not the fix |
| `nonfiction-discursive` | control; governs the first nonfiction book (new) | 8 works, 1.34M | the nonfiction register, and which fiction caps published exposition already fails | fiction, and modern nonfiction (Carnegie is not public domain until 2032); Darwin ×3 breaks one-work-per-author |
| `prescriptive-advice` | control (new) | 7, 963k | the how-to register the scanner was derived from | any fiction lane; it is a different reader contract |
| `contemporary-commercial` | planned (new) | 0 of ~30 needed | the rows nothing here can settle: M2, M4, D1, paragraph length | everything until the modern registry has rows |
| `layers` | study (new) | 7 works in 410 docs, 233k | dialogue/narration split experiments | not a register; must never govern a book |

### What the measurement already shows

`corpus-report.py` over the five lanes that have text, 2026-11-12:

| row | lane minimum | lane maximum | gate cap | cap inside the range |
|---|---|---|---|---|
| D1 em dash /1k | 6.4 (prescriptive) | 37.5 (era) | 10.0 | **yes** |
| D2 rule of three /1k | 1.2 (native-control) | 13.0 (layers) | 5.0 | **yes** |
| D3 -ly adverbs /1k | 16.4 (native-control) | 34.7 (layers) | 26.0 | **yes** |
| A23 parenthetical dash /1k | 1.0 | 6.0 (era) | 3.0 | **yes** |
| A25 antithesis /1k | 0.0 | 3.8 (layers) | 1.5 | **yes** |
| P1 repeated opener /1k | 0.8 (native-control) | 23.0 (layers) | 6.0 | **yes** |
| P3 longest short run | 7 | 40 (native-control) | 7 | no |

**Six of eight rows have the cap inside the cross-lane range**, and **18 of 40 lane-rows
are published prose already past a cap it was not derived on.** That is the flaw in one
table: the same number is defensible for one register and fails another.

Two things in that table need a person before they are cited. `layers` is a synthetic
split, so its 23 repeated openers per 1k are an artifact of cutting dialogue out of prose,
not a register — the strongest reason it must never govern. `native-control`'s 40-sentence
short run is anomalous for 1923–27 prose and is more likely a staging artifact than a fact
about Montgomery; check the file before repeating it.

Two lanes meet the size rule today: `multivolume` (6 works, 946k) and, marginally,
`prescriptive` (7 works, 963k). Everything else is a lane under construction, and the
registry should say so on every run — which the fit tool already does.

---

## 5. Widening, in the order that pays

1. **Install what is already registered.** Point `light-novel` at a path that exists, or
   copy the series in. Costs nothing and makes the governing lane re-measurable; today it
   is not. **Do this first** — a lane nobody can find is a cap with no provenance.
2. **Register the three unregistered corpora as lanes** (`multivolume`, `nonfiction`,
   `prescriptive`). 3.25M words become measurable by `corpus-report.py` without a byte of
   new text. It also makes the era confound visible in one table instead of one paragraph.
3. **Re-derive nothing.** Stage 2 changes the registry, not a cap. The report prints, per
   lane, what the cap *would* be at 1.5× that lane's worst document — which is the
   evidence for stage 4, not the act.
4. **One modern lane, lawfully.** Per `SOURCE_POLICY.md`: `local-copy` works the author
   owns, acquired documentedly, never committed, never redistributed, 8+ word runs
   forbidden in any committed artifact. ~30 works makes C-mod a threshold source; below
   that it is a sanity check on direction. This is the only route to settling M2 and M4,
   and the only one that can say whether this project's prose is modern or machine.
5. **Separate by register only where there is evidence.** `action-voice` — done
   2026-11-12, five works, with *Annihilation* separated out of it on its own numbers;
   `nonfiction-discursive` before the next nonfiction book.

Sizes, so the ask is concrete: **a lane is 5–10 works and 500k–1M words.** C-mod at 30
works is deliberately larger because its purpose is a *baseline*, not a threshold, and
`SOURCE_POLICY.md` fixes that number for the same reason.

---

## 6. What this does not do, and the one thing that needs a signature

- **No cap moves.** `deslop-check.sh` is untouched. Every cap in it remains the one derived
  from a single series, with that provenance now written down rather than assumed.
- **No strike replaces a measurement.** Widening the registry does not license a new number;
  it licenses a *report* about the number.
- **Per-lane caps are a freeze event.** The scanner reads one global set. Letting
  `action-voice` derive its own thresholds requires a lane dimension in the scanner, a
  `CALIBRATION.md` record per lane, and the author's sign-off — in that order. The default,
  stated in `ductus-designer`'s open questions, is that it waits. `corpus-report.py` exists
  so the decision can be made on numbers instead of instinct.

## 7. Open decisions for the author

1. **Is the light-novel series still the governing register** for the catalogue, or is it
   the corpus for one book and the era corpora take over for the rest?
2. **Per-lane caps: now or after C-mod?** After C-mod is cheaper and the report already
   quantifies the difference; now means touching the scanner twice.
3. **Who supplies the modern works** — the author's own shelf, or the study's fetch path?
   `SOURCE_POLICY.md` allows both; only the first is available today.
