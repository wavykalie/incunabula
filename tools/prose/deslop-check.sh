#!/usr/bin/env bash
# deslop-check.sh - AI-slop scanner for Book Genesis prose.
#
#   usage:  tools/deslop-check.sh FILE [FILE ...]   (a directory scans its *.md and *.txt)
#   exit 0 = PASS   exit 1 = FAIL
#
#   tools/deslop-check.sh --caps                      print the calibration table
#
# Rule set: tropes.fyi "AI Writing Tropes" (via the deslopify skill at
# .agents/skills/deslopify/references/style_guide.md), plus the humanizer's list.
#
# THRESHOLDS ARE MEASURED, NOT GUESSED.
# Calibrated against 175,144 words / 48 narrative documents of published prose:
#   Wandering Witch: The Journey of Elaina vols. 1/2/5 (Yen Press). Back matter
#   (afterword/appendix) excluded - it is not fiction.
#   Hollow Bridge chs. 1-11 (56,144 words) used as a native-English control.
#
# Why Elaina governs and Hollow Bridge only partly can: Hollow Bridge writes its dashes as
# "--" and its quotes straight, so it scores 0 em dashes and 0 curly quotes as a
# *formatting* fact, not a style one. It cannot calibrate D1 or A20. It does
# calibrate D2, P1-P3, -ly and every word-level rule.
#
# VALIDATION (tools/calibration/CALIBRATION.md):
#   Elaina, 51 files, 0 failing rows ....... PASS  (human control)
#   Hollow Bridge, 9/11 published chapters ..... FAIL  (AI-written control)
#   tools/calibration/slop-fixture.md ...... FAIL, 17 rows (positive control)
# A scanner that passes everything is worthless, and one that fails human prose is
# worse. All three controls are re-run by tools/validate-controls.sh whenever these
# caps change - that command is the gate's own check, and it exits nonzero if a
# control misbehaves or a directory scan expands to zero files.
# See tools/calibration/ for the corpus, the measurements and how to re-derive.
#
#   HARD     zero tolerance. Rule only qualifies if it has *zero* occurrences in
#            the calibration corpus. If published prose never does it, it is a tell.
#   DENSITY  published prose does this, so it cannot be banned - only overdone.
#            Cap = ~1.5x the worst single calibration document, so the reference
#            passes with headroom. Caps are rational (n per w words) because
#            integer per-1k math cannot express a limit below 1/1k.
#   PATTERN  algorithmic checks grep cannot do: anaphora, duplication, fragments.
#   NOTE     reported only, never fails - too noisy to judge mechanically.
#
# This proves the mechanical half. Clean-but-voiceless prose is still slop and
# no scanner can see that. Read it aloud too.

set -u

# ---------------------------------------------------------------- calibrated caps
# D1: worst published doc 8.9/1k, p90 6.7, median 3.8  (cap 10, warn 7)
# D2: worst 3.6/1k (cap 5, warn 4)   -ly: worst 24.3/1k (cap 26, warn 20)
# Worst-document rates are from tools/calibration/measure.py; each cap is set at
# roughly 1.5x its worst document so the reference passes with headroom.
OPEN_PER_N=6         # P1 fail: same 2-word opener > 6 times per 1000 words
OPEN_PER_W=1000
OPEN_SHARE_PCT=15    # P1 fail: top opener > 15% of all sentences
DUP_PER_W=2000       # P2 fail above 1 duplicate per 2000 words (min 1 allowed).
                     # Flat "0" was wrong: a published chapter repeats 4 sentences
                     # verbatim as a deliberate refrain. Scaled instead.
# P3 fail at 7+ in a row. Two human documents in the reference corpus reach 6, so 6
# must pass; the slop fixture runs to 9 and still fails. Measured, not chosen.
FRAG_RUN=7

# ------------------------------------------------- the explanatory coda (F1, A24)
# The closing move that turns the chapter's meaning over and hands the reader the
# interpretation: "That is why...", "Which is why...", "It is also why...",
# "the next chapter is about...".
#   published corpus: 6 hits in 177,047 words (0.03/1k), worst document 0.88/1k
#   and ZERO of 50 published chapters close on one.
# The rate is therefore capped like any density rule, but the POSITION is zero
# tolerance - ending a chapter this way is not a rate, it is a habit.
CODA_RE='(which|that|this) is (also )?why|it is (also )?why|that is (what|the) (makes|thing)|is the (closest|only|real) thing|the (next|following) chapter is|which is (the )?position'

