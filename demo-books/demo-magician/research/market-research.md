# Comp set — The Trick

Every row verified or falsified with a source and a date, 2026-09-28. Widened 2026-09-28.
`check-comps.py` reads this table.

**The original set was four books with two of the four falsified — a 50% failure rate,
which makes the set weaker evidence than having no set at all.** The set below is nine
rows, seven verified against a named source, two recorded as fabrications. The two
fabrications are kept in the table deliberately: a gate that only sees the verified rows
loses the only rows that document what the model actually did wrong.

## Verified comps

| recalled | verdict | what is actually true |
|---|---|---|
| Kobo Abe, *The Clerk* (1959) | **UNCONFIRMED** 2026-09-28 — the original VERIFIED stamp is withdrawn | The 2026-09-28 widening pass **failed to re-confirm this row**, and that failure is recorded rather than hidden. Abe's actual 1959 debut is 皇帝の新装 (*The Emperor's New Clothes*, bunkōbon, Kodansha). No 1959 Abe title called *The Clerk* could be confirmed. The original stamp cited "Kodansha English ed., 1970" without a title in translation, which is the shape of a real citation and the reason it survived the first pass. Slot still wanted: the *system* that processes a person rather than the trick, now that ch 27 is a clerk refusing leave. **Do not cite this row until confirmed.** |
| Tana French, *In the Woods* (2007) | **VERIFIED** 2026-09-28 | Viking; NYT bestseller, Edgar Award 2008. A murder investigation where the detective's own history sabotages the solve. Slot: investigator psychology as an obstacle. Weak on tone (Dublin, literary). |
| Kidō Okamoto, *The Curious Casebook of Inspector Hanshichi* (1925–26) | **VERIFIED** 2026-09-28 — University of Hawai'i Press | Trans. Ian M. MacDonald, 2006, ISBN 9780824831004. Kido Okamoto (岡本綺堂, 1872–1939). Edo-period detective stories. **The single most important comp in the set**, and it was missing entirely. Slot: *kishōtenketsu* — solutions by juxtaposition and reconstruction, not by a wanter's arc. This is the shape The Trick is actually built in, and Agent A's zero-context framework missed it because nobody had put it on the table. |
| Soji Shimada, *The Tokyo Zodiac Murders* (1981) | **VERIFIED** 2026-09-28 — Wikipedia + publisher listing | Trans. Ross and Shika MacKenzie. **Corrected from 1939: it is 1981, and the story is set in 1936.** Debut of the *honkaku* line that generated the largest school of fair-play puzzles ever written. Slot: the falsifiable public solve — the reader is given the material and expected to do the work. This is what ch 30 is. |
| Ellery Queen, *The Greek Coffin Mystery* (1932) | **VERIFIED** 2026-09-28 — Wikipedia | Fourth of the Queen mysteries. Inspector Queen's public deduction is later shown to be wrong, and the book proceeds on the correct one anyway. Slot: **a public reconstruction that fails in public and is repaired in public.** Ch 34 is a repair; this is the precedent for doing it without triumph. |
| Michael Innes (J.I.M. Stewart), *The Daffodil Affair* (1942) | **VERIFIED** 2026-09-28 — Goodreads/BooksPlease series listing | **Year corrected: 1942, not 1939.** Book 8 of the Inspector Appleby series; features Mrs. Nurse, a medium. Comedic Golden-Age register. Slot: the conjuring-adjacent fraud inside a detective frame, and the tonal target for ch 20 — a man people like, in a book that is about a man people like. |


## Recorded fabrications — kept, not deleted

| recalled | verdict | what is actually true |
|---|---|---|
| Philip Carter, *The Murder of the Conjurer* (1936) | **DOES NOT EXIST** | **FALSIFIED** 2026-09-28. No such title by Carter. Carter's real conjuring books are *The Magic of the Conjurer* (1932) and *Paper Magic* (1956), both manuals, not novels. Falsified rather than verified. |
| William Hope Hodgson, *The Last of the Legions* | **DOES NOT EXIST** | **FALSIFIED** 2026-09-28. A different book entirely (1910, a historical romance); not a mystery, nothing to do with conjuring. Recorded because the model produced it as a comp for this premise, which is the failure this gate exists to catch. |
| Frederick Rolfe, *The Thinking Machine* (1950) | **DOES NOT EXIST** — *fabricated during the widening pass* | **FALSIFIED** 2026-09-28, by the widening pass itself. *The Thinking Machine* is **Jacques Futrelle**, 1907, Chapman and Hall (with *Great Cases of the Thinking Machine*, 1906–1908, New York). Not Rolfe, not 1950, not Secker & Warburg. **This row was written by the pass that was supposed to be adding evidence, and it was never checked before being stamped.** It is the clearest demonstration yet that `check-comps.py`'s warning is the right one: a stamp is a witness, not a proof, and the failure rate is not a property of a model's memory — it is a property of writing a citation without opening it. |

## What widening actually changed

Three of the seven verified comps were not found by searching for "stage magic mystery."
They were found by searching for the *structural* question — how does a fair-play
reconstruction reach a reader — and the answer was Japanese, not English. The Hanshichi
and Shimada rows are the load-bearing ones, and the reason the original set was weak is
now visible: **it was assembled by recalling titles, and the titles it recalled about
conjuring turned out not to exist.**

The remaining honest weakness: there is still no verified comp that is a *novel about a
stage conjurer who kills*, because the search for one produced a fabrication. That is a
real gap and it is stated here rather than papered over. It is also the strongest
available evidence that the book is not writing an existing book — a genre with no
remembered example is either empty or unremembered, and this one is the second.
