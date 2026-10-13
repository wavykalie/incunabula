#!/usr/bin/env python3
# demo-magician edit pass 4: the last EXPANSION_PASS batch — ch 21 and ch 31.
# Each insertion answers "what is this chapter about that it has not finished saying?".
#   ch 21 — the reconstruction owes clue row L24: the Handover, the moment attention
#           passes from a thing to a person and back, in which nothing can be done.
#           The word appears nowhere in the manuscript; the outline gives the row to
#           ch 21 ("the reader gets the method here, on the page, named in plain words").
#           The sixth effect stays unnamed: the Handover is the moment, not the effect.
#   ch 31 — the title thesis was demonstrated and never stated: a trick is done to a
#           retinue, a hall of witnesses is the opposite of one, so the only thing a
#           hall can be given is a hand trick, which is why it was empty.
# Line endings are taken from each file (ch 21 LF, ch 31 CRLF). CRLF/LF preserved.
# Validates every anchor exists exactly once BEFORE applying anything.
import io, textwrap, os

CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manuscript", "chapters")
WRAP = 95

def wrap(prose, nl):
    paras = [p.strip() for p in prose.strip().split("\n\n")]
    return (nl * 2).join(textwrap.fill(" ".join(p.split()), width=WRAP) for p in paras)

def load(name):
    with io.open(os.path.join(CH, name), encoding="utf-8", newline="") as fh:
        return fh.read()

def save(name, text):
    with io.open(os.path.join(CH, name), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

EDITS = []
def A(name, anchor, prose):
    EDITS.append((name, anchor, prose))

A("chapter-21.md",
  "And he had not needed to move anything, because you cannot catch a word by watching it.",
  """
There is a word in the trade for the hole in the middle of every trick and she had not
used it once in eight days. The Handover: the moment the attention goes off the thing and
onto a face and comes back to the thing. Every method in the school happens inside one,
and every notebook she had been shown drew it as a hole, because nothing can be done in
it, and nothing can, because a room that is looking at a face has put the whole world down
and has no hands out for anything. She had been taught it at nine years old as the one
safe place in any effect, and she had believed it ever since, and it was true, and he had
spent his working life in it. The room put the world down for him and picked up again what
had been made for it in the meantime, and every one of them would tell the truth about
what they saw until the day they died.
""")

A("chapter-31.md",
  "and he did it because there was no paper\r\nfor it.",
  """
And the vanish was the whole of what a hall could be given. A trick is done to a retinue.
Four or five people who have seen it before and know what it costs and have come to watch
it done well, which is the only gift a performer has to give anybody. A hall where a
hundred and forty people have sat for two days listening to a case about three dead men
cannot be made into that, and what he gave them instead was the one trick that works on a
room of witnesses, which is a hand trick, an impossibility small enough to be seen once
and held and needing nobody in the room to have seen it before. It is the trick you hand
to people who have come to catch you. And it was empty because it was made of skill and
nothing else, and skill is the part of the trade that all ninety-one of them could take
home and practise, and he had stood up and spent it in public like small change.
""")

# validate
texts = {}
problems = []
for name, anchor, _ in EDITS:
    texts.setdefault(name, load(name))
    if texts[name].count(anchor) != 1:
        problems.append((name, anchor[:50], texts[name].count(anchor)))
if problems:
    for p in problems:
        print("ANCHOR PROBLEM:", p)
    raise SystemExit(1)

for name, anchor, prose in EDITS:
    t = texts[name]
    nl = "\r\n" if "\r\n" in t else "\n"
    t = t.replace(anchor, anchor + nl * 2 + wrap(prose, nl), 1)
    save(name, t)
print("edits applied:", len(EDITS))
