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
    python tools/ductus.py check      # every voice, its isolation, the unassigned books
    python tools/ductus.py cross      # any entry two voices both hold
    python tools/ductus.py list       # how far each voice has developed

Then **author it**. `new` writes the shape and nothing else; the identity is the
creator's. An agent can write the contract and the ledger entries as it works, and it
is free to invent a name and a life for the voice — a record's job is to say which
persona it is reading, not to check the biography.

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