# ---------------------------------------------------------------- tier 1: HARD
# Every pattern below scored ZERO hits in 175,144 words of published narrative.
HARD=(
  'A8|false suspense|(here.s the (thing|kicker|catch|problem)|here.s where it gets|here.s what most people)'
  'A10a|nonfiction filler|(it.s worth noting|it bears mentioning|interestingly,|notably,|at its core|due to the fact that)'
  'A11a|signposted close|(in summary|all in all|and so we return)'
  'A12|despite the challenges|despite (these|its|the) (challenges|obstacles|setbacks)'
  'A13|truth-is-simple|(the (reality|truth) is (simple|simpler|clear)|history is (clear|unambiguous)|the evidence is clear)'
  'A14|stakes inflation|(fundamentally reshape|define the next era|something entirely new|change everything|the very nature of)'
  'A15a|analytical -ing|, (highlighting|underscoring|emphasizing|symbolizing|showcasing|signaling|a reminder of)'
  'A16|vague attribution|(experts (say|argue|believe|suggest)|observers (have|noted|say)|industry reports|some critics|many would argue|several publications)'
  'A18|gerund litany|(^|[.!?] )([A-Z][a-z]+ing [^.!?]{0,40}\. ){2,}'
  'A20|unicode arrows|[→⇒←↔]'
  # NOT a slop rule - a project canon guard. It correctly fires on the excluded
  # book (Hollow Bridge scores 30 hits here). Zero tolerance is intended
  # for OTHER books; on a self-scan of the excluded book itself the rule demotes
  # to report-only (Freeze 11, and ERRATA 2026-10-01 where the observation is
  # recorded with n=2).
  # Bare absorb* was removed from this rule: "absorbed in a book" is ordinary
  # English and occurred 4x in the calibration corpus. That sense is now A22b.
  'A22|excluded-book residue|(What the [A-Z][a-z]+ Kept|guest book|a ledger|the ledger)'
)

# ---------------------------------------------------------------------------
# DEMOTED FROM ZERO TOLERANCE, ON EVIDENCE. Read this before promoting one back.
#
# A1a, A2a, A3a, A19 and A21 were all HARD, justified as "published prose: 0".
# That justification came from ONE corpus - a translated light novel in which
# these words happen not to appear - and a second native-English corpus
# (270,149 words of L.M. Montgomery, 1923-27) put all five to the test. Every
# single hit was a false positive on ordinary literary English:
#
#   A3a  "an intricate, headlong brook" / "a myriad of bees" /
#         "gold and silver brocade tapestry" (a literal wall hanging, twice) /
#         "the palpable bids for favor"
#   A2a  "a soul subtly akin to her own" / "the subtly sweet voices of the
#         night" / "creeping subtly and remorselessly"
#   A1a  "her robust, matter-of-fact Scotch common sense"
#   A19  "I suppose the first thing is to give your hair a good washing"
#   A21  "some one should ask her the great question"
#
# The common cause is that these lists were assembled by reading MODERN MACHINE
# OUTPUT, where the words are tics, and then applied to fiction, where they are
# not. "Subtly" and "robust" are not AI tells; they are English. A word is only
# a tell at a RATE, and 11 hits across 270,149 words is a rate of 0.04/1k.
#
# This is the same failure VERMILLION names about its own instrument - "the
# lexicons are the instrument... a different list would give different numbers" -
# and it is the fifth bug in this directory that all pointed the same way: a gate
# reporting itself more capable than it was. The rule that catches it is the one
# already in README.md: a hard rule requires LITERALLY ZERO across the corpus, and
# one corpus cannot establish that a word is never used in English fiction.
#
# Caps are set ~50x above the worst observed rate (0.039/1k), which is loose on
# purpose. Looseness is recoverable; a gate that fails Anne of Green Gables is not.
# Numerators are INTEGERS: the density comparison is bash integer arithmetic, and a
# decimal warn value silently aborts the loop - which was caught here the only way it
# could be, by checking that a rule the change was supposed to weaken actually still
# appears in the output. See calibration/CALIBRATION.md, "The hard tier did not survive
# a second corpus".
DEMOTED=(
  'A1a|delve family|2|1000|1|1000|(^|[^a-z])(delve|delves|delving|utilize[ds]?|utilizing|streamlin(e|es|ed|ing)|robust|seamless|cutting-edge)([^a-z]|$)'
  'A2a|magic adverbs|2|1000|1|1000|(^|[^a-z])(fundamentally|arguably|profoundly|subtly)([^a-z]|$)'
  'A3a|grandiose nouns|2|1000|1|1000|(^|[^a-z])(tapestry|paradigm|synergy|ecosystem|myriad|palpable|indelible|intricac(y|ies)|intricate|framework)([^a-z]|$)'
  'A19|listicle in prose|2|2000|1|2000|(The (first|second|third|fourth) (wall|takeaway|thing|point|problem|reason) is)'
  'A21|chatbot artifact|2|2000|1|2000|(I hope this helps|let me know if|great question|as an AI)'
)

