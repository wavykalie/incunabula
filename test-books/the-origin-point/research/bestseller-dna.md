# Bestseller DNA — The Origin Point

**What the Writer reads in Phase 3.** Phase 1 (/scout) deliverable.

## Read this first: what this file is not

**It contains no quoted prose and no stylistic rules lifted from any published
book.** Those are two reasons:

1. **Copyright.** Prose rules are the one thing that genuinely cannot be sourced
   by quotation. I can describe what a book *does*; I cannot reproduce how it
   sounds.
2. **Credibility.** Phase 1 found that two of six comps in this project's memory
   were **fabricated** — one invented outright, one invented twice over. A file of
   confident-sounding stylistic assertions, generated the same way from the same
   memory, would be the exact failure that was just caught. It would look like
   research and be no more trustworthy than the Yarbrough title.

So this file contains only claims I can attribute to something. Each rule is
labelled with its evidence class. Rules from class C are *design commitments for
this book*, not findings about the market — and they are marked so the Writer does
not mistake them for what other books do.

The honest summary: **scout found no published book that does this book.** There is
no bestseller to extract DNA from. What follows is a mechanism brief, honestly
labelled.

---

## Evidence classes used throughout

| class | meaning | weight |
|---|---|---|
| **A** | Attributable to a specific named source I read this session | use as constraint |
| **B** | Reader sentiment from a specific review I saw | use as risk, not rule |
| **C** | My design commitment for this book. Not a finding. | own it as a choice |
| **D** | Explicitly a guess | treat as null until tested |

---

## A. The one hard structural finding (class A)

**There is no procedural to join.** From every verified comp, the structure is:
*an investigator joins or runs a live investigation.* Detective Hayes recruits
Lorence/Paper Cage's records clerk to an active missing-persons case
(*Paper Cage*). Jack is a vicar in a village (*The Burning Girls*). Carmichael is
in a trial (*Apple Tree Yard*). Ruth Galloway is an archaeologist on a case.

**No comp has a protagonist reconstructing an institutional wrong from documents
alone, with no body, no investigator, and no ongoing case.** This is the structural
hole the book fills, and it is the *only* finding in this file with hard evidence
behind it.

**Class C consequence — the suspense has to be manufactured, not inherited.** A
documentary mystery gets no forward momentum for free. Every commercial mystery
above is momentum *donated* by an investigation already in progress. This book
must generate its own, deliberately, in the opening pages. There is no genre
convention doing the work.

---

## B. What the reader sentiment actually says (class B)

The two momentum-less comps in the corrected set both disappointed their readers:

- ***The Burning Girls*** (C.J. Tudor, 2021): *"great premise, starts off pretty
  decently… at the 80%…"* — the reader is sold the premise and then feels the
  book does not deliver it.
- ***Apple Tree Yard*** (Doughty, 2013): **3.5/5** on one review; accused of being
  a "ripping beach-read." Not even a "quiet literary book that stayed quiet" — a
  book read as *tooapy*.

**Class A corroboration:** *Murder & Mayhem* (30 Dec 2025) records a writer
stating plainly that readers want *"some sense of justice at the end… we don't get
enough of that kind of satisfactory closure in the real world."*

### Design rules that follow (class C, derived from the above)

1. **The clock must be visible from chapter 1.** The wrecking date is the only
   source of forward pressure a documentary mystery has. Readers of a quiet book
   have no other reason to turn the page. *This is the single most important
   consequence of the Tudor finding.*
2. **The reveal must land before the back third.** Tudor failed at the 80% mark.
   If the solution is not reachable and satisfying by ~ch 20 of 30, the reader
   concludes the book was never going to get there. Class B failure mode, made a
   structural requirement.
