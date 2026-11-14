# COMMONPLACE — Kalie Kirch

This voice's own taste ledger, and only this voice's. Nothing outside this directory is
evidence for a Kalie Kirch decision, and nothing here is enforced against a book.

The entry types and the ceremony are the root `COMMONPLACE.md`'s — `decision`,
`preference`, `outcome`, `promotion` — with the same formats and the same limits:

- **`decision`** — one real editorial choice, made between named alternatives.
- **`preference`** — distilled taste, written only after three agreeing decisions, and
  written `emergent`: guidance the next book may decline with a reason. A `limit:` line
  is required, because a preference without one is a rule.
- **`outcome`** — what readers did, with the prediction recorded before publication.
- **`promotion`** — a change the verifier stack adopted, with its falsifier.

**A preference that turns out to hold for another voice is not copied across.** It is
merged deliberately, dated, in `ductus/PROMOTIONS.md`, naming the evidence that
justified it in the second voice. A preference that appears in two ledgers by accident
has stopped being either one's, and `python tools/ductus.py cross` reports it.

## Entries

### 2026-11-11 — decision — the second job in chapter 7 is cut, not reconciled

- **chosen:** cut the wire-tie trade from chapter 7.
- **alternatives:** reconcile it against chapter 11's account of her work; keep it and
  amend the canon instead.
- **reason:** chapter 11 is the older account and the one the book's plot turns on, and a
  second job the timeline cannot hold is not a thing prose can repair by being better.
  Cutting cost four hundred words and the forty-seven-versus-Fifty count beat, which I
  regret and did not restore.
- **limit:** cutting is not the default. A contradiction inside a scene the book needs is
  a repair; deletion is for a scene the book does not owe.

### 2026-11-11 — decision — the tap signal is three, everywhere

- **chosen:** three taps, in every appearance, including the last one.
- **alternatives:** two, which reads as a knock; five, which reads as a code.
- **reason:** three is the shortest count that is unmistakably deliberate and the longest
  that a frightened person would still risk. It also lets the counting motif and the
  daughter's arithmetic sit in the same gesture without either one explaining the other.
- **limit:** a signal is not a symbol. If a reader can tell me what the three taps mean,
  I have written it wrong.

### 2026-11-11 — decision — the last line of the column stays blank

- **chosen:** he does not write her name; the line stays white and the book ends outside.
- **alternatives:** write it and end on the page; refuse by burning the sheet; confront
  the man who ordered the murder and settle it physically.
- **reason:** burning is a gesture the room would notice, and a confrontation makes the
  book's argument about one man rather than about the instrument. Leaving the line open
  is the only refusal that costs him the thing he is good at and cannot be witnessed.
- **limit:** withholding must be paid for. If the reader cannot feel what he gave up, the
  blank line is coyness, not restraint.

### 2026-11-12 — decision — pressure moves the prose; it no longer slows it

- **chosen:** strike the breaking rule that the voice "does not get louder; it gets more
  exact", and replace it with pressure *shortening and speeding up* the sentences.
- **alternatives:** keep the rule and fix the book's length; add an action mode beside the
  still one, selected per scene.
- **reason:** the rule was written against melodrama and became a licence to narrate the
  worst minute of a man's life at furniture speed. The measurement is in the draft: 15.4
  mean words and 29% short sentences in chapter 1, 23.6 and 11% by chapter 12, and 8 of
  13 chapters with no fight in them. A second mode would have made the flatness a
  legitimate choice rather than a fault.
- **limit:** speed is not volume. A short sentence is not a loud one, and nothing here
  licenses exclamation, italics or a narrator who tells me how frightened to be. The
  count and the body still carry it.

### 2026-11-12 — decision — a book may carry its own contract under this voice

- **chosen:** *The Parts Still Warm* gets `ductus.md` at the book root, under this persona
  as parent, and `tools/ductus.py` now reads the book's file when it exists.
- **alternatives:** keep the one contract and edit it per book; fork a separate persona for
  the thriller work.
- **reason:** a persona is the hand; a book is the hand on this material. One file for both
  makes every later book inherit whatever the last one needed, and forking personas would
  make two of me, which is the thing `cross` exists to report.
- **limit:** the book contract may tighten these numbers and may never loosen them. If a
  book needs a looser row, that is a change here, dated, with the reason.

### 2026-11-12 — decision — the book's speed targets are its own best chapters

- **chosen:** the wall for the rewrite is chapter 1 (15.4 words, 29% short, 29-word
  paragraphs) and chapter 4 (17.3, 31%, 24.1), held for all thirteen chapters.
- **alternatives:** wait for a measured action-voice lane; set the targets from the
  published horror band; leave the pace unnumbered.
- **reason:** there is no action corpus on disk — the lane is registered at zero books — and
  an unnumbered target is an adjective. The draft already proves the register is reachable
  in this voice, in its own opening chapter, so the target is held constant rather than
  invented. It is the weaker evidence and the contract says so.
- **limit:** self-derived targets cannot tell me the book is fast for the market, only that
  it is as fast as its own best pages. When the lane exists, the fit is re-run and this
  decision is superseded, not quietly amended.

### 2026-11-12 — decision — the hierarchy has three layers, because the series has ten volumes

- **chosen:** author → series → book. *The Parts Still Warm* gets
  `ductus/kalie-kirch/series/the-parts-still-warm.md`, `BOOKS.yaml` names the series on the
  book, and `tools/ductus.py contract` resolves book → series → persona and prints which
  layer answered.
