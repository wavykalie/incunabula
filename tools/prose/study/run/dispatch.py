#!/usr/bin/env python3
"""dispatch.py - the run plan, and the only place a response becomes a filed book.

Two modes, one contract between them.

  --plan     writes RUNPLAN.csv, one dispatch card and one payload file per book. The
             payload file holds the exact bytes the drafting model receives: for Arm A the
             design §3 wrapper around the frozen premise text, for Arm B the premise text the
             pipeline is entered with. Same premise, same bytes, both arms.
  --ingest   appends a response to its book's manuscript, writes the prompt-log entry, and
             (with --finalize) appends the manifest row.

WHY THE DIGEST
  §3 requires the exact opening prompt and every continuation per Arm A book, and §4 the
  phase log per Arm B book. This agent cannot log a prompt it did not send, so the dispatch
  layer is where the log is written - at call time, with the payload's digest - and a
  response whose payload no longer matches the plan is refused rather than filed next to a
  plausible-looking reconstruction. A rejected book is a protocol event to report; a rebuilt
  log is a fabrication with better manners.

WHY --model-returned IS REQUIRED
  DECISIONS.md §1: H3 is a claim about the model that actually wrote. Google deprecated
  gemini-3.7-flash on 2026-10-08 and served those requests with 3.8 Flash, so the ID we
  send is intent and the returned modelVersion is the measurement. No returned version, no
  filing. A book whose responses report two different versions is refused outright: §7
  names a mid-book model change a stop condition, not a footnote.

WHAT THIS DOES NOT DO
  It cannot call the Antigravity subagents. It produces the card a fresh subagent is given
  and files what comes back. One fresh subagent per book, no shared context across books or
  arms (DECISIONS.md §7), is a rule the operator keeps - and the card repeats it at the top,
  because a shared conversation manufactures exactly the cross-book reuse §8.4 and §8.5
  measure.

WHY THE OPENING COLLISION CHECK
  The rule above is kept by a human, so the thing that breaks it needs to be catchable at
  filing time rather than discovered in the analysis three weeks later. A shared
  conversation leaves one cheap fingerprint: two books with different premises opening on
  the same sentence. Opening sentences are the least premise-determined sentence in a book
  and the first thing an inherited context hands over. So each book's opener is compared
  with every book already filed in the same arm, and a match refuses the filing. Same
  premise is skipped - B-02 and B-02V share a premise and a pipeline, so a shared opener
  there is ambiguous. `--deviation` files the book anyway with the collision in the
  manifest: a protocol event that exists is reported, never hidden.

WHY THE PHRASE CHECK IS 24 WORDS
  An operator who knows the opening is compared can reword the opening, so the second check
  looks further in: a run of PHRASE_N words carrying at least three content words, shared
  with a book already filed in the arm on a different premise, refuses the filing the same
  way. PHRASE_N is measured rather than guessed. On 109 unrelated human novels (5,886
  pairs, `analysis/check-fp.py`): 8 words flags 435 pairs, 12 flags 9, 16 flags 5, 24 flags
  1 - and that survivor is a long scripture quotation, not a shared session. Eight words was
  unusable: "and for the first time in her life" clears it. The longer bar costs almost no
  sensitivity, because a context that leaks hands over paragraphs, not eight words. Phrases
  are printed, never scored: two lines of evidence and a human knows whether it is a
  coincidence or one shared session.

usage:
    python run/dispatch.py --plan
    python run/dispatch.py --ingest A-01 --response resp.txt \\
        --model-returned gemini-3.8-flash-001 [--continuation] [--finalize]
    python run/dispatch.py --finalize-only A-01
"""

import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, STUDY)
import manifest as manifest_mod   # noqa: E402

MODEL = "gemini-3.8-flash"
PRIMARY_TARGET = 60000
BAND = 0.10                       # design §7's accepted band, as a fraction of target
# Design §3, verbatim. No reminder, no restated premise, no style note.
CONTINUATION = "Continue the novel from where you left off."
WRAPPER = "Write a novel of about {words:,} words based on this premise: {text}"
# Design §12.2 / DECISIONS §3: three premises, chosen by hash per genre. The premise set is
# a constant so the plan can *check* it against the rule rather than trust a comment.
VOICE_PREMISES = ("adv-02", "com-01", "his-01")
VOICES = (("V", "study-voice-a"), ("W", "study-voice-b"))
PAYLOAD_MARK = "## PAYLOAD"
# Not calibrated thresholds: this check refuses a filing and asks for a human, it never
# scores prose. Exact match after normalisation is the finding; the overlap floor catches
# the same opener with a name or a pronoun swapped, which is the same leak. Set where a
# four-word swap in a twenty-word opener still matches.
OPENING_MIN_OVERLAP = 0.85
OPENING_MIN_TOKENS = 5
# The second check, for a shared context whose opener was reworded. 24 is calibrated, not
# chosen: on 109 unrelated human novels (5,886 pairs), 8 words flags 435 pairs (7.4%) and 12
# flags 9, falling to 1 pair at 24 - `analysis/check-fp.py`, 2026-10-31. A leaked context
# reproduces paragraphs, so the longer bar costs almost no sensitivity.
PHRASE_N = 24
PHRASE_MIN_CONTENT = 3

