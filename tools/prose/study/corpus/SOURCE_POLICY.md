# Corpus source policy — beyond Project Gutenberg (C-dist v2)

**Status:** proposed 2026-11-04, revised the same day to admit modern in-copyright prose that
the researcher lawfully holds. Applies to sources added **after** the 109-book PG baseline.
The baseline is not re-fetched, re-mixed or re-selected; it stays the public-domain stratum it
was measured as.

## 1. What is being changed

`corpus/fetch-dist.py` rule 1 is *"public domain — Project Gutenberg only"*. That is a
**licensing** rule, not a taste. It makes the right to copy unambiguous and lets the corpus be
rebuilt from a catalogue instead of assembled by hand.

It also has a scientific cost that the study has been carrying silently: 109 books of 19th- and
early-20th-century prose are the whole human baseline. Sentence length, paragraphing, dialogue
share, chapter length and em-dash rate all move with era. A 2026 generated novel is being
compared against a baseline from before 1930, and the report cannot separate "machine" from
"modern". That is the reason to broaden, and it is a stronger reason than convenience.

## 2. The legal position, stated accurately

The earlier draft of this policy overcorrected and treated "purchased" as unusable. That was
wrong for this study, and the distinction is worth stating once:

- **The exposure is in reproduction and distribution, not in measurement.** *Authors Guild v.
  HathiTrust* (2d Cir. 2014) upheld mass digitisation of in-copyright books for full-text search
  **and non-consumptive research**, precisely because the corpus was not made available for
  reading. *Authors Guild v. Google* (2d Cir. 2015) upheld search and snippet display on the
  same reasoning. Counting sentence lengths in a file you lawfully own is the non-consumptive
  case those decisions protect; shipping the file is not.
- **Acquisition is where the limits actually are.** Buying or being given a copy is lawful.
  Pirating one, or stripping DRM to obtain one, is not, and DMCA §1201 is a separate problem
  from copyright. A lawful copy analysed locally and never redistributed is a different act from
  a scraped copy, and this policy treats them differently.
- **Platform terms bind on the act of copying.** Downloading through a site's own export is
  using the mechanism it offers; bulk-scraping against its terms is not. That distinction is
  about how the bytes were obtained, not about what is done with them afterwards.
- **Non-commercial research is not a magic word.** It supports the fair-use factors; it does not
  replace them. What carries the weight here is non-consumptive use plus no redistribution.

This is a policy for an auditable study, not legal advice. The moment the corpus stops being
non-consumptive — text excerpts in a committed artifact, a published sample, a shared corpus —
this reasoning no longer applies and the row must be re-cleared.

**Three rules hold the position up, and none of them may be relaxed:**

1. Texts live in the git-ignored `books/` tree and are **never committed or redistributed**.
2. **No committed artifact carries a verbatim run of ≥ 8 words** from a `local-copy` work.
   Committed artifacts are source ids, counts, hashes, feature numbers and similarity scores.
   `corpus/check-nonconsumptive.py` enforces this.
3. Every work carries its provenance and the evidence for it in `corpus/sources-v2.tsv`.

## 3. Provenance classes

Recorded in the `license` column, because it is the provenance the gate can check — not a claim
about the copyright status of the work.

**Analysable as of right**

| class | basis | redistributable |
|---|---|---|
| `public-domain` | copyright expired (the existing PG baseline, Standard Ebooks) | yes |
| `cc0` / `cc-by` / `cc-by-sa` | the work's own stated licence (verify per work) | yes, with attribution |
| `author-permission` / `publisher-permission` | written grant on file | per the grant |

**Analysable as a local copy — the new class**

| class | basis | redistributable |
|---|---|---|
| `local-copy` | lawfully acquired (purchased, gifted, author-supplied, or downloaded through the platform's own export), analysed locally, never redistributed | **no** |

`local-copy` covers modern novels you own, Royal Road / AO3 / Scribble Hub / Wattpad works you
obtained through the site's own download, FanFiction.net and forum fiction, creepypasta reposts,
and indie freebies. It requires: an acquisition record (receipt, invoice, download date, or the
author's message), the date, and `redistributable=no`.

**Refused**

`pirated`, `drm-stripped`, `all-rights-reserved` (used as if it were a permission), and unknown.
`fair-use` is refused as a *licence value*: it is a defence to a claim, not a grant, and a
registry that records it as one cannot be audited.

## 4. What a source change does to the analysis

The C-dist corpus is the human baseline for every threshold. Mixing sources without saying so
would let a source effect masquerade as a human distribution. So:

- **Source is a stratum, never a pool.** Every v2 row carries `source` and `stratum`. Thresholds
  are derived and reported within stratum on a separate feature directory; a pooled figure is a
  sensitivity, never the primary baseline.
- **The PG baseline keeps its published thresholds.** C-dist (109 books, public domain) remains
  the shipped threshold set. The modern works form **C-mod**, a second baseline derived through
  the same frozen extractor, reported beside C-dist and used to ask whether a residual tell is
  era-driven or pipeline-driven. If the two baselines disagree, the honest answer is that the
  row is era-confounded — not that one of them is wrong.
- **Era is recorded, never adjusted away.** `publication_year` where known, `era_proxy=unknown`
  otherwise; source and era are reported as confounded.
- **Web serials are not novels.** Editing, chaptering and length differ. Segment-level features
  (2,500-word units) remain comparable; book-level rows are reported per source, not pooled.
- **Fan fiction carries fandom names and terms.** Name features are reported separately for that
  stratum; a fandom's cast list is not a prose tell.
- **One work per author still holds.** A prolific web author must not become the corpus.
- **A modern stratum needs volume to be useful.** Below ~30 works, C-mod is a sanity check on
  direction, not a threshold source (REDTEAM.md B1 applies unchanged).

## 5. What must happen before anything is fetched

1. Populate `corpus/sources-v2.tsv` — one row per work, with `license`, `license_evidence`
   (a licence or acquisition-record URL, or a path to the file on disk), `stratum`,
   `redistributable` and, for `local-copy`, an acquisition date in `notes`.
2. `python corpus/check-sources.py` must exit **0**. It refuses an empty registry: zero rows is
   NOT RUN, never a pass.
3. Add a **source-specific loader**. No generic scraper: each source has its own terms, its own
   metadata, and its own chapter structure. For `local-copy`, the loader reads a file already on
   disk and never fetches.
4. Extract into a stratum-specific directory (`corpus/dist-features-mod/` for C-mod) so no
   baseline silently absorbs another.
5. Run `python corpus/check-nonconsumptive.py` before any commit that touches analysis output.
6. Keep the text out of git (`books/C-*` is already ignored).
7. A `local-copy` text is deleted when the study is done with it; the registry row and the
   derived counts survive, the prose does not.

## 6. What this does not do

- It does not re-open or re-mix the 109-book PG baseline.
- It does not authorise scraping any platform.
- It does not make a 12-book modern sample equivalent to a 109-book baseline; it makes the
  comparison possible and the confounding visible.
