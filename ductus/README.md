# ductus/ — the author voices

One directory per voice. The name is Latin: *ductus* is the individual character of a
hand's writing — the style that belongs to one writer and nobody else. It is the exact
concept this layer holds, and it collides with nothing already in the tree (`press`,
by contrast, is already taken twice: the `press-ledger` and `presswork` skills use it
in the printing sense, and `readership`, `reader-swarm` and `proof-panel` use
"persona" for the *reader* side).

```
ductus/
  README.md          this file
  PROMOTIONS.md      the only channel between voices
  <slug>/
    ductus.md        the voice contract an agent pilots
    COMMONPLACE.md   that voice's own taste, which develops as it is used
```

## Create one

    python tools/ductus.py new my-voice --name "My Voice" --register "short declaratives"
    python tools/ductus.py new my-voice --random   # a seeded persona from the palette
    python tools/ductus.py check      # every voice, its isolation, the unassigned books
    python tools/ductus.py cross      # any entry, or contract, two voices both hold
    python tools/ductus.py list       # how far each voice has developed
    python tools/ductus.py log test-books/my-book --chapter 1 \
        --tone "cold, procedural" --register "first person, present" \
        --survives "the measurement and the refusal"
    python tools/ductus.py audit test-books/my-book

Then **author it**. `new` writes the shape and nothing else; the identity is the
creator's. An agent can write the contract and the ledger entries as it works, and it
is free to invent a name and a life for the voice — a record's job is to say which
persona it is reading, not to check the biography. `new --random` is the exception:
it writes a complete seeded persona from the palette and marks it as generated, so a
fresh book can start under a real voice without pretending the voice is a person.

## What develops

`ductus/<slug>/COMMONPLACE.md` is that voice's taste ledger, with the root ledger's
ceremony and its limits. `list` counts what has accumulated — decisions, preferences,
outcomes — and names when the ledger is still empty rather than showing a zero as
progress. A preference without a `limit:` line is a rule, and a voice that accretes
rules turns into a caricature of its first book; the expiry and the limit exist so a
voice a hundred books in is still a voice.

## Assigning a book

`ductus: <slug>` in `BOOKS.yaml`. That is the author's call, and `check` NAMES the
books that carry none instead of picking for them. A book with no ductus is drafted
under the root `COMMONPLACE.md` alone — which is where every book in the catalogue was
drafted.

## Carryover between sessions

A resolved contract is not enough if the next session cannot recover how the voice was
applied. `ductus.py log` writes one section per chapter to
`<book>/maintenance/DUCTUS_LOG.md`, naming the contract digest, the tone, the register,
and what must survive the chapter. `ductus.py audit` fails if a chapter has no entry,
if an entry has no tone/register/survival statement, or if the contract changed after
the entry was written. A survival line that quotes an object — `the brass lever` — is a
claim, and audit fails when the chapter no longer contains it; the unquoted part is prose
written for the next session's eye, so it is reported with the words that are missing and
not enforced. `tools/check-ductus.py` is the thin wrapper the gate suite calls.

`ductus.py calibrate <book>` measures the book against the numeric lines the contract
declares — negation, subject openings, texture — and exits 1 where the book leaves one.
It reads a fenced `ductus-invariants` block when a contract has one and the prose form
otherwise, and prints which it read. It is deliberately not in the gate suite: a declared
line is enforced where the author runs it.

At intake, `init-book.py --author "Name" --ductus SLUG` records the assignment and the
resolved digests in `PROJECT_STATE.yaml`. `--ductus random` seeds a complete persona from
the palette and assigns it to the new book; the persona is explicitly a generated voice,
not a claim about a real person.
