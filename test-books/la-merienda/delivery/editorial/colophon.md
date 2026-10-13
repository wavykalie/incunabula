# Colophon — *La merienda*

Editorial package, phase 14. Assembled by an autonomous run
(roll seed 594517907, dice 1) on 2026-10-05, from a brief nobody chose.

**Read this first.** The comp table in `research/market-research.md` is a first
pass by a run with no trade-market access. It is **provisional**. The premise
distinctness claim is a collision result, not a compliment. And the manuscript is
16,340 words against a declared floor of 25,000 — see *Delivery note* below.

---

## Logline

A weather observer is sent to close a mountain weather station for the winter
and finds, in its mailbox, a letter that has been waiting since 1983. The old
woman who kept the station before her walks up the pass every Thursday because
somebody told her there would be somebody there.

## Back-cover copy

The station at the Puerto de la Nieve was automated in 1983. Nobody was told;
the woman who had kept it for thirty-one years simply understood that she was
leaving. She walked out with what she was wearing.

Every Thursday for five winters she has climbed two hours to the old
observatory, because a postman told her in 2019 that there would be someone
there this winter.

There is someone. Nuria has a contract to a place that closes at the end of
March and a set of keys and no idea what anyone wants from her. On her first
afternoon she picks the lock on the mailbox, because nobody told her not to.

Inside there are nine letters. Two of them were returned to sender before it
was posted. One of them is addressed to a man who died in 1979.

*A novel about attention, and about what it costs to be late.*

## Synopsis

Nuria Bel, 38, has spent twelve years producing weather forecasts that arrive
before the weather does and cannot be argued with. She takes the last manual
posting in her qualification — a mountain weather station above a reservoir in
the Spanish Pyrenees — because it is the only work she is trained for that
nobody wants.

In the station's mailbox, under nine envelopes and forty years of pine needles,
is a letter postmarked 14 October 1983, addressed to Elvira Sarnago and never
collected. It is in German, from Elvira's brother, who emigrated and asked twice
whether she had received his letter of 1981.

Two of the nine envelopes are stamped *destinatario desconocido*, dated 1981 and
1982. She had already gone when he wrote.

The ninth is addressed not to Elvira but to her husband Tomás, who died in
1979. Nuria does not open it. By the end of November she does not have to: the
handwriting is Elvira's, and the postmarks run from 1983 to 1997, one a year —
fourteen letters, returned to sender and posted back by a woman who had not
once opened the mailbox in thirty-seven years, including the fourteen years in
which she was the one filling it.

And every Thursday at four o'clock, Elvira arrives.

The novel asks whether attention, offered decades late, can discharge a debt
that was never acknowledged. It does not answer. The station is not saved,
nobody forgives anybody, and the tea is made anyway.

## Query letter

> Dear [agent],
>
> *La merienda* is a 16,000-word Spanish-language novelette about a
> weather observer, an undelivered letter, and an eighty-one-year-old woman who
> has walked up a mountain every Thursday for five years on the strength of a
> remark made by a postman she has not seen since.
>
> The novel is narrated in the second person and it is warm in its register and
> cold in its diction, because the narrator is a professional who has learned to
> write the weather down without adding anything to it. The engine is a weekly
> tea ceremony: the merienda is the clock the whole book runs on, and it is also
> the instrument by which two women who are bad at friendship learn to put the
> kettle on.
>
> The comp set is Muñoz Molina's *El invierno en Lisboa* for the second-person
> grief, Díez's *Las estaciones provinciales* for the tone, Backman for the
> commercial promise, and Cercas for the structure of a quest that fails and is
> worth having made. No comp shares the engine: no other book in the set has a
> protagonist whose profession is measurement, and none has an undelivered
> letter as a debt that cannot be discharged.
>
> Nobody dies in this book. The eighty-one-year-old lives to the last page, and
> the station closes on the last day whether or not anyone has been able to save
> it. I think that restraint is the whole argument, and I would rather make it
> once, cleanly, than explain it.
>
> I am [author]. This is a first novel in Spanish. [Length of submission]

## Cover brief

- **Subject:** a small weather station on a bare mountain pass in winter, seen
  from a distance; a lit window; snow. No people on the cover.
- **Not:** a woman, a letter in close-up, a kettle. The book's two most obvious
  images are its two least interesting ones and will read as a genre signal the
  book is not paying.
- **Type:** the station's own nameplate, if it can be made to look like an
  enamel sign. `OBSERVATORIO 12-340 · PUERTO DE LA NIEVE · ALT. 1.640 M`.
- **Palette:** white, slate, one sodium-yellow from the window.
- **Reference:** the actual Puerto de la Nieve photographs — the pass exists and
  is documented. A stock "mountain observatory" image will not survive contact
  with a reader who has looked.

---

## Delivery note — the manuscript is short, deliberately

The roll declared **novella, 25,000–45,000 words**. The delivered manuscript is
**16,340 words**, which is a novelette.

The run's own recommendation at checkpoint two was to expand — roughly 8,700
words, in line with the pension-winter precedent, which added rather than
re-declared. **The author chose the other honest option: deliver short and let
the length gate fail.** The contract in `PROJECT_STATE.yaml` still reads
25,000–45,000, unchanged, so `check-length.py` reports the failure against the
number that was actually promised.

Recorded as **ruling R-002**. The alternative — moving `target_floor_words` to
16,000 — would have turned the same deliverable green in one line, and was
rejected because a length contract is a promise to the reader.

**A query built on this package should quote 16,000 words, not the rolled
contract.**

## Known gaps in this package

1. **No sales data of any kind.** No BookScan, no panel, no retailer contact.
   The "commercial" comp is an argument from a single book, not a market.
2. **The novella-in-Spanish risk is named, not quantified.** This book sits
   exactly where Spanish publishing is weakest commercially and strongest
   artistically. The dice chose that, not a market study.
3. **The comp table is provisional** and should be widened by a human with
   trade access. The standing comp risk in this harness is the inverse error —
   a real, on-point comp nobody named.
4. **Two debts are deliberately unresolved** (D-007 the reading asymmetry,
   D-008 the Zaragoza postmarks). Both are recorded in `NARRATIVE_LEDGER.yaml`
   with reasons. D-008 in particular is a real question the narrative opens and
   then refuses to enter, and a reviewer may reasonably call that a cheat.
5. **No EPUB or DOCX render.** No pandoc in this environment and no per-book
   renderer, as with Pension Winter.