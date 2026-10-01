# OPENING STRATEGY

`artifacts/07-opening-strategy.md`. Phase 2 output.

**The rule: the first line has to earn the second line. Nothing else.**

---

## THE PROMISE THE FIRST PAGE MAKES

Three things, in this order, and all three must be true by the end of page one:

1. **A woman is extremely good at something and it has already cost her.**
2. **She is doing the same work without the part that mattered, and the reader can tell
   the difference without knowing what the part was.**
3. **This is a book about two people, and the second one walks in during the last ten
   lines.**

An opening that promises a different book is the most expensive mistake in the
architecture phase, because everything downstream inherits it. This book promises a
two-hander, a professional register, and a competence that is already broken. The Vell does
not appear in chapter one. Nothing is explained. **The reader is given a woman who cannot
stop being excellent at a job she has left, and that is the entire romance in
compressed form**, because the reader will not learn for thirty chapters that the job was
a relationship.

---

## FIRST-LINE OPTIONS

Four tried. The chosen one is third. Recorded with reasons, because a discarded first line
that was better would be a finding and there are no findings in this file.

**1. "The rack was four hundred and ten pounds and he was going to wear it wrong."**
Sharp, funny, front-loads the competence. **Rejected:** it is a *mystery* opening, and it
promises that the competence is a puzzle. The competence is not a puzzle. It is a wound,
and a reader who starts the book expecting a puzzle reads the first twenty chapters
waiting for a reveal that is not coming and blames the book.

**2. "Ines Varga sold a full rack to a man who had never been underground."**
Clean, complete, and it names her on line one. **Rejected:** it names her, and the book's
best asset in chapter one is that we do not know her name until she is annoyed. Also it
spends the sentence describing the plot of the chapter.

**3. "She had watched him put the harness on wrong for four minutes and said nothing for
three of them, and she was not being kind."**
**CHOSEN.** It earns the second line because the second line exists to explain *why* three
minutes of silence was not kindness, and the reader cannot get past line one without line
two. It establishes voice (dry, exact, unsentimental about her own motives), it establishes
the wound without naming it (she is helping a man who does not need help because she cannot
stop), and it is a complete moral situation in one sentence. It also *withholds her name*,
which is the cheapest available gift to a reader.

**4. "The Vell took a partner and a career in the same afternoon, and four years later
Ines Varga was selling the equipment that did it."**
This is a synopsis, not an opening. **Rejected on the same grounds the pilot's outline
paragraph was corrected** (`muzzle-and-marrow/outline.md`, 2026-09-29): it tells the reader
the book's shape before the book can show it, and the reader spends the next forty
chapters confirming a thing they were told on page one. **It is also the version of this
premise that the premise gate would have rejected** — it states a *plot* where the
premise's engine is a *relationship*, and stating the plot is how a two-hander turns into
a mystery novel.

---

## AMENDMENT — the chosen first line did not survive the gate

**2026-09-29, Chapter 1, second pass.** Option 3 as written above opened:

> *She had watched him put the harness on wrong for four minutes and said nothing for three
> of them, and she was not being kind.*

`deslop-check.sh` returned **FAIL, A1b, 0.71/1k against a cap of 1 per 2,000 words** — and
in a 1,400-word chapter that cap permits **zero** instances. The rule's regex matches the
literal strings `harness` and `leverage` and nothing else.

This is worth recording rather than quietly fixing, because it is a **collision between a
slop rule and a book that is actually about the thing the rule is about.** `A1b` was
calibrated on published prose and its worst observed rate is 0.31/1k; the word is common in
19th-century fiction as a verb and modern genre fiction as equipment, and in neither does
it cluster. In a novel set in caves it is not decoration, it is the load-bearing noun of
the trade.

**The fix was to change the word, not the sentence, and not the gate.** Cavers on this side
of the channel say *waist belt* and *loops*, which is the regional usage and is the more
precise term for the object anyway. The chapter now opens:

> *She had watched him lace up wrong for four minutes and said nothing for three of them,
> and she was not being kind.*

**This is the only edit made to the first line and the reasoning is that the alternative
three were worse:** *put the kit on wrong* is vaguer, and *buckle up wrong* is idiomatic in
a way that loses the technical register the chapter is establishing. The line keeps the
three things it was chosen for — it earns line two, it withholds her name, and it puts the
moral position (silence that is not kindness) in the first eight words.

**The standing instruction for this book: A1b is a live constraint on the vocabulary of the
entire manuscript, not a chapter-one problem.** The Vell chapters are where it will bite.
Budget: **one use of *harness* or *leverage* per 2,000 words across the whole book**, and
the substitutes in use are *waist belt*, *belay*, *the rack*, *the sit*, *the loops*. If a
future revision wants the word back in a passage that genuinely needs it, the honest move is
to find the word it is displacing and cut that instead — not to raise the cap, and not to
edit the frozen gate.

---

## THE FIRST PAGE

Line one is the chosen line above. Then, in order, with nothing skipped:

- the sale, with its price, because this is a shop and prices are how shops talk
- the four minutes of watching, and the specific three errors, all of them the kind of
  error that a competent person cannot stop seeing
- **the one that matters, which is that he will go, and she will not stop him, and this
  has happened to her before in a room with worse lighting**
- Fabiola, one line, and the rhythm of nineteen years in a single clause
- the customer, the sale, and Ines saying the only useful thing she says all chapter
- **the gauge**, on the wall behind the counter, not explained, four words, glanced at by
  nobody. This is the eighth of its nine appearances in the book and the reader will not
  notice it for another thirty chapters. **It is planted here because the book has to be
  honest about its own construction and the only honest way to put a clock in a reader's
  head in chapter one is to make it furniture.**
- Ottoline, in the doorway, in weather, holding a proposal she has rehearsed badly

---

## WHERE CHAPTER ONE ENDS

**On the stranger in the doorway. Not on the sale, and not on an answer.**

Chapter one's last line must increase forward pressure rather than release it. The sale is
a completed transaction and would be a release. Instead the chapter ends on a woman
standing in a shop doorway holding a piece of paper, and the reader knows — from the
weather, the hold, the fact that she has rehearsed — that she is about to ask Ines Varga
for the one thing nobody has asked her for in four years.

**She does not ask in chapter one.** She asks in chapter three, in a stockroom, standing up,
with a kettle neither of them offers the other. The delay is the book's first structural
promise kept: this is a book in which people do not say the thing on the page they would
have said it on.

---

## WHAT THE OPENING DELIBERATELY DOES NOT DO

- **No cave.** The Vell is not named, described, or entered until chapter 9, and not by
  name until chapter 12. A book that opens in its own set piece has spent its best
  material in its first chapter.
- **No death.** Solveig Havelock is not mentioned in chapter one. She is mentioned in
  chapter 2, once, in passing, as a name in an invoice, and the reader has no idea that
  this is the death of the book.
- **No voice-over, no flashback, no letter.** The book has one timeline and it is
  chronological, and it earns that by not doing anything clever for thirty pages.
- **No sympathy.** The reader's first opinion of Ines is that she is unkind to a stranger
  in a shop. This is correct and it is what the book needs, because a reader who starts
  sympathetic to a competent woman has already decided and there is no book left.