# -------------------------------------------------------- tier 3: WARN ONLY
# Never fails, never passes silently. Canon-sensitive words a human must rule on.
WARN_ONLY=(
  'A22b|absorption sense (canon guard)|(^|[^a-z])(absorb(ed|s|ing|ption|ptions)?)([^a-z]|$)'
  # A26 is NOT calibrated - and cannot be, from this corpus. It is a heuristic list of
  # character-name clusters that language models converge on across projects, drawn from
  # published research on model naming behaviour rather than measured here. The
  # calibration corpus is a Japanese light novel, so it can neither confirm nor deny the
  # list; a name is not slop the way a phrase is slop. It warns so a human rules on it.
  # A real surname, or a name with cultural grounding, is the answer to this row; the
  # finding is a CAST drawn from the cluster, not one occurrence.
  'A26|default name cluster (heuristic)|(^|[^A-Za-z])(Elara|Elena|Amara|Aiden|Isabella|Kael|Vael|Veyl|Lirael|Garrick|Thorne|Voss|Aldren|Brenn|Sylvan|Okafor|Nguyen)([^a-z]|$)'
)

# ------------------------------------------------------------- tier 2: DENSITY
# Format: id|name|allow_n|allow_w|warn_n|warn_w|regex     (blank warn = no warn band)
# THE REGEX MUST BE THE LAST FIELD - it contains "|" alternation, so parsing
# from the left would truncate it and produce an unbalanced ( .
# Cap = ~1.5x the worst calibration document; see the trailing comment per row.
DENSITY=(
  'A1b|leverage/harness|1|2000|||(^|[^a-z])(harness(es|ed|ing)?|leverage[ds]?|leveraging)([^a-z]|$)'        # worst 0.31/1k
  'A2b|manner adverbs|2|1000|||(^|[^a-z])(quietly|deeply|remarkably|inevitably|undeniably)([^a-z]|$)'        # worst 0.95/1k
  'A3b|literal nouns|7|1000|||(^|[^a-z])(landscape|realm|vibrant)([^a-z]|$)'                                # worst 4.29/1k
  'A4|serves-as dodge|1|2000|||(serves as|serving as|stands as|standing as|acts as|marking a|represents a|represents an|is a testament)'  # 0.13/1k
  'A5|negative parallelism|2|1000|||(is not|was not|are not|were not|isn.t|wasn.t|aren.t|weren.t|rather than) (just|merely|only|about)'  # 0.61/1k
  'A6|not X not Y|2|1000|||(^|[^a-z])Not [a-z][^.!?]{0,30}\. Not [a-z]'                                    # worst 0.52/1k
  'A7|the X? a Y|1|2000|||(^|[^a-z])The (result|worst part|scary part|problem|answer|truth|catch|kicker)\? '  # 0.12/1k
  'A9|teacher voice|1|2000|||(let.s (break this down|unpack|explore|dive in)|think of it (as|like)|imagine a world where)'  # 0.16/1k
  'A10b|forum filler|2|1000|||(in order to|when it comes to|importantly,)'                                 # worst 1.13/1k
  'A17|invented label|1|2000|||the [a-z]+ (paradox|trap|creep|divide|vacuum|inversion)'                     # 1 hit in 175k ("the one divide")
  'A11b|soft conclusion|1|2000|||(in conclusion|to sum up)'                                                # worst 0.24/1k
  'A15b|participial -ing|3|1000|||, (realizing|knowing|feeling|understanding|reflecting|ensuring|allowing)'  # worst 1.69/1k
  'A23|parenthetical dash|3|1000|||—[^—\n]{1,70}—'                                                         # worst 1.79/1k
  'A24|explanatory coda|1|1000|1|2000|(which|that|this) is (also )?why|it is (also )?why|that is (what|the) (makes|thing)|the (next|following) chapter is'  # worst 0.88/1k
  'A25|antithesis formula|3|2000|1|2000|(was|were|is|are) not\b[^.!?]{0,50}[.!?] +(It|That|This|He|She|They) (was|were|is|are)'  # worst published CHAPTER 0.93/1k; raised from 1/2000, see REPORT block header. The \b after "not" is a bug fix, not a retune - see Freeze 7
  'D3|-ly adverbs|26|1000|20|1000|(^|[^a-z])[a-z]{4,}ly([^a-z]|$)'                                         # worst 24.30/1k
)