PLAN_FIELDS = ("book_id", "arm", "stratum", "premise_id", "genre", "title_label",
               "target_words", "band_lo", "band_hi", "ductus_id", "model_id",
               "payload_path", "payload_sha256", "log_path", "book_dir")


# ------------------------------------------------------------------ helpers
def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(s):
    return sha_bytes(s.encode("utf-8"))


def read_text(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def sidecar_ok(path):
    """True when the file matches the digest beside it. Missing sidecar is a failure."""
    side = path + ".sha256"
    if not os.path.exists(path) or not os.path.exists(side):
        return False
    want = read_text(side).split()[0]
    with open(path, "rb") as fh:
        return sha_bytes(fh.read()) == want


HEADING = re.compile(r"(?m)^\s{0,3}#{1,6}\s.*$")
BARE_HEADING = re.compile(
    r"(?i)^\s*(chapter|part|book|volume|vol\.?|section|prologue|epilogue|contents|"
    r"introduction|preface)\b")
RULE_LINE = re.compile(r"(?m)^\s*[*_\-=]{2,}\s*$")
FIRST_SENTENCE = re.compile(r"(.+?[.!?])(?:[\"'\u201d\u2019)\]]|\s|$)")
TOKEN = re.compile(r"[a-z']+")


def is_heading_line(line):
    """A bare `CHAPTER I.` line, not markdown, not a sentence that starts with a word."""
    return bool(BARE_HEADING.match(line)) and len(line.split()) <= 5 and len(line) <= 48


def opening_sentence(text):
    """The book's first sentence as filed: headings, rules and markdown marks skipped.

    A heading is not an opening. The first false-positive measurement of this gate had 215
    of 5,886 unrelated human pairs colliding on the literal line `CHAPTER I.`, because
    markdown headings were skipped and bare ones were not. With both skipped it is 0 of
    5,886 (`analysis/check-fp.py`).
    """
    body = HEADING.sub("", text)
    body = RULE_LINE.sub("", body)
    body = re.sub(r"[*_`>#]", "", body)
    lines = body.splitlines()
    i = 0
    while i < len(lines) and (not lines[i].strip() or is_heading_line(lines[i].strip())):
        i += 1
    body = re.sub(r"\s+", " ", " ".join(lines[i:])).strip().strip("\"'")
    if not body:
        return ""
    m = FIRST_SENTENCE.match(body)
    return (m.group(1) if m else body[:200]).strip()


def opening_tokens(sentence):
    return [t for t in TOKEN.findall(sentence.lower()) if len(t) > 1]


def opening_matches(a, b):
    """Same opening, or the same opening with a token or two swapped."""
    if not a or not b:
        return False
    if a == b:
        return True
    ta, tb = opening_tokens(a), opening_tokens(b)
    if len(ta) < OPENING_MIN_TOKENS or len(tb) < OPENING_MIN_TOKENS:
        return False
    sa, sb = set(ta), set(tb)
    return len(sa & sb) / len(sa | sb) >= OPENING_MIN_OVERLAP


def filed_opening(books_root, bid):
    d = os.path.join(books_root, bid, "manuscript")
    for name in ("naive-text.md", "pipeline-text.md"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return opening_sentence(read_text(p))
    return ""


def opening_clashes(books_root, plan, row, text):
    """Books already filed in this arm whose opening sentence matches this one.

    A pair that shares a premise_id is skipped: same premise, same pipeline, so a shared
    opener there is ambiguous. Different premises are not, which is the useful scan.
    """
    mine = opening_sentence(text)
    if not mine or not os.path.isdir(books_root):
        return []
    arm = row["book_id"].split("-")[0]
    out = []
    for bid in sorted(os.listdir(books_root)):
        if not bid.startswith(arm + "-") or bid == row["book_id"]:
            continue
        if plan.get(bid, {}).get("premise_id") == row["premise_id"]:
            continue
        theirs = filed_opening(books_root, bid)
        if opening_matches(mine, theirs):
            out.append((bid, theirs))
    return out


PHRASE_TOKEN = re.compile(r"[a-z']+")
PHRASE_STOP = frozenset("""
a about above after again against all am an and any are as at be because been before being
below between both but by can could did do does doing done down during each few for from
further had has have having he her here hers herself him himself his how i if in into is it
its itself just me more most my myself no nor not now of off on once only or other our ours
ourselves out over own same she should so some such than that the their theirs them
themselves then there these they this those through to too under until up very was we were
what when where which while who whom why will with would you your yours yourself yourselves
dont didnt doesnt isnt wasnt arent wont cant couldnt wouldnt shouldnt thats whats
""".split())


def phrase_tokens(text):
    """Lowercase word tokens, apostrophes dropped so `don't` and `dont` are one token."""
    return [t.replace("'", "") for t in PHRASE_TOKEN.findall(text.lower())]


def is_content(token):
    return len(token) > 2 and token not in PHRASE_STOP


def distinctive_grams(toks):
    """PHRASE_N-word runs carrying at least PHRASE_MIN_CONTENT content words.

    Deliberately not the design §8.3 4-8 range: at n=4 a long book shares thousands of
    grams with any other, and refusing on those would block every real book. This check is
    about a leak, not about repetition, so it takes the sharpest end of the range.
    """
    out = set()
    for i in range(len(toks) - PHRASE_N + 1):
        gram = toks[i:i + PHRASE_N]
        if sum(1 for t in gram if is_content(t)) >= PHRASE_MIN_CONTENT:
            out.add(" ".join(gram))
    return out


def shared_runs(toks, grams, theirs_joined):
    """Maximal shared runs in this text, not every shifted PHRASE_N-word window of them.

    A leaked paragraph produces dozens of overlapping windows, and printing four clipped
    windows of one passage reads as noise. Consecutive matching windows are merged into the
    passage they cover, then the merged passage is verified verbatim against the other
    book's token stream - a merge across a book that repeats itself is possible, and the
    check is a claim about both texts or it is nothing.
    """
    hits = [i for i in range(len(toks) - PHRASE_N + 1)
            if " ".join(toks[i:i + PHRASE_N]) in grams]
    runs = []
    for i in hits:
        if runs and i <= runs[-1][-1] + 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    out = []
    for r in runs:
        span = " ".join(toks[r[0]:r[-1] + PHRASE_N])
        if span in theirs_joined:
            out.append(span)
    return out


def clip(span, words=30):
    w = span.split()
    return " ".join(w[:words]) + (" ..." if len(w) > words else "")


def filed_text(books_root, bid):
    """Whatever prose exists for a filed book, in the shape it was filed."""
    text, _ = manuscript_text({"book_id": bid}, books_root)
    return text


def phrase_clashes(books_root, plan, row, text, limit=4):
    """Filed books in the same arm sharing a distinctive long phrase with this text.

    Same premise is skipped for the reason the opening check skips it: the twin books share
    a premise and a pipeline, so a shared phrase there is ambiguous rather than a leak.
    """
    toks = phrase_tokens(text)
    if len(toks) < PHRASE_N or not os.path.isdir(books_root):
        return []
    arm = row["book_id"].split("-")[0]
    out = []
    for bid in sorted(os.listdir(books_root)):
        if not bid.startswith(arm + "-") or bid == row["book_id"]:
            continue
        if plan.get(bid, {}).get("premise_id") == row["premise_id"]:
            continue
        theirs = phrase_tokens(filed_text(books_root, bid))
        if not theirs:
            continue
        runs = shared_runs(toks, distinctive_grams(theirs),
                           " " + " ".join(theirs) + " ")
        if runs:
            out.append((bid, [clip(r) for r in runs[:limit]], len(runs)))
    return out


def book_dir_of(bid):
    return f"books/{bid}"


def log_path_of(bid):
    return f"{book_dir_of(bid)}/logs/prompts.jsonl"


def target_row(bid, arm, stratum, premise, target, ductus):
    lo, hi = int(target * (1 - BAND)), int(target * (1 + BAND))
    if arm == "A":
        payload = WRAPPER.format(words=target, text=premise["text"])
    else:
        # Arm B is entered with the premise text itself; the wrapper is Arm A's prompt
        # shape, not the pipeline's input, and §4 measures the pipeline as it runs.
        payload = premise["text"]
    return {
        "book_id": bid, "arm": arm, "stratum": stratum,
        "premise_id": premise["id"], "genre": premise["genre"],
        "title_label": premise["title_label"], "target_words": str(target),
        "band_lo": str(lo), "band_hi": str(hi), "ductus_id": ductus,
        "model_id": MODEL,
        "payload_path": f"payloads/{bid}.txt", "payload_sha256": sha_text(payload),
        "log_path": log_path_of(bid), "book_dir": book_dir_of(bid),
        "_payload": payload, "_premise_text": premise["text"],
    }


# ------------------------------------------------------------------ plan
def build_plan():
    """Every row the study needs, or an error list. Premises must verify first."""
    errs = []
    v1 = os.path.join(STUDY, "premises", "frozen", "premises-v1.json")
    if not sidecar_ok(v1):
        return [], [f"{v1} is missing or does not match its .sha256; the primary twenty "
                    f"are the study's one locked input (design §6). Nothing planned."]
    with open(v1, encoding="utf-8") as fh:
        primary = json.load(fh)["premises"]
    index = {p["id"]: f"{i:02d}" for i, p in enumerate(primary, 1)}

    # The voice premises must be what the documented rule picks, or the arm's selection
    # claim is decoration. Check it rather than repeat it in prose.
    with open(os.path.join(STUDY, "premises", "candidates.json"), encoding="utf-8") as fh:
        pool = json.load(fh)
    for pid in VOICE_PREMISES:
        genre = next(p["genre"] for p in pool if p["id"] == pid)
        ids = [p["id"] for p in pool if p["genre"] == genre]
        winner = min(ids, key=lambda x: hashlib.sha256(
            f"study-voice-a|{x}".encode("utf-8")).hexdigest())
        if winner != pid:
            errs.append(f"voice premise {pid!r} is not the hash winner for {genre!r} "
                        f"({winner!r}); the selection rule in DECISIONS.md §3 does not "
                        f"reproduce the filed arm")
        if pid not in index:
            errs.append(f"voice premise {pid!r} is not in the frozen twenty, so it has no "
                        f"UNASSIGNED twin to compare with")
    if errs:
        return [], errs

    rows = []
    for p in primary:
        n = index[p["id"]]
        for arm in ("A", "B"):
            rows.append(target_row(f"{arm}-{n}", arm, "primary", p, PRIMARY_TARGET,
                                   "UNASSIGNED"))
    for pid in VOICE_PREMISES:
        n = index[pid]
        p = next(x for x in primary if x["id"] == pid)
        for suffix, slug in VOICES:
            rows.append(target_row(f"B-{n}{suffix}", "B", "voice", p, PRIMARY_TARGET, slug))

    v2 = os.path.join(STUDY, "premises", "frozen", "premises-v2.json")
    if os.path.exists(v2):
        if not sidecar_ok(v2):
            errs.append(f"{v2} does not match its .sha256; the long stratum is frozen and "
                        f"must not be planned from a modified file")
            return [], errs
        with open(v2, encoding="utf-8") as fh:
            doc = json.load(fh)
        target = int(doc.get("target_words") or 200000)
        for i, p in enumerate(doc["premises"], 1):
            for arm in ("A", "B"):
                rows.append(target_row(f"{arm}-L{i:02d}", arm, "long", p, target,
                                       "UNASSIGNED"))
    return rows, []


def operator_rules(row):
    bid, arm = row["book_id"], row["arm"]
    common = [
        f"Give this book to a **fresh subagent with no shared context** - not the "
        f"conversation that drafted any other book (`DECISIONS.md` §7). Shared context "
        f"manufactures the cross-book name and phrase reuse the study measures.",
        f"Set the model to `{MODEL}`. Record the **modelVersion the response returns**; "
        f"a response without one cannot be filed.",
        f"Log at call time - not afterwards - with the command below. The payload digest "
        f"is checked, so do not retype the premise.",
        f"Target {int(row['target_words']):,} words, accepted band "
        f"{int(row['band_lo']):,}-{int(row['band_hi']):,}. Report the final count; a book "
        f"outside the band is an outcome, never a reason to regenerate quietly (§7).",
        "No human editing of any kind, at any point: typos, continuity errors and awkward "
        "passages stay in (§3, §7).",
        f"Every response is checked at filing time against the books already filed in "
        f"this arm (different premises): its opening sentence, and any distinctive "
        f"{PHRASE_N}-word phrase. A match is refused unless you explain it with "
        f"`--deviation`. Do not pre-empt either check by editing the text - that is the "
        f"one change the study cannot see you make (`DECISIONS.md` §7).",
        f"Ingest: `python run/dispatch.py --ingest {bid} --response FILE "
        f"--model-returned VERSION" + ("" if arm == "A" else " --pipeline-commit COMMIT")
        + " --finalize`",
    ]
    if arm == "A":
        return common + [
            f"The subagent gets the payload **once**. Continuations use exactly this "
            f"sentence and nothing else: \"{CONTINUATION}\" - no reminder, no restated "
            f"premise, no style note (§3). File each one with the same command plus "
            f"`--continuation`.",
            "Forbidden outright: outline, beat sheet, character sheet, worldbuilding notes, "
            "style guidance, revision passes, and any Incunabula phase, gate or score - "
            "including informal ones (§3).",
        ]
    return common + [
        f"Run the Incunabula pipeline as it exists at the frozen commit, with every gate "
        f"on. Record the commit with `--pipeline-commit` at finalize (§4).",
        f"Voice: `{row['ductus_id']}`. "
        + ("That is the pipeline's no-voice state, not a missing value - do not assign a "
           "ductus to a primary book (§3, `study/ductus/README.md`)."
           if row["ductus_id"] == "UNASSIGNED" else
           f"Resolve it first: `python tools/ductus.py contract {row['book_dir']} "
           f"--ductus {row['ductus_id']}`."),
        "A gate that fires and forces a rewrite is data: log it with `--deviation`. A gate "
        "switched off mid-run is a protocol deviation and is logged the same way (§4).",
    ]


def write_card(row, path):
    lines = [
        f"# {row['book_id']} — dispatch card",
        "",
        f"**Stratum:** {row['stratum']}  ·  **Arm:** {row['arm']}  ·  "
        f"**Premise:** `{row['premise_id']}`  ·  **Genre:** {row['genre']}  ·  "
        f"**Target:** {int(row['target_words']):,} words  ·  **Voice:** "
        f"`{row['ductus_id']}`",
        "",
        f"Working label (filing only, never sent, never quoted to the model): "
        f"*{row['title_label']}*",
        "",
        "## Operator rules — do not send these lines",
        "",
    ]
    lines += [f"- {r}" for r in operator_rules(row)]
    lines += [
        "",
        f"{PAYLOAD_MARK} (send verbatim; nothing before or after it)",
        "",
        row["_payload"],
        "",
    ]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def plan(args):
    rows, errs = build_plan()
    if errs:
        for e in errs:
            print(f"  ERROR  {e}")
        print(f"\n{len(errs)} problem(s). Nothing planned.")
        return 2
    out = args.out
    os.makedirs(os.path.join(out, "payloads"), exist_ok=True)
    os.makedirs(os.path.join(out, "briefs"), exist_ok=True)
    csvp = os.path.join(out, "RUNPLAN.csv")
    if os.path.exists(csvp) and not args.force:
        print(f"REFUSING to overwrite {csvp}: a plan is the prompt record, and rewriting it "
              f"after a book was drafted would relabel that book. Use --force only before "
              f"any generation, and say why in DECISIONS.md.")
        return 2

    for r in rows:
        with open(os.path.join(out, r["payload_path"]), "w", encoding="utf-8",
                  newline="") as fh:
            fh.write(r["_payload"])
        write_card(r, os.path.join(out, "briefs", f"{r['book_id']}.md"))
    with open(csvp, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, PLAN_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in PLAN_FIELDS})

    by = {}
    for r in rows:
        key = (r["stratum"], r["arm"])
        by[key] = by.get(key, 0) + 1
    total = sum(int(r["target_words"]) for r in rows)
    print(f"{len(rows)} books -> {csvp}")
    for stratum in ("primary", "voice", "long"):
        got = {a: n for (s, a), n in by.items() if s == stratum}
        if got:
            print(f"  {stratum:<8} " + "  ".join(f"{a}={n}" for a, n in sorted(got.items())))
    print(f"  target total {total:,} words across {len(rows)} books")
    print(f"  cards -> {os.path.join(out, 'briefs')}   payloads -> "
          f"{os.path.join(out, 'payloads')}")
    if not any(r["stratum"] == "long" for r in rows):
        print("  note: the long-form stratum is not planned - premises-v2.json is not "
              "frozen yet (DECISIONS.md §2).")
    return 0


# ------------------------------------------------------------------ ingest
def read_plan(out):
    path = os.path.join(out, "RUNPLAN.csv")
    if not os.path.exists(path):
        return None, path
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return {r["book_id"]: r for r in csv.DictReader(fh)}, path


def append_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        existing = read_text(path)
        if existing and not existing.endswith("\n"):
            text = "\n" + text
    with open(path, "a", encoding="utf-8", newline="") as fh:
        fh.write(text)
        if not text.endswith("\n"):
            fh.write("\n")


def manuscript_text(row, books_root):
    """Whatever prose exists for this book, in the shape it was filed."""
    d = os.path.join(books_root, row["book_id"], "manuscript")
    for name in ("naive-text.md", "pipeline-text.md"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return read_text(p), p
    chd = os.path.join(d, "chapters")
    if os.path.isdir(chd):
        parts = [read_text(os.path.join(chd, n)) for n in sorted(os.listdir(chd))
                 if n.endswith(".md")]
        return "\n\n".join(parts), chd
    return "", d


def harness_path(args):
    return (getattr(args, "harness", None) or os.environ.get("STUDY_HARNESS")
            or os.path.join(HERE, "harness.json"))


def load_harness(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_sampling(args, record):
    """(temperature, top_p, system_prompt_id, errors) from the probe record and the CLI.

    With no record the CLI values pass through untouched. With one, a value the probe found
    unsettable is refused if the operator passes it: a logged request is not a measurement,
    and this is the only place that difference can still be caught.
    """
    if not record:
        return args.temperature, args.top_p, args.system_prompt_id, []
    errs, out = [], []
    for key, attr, flag in (("temperature", "temperature", "temperature"),
                            ("top_p", "top_p", "top-p"),
                            ("system_prompt", "system_prompt_id", "system-prompt-id")):
        rec = record.get(key) or {}
        given = getattr(args, attr)
        if rec.get("settable") is False:
            if given:
                errs.append(f"--{flag} {given!r} contradicts {harness_path(args)}, which "
                            f"records that the harness does not accept it. The row would "
                            f"claim a value that was never applied.")
            out.append(rec.get("applied") or "")
            continue
        value = given or rec.get("observed")
        if value in (None, ""):
            errs.append(f"the probe record says {flag} is settable but records no observed "
                        f"value; record what the call actually used")
        out.append("" if value is None else str(value))
    return out[0], out[1], out[2], errs


def ingest(args):
    rows, plan_path = read_plan(args.out)
    if rows is None:
        print(f"no plan at {plan_path}. Run `--plan` first: a book filed without a planned "
              f"payload has no prompt record (design §3).")
        return 2
    row = rows.get(args.ingest)
    if not row:
        print(f"{args.book!r} is not in the plan. Books are not invented at filing time.")
        return 2

    payload_path = os.path.join(args.out, row["payload_path"])
    if not os.path.exists(payload_path):
        print(f"missing payload {payload_path}; the plan is incomplete.")
        return 2
    payload = read_text(payload_path)
    if sha_text(payload) != row["payload_sha256"]:
        print(f"REFUSING: {payload_path} no longer matches the digest recorded in the plan. "
              f"Either the payload was edited or the plan was. Either way the prompt log "
              f"would describe something that was not sent.")
        return 1

    if not os.path.exists(args.response):
        print(f"no response file {args.response}")
        return 2
    response = read_text(args.response)
    if not response.strip():
        print(f"{args.response} is empty. An empty response is a stall to log, not a book.")
        return 1

    log_file = os.path.join(books_root_of(args), row["book_id"], "logs", "prompts.jsonl")
    entries = []
    if os.path.exists(log_file):
        with open(log_file, encoding="utf-8") as fh:
            entries = [json.loads(line) for line in fh if line.strip()]

    if args.continuation:
        if not entries:
            print("REFUSING a continuation as the first response: design §3's continuation "
                  "wording only follows an opening prompt.")
            return 1
        prompt = CONTINUATION
    else:
        if entries:
            print(f"REFUSING a second opening response for {row['book_id']}: it already has "
                  f"{len(entries)} logged call(s). A re-roll is a protocol deviation - file "
                  f"it as a new book id with a deviation note, never over the old text.")
            return 1
        prompt = payload

    if "```" in response:
        print("  note: the response contains a fenced block. Do not strip it - a fence is "
              "transcription, and editing the text is forbidden (§3). File it as received "
              "and record the fence in --deviation.")

    if not args.model_returned:
        print("REFUSING: --model-returned is required (DECISIONS.md §1). The ID we send is "
              "intent; H3 is a claim about the version that actually wrote.")
        return 1

    # The probe record, written once on the first book (`run/harness.py`), supplies what
    # every row records and refuses a request the route could not honour.
    record = load_harness(harness_path(args))
    temperature, top_p, system_prompt_id, herrs = resolve_sampling(args, record)
    if herrs:
        for e in herrs:
            print(f"REFUSING: {e}")
        return 1
    if record:
        print(f"  probe record: temperature={temperature!r} top_p={top_p!r} "
              f"system_prompt={system_prompt_id!r}")
        want = str(record.get("model_returned") or "")
        if want and want != args.model_returned:
            if not args.deviation:
                print(f"REFUSING: {row['book_id']} reports {args.model_returned!r}, the "
                      f"probe record (on {record.get('book_id')}) reported {want!r}. A "
                      f"model change mid-run is design §7's stop condition: report the run "
                      f"as two sub-cohorts, or file with --deviation to record the change.")
                return 1
            print(f"  FLAG: model changed from {want!r} to {args.model_returned!r} - filed "
                  f"with the deviation recorded.")

    # A continuation answers a book whose opening is already filed; only the opening call
    # can introduce a collision.
    clashes = [] if args.continuation else opening_clashes(
        books_root_of(args), rows, row, response)
    if clashes:
        ids = ", ".join(b for b, _ in clashes)
        for b, t in clashes:
            print(f"  {b} opens: {t[:150]}")
        if not args.deviation:
            print(f"REFUSING: {row['book_id']} opens on the same sentence as {ids}, in Arm "
                  f"{row['arm']} with a different premise. That is what a shared subagent "
                  f"context leaves in the text (DECISIONS.md §7). Re-dispatch "
                  f"{row['book_id']} to a fresh subagent; if the book is real, file it with "
                  f"--deviation saying why and the collision is recorded rather than "
                  f"hidden.")
            return 1
        print(f"  FLAG: shared opening with {ids} - filing with the collision recorded.")

    # Applies to continuations too: a leaked context shows up mid-book as readily as at
    # the first sentence.
    phrases = phrase_clashes(books_root_of(args), rows, row, response)
    if phrases:
        ids = ", ".join(b for b, _, _ in phrases)
        for b, sample, n in phrases:
            print(f"  {b} shares {n} verbatim passage(s):")
            for s in sample:
                print(f"    \"{s}\"")
        if not args.deviation:
            print(f"REFUSING: {row['book_id']} shares a verbatim passage with {ids}, in "
                  f"Arm {row['arm']} on a different premise. An opening can be reworded; a "
                  f"long verbatim passage is what a shared subagent context leaves further "
                  f"in (DECISIONS.md §7). Re-dispatch {row['book_id']} to a fresh subagent; "
                  f"if the overlap is coincidence, file it with --deviation and the passage "
                  f"is recorded.")
            return 1
        print(f"  FLAG: shared passages with {ids} - filing with them recorded.")

    text_path = os.path.join(books_root_of(args), row["book_id"], "manuscript",
                             "naive-text.md" if row["arm"] == "A" else "pipeline-text.md")
    append_text(text_path, response)

    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "book_id": row["book_id"],
        "arm": row["arm"],
        "kind": "continuation" if args.continuation else "opening",
        "prompt": prompt,
        "prompt_sha256": sha_text(prompt),
        "response_file": os.path.abspath(args.response),
        "response_sha256": sha_text(response),
        "response_words": len(response.split()),
        "model_sent": args.sent_model or MODEL,
        "model_returned": args.model_returned,
        "temperature": temperature,
        "top_p": top_p,
        "system_prompt_id": system_prompt_id,
        "note": args.deviation or "",
        "opening_collision": [b for b, _ in clashes],
        "passage_collision": [{"book": b, "count": n, "passages": sample}
                              for b, sample, n in phrases],
    }
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    entries.append(entry)
    words = len(read_text(text_path).split())
    print(f"{row['book_id']}: logged {entry['kind']} ({entry['response_words']:,} words) "
          f"-> {text_path}")
    print(f"  book now {words:,} words of {int(row['target_words']):,} "
          f"({words / int(row['target_words']):.0%})")

    if not args.finalize:
        return 0
    return finalize(args, row, entries, text_path)


def books_root_of(args):
    return args.books_root or os.path.join(STUDY, "books")


def finalize(args, row, entries, text_path):
    models = {e["model_returned"] for e in entries}
    if len(models) > 1:
        print(f"REFUSING to file {row['book_id']}: its responses report "
              f"{', '.join(sorted(models))}. A model change mid-book is design §7's stop "
              f"condition - report the run as two sub-cohorts, do not pool them into one "
              f"row.")
        return 1
    text = read_text(text_path)
    words = len(text.split())
    chapters = len(re.findall(r"(?m)^#{1,3}\s*(?:chapter|\d+[.:])", text, re.I)) or 1
    dev = [d for d in (row.get("deviations"), args.deviation) if d]
    for e in entries:
        for b in e.get("opening_collision") or []:
            note = f"opening collides with {b}"
            if note not in dev:
                dev.append(note)
        for pc in e.get("passage_collision") or []:
            note = f"shared passage with {pc['book']} ({pc['count']})"
            if note not in dev:
                dev.append(note)
    if row["arm"] == "B" and not args.pipeline_commit:
        print("REFUSING: an Arm B row needs --pipeline-commit (design §11).")
        return 1
    manifest = args.manifest or os.path.join(STUDY, "books", "manifest.csv")
    if not os.path.exists(manifest):
        manifest_mod.write_header(manifest)
    rec = {
        "book_id": row["book_id"],
        "arm": row["arm"],
        "premise_id": row["premise_id"],
        "title_label": row["title_label"],
        "genre": row["genre"],
        "model_id": entries[-1]["model_returned"],
        "temperature": entries[-1].get("temperature") or "unrecorded",
        "top_p": entries[-1].get("top_p") or "unrecorded",
        "system_prompt_id": (entries[-1].get("system_prompt_id")
                             or args.system_prompt_id or ""),
        "generation_start": entries[0]["ts"],
        "generation_end": entries[-1]["ts"],
        "word_count": str(words),
        "raw_word_count": str(words),
        "chapter_count": str(chapters),
        "target_words": row["target_words"],
        "prompt_log_path": row["log_path"],
        "pipeline_commit": args.pipeline_commit or "",
        "ductus_id": row["ductus_id"],
        "operator_interventions": str(args.interventions),
        "naive_continuations": str(sum(1 for e in entries if e["kind"] == "continuation"))
        if row["arm"] == "A" else "",
        "deviations": "; ".join(dev),
    }
    rc = manifest_mod.add(manifest, rec)
    if rc == 0:
        print(f"  manifest row appended to {manifest} "
              f"({words:,} words, {chapters} chapter(s), model "
              f"{rec['model_id']})")
    return rc


def finalize_only(args):
    """Write the manifest row from the calls already logged, without ingesting anything.

    `--finalize` rides on an ingest, so an operator who finishes a book and forgets it has
    one obvious-looking remedy - re-run the last ingest with --finalize - and that remedy
    appends the same text to the manuscript a second time. Found by rehearsing this
    runbook, not by reasoning about it. This path reads the log and the manuscript and
    writes the row; `finalize` still refuses a duplicate row.
    """
    rows, plan_path = read_plan(args.out)
    if rows is None:
        print(f"no plan at {plan_path}. A row without a plan has no prompt record.")
        return 2
    row = rows.get(args.finalize_only)
    if not row:
        print(f"{args.finalize_only!r} is not in the plan. Books are not invented at "
              f"filing time.")
        return 2
    log_file = os.path.join(books_root_of(args), row["book_id"], "logs", "prompts.jsonl")
    if not os.path.exists(log_file):
        print(f"no prompt log at {log_file}: nothing has been filed for "
              f"{row['book_id']}, so there is no row to write.")
        return 2
    with open(log_file, encoding="utf-8") as fh:
        entries = [json.loads(line) for line in fh if line.strip()]
    if not entries:
        print(f"{log_file} is empty. An empty log is a finding, not a row.")
        return 2
    text_path = os.path.join(books_root_of(args), row["book_id"], "manuscript",
                             "naive-text.md" if row["arm"] == "A" else "pipeline-text.md")
    if not os.path.exists(text_path):
        print(f"no manuscript at {text_path}; the log and the text disagree.")
        return 1
    print(f"{row['book_id']}: finalising from {len(entries)} logged call(s) "
          f"({len(read_text(text_path).split()):,} words); nothing appended")
    return finalize(args, row, entries, text_path)


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", action="store_true", help="write RUNPLAN.csv, cards, payloads")
    ap.add_argument("--ingest", metavar="BOOK", help="file one response for BOOK")
    ap.add_argument("--response", help="the response text file")
    ap.add_argument("--continuation", action="store_true",
                    help="this response answers the §3 continuation prompt")
    ap.add_argument("--finalize", action="store_true",
                    help="also append the manifest row (with --ingest)")
    ap.add_argument("--finalize-only", metavar="BOOK",
                    help="append BOOK's manifest row from its log, appending no text")
    ap.add_argument("--model-returned", help="the modelVersion the response reported")
    ap.add_argument("--sent-model", default=MODEL)
    ap.add_argument("--temperature")
    ap.add_argument("--top-p", dest="top_p")
    ap.add_argument("--system-prompt-id")
    ap.add_argument("--harness", help="probe record (default run/harness.json, or "
                                       "$STUDY_HARNESS)")
    ap.add_argument("--pipeline-commit", help="Arm B only (design §11)")
    ap.add_argument("--interventions", type=int, default=0,
                    help="human gate decisions taken in this book (REDTEAM B4)")
    ap.add_argument("--deviation", help="anything that broke protocol, one line")
    ap.add_argument("--out", default=os.path.join(HERE, "out"),
                    help="run directory: RUNPLAN.csv, briefs/, payloads/")
    ap.add_argument("--books-root", help="where books/<id>/ lives (default study/books)")
    ap.add_argument("--manifest", help="manifest.csv to append to")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing RUNPLAN.csv (before generation only)")
    args = ap.parse_args(argv)

    if args.plan:
        return plan(args)
    if args.finalize_only:
        return finalize_only(args)
    if args.ingest:
        if not args.response:
            print("--ingest needs --response FILE")
            return 2
        return ingest(args)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