- **alternatives:** leave two layers and let each volume's contract be written under the
  persona alone; write one series contract and drop the per-book layer.
- **reason:** the author states the series is ten books (2026-11-12). With two layers, the
  pace band this book spent 129,992 words learning is book one's private property, and book
  two would start from a persona that is a horror hand and never selected pace — the exact
  failure already recorded for book one. `ductus-designer`'s open question 4 had declared
  that each volume is written "under a series parent" since the skill was written; there was
  no file behind that sentence and nothing could read one. Dropping the book layer instead
  was refused: a series voice in one file cannot let a volume be specific to its material,
  which is the single finding that produced this book's own contract.
- **limit:** a series contract may tighten the persona and never loosen it, and a volume
  may tighten the series and never loosen it. It may not absorb a volume's local decision:
  if a rule only holds for one book, it belongs in that book's contract, and the test is
  whether volume two could be drafted under it. No number is declared at the series layer
  yet — the pace band lives in volume one and is inherited, not restated, so there is still
  exactly one copy of every number.

### 2026-11-12 — decision — the sentence has a fold, not a setting

- **chosen:** the voice moves between **the count** (nine to twelve words, half the
  sentences at eight or under) and **the open** (fifteen to seventeen, a third short, one
  sentence a movement allowed past thirty words), and a chapter is judged by the distance
  it covers, not by where it sits. A volume must spread its chapters across the fold.
- **alternatives:** keep one tempo at 16 words and 30% short and vary only the incident;
  raise the average and let the whole book run long; add a separate action mode selected
  per scene.
- **reason:** one tempo is what the author heard as flat. The book met the previous
  revision's pace and still read suffocating, because a book at one setting is a book with
  one temperature, however fast the setting. A second mode was refused in the previous
  decision for the right reason — it would make flatness legitimate — and the fold is not a
  second mode: it is the range the one mode has to travel.
- **limit:** the fold's ends are the lane's measured work range (mean 8.7–17.0, short
  28.2–59.1%, paragraph 25.3–40.9), not a licence to write long. Expansion past the open
  end is the old wallpaper with a new name.

### 2026-11-12 — decision — the diction is modern American, and the antique cadence goes

- **chosen:** ban archaism and British idiom outright — *whilst, amongst, upon, shall, ere,
  betwixt, mayhap, nay, aye, 'twas, learnt, towards, grey, colour, storey, centre, defence,
  realise, organise, kerb, queue, gaol, fortnight* — and ban the object-first clause, the
  semicolon chain and the line built to be quoted.
- **alternatives:** keep the diction and fix only the pace; limit the ban to the narrator
  and let the old men keep their aphorisms.
- **reason:** the author's second report was *too British, too flat, old-timey*. The cause
  is not the coinages — *vell*, *sare*, *hoy*, *smork* are the world's nouns and stay — but
  the grammar around them: inverted clauses, semicolon chains, and working men speaking in
  sentences shaped for a sampler. A city can be old without its sentences being antique.
- **limit:** the ban is on cadence, not on what the world owns. A coined noun learned from
  the sentence it stands in is still legal; a coinage explained is still a gloss. And the
  ban does not reach a character who is *meant* to sound like a book — there is one, late,
  and he lands wrong.

### 2026-11-12 — decision — action opens before it pays

- **chosen:** a fight, a pursuit or a door going in starts at the open end — longer
  sentence, the street and the height let in, the body light — and collapses to the count
  at the first cost, not before.
- **alternatives:** keep the previous breaking rule (pressure shortens from the first
  line); open only in the aftermath, when the cost is already known.
- **reason:** the author's phrase was *action needs to be freeing, expand the fold to the
  limits*. The previous rule made every violent scene a receipt written in advance: the
  reader was charged from the first sentence and never given the room the charge was for.
  Release first, then the bill, is the only order in which the loss is felt.
- **limit:** opening is not decorating. The long sentence in an action movement must be a
  body travelling or a distance closing, and the count must arrive inside the same
  movement. A chapter that opens and never pays is a travel brochure.

### 2026-11-12 — decision — pounds, not kilos; coats, not cloth catalogues

- **chosen:** the world counts in pounds, feet, inches, yards and paces; the trade names of
  cloth (moleskin, tweed, flannel, worsted, horsehair, ticking, serge, fustian) stop being
  the narrator's default nouns; no new coinage for an object that already has a name; the
  numbered handles are not extended and are queued for a rename pass.
- **alternatives:** keep metric and the fabric vocabulary and fix only the pace; keep the
  handles and treat the objection as taste.
- **reason:** the author named the words — *kilos*, *Knocker*, *Moulton*, the names of the
  different types of wool. Counted in the draft: 98 uses of *kilos*, 184 of *centimeters*,
  158 of *meters*, and 87 uses of the cloth names. That is not texture; it is a costume
  inventory, and it is the mechanism by which the district reads as a stage version of a
  British industrial city rather than as a place.
- **limit:** the correction runs one way and is not a licence to be vague. A weight is still
  a number, and the number is still the book's suspense; "heavy" is not an improvement on
  "forty pounds". *Knocker* and *Moulton* are not in the manuscript — the objection is to the
  register that produces them — and the rename pass touches 779 uses of *Tap Two* alone, so
  it waits for the author's word rather than being done to the book overnight.

Three decisions is the floor for closing a run. Before 2026-11-11 this ledger said *no
entries*, after a whole book — which is how a voice finishes a manuscript and learns
nothing from it. An empty ledger is honest only before the first chapter.