# ---------------------------------------------------------- tier 2b: REPORT ONLY
# Same arithmetic, same caps, same numbers - and no ability to fail anything.
#
# D1 and D2 were capped on the worst rate in a whole published DOCUMENT and then
# enforced against a CHAPTER, which made them fail real human prose: on 102 published
# chapters from the 140-novel corpus, D1 failed 13.7% and D2 18.6%, spread across 14 and
# 19 distinct novels. They are not tight by accident, they are wrong by unit.
#
# The reason they are reported rather than re-capped is the measurement that settles it.
# Against the AI control they are not a detector either: this project's own books spell a
# dash "--", so D1 reads 0.00/1k on all 22 control chapters, against a published maximum
# of 33.52/1k. D2's control chapters run p50 4.00, max 5.80, against a published median of
# 3.23 and a published maximum of 8.40 - the control sits INSIDE the human distribution,
# below its 95th percentile. So neither row separates machine prose from human prose at
# ANY cap. Raising them to clear published prose (D1 51/1k, D2 13/1k) would produce a
# row that passes every book, machine and human alike: a gate in name only, and worse than
# no row, because its green result would be read as evidence.
#
# So they keep their caps and their warn bands, a person still sees the number, and the
# number cannot accuse. Promote one back only on a corpus where the control and the human
# distribution actually separate.
#
# A25 IS THE COUNTEREXAMPLE, and the reason this block exists at all. A25 is a rate rule
# too, and it also failed a published chapter under its old 1/2000 cap - but its control
# chapters REACH ABOVE the published maximum (3.13/1k against a published chapter maximum
# of 0.93), so the two arms separate and a cap between them exists. Its cap was therefore
# RAISED, not demoted: 3/2000, which is 1.5x the worst published chapter and the one case
# in this table where the usual headroom convention fits. Effect: published failures 1 -> 0
# of 102 chapters, while 2 of the 3 control chapters that exceeded the old cap still do.
#
# A25 is also the one row whose regex had a plain correctness bug, and it was found by
# reading every hit in two finished books rather than by a control misbehaving. There was
# no word boundary after "not", so "was NOTHING in it worth the walk. It was ..." matched:
# the regex took "was not" and then "hing in it worth the walk" as the intervening clause.
# Read out one at a time, 24 of Merope's 25 hits are the real construction and 1 is that
# accident. The fix is one character and it can only ever REMOVE matches, so no cap moved
# and nothing that passed can start failing. Leaving it in place would mean editing a
# correct sentence to dodge a substring - which is the opposite of what a gate is for, and
# the cost falls on the manuscript instead of on the instrument.
#
# So the test is not "does the row false-fail on human prose" - that is true of D1, D2 and
# A25 alike. It is: does the AI control sit above the human distribution, or inside it.
REPORT=(
  'D1|em dash|10|1000|7|1000|—'                                                                            # worst published CHAPTER 33.52/1k
  'D2|rule of three|5|1000|4|1000|[^,.;:]{3,30}, [^,.;:]{3,30}, and [^,.;:]{3,30}'                         # worst published CHAPTER 8.40/1k
)

# ------------------------------------------------------------------ reporting
NOTE_CURLY=1   # curly quotes: typography, not slop. Published books use them
               # (~98/1k). Reported so the .md convention stays visible.
NOTE_DASHSPELL=1  # D1 counts U+2014 only, and 55% of a 140-novel corpus contains no U+2014
               # at all. This row counts any dash spelling so the D1 rate can be read
               # against the right denominator. Reported only, never fails.

fail=0
warn=0

rate() { awk -v n="$1" -v w="$2" 'BEGIN{ if (w<1) w=1; printf "%.2f", n*1000/w}'; }

