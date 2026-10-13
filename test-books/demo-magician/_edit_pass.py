#!/usr/bin/env python3
# demo-magician edit pass: genuine rewrite-UP expansions (per EXPANSION_PASS.md),
# narrative A25/U6 antithesis rewrites (dialogue stays per COMMONPLACE voice rule),
# and verified numeric/date continuity fixes. CRLF preserved.
# Validates every anchor exists exactly once BEFORE applying anything.
import io, textwrap, os

CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manuscript", "chapters")
WRAP = 95

def wrap(prose):
    paras = [p.strip() for p in prose.strip().split("\n\n")]
    out = []
    for p in paras:
        out.append(textwrap.fill(" ".join(p.split()), width=WRAP))
    return "\r\n\r\n".join(out)

def load(name):
    with io.open(os.path.join(CH, name), encoding="utf-8", newline="") as fh:
        return fh.read()

def save(name, text):
    with io.open(os.path.join(CH, name), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

# --- edits: (kind, file, anchor/old, prose/new) ---
EDITS = []

def R(name, old, new):
    EDITS.append(("replace", name, old, new))

def A(name, anchor, prose):
    EDITS.append(("insert", name, anchor, prose))

# ---- narrative A25/U6 antithesis rewrites (merge sentence break) ----
R("chapter-24.md",
  "The hall at Utrecht was not a court. That was the first thing Reiner noticed",
  "The hall at Utrecht was not a court, and that was the first thing Reiner noticed")
R("chapter-29.md",
  "it was not a large moment at all. It was a",
  "it was not a large moment at all, only a")

# ---- ch25 numeric continuity ----
R("chapter-25.md", "The assesseur asked eleven questions.", "The assesseur asked ten questions.")
R("chapter-25.md",
  "ninety minutes, eleven questions, nine of them hers by right and two of them the",
  "ninety minutes, ten questions, eight of them hers by right and two of them the")
R("chapter-25.md", "Seven noes, in a row, in a good suit", "Nine noes, in a row, in a good suit")

# ---- ch12 / ch09 date continuity ----
R("chapter-12.md",
  "The certificate was in Flemish and dated the eleventh of May, 1932",
  "The certificate was in Flemish and dated the eleventh of May, 1935")
R("chapter-12.md",
  "And then in May of 1932 a man who had not been in Brussels asks",
  "And then in May of 1935 a man who had not been in Brussels asks")
R("chapter-12.md", "\"Eleventh of May, 1932,\" she said.", "\"Eleventh of May, 1935,\" she said.")
R("chapter-09.md", "**1933. LYON.** Disputed by him.", "**1932. LYON.** Disputed by him.")

# =================== genuine rewrite-UP expansions ====================
A("chapter-02.md", "put in front of another human being.", """
**What nobody did.**

Twenty-two people in nine feet by eleven and a constable with a book, and not one of them asked him what he had done in the room. They asked each other and they asked the constable, and a baker asked a tribunal in nine lines, and every one of the nine lines was about a coffer and not about a room. I have turned the whole thing over on this boat and the only person who has put the question to me is a commercial traveller with a wind in his face who will be in Leeds on Thursday and will not think about it again.

And I did not ask it either. I sat in that room for four minutes and I came out and I asked what the trick was, which is the same as asking nothing at all, and a man who has been asked nothing for nine years has had nine years of answering everybody. I have watched him do it in a document and in a shed and there is not one question anybody has put to him that he has not been able to answer with a true sentence about somewhere else. A true sentence about a field. A true sentence about a date. A true sentence about a glass of water in a shop that nobody has looked at twice since 1929, and the true sentences are all of them answers, and not one of them is an answer to anything.
""")

A("chapter-05.md", "without knowing you were carrying it.", """
Because a man who is watched while he holds a glass learns how to hold one, and a man who asks for water in a shop is buying a minute with the one person in the building who was not in the room, and he spent the minute on a machine and a glass and a sentence he has been careful with ever since. That is the whole of him. He does not hide the method. He hides in the one place a method cannot be, which is the truth, told early, to nobody.
""")

A("chapter-12.md", "anybody in that trade can be asked.", """
And that is what the nine years have been. Not a case. A man laying down a floor of paper that a person in authority is required to stand on, so that when the day comes there is nowhere left for a question to stand, and a woman with a tin of two hundred and eleven pages has been counting the years to find the one where he did not lay a floor down.
""")

A("chapter-15.md", "discovered in front of everybody that she had just lost an argument by winning it.", """
Because the tent had answered her. Not the company and not the man from Rotterdam and not the room in the end. The tent is bigger than anybody in it, and a thing that is bigger than anybody in it cannot be named by anybody in it, and the moment she named the difficulty out loud the tent had already decided what it was going to do on the Saturday, and the deciding was done by a building, and nobody in the mess had been consulted.
""")

A("chapter-16.md", "being a man nobody can check.", """
And that is the whole of the sixth, and I will not say more than this about it. There is no name for it because a name is a claim, and a claim is a thing that can be answered, and the sixth is not a thing I do so much as a thing I do not do, which is be in a room where anybody can ask. The other five are hands and a light and a rope and a card and a box, and any man can learn them in four years and be better at them than me. The sixth is fifty years of never once letting the question land, and nobody can learn that from me, and I have not taught it, and I am not going to, and the reason I said five in that corridor is that the sixth has to stay a thing nobody has ever said out loud, or it stops being true.
""")

A("chapter-26.md", "and it was not about the trick at all.", """
That was the thing she could not put in a notebook for a fortnight. He had spent the whole of a four-day sitting arranging to be a man who asked a question, so that somewhere in a record there would be one line where he was the party who wanted a thing clarified rather than the party who answered everything, and the line cost him four seconds and a spelling and it was the only piece of vanity in nine years of perfect conduct, and he had done it for her, or for himself, or for the record, and she has never been able to decide which, and it does not matter, because he did it in French and in front of a clerk and it is in the transcript and nobody can take it out.
""")

# ---- validate all anchors up front ----
texts = {}
problems = []
for kind, name, anchor, _ in EDITS:
    if name not in texts:
        texts[name] = load(name)
    c = texts[name].count(anchor)
    if c != 1:
        problems.append((kind, name, anchor[:50], c))
if problems:
    for p in problems:
        print("ANCHOR PROBLEM:", p)
    raise SystemExit(1)

# ---- apply ----
for kind, name, anchor, payload in EDITS:
    t = texts[name]
    assert t.count(anchor) == 1
    if kind == "replace":
        t = t.replace(anchor, payload, 1)
    else:
        t = t.replace(anchor, anchor + "\r\n\r\n" + wrap(payload), 1)
    texts[name] = t
    save(name, t)

print("edits applied:", len(EDITS))
