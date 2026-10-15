# --- paths derived from this file, not from the machine that ran it ----------------
# The run happened at C:/Users/screa/incunabula; a clone is somewhere else, so walk up
# until the repository root (the directory holding tools/prose/) is found.
import os


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(d, "tools", "prose")):
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return d


REPO = _repo_root()
import io, sys

B = REPO + "/test-books/demo-magician/manuscript/chapters/"

# ---- ch 9: the Lausanne award he did not collect, and the Brussels certificate
p9 = B + "chapter-09.md"
t9 = io.open(p9, encoding="utf-8").read()

O = '''**1930. LAUSANNE.** Disputed by him against a *salle* for a matter of a broken engagement.
*Sentence:* the *salle* in fault; a sum awarded to him. He did not pursue the award.
**He won it and did not take the money. I have queried this in two places and the tribunal
clerk told me, politely, that it was not unusual and that the clerk had seen it four times
in thirty years and had never understood it either.**'''

N = '''**1930. LAUSANNE.** Disputed by him against a *salle* for a matter of a broken engagement.
*Sentence:* the *salle* in fault; a sum awarded to him. He did not pursue the award.
**He won it and did not take the money. I have queried this in two places and the tribunal
clerk told me, politely, that it was not unusual and that the clerk had seen it four times
in thirty years and had never understood it either.**

"Four hundred and six guilders," said L'Ombrière. "That is the sum. I have it from the
tribunal and it is not a large sum and it is not a small one; it is about nine months of a
room in a boarding house, and I have lived in nine rooms in my life and eight of them were
that."

"You have queried it in two places."

"Three. I have queried it in three places and I have written to a lawyer in Lausanne who
charged me forty guilders to tell me that the answer is contained in the sentence itself,
which is that an award runs to the person named in it, and that a person who does not
pursue an award within a stated period is treated as having waived it, and that the stated
period in 1930 was four years." She put her finger on the page. "He had until 1934. He did
not take it in 1934. He did not take it in 1935. It is still in the account of that court.
I checked in January."

"Why does a man win a case and not take the money?"

"That is precisely what I have asked three people and it is precisely what nobody can
answer, and I have begun to think, Miss Reiner, that the question is in the wrong tense.
He did not *not* take the money. He was **made** not to take it, and not by the *salle*,
who had already been beaten and had no further interest, and not by the court, which would
have paid a man his money."

She looked up.

"By whoever it is who has been making sure, for nine years, that this man never has money
and never has a claim on money and never stands to lose anything, anywhere, in any
country. There is a sum in Lausanne that has been sitting in an account since 1930 for a
man who has never asked for it, and if I write to the tribunal and say *does this man
exist*, then somebody has to be told that I am asking, and I have been keeping this file
for nine years on my own wages and I am not going to be the reason it ends."

Reiner put her own notebook down, which she did perhaps twice in her working life.

"L'Ombrière. How much is it to ask whether a person exists?"

"Eleven guilders and a bad morning."

"Then I am not going to ask it either," said Reiner, "and I want it written down somewhere
that the reason I am not is that you said *a bad morning* and I understood you, and not
because I have any respect for a court in Lausanne, which I have not, and which has had
four hundred and six guilders of a man's money since the year I was born."'''

if O not in t9:
    sys.exit("ch9b miss")
t9 = t9.replace(O, N, 1)
io.open(p9, "w", encoding="utf-8").write(t9)
print("ch9 now", len(t9.split()), "(target 3390)")

# ---- ch 11: the eleven hours
p11 = B + "chapter-11.md"
t11 = io.open(p11, encoding="utf-8").read()

O2 = '''He had asked about the tide **twice**, and had written the second answer down.'''

N2 = '''They talked for eleven hours and Reiner had the shape of it in four pieces, and the first
piece was that they had talked about the river for the first five of them.

Not about the lock. About the *river*, and at a level of detail that Reiner — who has been
in nine hundred rooms and can follow a conversation being conducted as a method — could
only just keep hold of. He had asked what the tide did at the bend below the house. He had
asked whether the current ever changed. He had asked what happened in a hard February.

And the woman of sixty had answered all of it, at length, and had enjoyed it, and Reiner
understood on about the second hour that this was the point.

"You are enjoying this."

"I am," the woman said, without any embarrassment at all. "I have had a man in my front
room for eleven hours in October asking me about the Scheldt and I have not had anybody ask
me about the Scheldt since my husband died, and he worked it, and he asked me whether the
*current* ever changes, and I said only in a hard February, and he said *what happens in a
hard February*, and I talked for about forty minutes, and it was the best conversation I
have had in this house since 1931, and I have thought about that a great deal and I do not
like it."

"Why not."

"Because I have not told anybody about it." She put her hands flat on the cloth. "I have
told a man from a court that I was a widow with no family and that a stranger was in my
house for eleven hours, and I did not tell him that we talked about the river, because it
does not bear on anything, and because a thing that does not bear on anything is the only
kind of thing I have had in this house in three years, and I was not going to hand it to a
man in a corridor."

Reiner wrote that down in full, and it is the only page in the case file that has nothing
to do with the case, and she has never been able to decide whether that is a weakness of the
case or the whole of it.

The second piece was the hands. She had noticed them at the table and had not been able to
put anything on them for six months, and in the front room of a house on the Scheldt she
got four sentences about them and the fourth was the one.

"He held a cup for about four hours," said the woman. "That is all. He held it. It was
half full and he did not drink it and he did not put it down, and at some point in the
afternoon I took it away and filled it and gave it back and he said thank you, and he held
it again."

"That is nothing."

"It is nothing to you and I have thought about it every day for a year," said the woman,
"because I do the same thing. Not with a cup. I hold the same cup for eleven hours when
somebody is in my front room and I have never once known I was doing it, and my husband used
to laugh at me about it, and he is dead, and I have not had anybody in this room since, and
on the eleventh of October a man I had never seen held a glass of water in my front room for
eleven hours and I have not been able to stop thinking about it, and I would like to know
what it is, and nobody has ever been able to tell me, and I have asked a doctor and he
laughed."

The third piece was that he had not once asked her anything about the corps, and the fourth
was the tide, and the fourth is the one that took eleven months off her.

He had asked about the tide **twice**, and had written the second answer down.'''

if O2 not in t11:
    sys.exit("ch11b miss")
t11 = t11.replace(O2, N2, 1)
io.open(p11, "w", encoding="utf-8").write(t11)
print("ch11 now", len(t11.split()), "(target 3390)")