# One density rule, shared by the DENSITY and DEMOTED tiers. The comparison is integer
# arithmetic on counts and denominators so it cannot drift with rounding, exactly as the
# original loop did; only the reporting moved into a function so two tiers can share it.
# The printed rate is always per 1,000 words and the cap is always quoted with its own
# denominator, because a cap of 1/2000 printed next to a per-1k rate is genuinely confusing.
#
# $3 is `gate` (default 1). At 0 the row keeps its cap, its warn band and its number, and
# cannot set `fail` - which is the whole point of the REPORT tier below.
density_entry() {
  entry="$1"; tag="$2"; gate="${3:-1}"
  id=${entry%%|*}; rest=${entry#*|}
  name=${rest%%|*}; rest=${rest#*|}
  an=${rest%%|*}; rest=${rest#*|}
  aw=${rest%%|*}; rest=${rest#*|}
  wn=${rest%%|*}; rest=${rest#*|}
  ww=${rest%%|*}; rest=${rest#*|}
  re=${rest}
  n=$(grep -oE "$re" "$f" | wc -l | tr -d ' ')
  r=$(rate "$n" "$words")
  suffix=""
  [ -n "$tag" ] && suffix="  [$tag]"
  if [ $(( n * aw )) -gt $(( an * words )) ]; then
    if [ "$gate" = "1" ]; then
      printf '   FAIL  %-5s %-22s %s per 1k (cap %s/%s)%s\n' "$id" "$name" "$r" "$an" "$aw" "$suffix"
      fail=1
    else
      printf '   --    %-5s %-22s %s per 1k (over %s/%s, reported not gated)%s\n' "$id" "$name" "$r" "$an" "$aw" "$suffix"
      warn=1
    fi
  elif [ -n "$wn" ] && [ $(( n * ww )) -gt $(( wn * words )) ]; then
    printf '   warn  %-5s %-22s %s per 1k (cap %s/%s)%s\n' "$id" "$name" "$r" "$an" "$aw" "$suffix"
    warn=1
  else
    printf '   ok    %-5s %-22s %s per 1k (cap %s/%s)%s\n' "$id" "$name" "$r" "$an" "$aw" "$suffix"
  fi
}

print_caps() {
  echo 'DENSITY CAPS - measured from published prose, not chosen'
  echo 'cap = the allowance; warn = the reference median band (a warning, not a defect)'
  echo
  printf '%-5s %-24s %s\n' 'id' 'rule' 'allowance'
  printf '%-5s %-24s %s\n' '-----' '------------------------' '-----------------------------------'
  for entry in "${DENSITY[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; rest=${rest#*|}
    an=${rest%%|*}; rest=${rest#*|}
    aw=${rest%%|*}; rest=${rest#*|}
    wn=${rest%%|*}; rest=${rest#*|}
    if [ -n "$wn" ]; then
      capstr="$an per $aw words (warn above $wn per $aw)"
    else
      capstr="$an per $aw words"
    fi
    printf '%-5s %-24s %s\n' "$id" "$name" "$capstr"
  done
  echo
  echo 'REPORTED, NOT GATED (same caps, cannot fail - see the REPORT block in this file):'
  for entry in "${REPORT[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; rest=${rest#*|}
    an=${rest%%|*}; rest=${rest#*|}
    aw=${rest%%|*}; rest=${rest#*|}
    wn=${rest%%|*}; rest=${rest#*|}
    if [ -n "$wn" ]; then
      capstr="$an per $aw words (warn above $wn per $aw)"
    else
      capstr="$an per $aw words"
    fi
    printf '%-5s %-24s %s\n' "$id" "$name" "$capstr"
  done
  echo
  echo 'HARD rules (zero tolerance) are the ones with 0 hits in the calibration corpus.'
  exit 0
}

[ "${1:-}" = "--caps" ] && print_caps

scan_file() {
  orig="$1"
  f="$orig"

  # Normalise line endings before ANY row is measured.
  #
  # A file with CRLF - or the \r\r\n this project produced for a while - hides its own
  # sentence boundaries from this gate. Every sentence rule here splits on "[.!?] "
  # (punctuation FOLLOWED BY A SPACE) and every density rule that crosses a sentence
  # ends its match with "[.!?] +". A stray \r sits exactly where that space belongs, so
  # the split never happens: on book-2/chapter-11 the awk counted 22 sentences in a
  # chapter that has 43, and P1 was computed against half the text it claims to cover.
  #
  # Measured across validation-series Merope, 15 of 22 chapters carried \r\r\n. On
  # normalisation P1 opener counts roughly DOUBLED and book-1/chapter-10 went from "ok"
  # to FAIL ("they were" x3) - so those chapters were not passing these rows, they were
  # evading them. A gate that under-reports is worse than no gate, because a green
  # result gets read as evidence.
  #
  # NOT ORDINARY CRLF - measured, and the distinction is load-bearing. On this platform
  # awk reads a file in text mode and eats one CR per LF, so a plain CRLF file arrives
  # clean. Synthetic controls and both books confirm it: CONTROL plain CRLF reads 4
  # sentences either way; demo-magician's 34 CRLF chapters read 120 either way, and the
  # regression run on all 34 is byte-identical before and after this fix. Only a LONE or
  # DOUBLED CR survives as a stray byte: \r\r\n loses its \r\n pair and leaves one \r,
  # and that is the case that counted 22 sentences in a chapter that has 43.
  #
  # An earlier survey of these books reported demo-magician as clean because it tested
  # for LONE CR only. That test was right about the question it asked and wrong about the
  # answer that mattered - the book was never affected, but it would have been declared
  # clean on a criterion that does not predict the defect.
  #
  # Fixed in the read path rather than in each row, because "this file is normalised"
  # is a property of the READ, not of any single rule. No cap moved, no rule was added,
  # no gate was added: the numbers are now what the existing caps always meant. The
  # cleanup at the end of this function already removes any copy, since it tests only
  # whether $f differs from $orig.
  #
  # The DETECTOR is tr, not grep, and that is not a style choice. The first version of
  # this fix used "grep -q $'\r'" and it silently never fired: the file under test has
  # 86 CR bytes, and "grep -c $'\r'" on it prints 0. On this platform grep reads the file
  # with CR stripped, so grep cannot see the character this whole fix is about - a gate
  # that reports a fix it did not apply. tr -cd '\r' | wc -c sees all 86. Always confirm
  # a guard fires before trusting a gate that depends on it.
  if [ "$(tr -cd '\r' <"$f" | wc -c | tr -d ' ')" != "0" ]; then
    eol_norm=$(mktemp)
    tr -d '\r' <"$f" >"$eol_norm"
    if [ -s "$eol_norm" ]; then
      f="$eol_norm"
    else
      rm -f "$eol_norm"
    fi
  fi

  words=$(wc -w <"$f" | tr -d ' ')
  [ "$words" -gt 0 ] || words=1

  # Strip Project Gutenberg boilerplate before anything is measured.
  #
  # A Gutenberg file carries its licence header, its transcriber's notes and sometimes an
  # index - editorially dense prose that is not the novel. Scanning it fires hard rules on
  # text nobody wrote on purpose: on the Montgomery corpus, A3a and A19 both tripped
  # inside the header before this was added. Any corpus sourced from Gutenberg is affected,
  # and this project has repeatedly tried to use Gutenberg as a calibration source.
  if grep -qE '^\*\*\* *START OF (THE|THIS) PROJECT GUTENBERG' "$f" 2>/dev/null; then
    stripped=$(mktemp)
    awk '/^\*\*\* *START OF (THE|THIS) PROJECT GUTENBERG/{body=1;next} /^\*\*\* *END OF (THE|THIS) PROJECT GUTENBERG/{body=0} body' "$f" > "$stripped"
    if [ -s "$stripped" ]; then
      f="$stripped"
      words=$(wc -w <"$f" | tr -d ' ')
      [ "$words" -gt 0 ] || words=1
    else
      rm -f "$stripped"
    fi
  fi

  printf '== %s  (%s words)\n' "$orig" "$words"

  # A22 self-scan demotion (Freeze 11, n=2 agreed in ERRATA 2026-10-01; re-keyed
  # in Freeze 12 - see GATE_FREEZE.md).
  #
  # A22 is the cross-contamination guard: its pattern is the previous book's own
  # plot vocabulary, and it exists to catch that vocabulary leaking into a NEW
  # book. When the scanned file belongs to the excluded book's own manuscript,
  # every hit is the book being itself - measured: the control book scores ~30
  # hits on `a ledger` / `the ledger`, its central device. The rule keeps its cap
  # and its number; in a self-scan it reports instead of failing, which is
  # exactly how the REPORT tier treats a row that cannot accuse.
  #
  # Freeze 12 re-key: the demotion used to grep the scanned path for one hardcoded
  # slug, which embedded a private book's name in a public gate. It now keys on a
  # SELFSCAN marker file at the book root - the directory three levels above
  # manuscript/chapters/<file> - so the mechanism is name-free, and any book can
  # declare itself the calibration control the same way.
  selfscan=0
  selfscan_root=$(dirname "$(dirname "$(dirname "$1")")")
  [ -f "$selfscan_root/SELFSCAN" ] && selfscan=1

  for entry in "${HARD[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; re=${rest#*|}
    n=$(grep -oiE "$re" "$f" | wc -l | tr -d ' ')
    if [ "$n" -gt 0 ]; then
      if [ "$selfscan" -eq 1 ] && [ "$id" = "A22" ]; then
        printf '   --    %-5s %-22s x%s  (self-scan: the excluded book itself - vocabulary reported, not gated)\n' "$id" "$name" "$n"
        warn=1
      else
        printf '   FAIL  %-5s %-22s x%s  (published prose: 0)\n' "$id" "$name" "$n"
        grep -noiE "$re" "$f" | head -3 | cut -c1-100 | sed 's/^/         /'
        fail=1
      fi
    fi
  done

  for entry in "${DENSITY[@]}"; do
    density_entry "$entry" "" 
  done

  # Demoted rules run through the same arithmetic, tagged so a reader can see that the
  # row was once zero-tolerance and why it is not any more.
  for entry in "${DEMOTED[@]}"; do
    density_entry "$entry" "demoted from HARD"
  done

  # Report-only density rules: same cap, same number, no ability to fail. Tagged so a
  # reader can see at a glance that a number here is a prompt and not an accusation.
  for entry in "${REPORT[@]}"; do
    density_entry "$entry" "report only" 0
  done

  # one awk pass for patterns: openers, duplication, fragments
  stats=$(awk '
    { buf = buf $0 " " }
    END {
      gsub(/[.!?] /, "\n", buf)
      n = split(buf, s, "\n")
      nsent = 0; dup = 0; run = 0; best = 0
      for (i = 1; i <= n; i++) {
        line = s[i]
        gsub(/^[^A-Za-z]+/, "", line)
        if (line == "") continue
        nsent++
        m = split(line, w, /[ \t]+/)
        wc = 0
        for (j = 1; j <= m; j++) if (w[j] ~ /[A-Za-z]/) wc++
        if (wc >= 1 && wc <= 4) { run++; if (run > best) best = run } else { run = 0 }
        if (wc >= 2) {
          a = tolower(w[1]); b = tolower(w[2])
          if (a ~ /^[a-z]+$/ && b ~ /^[a-z]+$/) { key = a " " b; cnt[key]++ }
        }
        if (wc >= 8) {
          norm = tolower(line)
          gsub(/[^a-z ]/, "", norm)
          if (length(norm) > 40) {
            if (norm in seen) dup++
            else seen[norm] = 1
          }
        }
      }
      mk = ""
      for (k in cnt) if (mk == "" || cnt[k] > cnt[mk] || (cnt[k] == cnt[mk] && k < mk)) mk = k
      # The opener key is TWO words, so it must come LAST: when it sat in field 4,
      # field 5 held its second word, the fragment-run length was read off it, and
      # P3 could never fire ([ "was" -ge 6 ] is an error, which is false).
      printf "%d %d %d %d %s\n", nsent, (mk == "" ? 0 : cnt[mk]), dup, best, (mk == "" ? "-" : mk)
    }' "$f")
  nsent=$(echo "$stats" | awk '{print $1}')
  mopen=$(echo "$stats" | awk '{print $2}')
  dups=$(echo "$stats" | awk '{print $3}')
  mrun=$(echo "$stats" | awk '{print $4}')
  mkey=$(echo "$stats" | cut -d' ' -f5-)
  [ "$nsent" -gt 0 ] || nsent=1

  share=$(awk -v a="$mopen" -v b="$nsent" 'BEGIN{printf "%.1f", 100*a/b}')
  if [ $(( mopen * OPEN_PER_W )) -gt $(( OPEN_PER_N * words )) ] || awk -v s="$share" -v c="$OPEN_SHARE_PCT" 'BEGIN{exit !(s>c)}'; then
    printf '   FAIL  P1    anaphora abuse          "%s" x%s (%s%% of sentences)\n' "$mkey" "$mopen" "$share"
    fail=1
  else
    printf '   ok    P1    anaphora abuse          "%s" x%s (%s%% of sentences)\n' "$mkey" "$mopen" "$share"
  fi

  dup_allow=$(( words / DUP_PER_W ))
  [ "$dup_allow" -lt 1 ] && dup_allow=1
  if [ "$dups" -gt "$dup_allow" ]; then
    printf '   FAIL  P2    duplicate sentence      %s (allowed %s at %s words)\n' "$dups" "$dup_allow" "$words"
    fail=1
  else
    printf '   ok    P2    duplicate sentence      %s (allowed %s)\n' "$dups" "$dup_allow"
  fi

  # P3 now WARNS instead of failing, on evidence from the second corpus.
  #
  # Anne of Avonlea carries a run of 29 consecutive fragments of three words or fewer, in
  # the body and not in front matter (its verse dedication only reaches a run of 1, because
  # undotted lines merge into one long "sentence"). That is a deliberate technique - clipped
  # beats at a heightened moment - and it is what VERMILLION calls *justified inconsistency*:
  # the anomaly is recoverable because a reader can infer the motive.
  #
  # The cap cannot be raised to admit it, because the slop fixture runs to 9. A threshold
  # that passes Montgomery's 29 also passes the fixture's 9, so run length alone does not
  # separate a deliberate clipped sequence from a machine tic. That is not a tuning problem,
  # it is the limit of the measure, and the honest response is to report it and let a person
  # rule - which is exactly how this directory already treats anaphora ("Anaphora is kept;
  # accidental repetition is fixed"). The fixture still fails on 17 other rows.
  if [ "$mrun" -ge "$FRAG_RUN" ]; then
    printf '   warn  P3    short-fragment run      %s in a row (was cap %s; warns only - a long\n' "$mrun" "$((FRAG_RUN-1))"
    printf '                                          clipped sequence can be deliberate; judge it)\n'
    warn=1
  else
    printf '   ok    P3    short-fragment run      %s in a row (cap %s)\n' "$mrun" "$((FRAG_RUN-1))"
  fi

  # F1: the closing coda. A POSITION rule, so it cannot live in the HARD array -
  # those grep the whole file, and this only judges the final paragraph.
  # Published prose: 0 of 50 chapters close this way.
  # The \r strip must happen BEFORE awk, not after. awk's paragraph mode (RS="")
  # splits on empty lines, and on a CRLF file every blank line contains a bare \r
  # that awk does not treat as empty - so the whole file collapsed into one record
  # and F1 silently checked the entire chapter for a coda phrase instead of the
  # closing paragraph. Every CRLF chapter failed; no LF chapter did.
  tailpara=$(tr -d '\r' < "$f" | awk 'BEGIN{RS=""} {last=$0} END{print last}' | tr '\n' ' ')
  if printf '%s' "$tailpara" | grep -qiE "$CODA_RE"; then
    printf '   FAIL  F1    closing coda            the chapter ends on an explanatory coda\n'
    printf '         (published prose: 0 of 50 chapters)  %s\n' "$(printf '%s' "$tailpara" | cut -c1-96)"
    fail=1
  else
    printf '   ok    F1    closing coda            none\n'
  fi

  for entry in "${WARN_ONLY[@]}"; do
    id=${entry%%|*}; rest=${entry#*|}
    name=${rest%%|*}; re=${rest#*|}
    n=$(grep -oiE "$re" "$f" | wc -l | tr -d ' ')
    if [ "$n" -gt 0 ]; then
      printf '   warn  %-5s %-22s x%s  (eyeball: excluded-engine sense?)\n' "$id" "$name" "$n"
      warn=1
    fi
  done

  if [ "$NOTE_CURLY" -eq 1 ]; then
    curly=$(grep -oE '[“”‘’]' "$f" | wc -l | tr -d ' ')
    printf '   note  —     curly quotes            %s (typography, not slop; published ~98/1k)\n' "$curly"
  fi

  if [ "$NOTE_DASHSPELL" -eq 1 ]; then
    # D1 above counts the Unicode em dash and nothing else, so it reads 0 for any file
    # that spells its dashes "--" or " - ". Measured over 140 public-domain English
    # novels, only 45% contain a U+2014 at all: the other 55% score zero while being
    # identically punctuated. The Montgomery corpus shows it inside a single author -
    # Anne of Green Gables reads 0.0 on D1 at 6.4/1k of actual dashes, and Anne of the
    # Island reads 9.1 at 9.1. This row counts the HABIT - any of the three spellings -
    # so the D1 number can be read against the right denominator. It never fails; see
    # calibration/CALIBRATION.md, "D1 measures typography as well as style".
    aw=$(awk 'END{print NR}' "$f")
    [ "${aw:-0}" -gt 0 ] || aw=1
    em=$(grep -o '—' "$f" | wc -l | tr -d ' ')
    dbl=$(grep -o -- '--' "$f" | wc -l | tr -d ' ')
    spc=$(grep -oE ' - ' "$f" | wc -l | tr -d ' ')
    any=$((em + dbl + spc))
    rate=$(awk -v a="$any" -v w="$aw" 'BEGIN{printf "%.1f", 1000*a/w}')
    emrate=$(awk -v a="$em" -v w="$aw" 'BEGIN{printf "%.1f", 1000*a/w}')
    printf '   note  —     dash spelling           %s/1k any form (%s/1k U+2014, %s --, %s spaced)\n' \
      "$rate" "$emrate" "$dbl" "$spc"
    printf '          19th-c. English novels, any form: median 5.8, max 20.6; 24%% over D1'"'"'s 10/1k cap.\n'
    printf '          If D1 passes at 0 while this reads high, the file spells dashes "--" and\n'
    printf '          D1 measured the encoding. That is a typography fact, not a style one.\n'
  fi

  # The stripped copy, if any, is no longer needed.
  if [ "$f" != "$orig" ] && [ -n "${f:-}" ]; then rm -f "$f"; fi
}

for target in "$@"; do
  if [ -d "$target" ]; then
    scanned=0
    for f in "$target"/*.md "$target"/*.txt; do
      [ -f "$f" ] && { scan_file "$f"; scanned=$((scanned+1)); }
    done
    # An empty expansion used to fall through to a vacuous PASS, because nothing
    # ran and "fail" stayed 0. A control that scans zero files proves nothing.
    if [ "$scanned" -eq 0 ]; then
      printf '   FAIL  empty scan: no .md or .txt prose in %s\n' "$target"
      fail=1
    fi
  elif [ -f "$target" ]; then
    scan_file "$target"
  else
    printf 'missing: %s\n' "$target"
    fail=1
  fi
done

echo
if [ "$fail" -eq 0 ] && [ "$warn" -eq 0 ]; then
  echo "RESULT: PASS (mechanical only - read it aloud before calling it clean)"
  exit 0
fi
if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS with warnings - inside every published cap, above the reference median."
  echo "        Warnings are not defects. Read it aloud before calling it clean."
  exit 0
fi
echo "RESULT: FAIL - fix the rows above before this chapter counts as drafted"
exit 1