3. **Give the reader closure on the protagonist.** The trade evidence asks for
   satisfaction; `A8` (ambiguity about Wren's guilt) runs directly against it.
   Ambiguity about a *crime* is fair play. Ambiguity about whether the
   protagonist committed it reads as a cheat, and the sources indicate readers
   punish that specifically. **This is now a conflict between two live findings
   and it must be resolved in the outline, not at the beta read.**
4. **No twee.** Doughty's sin was softness. The register is "quiet," not "gentle."
   Class D note: I cannot specify the replacement register yet. Flagged.

---

## C. Form and format (class A/B)

- **Length 80,000–95,000**, declared at Phase 0 and enforced by `check-length.py`.
  Genre median for this kind of book: *not established by this research.* The
  honest position is that the range came from the length contract, not from
  measured genre data. Class D — a real gap in Phase 1.
- **Chapter count 30**, targets 1,300–5,100, mean 2,820, CV 35.7%. The CV is in
  the published-fiction band (33.4–45.1%) and was verified before any prose. Class
  A for the arithmetic; class C for the suitability.
- **Structure variety**: 8 structures, no two adjacent identical. This guards
  against the uniformity the tic-scan (`check-uniformity.py`) exists to catch.
- **POV**: close third on Wren. Class C. Note the comps split — *The Burning
  Girls* is single-POV, *Paper Cage* is multi-POV. Single-POV is the safer choice
  for a book whose whole argument is about *one person's* compromised seeing.
- **The clue ledger is 10 items and fair-play** (in `outline.md`). Class D: an
  intention, not a proof. `A9` is untested. **Chapter 1 should not be drafted
  until an independent solve confirms the ledger is actually solvable.**

---

## D. The positioning problem, stated for the Writer (class A)

**The 2025 best-of lists contain no quiet documentary procedural.** The trade
describes a **bifurcation**: readers who want escape (cozy, puzzle, community) and
readers who want the dark/deceptive end. Not a market with a quiet middle.

The books in those lists that *are* small-town and rural are **quiet in setting,
propulsive in structure.** Body, chase, deception, detective. Nothing gets its
suspense from a filing date.

**The ensemble signal is clear (class A):** *The Thursday Murder Club* and *Picking
Up the Pieces* are both named in trade reporting as current models. In both, an
amateur sleuth is helped by a **network of people** rather than a single
professional. `Picking Up the Pieces* is specifically puzzle-enthusiasts clearing a
family's name.

**That is a nearer structural neighbour to this book than anything in the
literary comp set** — a group of people working a paper puzzle to correct a
wrongful record. It is a cozier register than this book wants, but the *shape*
matches and the shape is what the trade says is working.

**Design consequence (class C):** the outline should carry more ensemble and fewer
solo scenes. The record-keeper is the *access*, not the *cast*.

---

## E. What is explicitly unknown

Recording these so that the next phase does not treat silence as permission.

- **No sales data.** Amazon review counts were used as a rough proxy
  (*The Dark Angel*: 11,265 reviews at 4.5). Nothing was scraped, and review
  counts are not sales. No book in the set has a verified sales figure.
- **No genre length median** for the documentary/quiet subgenre. See §C.
- **No practitioner opinion.** The `PubQ` thread on the state of the classic
  mystery is unreadable — Reddit serves no text to the fetcher and
  `old.reddit.com` redirects to a login wall. **This is the best available direct
  source on the quiet pole and it has not been read.** Worth another route.
- **No comp is a debut with the same mechanism.** `Paper Cage` is the closest
  single book and it differs at the engine. *The Dark Angel* is book 10 of 15.
- **No evidence the mechanism is solvable by a reader** — `A9` open.

---

## F. The rules, condensed

1. Clock visible from ch 1. It is the engine; nothing else is pushing.
2. Solution landable by ~ch 20. The 80% mark is where *The Burning Girls* failed.
3. Closure on the protagonist, or the ending reads as a cheat. Conflicts with
   `A8` — resolve in the outline.
4. Register: quiet, not gentle. Doughty was punished for softness.
5. More ensemble, fewer solos. The trade says the network is the current shape.
6. Clue ledger must survive an independent solve before ch 1 is drafted.
7. Single close-third POV. The argument is about one compromised witness.
8. Do not market this as a documentary procedural. Sell the deception; the
   records are how it is solved.
