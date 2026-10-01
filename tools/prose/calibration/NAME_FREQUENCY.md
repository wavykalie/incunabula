# Name frequency data — the denominator for the name-default filter

**Purpose.** `check-names.py` needs to answer one question: *is this first name a name the
model reaches for by default?* That question cannot be answered from the 1813–1905 prose
corpus, and the reason is worth recording because it is the same failure mode as `U1` once
already:

> A stylometric finding about period prose measures the period.

**Why not the prose corpus.** Measured 2026-09-28 over `calibration/corpus/multivolume`
(303 files, 945,924 words). Nineteenth-century fiction names characters behind
honorifics — *Miss Bennet*, *Sir William*, *Lady Lucas*. Extracting `First Last` pairs
yields 481 distinct first tokens, of which the top entries are `Miss` (802), `Sir` (326),
`Lady` (165), `Mr` (69) and `Mrs` (116). Bare given names barely register: `Elizabeth`
appears 2 times, `Mary` 57, `Jane` 45. **`Roy` and `Ruth` appear zero times in 946k
words of published fiction.**

A threshold derived from that corpus would not measure model defaults. It would measure
that English literature before 1900 did not often write people's names in the two-word
capitalised form this filter reads. Using it would produce confident nonsense.

**Therefore the denominator is real-world name frequency**, which is a public dataset about
actual people rather than a dataset about how nineteenth-century prose transcribes a
postal directory.

## What is measured, and what is not

| | |
|---|---|
| **Measured** | how common a given first name is among people actually born with it |
| **Not measured** | whether the name suits this book's setting, era, region, or theme |

Those are different things and this file is only about the first. A filter that encoded
the second would be an author's taste written into an instrument, and an instrument that
enforces taste is not a measurement — it cannot be re-derived, cannot be argued with, and
will silently overrule the person who has to live with the result.

## The lists

**Tier A — SSA national top 20** (Social Security Administration, births 1926–2025, top
five per year, both sexes). The strongest available statement of "the name a model has
seen most." 20 names.

**Tier B — Nameberry top 100 girls + top 100 boys, 2025** (nameberry.substack.com,
Dec 2025, pageview-derived). A broader, style-aware list that tracks the front edge of
naming fashion rather than the settled centre. 199 names.

Tier B is deliberately *not* a failure on its own. See the thresholds below.

## Thresholds

| tier | condition | severity | reasoning |
|---|---|---|---|
| **A** | first name in the SSA top 20 | **FAIL** | the highest-prior name in the language; using it is close to invisible as a choice |
| **B** | first name in the Nameberry top 100 | **WARN** | report it, let the author rule |
| — | not on either list | pass | |

**Why B is a warning and not a failure.** A top-100 name is not per se a defect. `Cora`
is Nameberry #28 and is also a perfectly ordinary name for a 74-year-old woman in a rural
American county — where it is *more* correct than a fashionable one, because the
character was born in 1951. Popularity measures what a name is now, and a book's cast is
mostly people who were named long before now. What makes a popular name a tell is
**anachronism and convergence**, not popularity by itself: a 1951-born woman called
Aria is a defect; the same woman called Cora is not.

So B is reported rather than blocked, and the deciding question is always *when was this
character born, and where would they have been living.* A gate cannot answer that. The
author can, in one sentence.

**Why A is a failure but still not absolute.** A top-20 name can be correct — a character
born in 2001 plausibly. A25/U6-style rows are `fail` because the rate is disqualifying at
any plausible setting; a name is not. This row is `fail` because the prior is strong
enough that reaching for it is a default rather than a decision, and the whole point of
the filter is to force a decision.

## What this filter is not for

- **It is not a rule that names must be thematic.** The author's own position is that names
  should carry meaning — the flower, the ancestor, the thing the character is. That is a
  *craft* standard and it belongs to the author and to the voice matrix, which is where
  meaning is recorded. Encoding "must be thematic" in a gate would make the pipeline
  unable to produce a plain name for a character who needs one, and would convert a
  preference into a rule that generates a different preference in disguise — choosing
  flowers because the gate said flowers.
- **It is not a cross-book collision check.** That is `check-names.py`'s other job, and it
  is a hard failure on a different axis: not "this name is common" but "you have already
  used this name."

## Reproducing

The lists in `NAME_FREQUENCY.tsv` were transcribed from those two public sources on
2026-09-28. `check-names.py` reads the TSV and does no network access, so a gate result is
attributable to a fixed file rather than to whatever a website served on the day.

| list | source | retrieved |
|---|---|---|
| SSA top 20 | ssa.gov/oact/babynames/top5names.html | 2026-09-28 (via search summary; page returns 403 to automated fetch) |
| Nameberry 100+100 | nameberry.substack.com/p/these-were-the-top-baby-names-of | 2026-09-28 (fetched in full) |

The SSA figure is the weaker of the two citations: the canonical page refuses automated
requests, so the top-20 set was assembled from the search result rather than from the
page itself. It is corroborated across several independent outlets reporting the same
SSA figures. If a future run needs this list to be exact rather than corroborated, it
should be transcribed from the page by hand.
